#!/usr/bin/env python3
"""Serial archival only; never overwrite an existing completed plan."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from plan_tools import metadata, plan_files


def archive():
    active, completed = Path("impl-plans/active"), Path("impl-plans/completed")
    archived, skipped = [], []
    for path in plan_files(active):
        record = metadata(path)
        if not record["complete"]:
            skipped.append({"planPath": str(path), "reason": "not complete", "status": record["status"]})
            continue
        destination = completed / path.name
        completed.mkdir(parents=True, exist_ok=True)
        try:
            # Hard-link creation is exclusive and atomic on the repository filesystem.
            os.link(path, destination)
        except FileExistsError:
            skipped.append({"planPath": str(path), "reason": f"destination exists: {destination}", "status": record["status"]})
            continue
        path.unlink()
        archived.append({"planPath": str(path), "completedPath": str(destination),
                         "planName": path.stem, "status": record["status"], "designReference": record["designReference"]})
    readme = Path("impl-plans/README.md")
    readme_updated = False
    if readme.exists():
        before = readme.read_text()
        rows = ["## Active Plans", "", "| Plan | Status | Design Reference |", "| ---- | ------ | ---------------- |"]
        for path in plan_files(active):
            record = metadata(path)
            rows.append(f"| `active/{path.stem}` | {record['status']} | {record['designReference']} |")
        text = re.sub(r"## Active Plans\n.*?(?=## Recently Completed\n)", "\n".join(rows) + "\n\n", before, flags=re.S)
        today = datetime.now(timezone.utc).date().isoformat()
        added = [f"| `{p['planName']}` | {today} | {p['designReference']} |" for p in archived if f"| `{p['planName']}` " not in text]
        if added:
            text = re.sub(r"(## Recently Completed\n\n\| Plan[^\n]*\n\|[- |]*\n)", lambda m: m[0] + "\n".join(added) + "\n", text)
        if text != before:
            readme.write_text(text)
            readme_updated = True
    progress_path = Path("impl-plans/PROGRESS.json")
    progress_updated = False
    if progress_path.exists() and archived:
        progress = json.loads(progress_path.read_text())
        for item in archived:
            record = progress.get("plans", {}).get(item["planName"])
            if record is None:
                continue
            record["status"] = "Completed"
            phase = progress.get("phases", {}).get(str(record.get("phase")))
            if phase is not None:
                phase["status"] = "COMPLETED"
            progress_updated = True
        if progress_updated:
            progress["lastUpdated"] = datetime.now(timezone.utc).isoformat()
            progress_path.write_text(json.dumps(progress, indent=2) + "\n")
    return {"payload": {"status": "archived-completed-plans", "archivedPlans": archived,
                        "skippedPlans": skipped, "activePlansRemaining": [str(p) for p in plan_files(active)],
                        "readmeUpdated": readme_updated, "progressUpdated": progress_updated}}


if __name__ == "__main__":
    try:
        print(json.dumps(archive()))
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        sys.exit(1)
