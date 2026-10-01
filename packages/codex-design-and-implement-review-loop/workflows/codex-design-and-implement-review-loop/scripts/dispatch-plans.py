#!/usr/bin/env python3
"""Project an accepted implementation manifest into native Riela fanout items."""

from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


# Native fanout change-tracking limits. These mirror the Riela core contract
# exactly; the preflight below never raises, lowers, or silently drops paths.
SOURCE_PATH_LIMIT = 512
SOURCE_ENTRY_LIMIT = 512
SOURCE_FILE_BYTE_LIMIT = 8_000_000
SOURCE_TOTAL_BYTE_LIMIT = 64_000_000
ARTIFACT_ROOT_LIMIT = 64
# Reporting bound for a single scanned root (the core artifact scan uses the
# same bound). Exceeding it only truncates counts; it never hides a violation.
SCAN_ENTRY_CAP = 200_000
AMENDMENT = "bounded checkpoint amendment required"


REVIEW_CONTEXT_KEYS = (
    "issueReference",
    "userProblem",
    "requiredOutcomes",
    "nonGoals",
    "constraints",
    "designDecisionsAndRationale",
    "intentionalTradeoffs",
    "supportedEdgeCases",
    "outOfScopeEdgeCases",
    "sourcePaths",
)


def messages_from(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    input_payload = envelope.get("input")
    metadata = input_payload.get("_rielaInput") if isinstance(input_payload, dict) else None
    messages = metadata.get("messages") if isinstance(metadata, dict) else None
    if not isinstance(messages, list):
        return []
    return sorted(
        (message for message in messages if isinstance(message, dict)),
        key=lambda message: message.get("createdOrder", 0),
    )


def nested_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, dict):
        return []
    result = [value]
    for nested in value.values():
        if isinstance(nested, dict):
            result.extend(nested_dicts(nested))
    return result


def latest_value(messages: list[dict[str, Any]], key: str) -> Any:
    for message in reversed(messages):
        payload = message.get("payload")
        for candidate in nested_dicts(payload):
            if key in candidate:
                return candidate[key]
    return None


def latest_integration_feedback(messages: list[dict[str, Any]]) -> dict[str, Any] | None:
    for message in reversed(messages):
        if message.get("fromStepId") != "integration-review":
            continue
        for candidate in nested_dicts(message.get("payload")):
            if candidate.get("needs_revision") is not True:
                continue
            findings = candidate.get("findings")
            if not isinstance(findings, list) or any(not isinstance(item, dict) for item in findings):
                raise ValueError("integration-review revision must provide structured findings")
            diagnostic = candidate.get("recoveryDiagnostic")
            if isinstance(diagnostic, dict):
                diagnostic = json.dumps(diagnostic, sort_keys=True, separators=(",", ":"))
            if diagnostic is not None and not isinstance(diagnostic, str):
                raise ValueError("integration-review recoveryDiagnostic must be text or an object")
            return {
                "findings": findings,
                "recoveryDiagnostic": diagnostic or "",
            }
        return None
    return None


def path_is_owned(path: str, owned_paths: list[str]) -> bool:
    return any(path == owned or path.startswith(f"{owned}/") for owned in owned_paths)


def clean_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def clean_string_list(value: Any, field: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{field} must be an array of non-empty strings")
    result = list(dict.fromkeys(item.strip() for item in value))
    if nonempty and not result:
        raise ValueError(f"{field} must not be empty")
    return result


def verification_commands(value: Any, field: str) -> list[str]:
    # A committed checkpoint from an earlier package may carry richer
    # verification notes. Project its commands without rewriting that commit.
    if isinstance(value, dict):
        if set(value) - {"commands", "evidenceRequirements"}:
            raise ValueError(f"{field} has unsupported fields")
        clean_string_list(value.get("evidenceRequirements", []), f"{field}.evidenceRequirements")
        value = value.get("commands")
    return clean_string_list(value, field)


def design_decisions(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("reviewContext.designDecisionsAndRationale must be an array")
    normalized: list[str] = []
    for item in value:
        if isinstance(item, dict) and set(item) == {"decision", "rationale"}:
            decision = clean_string(item["decision"], "reviewContext.designDecisionsAndRationale[].decision")
            rationale = clean_string(item["rationale"], "reviewContext.designDecisionsAndRationale[].rationale")
            normalized.append(f"{decision} Rationale: {rationale}")
        else:
            normalized.append(clean_string(item, "reviewContext.designDecisionsAndRationale[]"))
    return list(dict.fromkeys(normalized))


def safe_relative_path(value: Any, field: str, root: Path) -> str:
    path_text = clean_string(value, field)
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
        raise ValueError(f"{field} must be a safe repository-relative path")
    resolved = (root / path).resolve()
    if root != resolved and root not in resolved.parents:
        raise ValueError(f"{field} escapes the working directory")
    return path.as_posix()


def concrete_repository_path(value: Any, field: str, root: Path) -> str:
    if not isinstance(value, str):
        raise ValueError(
            f"{field} value {value!r} must be a concrete repository-relative file or directory path string "
            "(no objects, comma lists, braces, globs, or prose)"
        )
    path_text = value.strip()
    if not path_text or re.search(r"[,{}*?\[\]\s]", path_text):
        raise ValueError(
            f"{field} value {value!r} must be a concrete repository-relative file or directory path string "
            "(no objects, comma lists, braces, globs, or prose)"
        )
    return safe_relative_path(path_text, field, root)


def tracking_limits() -> dict[str, int]:
    return {
        "sourcePaths": SOURCE_PATH_LIMIT,
        "sourceEntries": SOURCE_ENTRY_LIMIT,
        "sourceFileBytes": SOURCE_FILE_BYTE_LIMIT,
        "sourceTotalBytes": SOURCE_TOTAL_BYTE_LIMIT,
        "artifactRoots": ARTIFACT_ROOT_LIMIT,
    }


def concrete_path_list(plan: dict[str, Any], key: str, plan_id: str, root: Path, *, required: bool) -> list[str]:
    value = plan.get(key) if required else plan.get(key, [])
    if not isinstance(value, list):
        raise ValueError(
            f"{plan_id}.{key} value {value!r} must be an array of concrete repository-relative file or directory path strings"
        )
    return [concrete_repository_path(path, f"{plan_id}.{key}[]", root) for path in value]


def plan_tracking_contract(plan: dict[str, Any], plan_id: str, root: Path) -> dict[str, list[str]]:
    """Split write ownership, source snapshot paths, and generated artifact roots.

    writePaths/sharedPaths keep ownership and conflict detection. artifactRoots
    (default []) name generated tool installs, caches, and binaries that the
    native fanout records as bounded manifests instead of content snapshots.
    """
    write_paths = concrete_path_list(plan, "writePaths", plan_id, root, required=True)
    shared_paths = concrete_path_list(plan, "sharedPaths", plan_id, root, required=False)
    artifact_roots = list(dict.fromkeys(
        concrete_path_list(plan, "artifactRoots", plan_id, root, required=False)
    ))
    if len(artifact_roots) > ARTIFACT_ROOT_LIMIT:
        raise ValueError(
            f"{AMENDMENT}: {plan_id}.artifactRoots declares {len(artifact_roots)} roots "
            f"(limit {ARTIFACT_ROOT_LIMIT})"
        )
    for artifact in artifact_roots:
        if artifact not in write_paths:
            raise ValueError(
                f"{AMENDMENT}: {plan_id}.artifactRoots entry '{artifact}' must exactly equal one of the plan's "
                "writePaths so write ownership is preserved"
            )
        if artifact in shared_paths:
            raise ValueError(
                f"{AMENDMENT}: {plan_id}.artifactRoots entry '{artifact}' must not appear in sharedPaths; "
                "a generated artifact root is uniquely owned by one plan"
            )
    for artifact in artifact_roots:
        for other in artifact_roots:
            if other != artifact and artifact.startswith(f"{other}/"):
                raise ValueError(
                    f"{AMENDMENT}: {plan_id}.artifactRoots overlap: '{artifact}' lies inside '{other}'"
                )
    artifact_set = set(artifact_roots)
    tracked_paths = [path for path in dict.fromkeys(write_paths + shared_paths) if path not in artifact_set]
    if not tracked_paths:
        if artifact_roots:
            raise ValueError(
                f"{AMENDMENT}: {plan_id} has no source snapshot paths after removing artifactRoots; "
                "add the authored audit manifest (for example <tool-root>/toolchain.json) or the plan's "
                "source files to writePaths"
            )
        raise ValueError(f"{plan_id} has no tracked write or shared paths")
    if len(tracked_paths) > SOURCE_PATH_LIMIT:
        raise ValueError(
            f"{AMENDMENT}: {plan_id} declares {len(tracked_paths)} source snapshot paths "
            f"(limit {SOURCE_PATH_LIMIT}); narrow writePaths/sharedPaths"
        )
    for artifact in artifact_roots:
        for tracked in tracked_paths:
            if artifact.startswith(f"{tracked}/"):
                raise ValueError(
                    f"{AMENDMENT}: {plan_id}.artifactRoots entry '{artifact}' lies inside source snapshot path "
                    f"'{tracked}'; narrow the source path to authored files (a narrow source file inside an "
                    "artifact root, such as an audit manifest, is allowed)"
                )
    return {
        "writePaths": write_paths,
        "sharedPaths": shared_paths,
        "artifactRoots": artifact_roots,
        "trackedPaths": tracked_paths,
    }


def symlink_ancestor(root: Path, relative: str) -> str | None:
    current = root
    parts: list[str] = []
    for part in Path(relative).parts:
        current = current / part
        parts.append(part)
        try:
            if stat.S_ISLNK(os.lstat(current).st_mode):
                return "/".join(parts)
        except FileNotFoundError:
            return None
    return None


def scan_root(root: Path, relative: str, selection: str, seen: set[str] | None = None) -> dict[str, Any]:
    """Walk one root without following symlinks and count it like the core.

    Directories and the root itself count as entries, and a missing declared
    root counts as one entry. `seen` deduplicates overlapping source roots,
    because the core expands every source path of an item into one shared map.
    """
    report: dict[str, Any] = {
        "path": relative,
        "selection": selection,
        "exists": False,
        "kind": "missing",
        "entries": 0,
        "bytes": 0,
        "maxFileBytes": 0,
        "maxFilePath": None,
        "expectedToGrow": selection == "artifact",
        "scanTruncated": False,
        "problems": [],
        "oversizedFiles": [],
    }
    seen = set() if seen is None else seen

    def problem(path: str, message: str) -> None:
        report["problems"].append({"path": path, "message": message})

    ancestor = symlink_ancestor(root, relative)
    if ancestor is not None:
        problem(ancestor, "fanout change tracking refuses symlink ancestry")
        report.update(exists=True, kind="symlink")
        return report
    try:
        status = os.lstat(root / relative)
    except FileNotFoundError:
        if relative not in seen:
            seen.add(relative)
            report["entries"] = 1
        return report
    except PermissionError:
        problem(relative, "fanout snapshot refuses unreadable entries")
        return report
    report["exists"] = True
    stack = [(relative, status)]
    while stack:
        path, entry = stack.pop()
        if report["entries"] >= SCAN_ENTRY_CAP:
            report["scanTruncated"] = True
            break
        mode = entry.st_mode
        if path == relative:
            report["kind"] = (
                "directory" if stat.S_ISDIR(mode) else "file" if stat.S_ISREG(mode) else "special"
            )
        if path in seen:
            # Already expanded through an enclosing source root of this plan.
            continue
        seen.add(path)
        report["entries"] += 1
        if stat.S_ISREG(mode):
            size = entry.st_size
            report["bytes"] += size
            if size > SOURCE_FILE_BYTE_LIMIT:
                report["oversizedFiles"].append({"path": path, "bytes": size})
            if size > report["maxFileBytes"]:
                report["maxFileBytes"], report["maxFilePath"] = size, path
            # The core opens source files and artifact-root files, but only
            # lstat()s regular files inside an artifact directory.
            if (selection == "source" or path == relative) and not os.access(root / path, os.R_OK):
                problem(path, "fanout snapshot refuses unreadable entries")
            continue
        if stat.S_ISLNK(mode):
            if selection == "source":
                problem(path, "fanout snapshot refuses symlink entries inside a source root")
            continue
        if not stat.S_ISDIR(mode):
            if selection == "source" or path == relative:
                problem(path, "fanout snapshot refuses special entries")
            continue
        try:
            children = sorted(os.listdir(root / path), reverse=True)
        except PermissionError:
            problem(path, "fanout snapshot refuses unreadable entries")
            continue
        for child in children:
            child_path = f"{path}/{child}"
            if child == ".git" and selection == "source":
                problem(child_path, "unsafe fanout change tracking path")
                continue
            try:
                stack.append((child_path, os.lstat(root / child_path)))
            except FileNotFoundError:
                problem(child_path, "entry disappeared during preflight scan")
    return report


def preflight_tracking(plan_id: str, contract: dict[str, list[str]], root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Report every selected root and reject source selections the core would refuse.

    Entry and byte limits apply to the union of the plan's source snapshot
    paths, exactly as the core expands them into one snapshot per capture.
    """
    roots: list[dict[str, Any]] = []
    errors: list[str] = []
    seen: set[str] = set()
    entries = 0
    total = 0
    advice = (
        "declare generated tool installs, caches, and binaries in artifactRoots (each must also be a writePaths "
        "entry) and keep an authored audit manifest in writePaths, or narrow writePaths"
    )
    for path in sorted(set(contract["trackedPaths"])):
        report = scan_root(root, path, "source", seen)
        roots.append(report)
        for item in report["problems"]:
            errors.append(f"{AMENDMENT}: plan {plan_id} source root '{path}': {item['message']} at '{item['path']}'")
        for oversized in report["oversizedFiles"]:
            errors.append(
                f"{AMENDMENT}: plan {plan_id} source root '{path}' contains '{oversized['path']}' with "
                f"{oversized['bytes']} bytes (limit {SOURCE_FILE_BYTE_LIMIT} per file); {advice}"
            )
        entries_before, total_before = entries, total
        entries += report["entries"]
        total += report["bytes"]
        if entries > SOURCE_ENTRY_LIMIT >= entries_before:
            errors.append(
                f"{AMENDMENT}: plan {plan_id} source root '{path}' currently has {report['entries']} entries "
                f"(the plan's source snapshot paths expand to {entries}"
                f"{'+' if report['scanTruncated'] else ''} entries; limit {SOURCE_ENTRY_LIMIT}); {advice}"
            )
        if total > SOURCE_TOTAL_BYTE_LIMIT >= total_before:
            errors.append(
                f"{AMENDMENT}: plan {plan_id} source root '{path}' brings the source snapshot total to {total} bytes "
                f"(limit {SOURCE_TOTAL_BYTE_LIMIT}); {advice}"
            )
    for path in contract["artifactRoots"]:
        report = scan_root(root, path, "artifact")
        report["oversizedFiles"] = []
        roots.append(report)
        for item in report["problems"]:
            errors.append(f"{AMENDMENT}: plan {plan_id} artifact root '{path}': {item['message']} at '{item['path']}'")
    return roots, errors


def validate_manifest_contract(
    manifest: Any, root: Path, *, skip_plan_ids: set[str] | None = None
) -> dict[str, Any]:
    """Validate every manifest plan's tracking contract and report current root sizes."""
    skip_plan_ids = skip_plan_ids or set()
    report: dict[str, Any] = {"valid": False, "limits": tracking_limits(), "plans": [], "errors": []}
    if not isinstance(manifest, dict) or not isinstance(manifest.get("plans"), list) or not manifest["plans"]:
        report["errors"].append("dispatch manifest plans must be a non-empty array")
        return report
    seen_ids: set[str] = set()
    for index, plan in enumerate(manifest["plans"]):
        entry: dict[str, Any] = {"planId": None, "limits": tracking_limits(), "roots": [], "errors": []}
        report["plans"].append(entry)
        try:
            if not isinstance(plan, dict):
                raise ValueError(f"plans[{index}] must be an object")
            plan_id = clean_string(plan.get("planId"), "plans[].planId")
            entry["planId"] = plan_id
            if plan_id in seen_ids:
                raise ValueError(f"dispatch manifest plan IDs must be unique: {plan_id}")
            seen_ids.add(plan_id)
            contract = plan_tracking_contract(plan, plan_id, root)
            entry.update(contract)
            if plan_id not in skip_plan_ids:
                entry["roots"], errors = preflight_tracking(plan_id, contract, root)
                entry["errors"].extend(errors)
        except ValueError as error:
            entry["errors"].append(str(error))
        report["errors"].extend(entry["errors"])
    report["valid"] = not report["errors"]
    return report


def checkpoint_source(messages: list[dict[str, Any]], root: Path) -> tuple[str, str]:
    pushes = [message for message in messages if message.get("fromStepId") == "plan-git-push"]
    commits = [message for message in messages if message.get("fromStepId") == "plan-git-commit"]
    if pushes:
        if len(pushes) != 1:
            raise ValueError("dispatch requires exactly one plan-git-push message")
        payload = pushes[0].get("payload")
        git_payload = payload.get("git") if isinstance(payload, dict) else None
        if not isinstance(git_payload, dict) or git_payload.get("operation") != "push" or git_payload.get("status") not in {"pushed", "already-pushed"}:
            raise ValueError("plan-git-push must attest a successful push")
        commit = clean_string(git_payload.get("commitHash"), "plan-git-push.git.commitHash")
        if re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit) is None:
            raise ValueError("plan-git-push commit hash is invalid")
        changed = git(root, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit)
        if changed.returncode != 0:
            raise ValueError("cannot read checkpoint committed files")
        committed = changed.stdout.splitlines()
    else:
        if len(commits) != 1:
            raise ValueError("dispatch requires exactly one checkpoint commit or push message")
        payload = commits[0].get("payload")
        git_payload = payload.get("git") if isinstance(payload, dict) else None
        if not isinstance(git_payload, dict) or git_payload.get("operation") != "commit":
            raise ValueError("plan-git-commit payload must contain commit metadata")
        commit = clean_string(git_payload.get("commitHash"), "plan-git-commit.git.commitHash")
        committed = git_payload.get("committedFiles")
    if not isinstance(committed, list):
        raise ValueError("checkpoint committed files must be an array")
    manifests: list[str] = []
    for value in committed:
        relative = safe_relative_path(value, "checkpoint.committedFiles[]", root)
        path = root / relative
        if path.suffix != ".json" or path.is_symlink() or not path.is_file():
            continue
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("plans"), list):
            manifests.append(relative)
    if len(manifests) == 1:
        return manifests[0], commit
    if len(manifests) > 1:
        added = git(
            root, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r",
            "--diff-filter=A", commit,
        )
        if added.returncode != 0:
            raise ValueError("cannot read newly added checkpoint files")
        new_manifests = set(added.stdout.splitlines()).intersection(manifests)
        if len(new_manifests) == 1:
            return new_manifests.pop(), commit
    raise ValueError("checkpoint must contain exactly one dispatch manifest")


def git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=False, capture_output=True, text=True
    )


def verify_checkpoint(root: Path, manifest_path: str, checkpoint: str) -> None:
    head = git(root, "rev-parse", "HEAD")
    if head.returncode != 0 or not head.stdout.strip():
        raise ValueError("working directory is not a Git checkout with a HEAD commit")
    if checkpoint != head.stdout.strip():
        raise ValueError("checkpointCommit must equal the current HEAD before implementation finalization")
    tracked = git(root, "cat-file", "-e", f"{checkpoint}:{manifest_path}")
    if tracked.returncode != 0:
        raise ValueError("dispatch manifest is not present in checkpointCommit")
    unchanged = git(root, "diff", "--quiet", checkpoint, "--", manifest_path)
    if unchanged.returncode != 0:
        raise ValueError("dispatch manifest differs from the committed checkpoint")


def issue_reference(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        identifier = value.get("communicationId") or value.get("intakeCommunication") or value.get("number")
        title = value.get("title")
        url = value.get("url")
        repository = value.get("repository")
        issue_number = value.get("issueNumber")
        draft_pr = value.get("draftPR")
        if isinstance(repository, str) and repository.strip():
            if type(issue_number) is int and issue_number > 0:
                return f"{repository.strip()}#{issue_number}"
            if type(draft_pr) is int and draft_pr > 0:
                suffix = f": {identifier}" if isinstance(identifier, str) and identifier.strip() else ""
                return f"{repository.strip()} Draft PR #{draft_pr}{suffix}"
        parts = [str(part).strip() for part in (identifier, title, url) if part not in (None, "")]
        if parts:
            return ": ".join(parts)
    raise ValueError("reviewContext.issueReference must identify the accepted request")


def normalized_review_context(value: Any, root: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("reviewContext must be an object")
    reference = value.get("issueReference")
    if reference is None:
        reference = {"communicationId": value.get("intakeCommunicationId")}
    result: dict[str, Any] = {"issueReference": issue_reference(reference)}
    result["userProblem"] = clean_string(value.get("userProblem"), "reviewContext.userProblem")
    for key in REVIEW_CONTEXT_KEYS[2:]:
        result[key] = (
            design_decisions(value.get(key))
            if key == "designDecisionsAndRationale"
            else clean_string_list(
                value.get(key),
                f"reviewContext.{key}",
                nonempty=key in {"requiredOutcomes", "sourcePaths"},
            )
        )
    result["sourcePaths"] = [
        safe_relative_path(path, "reviewContext.sourcePaths[]", root)
        for path in result["sourcePaths"]
    ]
    return result


def manifest_evidence_root(manifest: dict[str, Any], root: Path) -> str:
    value = manifest.get("evidenceRoot")
    if value is None:
        # Older committed manifests can use the documented tmp/<task-id> layout.
        task_id = clean_string(manifest.get("taskId"), "taskId")
        if re.fullmatch(r"[A-Za-z0-9_-]+", task_id) is None:
            raise ValueError("taskId must be a safe path component")
        value = f"tmp/{task_id}"
    return safe_relative_path(value, "evidenceRoot", root)


def accepted_dependency_ids(manifest: dict[str, Any], root: Path) -> set[str]:
    value = manifest.get("acceptedDependencies", [])
    if not isinstance(value, list):
        raise ValueError("acceptedDependencies must be an array")
    plan_ids: set[str] = set()
    for index, dependency in enumerate(value):
        field = f"acceptedDependencies[{index}]"
        if not isinstance(dependency, dict):
            raise ValueError(f"{field} must be an object")
        plan_id = clean_string(dependency.get("planId"), f"{field}.planId")
        if plan_id in plan_ids:
            raise ValueError(f"acceptedDependencies plan IDs must be unique: {plan_id}")
        plan_ids.add(plan_id)
        if "planPath" in dependency:
            safe_relative_path(dependency["planPath"], f"{field}.planPath", root)
    return plan_ids


def project(envelope: dict[str, Any]) -> dict[str, Any]:
    root = Path.cwd().resolve()
    messages = messages_from(envelope)
    if not messages:
        raise ValueError("dispatch-plans requires direct inbox messages")

    relative_manifest, checkpoint = checkpoint_source(messages, root)
    manifest_file = root / relative_manifest
    if manifest_file.is_symlink() or not manifest_file.is_file():
        raise ValueError("dispatch manifest must be a regular non-symlink file")
    try:
        manifest = json.loads(manifest_file.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read dispatch manifest {relative_manifest}: {error}") from error
    if not isinstance(manifest, dict):
        raise ValueError("dispatch manifest must be an object")

    accepted_value = latest_value(messages, "acceptedPlanIds")
    accepted = clean_string_list(accepted_value if accepted_value is not None else [], "acceptedPlanIds")
    plans = manifest.get("plans")
    if not isinstance(plans, list) or not plans:
        raise ValueError("dispatch manifest plans must be a non-empty array")

    plan_ids = [clean_string(plan.get("planId"), "plans[].planId") for plan in plans if isinstance(plan, dict)]
    if len(plan_ids) != len(plans) or len(set(plan_ids)) != len(plan_ids):
        raise ValueError("dispatch manifest plan IDs must be unique objects")
    external_plan_ids = accepted_dependency_ids(manifest, root)
    known_plan_ids = set(plan_ids) | external_plan_ids
    unknown_accepted = sorted(set(accepted) - known_plan_ids)
    if unknown_accepted:
        raise ValueError(f"acceptedPlanIds contain unknown plans: {', '.join(unknown_accepted)}")
    accepted_manifest_plan_ids = set(accepted) & set(plan_ids)
    accepted_dispatch_ids = [plan_id for plan_id in accepted if plan_id in set(plan_ids)]
    if not set(plan_ids) - accepted_manifest_plan_ids:
        raise ValueError("dispatch requested after every manifest plan was accepted")

    verify_checkpoint(root, relative_manifest, checkpoint)
    context = normalized_review_context(manifest.get("reviewContext"), root)
    implementation_branch = clean_string(manifest.get("implementationBranch"), "implementationBranch")
    base_branch = clean_string(manifest.get("baseBranch"), "baseBranch")
    remote = clean_string(manifest.get("remote"), "remote")
    evidence_root = manifest_evidence_root(manifest, root)
    feedback = latest_integration_feedback(messages)

    items: list[dict[str, Any]] = []
    unmatched_material_paths: set[str] = set()
    for plan in plans:
        plan_id = clean_string(plan.get("planId"), "plans[].planId")
        dependencies = clean_string_list(plan.get("dependsOn", []), f"{plan_id}.dependsOn")
        unknown_dependencies = sorted(set(dependencies) - known_plan_ids)
        if unknown_dependencies:
            raise ValueError(f"{plan_id}.dependsOn contain unknown plans: {', '.join(unknown_dependencies)}")
    if feedback is not None:
        for finding in feedback["findings"]:
            if finding.get("severity") not in {"high", "mid", "medium"}:
                continue
            file_path = finding.get("file") or finding.get("filePath")
            if file_path is not None:
                relative = safe_relative_path(file_path, "integration-review.findings[].file", root)
                # Evidence logs are read-only review inputs, not source edits
                # requiring a new manifest write owner.
                if not path_is_owned(relative, ["tmp", evidence_root]):
                    unmatched_material_paths.add(relative)
    for plan in plans:
        plan_id = clean_string(plan.get("planId"), "plans[].planId")
        contract = plan_tracking_contract(plan, plan_id, root)
        write_paths = contract["writePaths"]
        if plan_id not in accepted_manifest_plan_ids:
            # Accepted plans are skipped by the runtime and never re-captured.
            _, preflight_errors = preflight_tracking(plan_id, contract, root)
            if preflight_errors:
                raise ValueError("; ".join(preflight_errors))
        plan_findings: list[dict[str, Any]] = []
        if feedback is not None:
            for finding in feedback["findings"]:
                file_path = finding.get("file") or finding.get("filePath")
                if file_path is None:
                    plan_findings.append(finding)
                    continue
                relative = safe_relative_path(file_path, "integration-review.findings[].file", root)
                evidence_path = path_is_owned(relative, ["tmp", evidence_root])
                if plan_id not in accepted_manifest_plan_ids and (
                    path_is_owned(relative, write_paths)
                    or evidence_path
                ):
                    plan_findings.append(finding)
                    unmatched_material_paths.discard(relative)
        dependencies = clean_string_list(plan.get("dependsOn", []), f"{plan_id}.dependsOn")
        items.append(
            {
                "planId": plan_id,
                "planPath": safe_relative_path(plan.get("planPath"), f"{plan_id}.planPath", root),
                "dependsOn": [dependency for dependency in dependencies if dependency in set(plan_ids)],
                "acceptedPlanIds": accepted_dispatch_ids,
                "writePaths": write_paths,
                "sharedPaths": contract["sharedPaths"],
                "trackedPaths": contract["trackedPaths"],
                "artifactRoots": contract["artifactRoots"],
                "acceptanceCriteria": clean_string_list(
                    plan.get("acceptanceCriteria"), f"{plan_id}.acceptanceCriteria", nonempty=True
                ),
                "verification": verification_commands(plan.get("verification", []), f"{plan_id}.verification"),
                "reviewContext": context,
                "reviewFeedback": {
                    "findings": plan_findings,
                    "recoveryDiagnostic": feedback["recoveryDiagnostic"] if feedback else "",
                },
                "manifestPath": relative_manifest,
                "checkpointCommit": checkpoint,
                "implementationBranch": implementation_branch,
                "baseBranch": base_branch,
                "remote": remote,
                "evidenceRoot": evidence_root,
            }
        )

    if unmatched_material_paths:
        paths = ", ".join(sorted(unmatched_material_paths))
        raise ValueError(
            "bounded checkpoint amendment required before redispatch: "
            f"material integration-review paths outside manifest writePaths: {paths}"
        )

    return {
        "when": {"always": True},
        "payload": {
            "implementationItems": items,
            "acceptedPlanIds": accepted_dispatch_ids,
            "manifestPath": relative_manifest,
            "checkpointCommit": checkpoint,
        },
    }


def validate_manifest_cli(manifest_argument: str) -> int:
    root = Path.cwd().resolve()
    try:
        relative = safe_relative_path(manifest_argument, "--validate-manifest", root)
        manifest_file = root / relative
        if manifest_file.is_symlink() or not manifest_file.is_file():
            raise ValueError("dispatch manifest must be a regular non-symlink file")
        manifest = json.loads(manifest_file.read_text())
        report = validate_manifest_contract(manifest, root)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        relative = manifest_argument
        report = {"valid": False, "limits": tracking_limits(), "plans": [], "errors": [str(error)]}
    report = {"manifestPath": relative, **report}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["valid"] else 1


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--validate-manifest":
        return validate_manifest_cli(sys.argv[2])
    if len(sys.argv) > 1:
        print(json.dumps({"error": "usage: dispatch-plans.py [--validate-manifest <manifest.json>]"}), file=sys.stderr)
        return 2
    try:
        envelope = json.loads(sys.stdin.readline())
        if not isinstance(envelope, dict):
            raise ValueError("stdio envelope must be an object")
        print(json.dumps(project(envelope), separators=(",", ":"), ensure_ascii=False))
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, separators=(",", ":")), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
