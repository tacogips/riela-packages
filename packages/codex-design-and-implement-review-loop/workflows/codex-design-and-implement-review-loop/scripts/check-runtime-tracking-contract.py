#!/usr/bin/env python3
"""Route native tracking rejections to the plan author after all workers join."""
import json
import sys

POLICY_PREFIXES = (
    "policy_blocked: fanout snapshot",
    "policy_blocked: fanout change tracking",
    "policy_blocked: fanout artifact",
)
DIAGNOSTIC_KEYS = ("branchId", "node", "phase", "selection", "root", "path", "observed", "limit")


def classify(envelope):
    metadata = envelope.get("input", {}).get("_rielaInput", {})
    messages = sorted(metadata.get("messages", []), key=lambda message: message.get("createdOrder", 0))
    join = None
    for message in reversed(messages):
        payload = message.get("payload", {})
        if isinstance(payload, dict) and isinstance(payload.get("fanoutJoin"), dict):
            join = payload["fanoutJoin"]
            break
    if join is None:
        # A standalone Step 6 resume has no native wave. Preserve its terminal
        # branch classification for the existing outcome path.
        for message in reversed(messages):
            if message.get("fromStepId") in {"implementation-progress-check", "branch-evidence"}:
                payload = message.get("payload")
                if isinstance(payload, dict) and payload:
                    return {"when": {"tracking_contract_rejected": False},
                            "payload": {**payload, "tracking_contract_rejected": False}}
        raise ValueError("tracking gate requires a native fanoutJoin or terminal branch evidence in its direct inbox")
    evidence = join.get("changeEvidence", {})
    diagnostics = evidence.get("captureFailures", []) + evidence.get("reduceFailures", [])
    findings = []
    affected = []
    for branch in join.get("branches", []):
        reason = branch.get("failureReason", "")
        if isinstance(reason, str) and reason.startswith(POLICY_PREFIXES):
            plan = branch.get("branchId") or branch.get("item", {}).get("planId")
            if plan and plan not in affected:
                affected.append(plan)
            findings.append({"severity": "high", "targetStep": "step4-impl-plan-create",
                             "planId": plan, "message": reason})
    for diagnostic in diagnostics:
        diagnostic = {key: diagnostic[key] for key in DIAGNOSTIC_KEYS if key in diagnostic}
        plan = diagnostic.get("branchId")
        if plan and plan not in affected:
            affected.append(plan)
        findings.append({"severity": "high", "targetStep": "step4-impl-plan-create",
                         "planId": plan, "diagnostic": diagnostic,
                         "message": "Native tracking contract rejected during implementation or reduction"})
    rejected = bool(findings) or evidence.get("complete") is False
    if rejected and not findings:
        findings.append({"severity": "high", "targetStep": "step4-impl-plan-create",
                         "message": "Native change evidence is incomplete; revalidate the entire wave contract"})
    # Only runtime-reported previously completed plans are retained. Successful
    # siblings of this rejected wave remain unaccepted until independent review.
    payload = {"tracking_contract_rejected": rejected, "fanoutJoin": join,
               "findings": findings, "affectedPlanIds": affected,
               "acceptedPlanIds": join.get("completedBranchIds", [])}
    if rejected:
        payload["needs_revision"] = True
        payload["resumeCriteria"] = ["Amend plans and checkpoint: declare artifactRoots or narrow source paths; repeat independent plan review and dispatch"]
    return {"when": {"tracking_contract_rejected": rejected}, "payload": payload}


def main():
    try:
        print(json.dumps(classify(json.loads(sys.stdin.readline())), separators=(",", ":")))
    except (ValueError, TypeError, KeyError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
