#!/usr/bin/env python3
"""Classify branch-local Step 6 progress from Riela's stdio input envelope."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any


NON_TEST_COMMAND_PATTERNS: tuple[str, ...] = (
    r"\bcargo\s+(?:build|check|clippy|fmt|doc)\b",
    r"\bgo\s+(?:build|vet|fmt)\b",
    r"\bswift\s+build\b",
    r"\b(?:npm|pnpm|yarn|bun)\s+run\s+(?:build|lint|format|fmt|typecheck|check)\b",
    r"\bmake\s+(?:build|lint|fmt|format|check)\b",
    r"\b(?:tsc|eslint|prettier|rustfmt|gofmt|swiftlint|swiftformat|ruff|black|mypy|shellcheck)\b",
    r"\bgit\s+(?:diff|status|log|show)\b",
    r"\bdiff\b",
    r"\bwasm-pack\s+build\b",
    r"\btree-sitter\s+generate\b",
    r"\bpython(?:3(?:\.\d+)?)?\s+-m\s+(?:json\.tool|py_compile|compileall)\b",
)


def safe_repo_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    value = value[2:] if value.startswith("./") else value
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in ("..", ".git") for part in path.parts):
        return None
    return path.as_posix()


def path_owned(path: str, owned: list[str]) -> bool:
    return any(path == entry or path.startswith(entry.rstrip("/") + "/") for entry in owned)


def checkpoint_manifest(item: dict[str, Any]) -> dict[str, Any] | None:
    commit = item.get("checkpointCommit")
    manifest_path = safe_repo_path(item.get("manifestPath"))
    if not isinstance(commit, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit) or manifest_path is None:
        return None
    try:
        result = subprocess.run(
            ["git", "show", f"{commit}:{manifest_path}"],
            cwd=Path.cwd(), capture_output=True, text=True, check=False,
        )
    except (OSError, UnicodeError):
        return None
    if result.returncode != 0:
        return None
    try:
        manifest = json.loads(result.stdout)
    except (json.JSONDecodeError, UnicodeError):
        return None
    return manifest if isinstance(manifest, dict) else None


def sibling_owned_blockers(envelope: dict[str, Any], blockers: list[Any]) -> list[dict[str, Any]] | None:
    variables = envelope.get("variables")
    item = variables.get("implementation") if isinstance(variables, dict) else None
    if not isinstance(item, dict):
        return None
    own_id = item.get("planId")
    own_paths_raw = item.get("writePaths")
    accepted_raw = item.get("acceptedPlanIds", [])
    if not isinstance(own_id, str) or not isinstance(own_paths_raw, list) or not isinstance(accepted_raw, list):
        return None
    own_paths = [safe_repo_path(path) for path in own_paths_raw]
    if any(path is None for path in own_paths):
        return None
    accepted = {plan_id for plan_id in accepted_raw if isinstance(plan_id, str)}
    manifest = checkpoint_manifest(item)
    if manifest is None or not isinstance(manifest.get("plans"), list):
        return None
    siblings: list[tuple[str, list[str]]] = []
    for plan in manifest["plans"]:
        if not isinstance(plan, dict):
            continue
        plan_id = plan.get("planId")
        plan_paths = plan.get("writePaths")
        if not isinstance(plan_id, str) or plan_id == own_id or plan_id in accepted or not isinstance(plan_paths, list):
            continue
        safe_paths = [safe_repo_path(path) for path in plan_paths]
        if any(path is None for path in safe_paths):
            continue
        siblings.append((plan_id, safe_paths))

    classified: list[dict[str, Any]] = []
    if not blockers:
        return None
    for blocker in blockers:
        if not isinstance(blocker, dict):
            return None
        raw_paths = blocker.get("paths")
        if raw_paths is None:
            raw_paths = [blocker.get("path")] if isinstance(blocker.get("path"), str) else None
        if not isinstance(raw_paths, list) or not raw_paths or any(not isinstance(path, str) for path in raw_paths):
            return None
        paths = [safe_repo_path(path) for path in raw_paths]
        if any(path is None or path_owned(path, own_paths) for path in paths):
            return None
        owners: set[str] = set()
        for path in paths:
            path_owners = {plan_id for plan_id, write_paths in siblings if path_owned(path, write_paths)}
            if not path_owners:
                return None
            owners.update(path_owners)
        entry: dict[str, Any] = {"paths": paths, "ownerPlanIds": sorted(owners)}
        for key in ("command", "exitStatus", "message"):
            if key in blocker:
                entry[key] = blocker[key]
        classified.append(entry)
    return classified


def write_sibling_blocker_evidence(item: dict[str, Any], deferred: list[dict[str, Any]]) -> str | None:
    evidence_root = safe_repo_path(item.get("evidenceRoot"))
    plan_id = item.get("planId")
    if (evidence_root is None or PurePosixPath(evidence_root).parts[0] != "tmp"
            or not isinstance(plan_id, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", plan_id)):
        return None
    repository = Path.cwd().resolve()
    tmp_root = (repository / "tmp").resolve()
    target_dir = repository / evidence_root / plan_id
    try:
        resolved_dir = target_dir.resolve()
        resolved_dir.relative_to(tmp_root)
        target_dir.mkdir(parents=True, exist_ok=True)
        resolved_dir = target_dir.resolve()
        resolved_dir.relative_to(tmp_root)
        document = {
            "schemaVersion": 1,
            "planId": plan_id,
            "checkpointCommit": item["checkpointCommit"],
            "manifestPath": safe_repo_path(item["manifestPath"]),
            "siblingOwnedBlockers": deferred,
        }
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=resolved_dir, delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                json.dump(document, temporary, separators=(",", ":"), ensure_ascii=False)
                temporary.write("\n")
            destination = resolved_dir / "sibling-owned-blockers.json"
            os.replace(temporary_path, destination)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
        return (Path(evidence_root) / plan_id / "sibling-owned-blockers.json").as_posix()
    except (OSError, ValueError, KeyError):
        return None


def normalized_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return [item for item in value if item not in (None, "", [], {})]


def canonical_items(value: Any) -> list[Any]:
    unique: dict[str, Any] = {}
    for item in normalized_list(value):
        key = json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        unique[key] = item
    return [unique[key] for key in sorted(unique)]


def concrete_verification(value: Any) -> list[dict[str, Any]]:
    records = canonical_items(value)
    return [
        record
        for record in records
        if isinstance(record, dict)
        and (
            record.get("negativeControl") is True
            or (
                isinstance(record.get("command"), str)
                and bool(record["command"].strip())
                and any(record.get(key) not in (None, "") for key in ("outcome", "exitStatus", "exitCode", "status"))
            )
        )
    ]


def _structured_exit_status(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"-?\d+", value):
        return int(value)
    return None


def _outcome_exit_status(record: dict[str, Any]) -> int | None:
    outcome = record.get("outcome")
    if not isinstance(outcome, str):
        return None
    match = re.match(
        r"^\s*exit(?:\s+(?:status|code))?\s*[=:]?\s*(-?\d+)\b",
        outcome,
        re.IGNORECASE,
    )
    return int(match.group(1)) if match else None


def record_exit_status(record: dict[str, Any]) -> int | None:
    """Read an integer status, preferring structured fields over outcome text."""
    for key in ("exitStatus", "exitCode"):
        if key in record and record.get(key) not in (None, ""):
            parsed = _structured_exit_status(record.get(key))
            if parsed is not None:
                return parsed
    return _outcome_exit_status(record)


def exit_status_invalid(record: dict[str, Any]) -> bool:
    structured: list[int] = []
    for key in ("exitStatus", "exitCode"):
        value = record.get(key)
        if key not in record or value in (None, ""):
            continue
        parsed = _structured_exit_status(value)
        if parsed is None:
            return True
        structured.append(parsed)
    if len(structured) == 2 and structured[0] != structured[1]:
        return True
    outcome_status = _outcome_exit_status(record)
    return bool(structured and outcome_status is not None and structured[0] != outcome_status)


def normalize_command(text: str) -> str:
    return " ".join(text.split())


def negative_control_status(record: dict[str, Any], planned: list[str] | None) -> str | None:
    if record.get("negativeControl") is not True:
        return None
    status = record_exit_status(record)
    expected = record.get("expectedExitStatus")
    if (
        exit_status_invalid(record)
        or isinstance(status, bool)
        or not isinstance(status, int)
        or status == 0
        or ("expectedExitStatus" in record and (
            isinstance(expected, bool) or not isinstance(expected, int) or expected != status
        ))
    ):
        return "invalid"
    command = record.get("command")
    if not isinstance(command, str) or not command.strip():
        return "invalid"
    if planned is not None:
        if normalize_command(command) in {normalize_command(item) for item in planned}:
            return "invalid"
    return "valid"


def verification_succeeded(record: dict[str, Any]) -> bool:
    if record.get("environmentBlocked") is True or record.get("environment_blocked") is True:
        return False
    failure_count_keys = {"failureCount", "failedTestCount", "testsFailed"}

    def has_nonzero_or_invalid_failure_count(value: Any) -> bool:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in failure_count_keys:
                    if (
                        isinstance(nested, bool)
                        or not isinstance(nested, (int, float))
                        or nested != 0
                    ):
                        return True
                if has_nonzero_or_invalid_failure_count(nested):
                    return True
        elif isinstance(value, list):
            return any(has_nonzero_or_invalid_failure_count(item) for item in value)
        return False

    if has_nonzero_or_invalid_failure_count(record):
        return False
    for key in ("status", "outcome"):
        value = record.get(key)
        if not isinstance(value, str):
            continue
        normalized = value.strip().lower()
        if normalized in {
            "blocked", "cancelled", "canceled", "failed", "failure", "not run", "skipped",
        } or re.match(r"^(?:blocked|cancelled|canceled|failed|failure|not run|skipped)\b", normalized):
            return False
        if re.search(r"\b[1-9]\d*\s+(?:(?:tests?|checks?)\s+)?(?:failed|failures?)\b", normalized):
            return False
    if exit_status_invalid(record):
        return False
    status = record_exit_status(record)
    if status is not None:
        return status == 0
    for key in ("status", "outcome"):
        value = record.get(key)
        if isinstance(value, str) and value.strip().lower() in {"pass", "passed", "success", "succeeded", "ok"}:
            return True
    return False


def declared_behavioral(record: dict[str, Any]) -> bool:
    kind = record.get("kind")
    return isinstance(kind, str) and kind.strip().lower() == "behavioral-test"


def allowlisted_test_command(command: str) -> bool:
    command = command.lower()
    test_patterns = (
        r"\bswift\s+test\b", r"\bcargo\s+test\b",
        r"\bcargo\s+nextest\s+run\b", r"\bgo\s+test\b", r"\bpytest\b",
        # Standard-library Python runner used by package tests.
        r"\bpython(?:3(?:\.\d+)?)?\s+-m\s+unittest\b",
        r"\bctest\b", r"\bbun\s+test\b", r"\bvitest\s+run\b",
        # Some packages run a deterministic Bun regression runner directly.
        # Require a test-directory runner name; the positive count is checked
        # separately before it can satisfy the behavioral gate.
        r"\bbun\s+(?:\S*/)?tests?/(?:check|test|verify)[\w.-]*\.(?:[cm]?[jt]s|[jt]sx)\b",
        r"\b(?:npm|pnpm|yarn)\s+(?:run\s+)?test\b",
        r"\b(?:task|mise\s+run|make)\s+test\b", r"\bxcodebuild\b.*\btest\b",
        # Grammar and runtime-native runners; project tasks whose name
        # contains "test" (for example `mise run ts-test`, `npm run test:unit`).
        r"\btree-sitter\s+test\b", r"\bdeno\s+test\b", r"\bnode\s+--test\b",
        r"\b(?:task|mise\s+run|make|(?:npm|pnpm|yarn|bun)\s+run)\s+[\w:.-]*test[\w:.-]*",
    )
    return any(re.search(pattern, command) for pattern in test_patterns)


def behavioral_kind(record: dict[str, Any]) -> str | None:
    raw_command = record.get("command", "")
    command = raw_command.lower() if isinstance(raw_command, str) else ""
    # Discovery proves test registration, not behavioral execution. It may
    # accompany a later positive-count test run without failing that run.
    if re.search(r"\bswift\s+test\b", command) and re.search(
        r"(?:\slist(?:\s|$)|--list-tests\b)", command
    ):
        return None
    if allowlisted_test_command(command):
        return "test"
    if declared_behavioral(record) and not any(
        re.search(pattern, command) for pattern in NON_TEST_COMMAND_PATTERNS
    ):
        return "test"
    return None


def positive_test_count(record: dict[str, Any]) -> bool:
    count_keys = {"testCount", "testsRun", "testsPassed", "positiveTestCount", "passedTestCount"}
    structured_counts: list[float] = []

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in count_keys:
                    try:
                        structured_counts.append(float(nested))
                    except (TypeError, ValueError):
                        pass
                collect(nested)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    collect(record)
    if structured_counts:
        return all(count > 0 for count in structured_counts)

    outcome = record.get("outcome")
    if not isinstance(outcome, str):
        return False
    match = re.search(
        r"^\s*(?:passed\s+[1-9]\d*\s+selected\s+tests?|"
        r"[1-9]\d*\s+selected\s+tests?\s+passed|"
        r"[1-9]\d*\s+selected\s+tests?|"
        r"passed:\s*[1-9]\d*\s+tests?)(?:\s+with\s+|,\s*)0\s+failures?\b",
        outcome,
        flags=re.IGNORECASE,
    )
    return match is not None


def successful_behavioral_verification(record: dict[str, Any]) -> bool:
    if not behavioral_kind(record) or not verification_succeeded(record) or not positive_test_count(record):
        return False
    command = record.get("command")
    if declared_behavioral(record) and not (
        isinstance(command, str) and allowlisted_test_command(command)
    ):
        return (
            record_exit_status(record) == 0
            and type(record.get("testsRun")) is int
            and record["testsRun"] > 0
            and type(record.get("failureCount")) is int
            and record["failureCount"] == 0
        )
    return True


def source_identity(record: dict[str, Any]) -> str | None:
    identity_keys = {"sourceHash", "treeHash", "revision", "commitHash", "sourceIdentity"}

    def find(value: Any) -> str | None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in identity_keys and isinstance(nested, str) and nested.strip():
                    return nested.strip()
            for nested in value.values():
                found = find(nested)
                if found:
                    return found
        elif isinstance(value, list):
            for nested in value:
                found = find(nested)
                if found:
                    return found
        return None

    return find(record)


def environment_blocked(record: dict[str, Any]) -> bool:
    if record.get("environmentBlocked") is True or record.get("environment_blocked") is True:
        return True
    blocker_type = record.get("blockerType")
    status = record.get("status")
    return (
        isinstance(blocker_type, str) and blocker_type.lower() in {"environment", "environmental"}
    ) or (isinstance(status, str) and status.lower() in {"environment-blocked", "blocked-environment"})


def inherited_behavioral_evidence(
    current: list[dict[str, Any]],
    previous: list[dict[str, Any]],
    current_identity: str | None = None,
    previous_identity: str | None = None,
) -> bool:
    prior_by_identity = {
        source_identity(record) or previous_identity
        for record in previous
        if successful_behavioral_verification(record) and (source_identity(record) or previous_identity)
    }
    return bool(prior_by_identity) and any(
        behavioral_kind(record)
        and environment_blocked(record)
        and (source_identity(record) or current_identity) in prior_by_identity
        for record in current
    )


def has_behavioral_evidence(
    current: list[dict[str, Any]],
    previous: list[dict[str, Any]],
    current_identity: str | None = None,
    previous_identity: str | None = None,
) -> bool:
    return any(successful_behavioral_verification(record) for record in current) or inherited_behavioral_evidence(
        current, previous, current_identity, previous_identity
    )


def planned_verification_commands(envelope: dict[str, Any]) -> list[str] | None:
    """Return the committed plan verification commands from the fanout item."""
    variables = envelope.get("variables")
    item = variables.get("implementation") if isinstance(variables, dict) else None
    commands = item.get("verification") if isinstance(item, dict) else None
    if not isinstance(commands, list):
        return None
    cleaned = [command for command in commands if isinstance(command, str) and command.strip()]
    return cleaned or None


def plan_requires_behavioral_tests(envelope: dict[str, Any]) -> bool:
    """A committed plan whose verification contract has no test runner is static-only.

    Documentation, packaging, and script-only plans legitimately verify with
    lint, syntax, and content checks. Fail closed when the committed contract
    is unavailable so code plans keep the positive-count behavioral gate.
    """
    planned = planned_verification_commands(envelope)
    if planned is None:
        return True
    return any(behavioral_kind({"command": command}) for command in planned)


def has_failed_behavioral_evidence(
    current: list[dict[str, Any]],
    previous: list[dict[str, Any]],
    current_identity: str | None = None,
    previous_identity: str | None = None,
) -> bool:
    inherited = inherited_behavioral_evidence(current, previous, current_identity, previous_identity)
    return any(
        behavioral_kind(record)
        and not successful_behavioral_verification(record)
        and not (environment_blocked(record) and inherited)
        for record in current
    )


def task_local_evidence_file(value: Any) -> Path | None:
    if not isinstance(value, str):
        return None
    relative = Path(value)
    if relative.is_absolute() or not relative.parts or relative.parts[0] != "tmp":
        return None
    root = (Path.cwd() / "tmp").resolve()
    resolved = (Path.cwd() / relative).resolve()
    return resolved if resolved.is_relative_to(root) and resolved.is_file() else None


def baseline_review_candidate(record: dict[str, Any]) -> dict[str, Any] | None:
    """Forward a proven matching failure set for review, never as a passing test."""
    if not behavioral_kind(record) or verification_succeeded(record):
        return None
    count = record.get("failureCount")
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        return None
    tests_run = record.get("testsRun")
    if isinstance(tests_run, bool) or not isinstance(tests_run, int) or tests_run <= count:
        return None
    exit_code = record.get("exitCode")
    if isinstance(exit_code, bool) or not isinstance(exit_code, int) or exit_code == 0:
        return None

    reference = record.get("comparison")
    comparison_path = reference.get("path") if isinstance(reference, dict) else reference
    comparison_file = task_local_evidence_file(comparison_path)
    if comparison_file is None or task_local_evidence_file(record.get("log")) is None:
        return None
    try:
        comparison = json.loads(comparison_file.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(comparison, dict) or comparison.get("identical") is not True:
        return None
    if isinstance(reference, dict) and any(
        reference.get(key) != comparison.get(key)
        for key in ("identical", "aggregateAssertionCount", "baselineAssertionCount", "aggregateOnly", "baselineOnly")
    ):
        return None
    counts = (comparison.get("aggregateAssertionCount"), comparison.get("baselineAssertionCount"))
    if any(isinstance(value, bool) or not isinstance(value, int) or value != count for value in counts):
        return None
    if comparison.get("aggregateOnly") != [] or comparison.get("baselineOnly") != []:
        return None
    aggregate_log = comparison.get("aggregateLog")
    if aggregate_log is not None and aggregate_log != record["log"]:
        return None
    baseline_log = comparison.get("baselineLog")
    if baseline_log is not None and task_local_evidence_file(baseline_log) is None:
        return None
    return {
        "command": record["command"],
        "exitCode": record["exitCode"],
        "failureCount": count,
        "comparison": comparison_path,
        "log": record["log"],
        "baselineLog": baseline_log,
        "decision": "pending-independent-review",
    }


def matched_baseline_record(record: dict[str, Any], candidates: list[dict[str, Any]]) -> bool:
    """A failed baseline command supports a candidate; it is not a current-source gate."""
    return bool(behavioral_kind(record)) and any(
        candidate["baselineLog"] == record.get("log")
        and record.get("failureCount") == candidate["failureCount"]
        and isinstance(record.get("testsRun"), int)
        and not isinstance(record["testsRun"], bool)
        and record["testsRun"] > candidate["failureCount"]
        and isinstance(record.get("exitCode"), int)
        and not isinstance(record["exitCode"], bool)
        and record["exitCode"] != 0
        for candidate in candidates
        if candidate["baselineLog"] is not None
    )


# Finding statuses that do not leave work open in this plan: the finding is
# already resolved, or it is explicitly handed to a later owning plan.
NON_BLOCKING_FINDING_STATUSES = {
    "resolved", "fixed", "closed", "addressed", "not_applicable", "superseded",
    "pending_downstream", "owned_elsewhere",
}


def open_finding_status(finding: dict[str, Any]) -> bool:
    status = finding.get("status")
    if not isinstance(status, str):
        return True
    return re.sub(r"[\s-]+", "_", status.strip().lower()) not in NON_BLOCKING_FINDING_STATUSES


def material_findings(payload: dict[str, Any]) -> list[Any]:
    self_check = payload.get("authorSelfCheck")
    self_check = self_check if isinstance(self_check, dict) else {}
    candidates = (
        normalized_list(payload.get("risks"))
        + normalized_list(payload.get("findings"))
        + normalized_list(self_check.get("findings"))
        + normalized_list(self_check.get("residualRisks"))
    )
    return [
        finding
        for finding in candidates
        if (
            isinstance(finding, dict)
            and isinstance(finding.get("severity"), str)
            and finding["severity"].lower() in {"critical", "high", "mid", "medium"}
            and open_finding_status(finding)
        ) or (
            isinstance(finding, str)
            and re.match(r"^\s*(?:critical|high|mid|medium)\s*[:\-]\s*\S", finding, re.IGNORECASE)
        )
    ]


def normalized_evidence(payload: dict[str, Any]) -> dict[str, list[Any]]:
    return {
        "changedFiles": canonical_items(payload.get("changedFiles")),
        "verification": concrete_verification(payload.get("verification")),
        "implPlanUpdates": canonical_items(payload.get("implPlanUpdates")),
    }


def canonical_fingerprint(payload: dict[str, Any]) -> str:
    evidence = normalized_evidence(payload)
    encoded = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def implementation_messages(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    input_payload = envelope.get("input", {})
    metadata = input_payload.get("_rielaInput", {}) if isinstance(input_payload, dict) else {}
    messages = metadata.get("messages", []) if isinstance(metadata, dict) else []
    if not isinstance(messages, list):
        return []
    candidates = [
        message
        for message in messages
        if isinstance(message, dict)
        and message.get("fromStepId") == "step6-implement"
        and isinstance(message.get("payload"), dict)
    ]
    return sorted(candidates, key=lambda message: message.get("createdOrder", 0))


def blocked_result(
    current: dict[str, Any], blocker_type: str, message: str, fingerprint: str,
    failing_commands: list[str] | None = None,
) -> dict[str, Any]:
    plan_id = current.get("planId") or current.get("dispatchId") or current.get("branchId")
    if not plan_id:
        implementation_item = current.get("implementationItem")
        if isinstance(implementation_item, dict):
            plan_id = implementation_item.get("planId") or implementation_item.get("dispatchId")
    if not plan_id:
        plan_paths = current.get("implPlanPaths")
        if isinstance(plan_paths, list) and plan_paths and isinstance(plan_paths[0], str):
            plan_id = Path(plan_paths[0]).stem
    plan_id = plan_id or "unknown-plan"
    existing = normalized_list(current.get("blockers"))
    blocker = {
        "type": blocker_type,
        "planId": plan_id,
        "message": message,
        "evidenceFingerprint": fingerprint,
    }
    if failing_commands:
        blocker["failingCommands"] = failing_commands[:5]
    resume = {
        "implementation-dependency": "Resolve the reported dependency and rerun the blocked plan.",
        "implementation-incomplete": "Complete the accepted implementation work and clear the explicit incomplete state before review.",
        "implementation-material-finding": "Resolve every high or medium implementation finding before review.",
        "implementation-no-progress": "Make a concrete source/test/plan change and report the changed paths plus new verification evidence.",
        "implementation-materially-unverified": (
            "Run and report verification that exercises the changed implementation before review. "
            "Accepted runners include swift test, cargo test, cargo nextest run, go test, pytest, "
            "python -m unittest, ctest, bun test, vitest run, npm/pnpm/yarn test, tree-sitter test, "
            "deno test, node --test, and task/mise run/make/npm|pnpm|yarn|bun run commands whose "
            "name contains test. Other runners must report "
            '{"kind": "behavioral-test", "exitStatus": 0, "testsRun": >0, "failureCount": 0}. '
            "Build, lint, format and diff commands never count."
        ),
        "implementation-invalid-evidence": "Return the required Step 6 evidence arrays in the implementation output.",
    }[blocker_type]
    payload = {
        **current,
        "implementation_blocked": True,
        "implementation_continue": False,
        "status": "blocked",
        "blockerType": blocker_type,
        "evidenceFingerprint": fingerprint,
        "blockers": existing + [blocker],
        "resumeCriteria": normalized_list(current.get("resumeCriteria")) + [resume],
    }
    return {"when": {"implementation_blocked": True}, "payload": payload}


def continuation_result(current: dict[str, Any], fingerprint: str, attempt: int) -> dict[str, Any]:
    payload = {
        **current,
        "implementation_blocked": False,
        "implementation_continue": True,
        "status": "implementation-in-progress",
        "evidenceFingerprint": fingerprint,
        "continuationAttempt": attempt,
        "blockers": [],
        "resumeCriteria": [],
    }
    return {"when": {"implementation_continue": True}, "payload": payload}


def incomplete_streak(messages: list[dict[str, Any]]) -> int:
    count = 0
    for message in reversed(messages):
        payload = message["payload"]
        if payload.get("implementationIncomplete") is not True and payload.get("implementation_incomplete") is not True:
            break
        count += 1
    return count


def classify(envelope: dict[str, Any]) -> dict[str, Any]:
    messages = implementation_messages(envelope)
    if not messages:
        empty_fingerprint = canonical_fingerprint({})
        return blocked_result(
            {},
            "implementation-invalid-evidence",
            "No Step 6 implementation output was delivered to the progress gate.",
            empty_fingerprint,
        )

    current = messages[-1]["payload"]
    fingerprint = canonical_fingerprint(current)
    current_evidence = normalized_evidence(current)
    changed_files = current_evidence["changedFiles"]
    verification = current_evidence["verification"]
    plan_updates = current_evidence["implPlanUpdates"]
    previous_evidence = normalized_evidence(messages[-2]["payload"]) if len(messages) > 1 else None

    raw_blockers = current.get("blockers") if isinstance(current.get("blockers"), list) else []
    deferred: list[dict[str, Any]] = []
    if current.get("implementation_blocked") is True or raw_blockers:
        classified = sibling_owned_blockers(envelope, raw_blockers) if raw_blockers else None
        if classified is None:
            return blocked_result(
                current,
                "implementation-dependency",
                "Step 6 reported an unresolved implementation blocker.",
                fingerprint,
            )
        deferred = classified
    incomplete = current.get("implementationIncomplete") is True or current.get("implementation_incomplete") is True
    required = ("changedFiles", "verification", "implPlanUpdates")
    if not all(key in current and isinstance(current[key], list) for key in required):
        return blocked_result(
            current,
            "implementation-invalid-evidence",
            "Step 6 omitted one or more required evidence arrays.",
            fingerprint,
        )
    if not changed_files and not verification and not plan_updates:
        return blocked_result(
            current,
            "implementation-no-progress",
            "Step 6 produced no changed files, new verification, or implementation-plan progress.",
            fingerprint,
        )
    if (changed_files or plan_updates) and not verification:
        return blocked_result(
            current,
            "implementation-materially-unverified",
            "Step 6 reported material changes without verification evidence.",
            fingerprint,
        )
    findings = material_findings(current)
    if findings:
        return blocked_result(
            current,
            "implementation-material-finding",
            "Step 6 reported unresolved high or medium implementation findings or risks.",
            fingerprint,
        )
    planned = planned_verification_commands(envelope)
    negative_valid = [record for record in verification if negative_control_status(record, planned) == "valid"]
    negative_invalid = [record for record in verification if negative_control_status(record, planned) == "invalid"]
    if negative_invalid:
        return blocked_result(
            current,
            "implementation-materially-unverified",
            "Step 6 reported a negative-control record that did not fail as declared or names a committed verification command.",
            fingerprint,
            [record["command"] for record in negative_invalid if isinstance(record.get("command"), str)],
        )
    gated = [record for record in verification if negative_control_status(record, planned) is None]
    prior_verification = previous_evidence["verification"] if previous_evidence else []
    previous_payload = messages[-2]["payload"] if len(messages) > 1 else {}
    current_identity = source_identity(current)
    previous_identity = source_identity(previous_payload)
    reviewable_records = (
        [(record, candidate) for record in gated if (candidate := baseline_review_candidate(record))]
        if not incomplete else []
    )
    baseline_candidates = [candidate for _, candidate in reviewable_records]
    unreviewable_verification = [
        record for record in gated
        if not any(record is item for item, _ in reviewable_records)
        and not matched_baseline_record(record, baseline_candidates)
    ]
    if has_failed_behavioral_evidence(
        unreviewable_verification, prior_verification, current_identity, previous_identity
    ):
        return blocked_result(
            current,
            "implementation-materially-unverified",
            "Step 6 reported a failed, blocked, skipped, or zero-count behavioral test command.",
            fingerprint,
            [record["command"] for record in unreviewable_verification
             if behavioral_kind(record) and not successful_behavioral_verification(record)
             and isinstance(record.get("command"), str)],
        )
    requires_behavioral_tests = plan_requires_behavioral_tests(envelope)
    if requires_behavioral_tests and not has_behavioral_evidence(
        gated, prior_verification, current_identity, previous_identity
    ):
        return blocked_result(
            current,
            "implementation-materially-unverified",
            "Step 6 reported no successful behavioral test evidence with a positive test count.",
            fingerprint,
            [record["command"] for record in gated if isinstance(record.get("command"), str)],
        )
    if not requires_behavioral_tests and not any(verification_succeeded(record) for record in gated):
        return blocked_result(
            current,
            "implementation-materially-unverified",
            "Step 6 reported no successful verification for a plan whose committed verification contract has no behavioral test command.",
            fingerprint,
            [record["command"] for record in gated if isinstance(record.get("command"), str)],
        )

    has_new_item = previous_evidence is None or any(
        set(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for item in current_evidence[key])
        - set(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for item in previous_evidence[key])
        for key in current_evidence
    )
    if not has_new_item:
        return blocked_result(
            current,
            "implementation-no-progress",
            "Step 6 added no branch-local changed file, concrete verification, or implementation-plan progress item beyond the immediately preceding attempt.",
            fingerprint,
        )

    if incomplete:
        streak = incomplete_streak(messages)
        if changed_files and plan_updates and streak < 3:
            return continuation_result(current, fingerprint, streak)
        return blocked_result(
            current,
            "implementation-incomplete",
            "Step 6 remains incomplete after the bounded continuation attempts or lacks changed-file/plan-progress evidence.",
            fingerprint,
        )

    self_check = current.get("authorSelfCheck")
    verification_gaps = normalized_list(self_check.get("verificationGaps")) if isinstance(self_check, dict) else []
    if verification_gaps and not inherited_behavioral_evidence(
        gated, prior_verification, current_identity, previous_identity
    ):
        return blocked_result(
            current,
            "implementation-materially-unverified",
            "Step 6 author self-check reported unresolved verification gaps.",
            fingerprint,
        )

    payload = {
        **current,
        "implementation_blocked": False,
        "implementation_continue": False,
        "status": "ready-for-test-integrity",
        "verificationPolicy": "behavioral-tests" if requires_behavioral_tests else "plan-declared-static",
        "blockerType": None,
        "evidenceFingerprint": fingerprint,
        "blockers": [],
        "resumeCriteria": [],
        "baselineReviewPending": baseline_candidates,
    }
    if deferred:
        variables = envelope.get("variables", {})
        item = variables.get("implementation", {}) if isinstance(variables, dict) else {}
        evidence_path = write_sibling_blocker_evidence(item, deferred) if isinstance(item, dict) else None
        if evidence_path is None:
            return blocked_result(
                current,
                "implementation-dependency",
                "Step 6 sibling-owned blockers could not be recorded for integration review.",
                fingerprint,
            )
        payload["siblingOwnedBlockers"] = deferred
        payload["siblingOwnedBlockersPath"] = evidence_path
    if negative_valid:
        payload["negativeControlEvidence"] = negative_valid
    else:
        payload.pop("negativeControlEvidence", None)
    return {"when": {"implementation_blocked": False}, "payload": payload}


def main() -> int:
    try:
        line = sys.stdin.readline()
        envelope = json.loads(line)
        if not isinstance(envelope, dict):
            raise ValueError("stdio envelope must be an object")
        print(json.dumps(classify(envelope), separators=(",", ":"), ensure_ascii=False))
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, separators=(",", ":")), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
