#!/usr/bin/env python3
"""Route dispatch amendments without changing the shared dispatch projection."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def load_dispatch_module():
    script = Path(__file__).resolve().with_name("dispatch-plans.py")
    spec = importlib.util.spec_from_file_location("riela_dispatch_plans", script)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load dispatch helpers from {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dispatch = load_dispatch_module()
MAX_CHECKPOINT_AMENDMENTS = 2
CHECKPOINT_STEPS = ("plan-git-push", "plan-git-commit", "plan-push-gate")
UNMATCHED_MARKER = "outside manifest writePaths: "
FINDINGS_CAP = 20
ROUTE_KEYS = ("dispatch_ready", "amendment_required", "amendment_blocked")
AMENDMENT_PAYLOAD_KEYS = (
    "dispatch_ready", "amendment_required", "amendment_blocked", "acceptedPlanIds",
    "manifestPath", "checkpointCommit", "checkpointAmendment", "pendingPlanIds",
    "blockedPlanIds", "successfulPlanIds", "issueReference", "blockers",
    "resumeCriteria", "nextStep",
)


def amendment_result(envelope: dict[str, Any], error: ValueError) -> dict[str, Any]:
    root = Path.cwd().resolve()
    messages = dispatch.messages_from(envelope)
    manifest_path, commit = dispatch.checkpoint_source(messages, root)
    manifest = json.loads((root / manifest_path).read_text())
    accepted_value = dispatch.latest_value(messages, "acceptedPlanIds")
    accepted = [item for item in accepted_value or [] if isinstance(item, str)]
    plans = manifest.get("plans")
    if not isinstance(plans, list):
        raise ValueError("dispatch manifest plans must be an array")
    plan_ids = [plan["planId"] for plan in plans if isinstance(plan, dict) and isinstance(plan.get("planId"), str)]
    pending = [plan_id for plan_id in plan_ids if plan_id not in accepted]

    text = str(error)
    reason = "integration-paths-outside-writePaths" if UNMATCHED_MARKER in text else "tracking-contract"
    unmatched_paths = (
        sorted(part.strip() for part in text.split(UNMATCHED_MARKER, 1)[1].split(", "))
        if UNMATCHED_MARKER in text else []
    )
    owner_candidates = []
    for path in unmatched_paths:
        owners = []
        for plan in plans:
            if not isinstance(plan, dict) or not isinstance(plan.get("planId"), str):
                continue
            write_paths = plan.get("writePaths", [])
            if isinstance(write_paths, list) and dispatch.path_is_owned(path, write_paths):
                owners.append({"planId": plan["planId"], "accepted": plan["planId"] in accepted})
        owner_candidates.append({"path": path, "plans": owners})

    feedback = dispatch.latest_integration_feedback(messages)
    findings = []
    if feedback is not None:
        path_set = set(unmatched_paths)
        findings = [
            finding for finding in feedback["findings"]
            if (finding.get("file") or finding.get("filePath")) in path_set
        ][:FINDINGS_CAP]

    checkpoint_hashes = {
        payload["git"]["commitHash"]
        for message in messages
        if message.get("fromStepId") in CHECKPOINT_STEPS
        and isinstance((payload := message.get("payload")), dict)
        and isinstance(payload.get("git"), dict)
        and isinstance(payload["git"].get("commitHash"), str)
    }
    amendment_round = max(0, len(checkpoint_hashes) - 1)
    required = amendment_round < MAX_CHECKPOINT_AMENDMENTS
    flags = {
        "dispatch_ready": False,
        "amendment_required": required,
        "amendment_blocked": not required,
    }
    review_context = manifest.get("reviewContext")
    review_context = review_context if isinstance(review_context, dict) else {}
    issue_value = review_context.get("issueReference")
    if issue_value is None and review_context.get("intakeCommunicationId") is not None:
        issue_value = {"communicationId": review_context["intakeCommunicationId"]}
    try:
        issue_reference = dispatch.issue_reference(issue_value)
    except ValueError:
        issue_reference = str(manifest.get("taskId") or manifest_path)

    blocker_type = "checkpoint-amendment-required" if required else "checkpoint-amendment-exhausted"
    blockers = [{
        "type": blocker_type,
        "dependency": manifest_path,
        "planIds": pending,
        "paths": unmatched_paths,
        "message": text,
    }]
    if required:
        resume_criteria = [
            "Amend the dispatch manifest so every listed path is owned by a pending plan's writePaths, "
            "or narrow/reclassify tracked paths, then repeat Step 5 review and the plan checkpoint before redispatch."
        ]
        next_step = "step4-impl-plan-create: bounded checkpoint amendment"
    else:
        resume_criteria = [
            f"Operator: amend {manifest_path} so the listed paths are owned or narrowed, commit a new plan checkpoint, and start a resume run."
        ]
        next_step = ", ".join(unmatched_paths) if unmatched_paths else text

    checkpoint_amendment = {
        "reason": reason,
        "error": text,
        "unmatchedPaths": unmatched_paths,
        "ownerCandidates": owner_candidates,
        "findings": findings,
        "manifestPath": manifest_path,
        "previousCheckpointCommit": commit,
        "amendmentRound": amendment_round,
        "maxAmendmentRounds": MAX_CHECKPOINT_AMENDMENTS,
    }
    payload = {
        "dispatch_ready": False,
        "amendment_required": required,
        "amendment_blocked": not required,
        "acceptedPlanIds": accepted,
        "manifestPath": manifest_path,
        "checkpointCommit": commit,
        "checkpointAmendment": checkpoint_amendment,
        "pendingPlanIds": pending,
        "blockedPlanIds": pending,
        "successfulPlanIds": accepted,
        "issueReference": issue_reference,
        "blockers": blockers,
        "resumeCriteria": resume_criteria,
        "nextStep": next_step,
    }
    return {"when": flags, "payload": payload}


def route(envelope: dict[str, Any]) -> dict[str, Any]:
    try:
        projected = dispatch.project(envelope)
    except ValueError as error:
        if not str(error).startswith(dispatch.AMENDMENT):
            raise
        return amendment_result(envelope, error)
    flags = {"dispatch_ready": True, "amendment_required": False, "amendment_blocked": False}
    return {"when": flags, "payload": {**projected["payload"], **flags}}


def main() -> int:
    try:
        envelope = json.loads(sys.stdin.readline())
        if not isinstance(envelope, dict):
            raise ValueError("stdio envelope must be an object")
        print(json.dumps(route(envelope), separators=(",", ":"), ensure_ascii=False))
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, separators=(",", ":"), ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
