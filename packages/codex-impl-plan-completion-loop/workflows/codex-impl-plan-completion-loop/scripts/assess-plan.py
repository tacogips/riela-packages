#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
from plan_tools import metadata, plan_files


def assess():
    requested = os.environ.get("PLAN_PATH", "").strip()
    raw_targets = os.environ.get("TARGET_TASKS_JSON", "").strip()
    targets = json.loads(raw_targets) if raw_targets else None
    if targets is not None and (not isinstance(targets, list) or not all(isinstance(t, str) for t in targets)):
        raise ValueError("TARGET_TASKS_JSON must be an array of task IDs")
    candidates = [Path(requested)] if requested else plan_files("impl-plans/active")
    records = [(p, metadata(p)) for p in candidates]
    pending = [(p, m) for p, m in records if not m["complete"]]
    selected = records[0] if requested and records else (pending[0] if pending else None)
    payload = {"plan_complete": not pending, "activePlanFound": selected is not None,
               "planPath": str(selected[0]) if selected else None,
               "planSelectionMode": "explicit" if requested else "active-auto",
               "candidatePlans": [str(p) for p, _ in records],
               "completedCandidatePlans": [str(p) for p, m in records if m["complete"]],
               "implementationPlanPaths": [str(p) for p, _ in pending],
               "targetTasks": targets, "completedTasks": [], "incompleteTasks": [],
               "taskCount": 0, "remainingCount": 0, "nextTaskId": None,
               "nextTaskTitle": None, "nextTaskStatus": None, "completionCriteria": [],
               "designReference": selected[1]["designReference"] if selected else None}
    if selected:
        tasks = [t for t in selected[1]["tasks"] if targets is None or t["taskId"] in targets]
        incomplete = [t for t in tasks if t["status"] != "Completed"]
        if not selected[1]["complete"] and not incomplete:
            incomplete = [{"taskId": "PLAN-STATUS", "title": "Complete remaining plan-level work",
                           "status": selected[1]["status"], "dependencies": "See full plan",
                           "completionCriteria": []}]
        payload.update(taskCount=len(tasks), remainingCount=len(incomplete),
                       completedTasks=[{k: t[k] for k in ("taskId", "title", "status")} for t in tasks if t["status"] == "Completed"],
                       incompleteTasks=[{**t, "uncheckedCriteria": [c["text"] for c in t["completionCriteria"] if not c["done"]]} for t in incomplete])
        priority = {"In Progress": 0, "Not Started": 1, "Ready": 2}
        if incomplete:
            task = min(incomplete, key=lambda t: priority.get(t["status"], 3))
            payload.update(nextTaskId=task["taskId"], nextTaskTitle=task["title"],
                           nextTaskStatus=task["status"], completionCriteria=task["completionCriteria"])
    payload["guidance"] = ("No incomplete active implementation plans remain." if not pending else
                           "Delegate the complete implementationPlanPaths batch for single-author dependency planning and shared-branch implementation/review waves.")
    return {"when": {"plan_complete": payload["plan_complete"]}, "payload": payload}


if __name__ == "__main__":
    try:
        print(json.dumps(assess()))
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        sys.exit(1)
