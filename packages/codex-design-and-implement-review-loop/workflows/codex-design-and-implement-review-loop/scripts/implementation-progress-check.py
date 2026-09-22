#!/usr/bin/env python3
"""Classify branch-local Step 6 progress from Riela's stdio input envelope."""

from __future__ import annotations

import hashlib
import json
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
        "implementation-no-progress": "Make a concrete source/test/plan change and report the changed paths plus new verification evidence.",
        "implementation-materially-unverified": "Run and report verification that exercises the changed implementation before review.",
        "implementation-invalid-evidence": "Return the required Step 6 evidence arrays in the implementation output.",
    }[blocker_type]
    payload = {
        **current,
        "implementation_blocked": True,
        "status": "blocked",
        "blockerType": blocker_type,
        "evidenceFingerprint": fingerprint,
        "blockers": existing + [blocker],
        "resumeCriteria": normalized_list(current.get("resumeCriteria")) + [resume],
    }
    return {"when": {"implementation_blocked": True}, "payload": payload}


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

    if current.get("implementation_blocked") is True or normalized_list(current.get("blockers")):
        return blocked_result(
            current,
            "implementation-dependency",
            "Step 6 reported an unresolved implementation blocker.",
            fingerprint,
        )
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

    previous_evidence = normalized_evidence(messages[-2]["payload"]) if len(messages) > 1 else None
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

    payload = {
        **current,
        "implementation_blocked": False,
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
