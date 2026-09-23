#!/usr/bin/env python3
"""Classify branch-local Step 6 progress from Riela's stdio input envelope."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from typing import Any


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
        and isinstance(record.get("command"), str)
        and bool(record["command"].strip())
        and any(record.get(key) not in (None, "") for key in ("outcome", "exitStatus", "exitCode", "status"))
    ]


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
    saw_exit_status = False
    for key in ("exitStatus", "exitCode"):
        if key in record and record.get(key) not in (None, ""):
            saw_exit_status = True
            if record.get(key) != 0 and record.get(key) != "0":
                return False
    if saw_exit_status:
        return True
    for key in ("status", "outcome"):
        value = record.get(key)
        if isinstance(value, str) and value.strip().lower() in {"pass", "passed", "success", "succeeded", "ok"}:
            return True
    return False


def behavioral_kind(record: dict[str, Any]) -> str | None:
    command = record.get("command", "").lower()
    test_patterns = (
        r"\bswift\s+test\b", r"\bcargo\s+test\b", r"\bgo\s+test\b", r"\bpytest\b",
        r"\bctest\b", r"\bbun\s+test\b", r"\b(?:npm|pnpm|yarn)\s+(?:run\s+)?test\b",
        r"\b(?:task|mise\s+run|make)\s+test\b", r"\bxcodebuild\b.*\btest\b",
    )
    if any(re.search(pattern, command) for pattern in test_patterns):
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
    return bool(behavioral_kind(record) and verification_succeeded(record) and positive_test_count(record))


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


def material_findings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    self_check = payload.get("authorSelfCheck")
    self_check = self_check if isinstance(self_check, dict) else {}
    candidates = (
        normalized_list(payload.get("risks"))
        + normalized_list(self_check.get("findings"))
        + normalized_list(self_check.get("residualRisks"))
    )
    return [
        finding
        for finding in candidates
        if isinstance(finding, dict)
        and isinstance(finding.get("severity"), str)
        and finding["severity"].lower() in {"critical", "high", "mid", "medium"}
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
    current: dict[str, Any], blocker_type: str, message: str, fingerprint: str
) -> dict[str, Any]:
    plan_id = current.get("planId") or current.get("dispatchId") or "unknown-plan"
    existing = normalized_list(current.get("blockers"))
    blocker = {
        "type": blocker_type,
        "planId": plan_id,
        "message": message,
        "evidenceFingerprint": fingerprint,
    }
    resume = {
        "implementation-dependency": "Resolve the reported dependency and rerun the blocked plan.",
        "implementation-incomplete": "Complete the accepted implementation work and clear the explicit incomplete state before review.",
        "implementation-material-finding": "Resolve every high or medium implementation finding before review.",
        "implementation-no-progress": "Make a concrete source/test/plan change and report the changed paths plus new verification evidence.",
        "implementation-materially-unverified": "Run and report verification that exercises the changed implementation before review.",
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

    if current.get("implementation_blocked") is True or normalized_list(current.get("blockers")):
        return blocked_result(
            current,
            "implementation-dependency",
            "Step 6 reported an unresolved implementation blocker.",
            fingerprint,
        )
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
    prior_verification = previous_evidence["verification"] if previous_evidence else []
    previous_payload = messages[-2]["payload"] if len(messages) > 1 else {}
    current_identity = source_identity(current)
    previous_identity = source_identity(previous_payload)
    if not has_behavioral_evidence(verification, prior_verification, current_identity, previous_identity):
        return blocked_result(
            current,
            "implementation-materially-unverified",
            "Step 6 reported no successful behavioral test evidence with a positive test count.",
            fingerprint,
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

    findings = material_findings(current)
    if findings:
        return blocked_result(
            current,
            "implementation-material-finding",
            "Step 6 reported unresolved high or medium implementation findings or risks.",
            fingerprint,
        )

    self_check = current.get("authorSelfCheck")
    verification_gaps = normalized_list(self_check.get("verificationGaps")) if isinstance(self_check, dict) else []
    if verification_gaps and not inherited_behavioral_evidence(
        verification, prior_verification, current_identity, previous_identity
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
        "blockerType": None,
        "evidenceFingerprint": fingerprint,
        "blockers": [],
        "resumeCriteria": [],
    }
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
