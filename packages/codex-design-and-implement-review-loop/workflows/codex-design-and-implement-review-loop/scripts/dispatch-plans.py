#!/usr/bin/env python3
"""Project an accepted implementation manifest into native Riela fanout items."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


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
    if len(manifests) != 1:
        raise ValueError("checkpoint must contain exactly one dispatch manifest")
    return manifests[0], commit


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
        identifier = value.get("communicationId") or value.get("number")
        title = value.get("title")
        url = value.get("url")
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
    unknown_accepted = sorted(set(accepted) - set(plan_ids))
    if unknown_accepted:
        raise ValueError(f"acceptedPlanIds contain unknown plans: {', '.join(unknown_accepted)}")
    if not set(plan_ids) - set(accepted):
        raise ValueError("dispatch requested after every manifest plan was accepted")

    verify_checkpoint(root, relative_manifest, checkpoint)
    context = normalized_review_context(manifest.get("reviewContext"), root)
    implementation_branch = clean_string(manifest.get("implementationBranch"), "implementationBranch")
    base_branch = clean_string(manifest.get("baseBranch"), "baseBranch")
    remote = clean_string(manifest.get("remote"), "remote")
    evidence_root = manifest_evidence_root(manifest, root)

    items: list[dict[str, Any]] = []
    for plan in plans:
        plan_id = clean_string(plan.get("planId"), "plans[].planId")
        write_paths = [
            safe_relative_path(path, f"{plan_id}.writePaths[]", root)
            for path in clean_string_list(plan.get("writePaths"), f"{plan_id}.writePaths")
        ]
        shared_paths = [
            safe_relative_path(path, f"{plan_id}.sharedPaths[]", root)
            for path in clean_string_list(plan.get("sharedPaths", []), f"{plan_id}.sharedPaths")
        ]
        tracked_paths = list(dict.fromkeys(write_paths + shared_paths))
        if not tracked_paths:
            raise ValueError(f"{plan_id} has no tracked write or shared paths")
        items.append(
            {
                "planId": plan_id,
                "planPath": safe_relative_path(plan.get("planPath"), f"{plan_id}.planPath", root),
                "dependsOn": clean_string_list(plan.get("dependsOn", []), f"{plan_id}.dependsOn"),
                "acceptedPlanIds": accepted,
                "writePaths": write_paths,
                "sharedPaths": shared_paths,
                "trackedPaths": tracked_paths,
                "acceptanceCriteria": clean_string_list(
                    plan.get("acceptanceCriteria"), f"{plan_id}.acceptanceCriteria", nonempty=True
                ),
                "verification": verification_commands(plan.get("verification", []), f"{plan_id}.verification"),
                "reviewContext": context,
                "manifestPath": relative_manifest,
                "checkpointCommit": checkpoint,
                "implementationBranch": implementation_branch,
                "baseBranch": base_branch,
                "remote": remote,
                "evidenceRoot": evidence_root,
            }
        )

    return {
        "when": {"always": True},
        "payload": {
            "implementationItems": items,
            "acceptedPlanIds": accepted,
            "manifestPath": relative_manifest,
            "checkpointCommit": checkpoint,
        },
    }


def main() -> int:
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
