#!/usr/bin/env python3
"""Deterministically classify a fanout join and persist a bounded wave summary."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SUMMARY_BYTE_LIMIT = 49152
VERDICT_BYTE_LIMIT = 16384
WAVE_ROOT = "tmp/opus-terra-waves"
TRACKING_RESUME_CRITERION = "amend checkpoint: declare artifactRoots / narrow writePaths"
POLICY_PREFIXES = (
    "policy_blocked: fanout snapshot",
    "policy_blocked: fanout change tracking",
    "policy_blocked: fanout artifact",
)
DIAGNOSTIC_KEYS = ("branchId", "node", "phase", "selection", "root", "path", "observed", "limit")
LEVELS = (
    {"paths": 40, "kinds": 3, "branchIds": 5, "changedFiles": 50, "evidencePaths": 20, "blockers": 10, "resumeCriteria": 10, "diagnostics": 20, "artifactPaths": 20, "byKind": 20, "items": 10, "depth": 4, "string": 300},
    {"paths": 20, "kinds": 2, "branchIds": 3, "changedFiles": 20, "evidencePaths": 10, "blockers": 5, "resumeCriteria": 5, "diagnostics": 10, "artifactPaths": 10, "byKind": 10, "items": 5, "depth": 3, "string": 160},
    {"paths": 5, "kinds": 1, "branchIds": 2, "changedFiles": 5, "evidencePaths": 5, "blockers": 3, "resumeCriteria": 3, "diagnostics": 5, "artifactPaths": 5, "byKind": 5, "items": 3, "depth": 2, "string": 80},
    {"paths": 0, "kinds": 0, "branchIds": 0, "changedFiles": 0, "evidencePaths": 0, "blockers": 1, "resumeCriteria": 1, "diagnostics": 0, "artifactPaths": 0, "byKind": 0, "items": 0, "depth": 0, "string": 80},
)
SCHEMA_KEYS = ("implementation_blocked", "partial_success", "blockedPlanIds", "successfulPlanIds", "blockers", "resumeCriteria")


def compact(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _message_order(message: dict[str, Any]) -> tuple[float, int]:
    value = message.get("createdOrder", 0)
    try:
        order = float(value)
    except (TypeError, ValueError):
        order = 0
    return order, 0


def _messages(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    input_obj = envelope.get("input", {})
    runtime = input_obj.get("_rielaInput", {}) if isinstance(input_obj, dict) else {}
    messages = runtime.get("messages", []) if isinstance(runtime, dict) else []
    return [m for m in messages if isinstance(m, dict)] if isinstance(messages, list) else []


def _join(envelope: dict[str, Any]) -> dict[str, Any]:
    messages = _messages(envelope)
    joins = [m for m in messages if isinstance((m.get("payload") or {}).get("fanoutJoin") if isinstance(m.get("payload"), dict) else None, dict)]
    if joins:
        return max(joins, key=_message_order)["payload"]["fanoutJoin"]
    candidates = [m for m in messages if m.get("fromStepId") in {"implementation-progress-check", "branch-evidence"} and isinstance(m.get("payload"), dict)]
    if not candidates:
        raise ValueError("fanout join or standalone progress message is required")
    payload = max(candidates, key=_message_order)["payload"]
    plan_id = payload.get("planId")
    if not isinstance(plan_id, str) or not plan_id:
        ids = payload.get("blockedPlanIds")
        plan_id = ids[0] if isinstance(ids, list) and ids and isinstance(ids[0], str) else None
    if not plan_id:
        raise ValueError("standalone progress message has no planId")
    return {"branches": [{"branchId": plan_id, "status": "completed", "output": payload}], "dispatchedBranchIds": [plan_id]}


def _diagnostics(evidence: dict[str, Any], key: str) -> list[dict[str, Any]]:
    values = evidence.get(key, [])
    if not isinstance(values, list):
        return []
    result = []
    for item in values:
        if isinstance(item, dict):
            result.append({k: item[k] for k in DIAGNOSTIC_KEYS if k in item})
    return result


def _ids(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(x) for x in value if isinstance(x, (str, int)) and str(x)]


def _safe_dirs(root: Path, execution_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", execution_id) or ".." in execution_id:
        raise ValueError("unsafe or missing workflowExecutionId")
    paths = [root / "tmp", root / "tmp" / "opus-terra-waves", root / "tmp" / "opus-terra-waves" / execution_id]
    for path in paths:
        if path.is_symlink():
            raise ValueError(f"wave directory is symlinked: {path}")
        if path.exists() and not path.is_dir():
            raise ValueError(f"wave path is not a directory: {path}")
        path.mkdir(exist_ok=True)
    return paths[-1]


def _allocate(session: Path) -> tuple[int, Path]:
    while True:
        ordinals = [int(m.group(1)) for p in session.iterdir() if (m := re.fullmatch(r"wave-(\d{3})", p.name)) and p.is_dir()]
        ordinal = max(ordinals, default=0) + 1
        if ordinal > 999:
            raise ValueError("wave ordinal exceeds 999")
        path = session / f"wave-{ordinal:03d}"
        try:
            path.mkdir(exist_ok=False)
            return ordinal, path
        except FileExistsError:
            continue


def _atomic(path: Path, data: bytes) -> None:
    temp = path.with_name(path.name + ".tmp")
    with temp.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def _text(value: Any, cap: int, pointer: str, raw_path: str) -> str:
    text = value if isinstance(value, str) else str(value)
    if len(text) <= cap:
        return text
    suffix = f"…[truncated {len(text)-cap} chars; see {raw_path}#{pointer}]"
    return text[:max(0, cap-len(suffix))] + suffix


def _bounded(value: Any, level: dict[str, int], pointer: str, raw_path: str, depth: int = 0) -> Any:
    if isinstance(value, str):
        return _text(value, level["string"], pointer, raw_path)
    if depth >= level["depth"]:
        return "[omitted; see raw join]"
    if isinstance(value, list):
        return [_bounded(v, level, f"{pointer}/{i}", raw_path, depth+1) for i, v in enumerate(value[:level["items"]])]
    if isinstance(value, dict):
        return {str(k): _bounded(v, level, f"{pointer}/{_escape(str(k))}", raw_path, depth+1) for k, v in list(value.items())[:level["items"]]}
    return value


def _escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _classify_join(join: dict[str, Any], summary_path: str) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    branches = join.get("branches", [])
    if not isinstance(branches, list):
        branches = []
    dispatched = _ids(join.get("dispatchedBranchIds"))
    pending = _ids(join.get("pendingBranchIds"))
    evidence = join.get("changeEvidence") if isinstance(join.get("changeEvidence"), dict) else {}
    capture = _diagnostics(evidence, "captureFailures")
    reduce = _diagnostics(evidence, "reduceFailures")
    bad_ids = {str(x.get("branchId")) for x in capture + reduce if isinstance(x.get("branchId"), (str, int))}
    unattributed_incomplete = evidence.get("complete") is False and not bad_ids
    plans: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    resume: list[str] = []
    blocked_ids: list[str] = []
    successful_ids: list[str] = []
    branch_plan_ids: set[str] = set()
    for i, branch in enumerate(branches):
        if not isinstance(branch, dict):
            continue
        output = branch.get("output") if isinstance(branch.get("output"), dict) else {}
        plan_id = branch.get("branchId") or output.get("planId")
        if not isinstance(plan_id, str) or not plan_id:
            continue
        branch_plan_ids.add(plan_id)
        status = str(branch.get("status", "unknown"))
        reason = str(branch.get("failureReason", ""))
        tracking = next((prefix for prefix in POLICY_PREFIXES if reason.startswith(prefix)), None)
        evidence_bad = plan_id in bad_ids or unattributed_incomplete
        is_blocked = bool(tracking or evidence_bad or output.get("implementation_blocked") is True or output.get("status") == "blocked")
        success = status.lower() in {"completed", "succeeded", "success"} and not is_blocked and isinstance(output.get("evidencePaths"), list) and bool(output["evidencePaths"]) and isinstance(output.get("changedFiles"), list)
        if tracking:
            classification, blocker_type, source = "tracking-rejected", "tracking-contract", "tracking-contract"
        elif evidence_bad:
            classification, blocker_type, source = "evidence-incomplete", "change-evidence-incomplete", "change-evidence"
        elif is_blocked:
            classification, blocker_type, source = "blocked", str(output.get("blockerType") or "implementation-blocked"), "progress-gate"
        elif success:
            classification, blocker_type, source = "successful", "", ""
        elif status.lower() == "cancelled":
            classification, blocker_type, source = "cancelled", "", ""
        elif status.lower() in {"failed", "error"}:
            classification, blocker_type, source = "failed", "", ""
        elif status.lower() in {"completed", "succeeded", "success"}:
            classification, blocker_type, source = "evidence-missing", "", ""
        else:
            classification, blocker_type, source = status.lower(), "", ""
        if is_blocked:
            blocked_ids.append(plan_id)
            raw_blockers = output.get("blockers", []) if isinstance(output.get("blockers"), list) else []
            if tracking or evidence_bad:
                raw_blockers = ["Fanout change tracking rejected this branch." if tracking else "Fanout change evidence is incomplete."]
            if not raw_blockers:
                raw_blockers = [f"{plan_id}: {blocker_type} requires resolution."]
            for value in raw_blockers:
                item = {"planId": plan_id, "blockerType": blocker_type, "source": source, "message": value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(",", ":"))}
                if tracking or evidence_bad:
                    relevant = [d for d in capture + reduce if d.get("branchId") == plan_id]
                    if relevant:
                        item["diagnostic"] = relevant[0]
                blockers.append(item)
            raw_resume = output.get("resumeCriteria", []) if isinstance(output.get("resumeCriteria"), list) else []
            if tracking or evidence_bad:
                raw_resume = [TRACKING_RESUME_CRITERION]
            if not raw_resume:
                raw_resume = [f"{plan_id}: resolve the {blocker_type} blockers recorded in {summary_path} and redispatch"]
            resume.extend(x for x in raw_resume if isinstance(x, str))
        elif success:
            successful_ids.append(plan_id)
        plans.append({"planId": plan_id, "status": status, "classification": classification, "rawPointer": f"/branches/{i}", "sessionId": branch.get("sessionId"), "failureReason": reason or None, "blockerType": blocker_type or None, "blockers": raw_blockers if is_blocked else [], "resumeCriteria": raw_resume if is_blocked else [], "changedFiles": output.get("changedFiles", []), "evidencePaths": output.get("evidencePaths", []), "reviewDecisions": output.get("reviewDecisions", []), "checkpointProvenance": output.get("checkpointProvenance", {}), "baselineReviewPending": output.get("baselineReviewPending", False)})
    for plan_id in pending:
        if plan_id not in branch_plan_ids:
            plans.append({"planId": plan_id, "status": "pending", "classification": "pending", "rawPointer": None, "sessionId": None, "failureReason": None, "blockerType": None, "blockers": [], "resumeCriteria": [], "changedFiles": [], "evidencePaths": [], "reviewDecisions": [], "checkpointProvenance": {}, "baselineReviewPending": False})
    unique_resume = list(dict.fromkeys(resume))
    verdict = {"implementation_blocked": bool(blocked_ids), "partial_success": bool(blocked_ids and successful_ids), "blockedPlanIds": blocked_ids, "successfulPlanIds": successful_ids, "blockers": blockers, "resumeCriteria": unique_resume}
    obs = evidence.get("observations", []) if isinstance(evidence.get("observations"), list) else []
    by_path: dict[str, dict[str, Any]] = {}
    by_kind = Counter()
    by_selection = Counter()
    for observation in obs:
        if not isinstance(observation, dict):
            continue
        kind = str(next((observation[key] for key in ("kind", "type", "reason") if observation.get(key)), "unknown"))
        path = str(observation.get("path", observation.get("root", "")))
        selection = str(observation.get("selection", "other"))
        by_kind[kind] += 1
        by_selection[selection if selection in {"source", "artifact"} else "other"] += 1
        if path:
            entry = by_path.setdefault(path, {"path": path, "selection": selection if selection in {"source", "artifact"} else "other", "observationCount": 0, "kinds": Counter(), "branchIds": set()})
            entry["observationCount"] += 1
            entry["kinds"][kind] += 1
            ids = observation.get("branchIds", [observation.get("branchId")] if observation.get("branchId") else [])
            entry["branchIds"].update(str(x) for x in ids if isinstance(x, (str, int)))
    def severity(kinds: Counter) -> int:
        keys = " ".join(kinds).lower()
        # Amended D4 orders removed, content, added, mode, then other kinds.
        if any(x in keys for x in ("deleted", "removed", "overwrite")):
            return 0
        if "content" in keys:
            return 1
        if any(x in keys for x in ("added", "new", "membership")):
            return 2
        if any(x in keys for x in ("mode", "kind")):
            return 3
        return 4
    paths = sorted(by_path.values(), key=lambda e: (severity(e["kinds"]), {"source":0,"artifact":1}.get(e["selection"],2), -e["observationCount"], e["path"]))
    projection = {"plans": plans, "dispatchedBranchIds": dispatched, "pendingBranchIds": pending, "completedBranchIds": _ids(join.get("completedBranchIds")), "changeEvidence": {"complete": evidence.get("complete"), "hasDrift": evidence.get("hasDrift", len(obs)>0), "observationTotal": len(obs), "pathTotal": len(by_path), "bySelection": {k: by_selection[k] for k in ("source", "artifact", "other")}, "byKind": dict(sorted(by_kind.items())), "captureFailuresTotal": len(evidence.get("captureFailures", [])) if isinstance(evidence.get("captureFailures"), list) else 0, "reduceFailuresTotal": len(evidence.get("reduceFailures", [])) if isinstance(evidence.get("reduceFailures"), list) else 0, "captureFailures": capture, "reduceFailures": reduce, "artifactPaths": evidence.get("artifactPaths", []) if isinstance(evidence.get("artifactPaths"), list) else [], "paths": paths}}
    return verdict, plans, projection


def _cap_verdict(verdict: dict[str, Any], plans: list[dict[str, Any]], summary_path: str, blocker_cap: int, resume_cap: int, string_cap: int) -> dict[str, Any]:
    result = dict(verdict)
    out = []
    totals: Counter[str] = Counter()
    for item in verdict["blockers"]:
        plan = item["planId"]
        seen = totals[plan]
        totals[plan] += 1
        if seen < blocker_cap:
            clean = dict(item)
            clean["message"] = _text(clean["message"], string_cap, "/verdict/blockers", "rawJoinPath")
            out.append(clean)
    for plan, total in totals.items():
        omitted = total - blocker_cap
        if omitted > 0:
            out.append({"planId": plan, "blockerType": "additional-blockers-omitted", "source": "summary", "message": f"{omitted} additional blockers omitted; see {summary_path}", "omittedCount": omitted, "summaryPath": summary_path})
    result["blockers"] = out
    resumes = []
    criteria_by_plan = {plan["planId"]: plan.get("resumeCriteria", []) for plan in plans}
    for plan_id in verdict["blockedPlanIds"]:
        kept_for_plan = 0
        for text in criteria_by_plan.get(plan_id, []):
            if not isinstance(text, str):
                continue
            if kept_for_plan >= resume_cap:
                break
            kept_for_plan += 1
            bounded = _text(text, string_cap, "/verdict/resumeCriteria", "rawJoinPath")
            if bounded not in resumes:
                resumes.append(bounded)
    result["resumeCriteria"] = resumes
    return result


def _summary_for_level(join: dict[str, Any], verdict: dict[str, Any], plans: list[dict[str, Any]], projection: dict[str, Any], execution_id: str, ordinal: int, summary_path: str, raw_path: str, raw_bytes: bytes, level: dict[str, int]) -> dict[str, Any]:
    trunc = 0
    bounded_plans = []
    for plan in plans:
        p = dict(plan)
        for field, cap in (("changedFiles", level["changedFiles"]), ("evidencePaths", level["evidencePaths"]), ("blockers", level["blockers"]), ("resumeCriteria", level["resumeCriteria"])):
            original = p.get(field, [])
            p[field + "Total"] = len(original) if isinstance(original, list) else 0
            if field == "blockers" and len(original) > cap:
                p[field] = original[:cap]
                trunc += 1
            else:
                p[field] = original[:cap] if isinstance(original, list) else []
        # Pending (not yet dispatched) plans have no raw branch pointer.
        pointer = p.get("rawPointer") or ""
        p["reviewDecisions"] = _bounded(p.get("reviewDecisions"), level, pointer + "/output/reviewDecisions", raw_path)
        p["checkpointProvenance"] = _bounded(p.get("checkpointProvenance"), level, pointer + "/output/checkpointProvenance", raw_path)
        bounded_plans.append(p)
    ce = dict(projection["changeEvidence"])
    for field, cap in (("captureFailures", level["diagnostics"]), ("reduceFailures", level["diagnostics"]), ("artifactPaths", level["artifactPaths"])):
        values = ce.get(field, [])
        ce[field + "Omitted"] = max(0, len(values)-cap)
        ce[field] = values[:cap]
        if ce[field + "Omitted"]: trunc += 1
    ce["byKind"], ce["kindsOmitted"] = dict(list(ce["byKind"].items())[:level["byKind"]]), max(0, len(ce["byKind"])-level["byKind"])
    ce["paths"] = [{"path": e["path"], "selection": e["selection"], "observationCount": e["observationCount"], "kinds": list(e["kinds"].most_common(level["kinds"])), "branchIds": sorted(e["branchIds"])[:level["branchIds"]]} for e in projection["changeEvidence"]["paths"][:level["paths"]]]
    ce["pathsOmitted"] = max(0, projection["changeEvidence"]["pathTotal"]-len(ce["paths"]))
    if ce["pathsOmitted"]: trunc += 1
    result = {"schemaVersion":1,"generatedBy":"implementation-wave-outcome.py","workflowExecutionId":execution_id,"waveOrdinal":ordinal,"summaryPath":summary_path,"rawJoinPath":raw_path,"rawJoinBytes":len(raw_bytes),"rawJoinSha256":hashlib.sha256(raw_bytes).hexdigest(),"verdict":verdict,"dispatchedBranchIds":projection["dispatchedBranchIds"],"pendingBranchIds":projection["pendingBranchIds"],"completedBranchIds":projection["completedBranchIds"],"plans":bounded_plans,"changeEvidence":ce,"truncation":{"level":LEVELS.index(level),"truncatedFieldCount":trunc}}
    return result


def classify(envelope: dict[str, Any], root: Path) -> dict[str, Any]:
    join = _join(envelope)
    runtime = envelope.get("input", {}).get("_rielaInput", {})
    execution_id = runtime.get("workflowExecutionId") if isinstance(runtime, dict) else None
    session = _safe_dirs(root, execution_id if isinstance(execution_id, str) else "")
    ordinal, wave_dir = _allocate(session)
    summary_path = (wave_dir / "wave-summary.json").relative_to(root).as_posix()
    raw_path = (wave_dir / "fanout-join.json").relative_to(root).as_posix()
    raw = compact(join)
    _atomic(wave_dir / "fanout-join.json", raw)
    verdict, plans, projection = _classify_join(join, summary_path)
    for blocker in verdict["blockers"]:
        if blocker.get("source") == "progress-gate" and not blocker.get("message"):
            blocker["message"] = f"Resolve blockers recorded in {summary_path} and redispatch."
    result = None
    for blocker_cap, resume_cap, string_cap in ((3,3,300),(1,1,120)):
        payload = _cap_verdict(verdict, plans, summary_path, blocker_cap, resume_cap, string_cap)
        if len(compact(payload)) > VERDICT_BYTE_LIMIT:
            continue
        for level in LEVELS:
            summary = _summary_for_level(join, payload, plans, projection, execution_id, ordinal, summary_path, raw_path, raw, level)
            if len(compact(summary)) <= SUMMARY_BYTE_LIMIT and len(compact(summary)) + len(compact(payload)) <= 65536:
                result = summary
                break
        if result is not None:
            break
    if result is None:
        raise ValueError(f"bounded wave summary cannot fit for {len(plans)} plans")
    _atomic(wave_dir / "wave-summary.json", compact(result))
    return {"when":{"implementation_blocked":payload["implementation_blocked"],"partial_success":payload["partial_success"]},"payload":payload}


def main() -> int:
    try:
        line = sys.stdin.readline()
        if not line:
            raise ValueError("stdin envelope is required")
        envelope = json.loads(line)
        result = classify(envelope, Path.cwd().resolve())
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, separators=(",", ":")), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
