#!/usr/bin/env python3
"""Apply Step 8 implementation-plan archive requests without invoking git."""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ACTIVE = "impl-plans/active"
COMPLETED = "impl-plans/completed"
STEP8 = "step8-docs-refresh"
MAX_DOCS_REFRESH_ROUNDS = 3


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


def _result(source: Any, destination: Any, status: str, message: str = "") -> dict[str, Any]:
    return {"source": source, "destination": destination, "status": status, "message": message}


def _safe_request(request: Any) -> tuple[str, str] | str:
    if not isinstance(request, dict):
        return "archive request must be an object"
    source = request.get("source")
    destination = request.get("destination")
    if not isinstance(source, str) or not isinstance(destination, str):
        return "source and destination must be strings"
    source_path = PurePosixPath(source)
    destination_path = PurePosixPath(destination)
    if (
        source_path.is_absolute()
        or destination_path.is_absolute()
        or any(not part for part in source.split("/"))
        or any(not part for part in destination.split("/"))
        or ".." in source_path.parts
        or ".." in destination_path.parts
        or ".git" in source_path.parts
        or ".git" in destination_path.parts
        or "\\" in source
        or "\\" in destination
        or source_path.parent != PurePosixPath(ACTIVE)
        or destination != f"{COMPLETED}/{source_path.name}"
    ):
        return "source or destination is not an allowed archive path"
    return source, destination


def _directory_check(root: Path) -> str | None:
    plans = root / "impl-plans"
    active = plans / "active"
    completed = plans / "completed"
    for path in (plans, active, completed):
        try:
            mode = os.lstat(path).st_mode
        except FileNotFoundError:
            continue
        except OSError as error:
            return str(error)
        if stat.S_ISLNK(mode):
            return f"{path.relative_to(root).as_posix()} is a symlink"
        if not stat.S_ISDIR(mode):
            return f"{path.relative_to(root).as_posix()} is not a directory"
    if not completed.exists():
        try:
            if not stat.S_ISDIR(os.lstat(plans).st_mode):
                return "impl-plans is not a real directory"
            os.mkdir(completed)
        except OSError as error:
            return str(error)
    return None


def _apply_request(root: Path, request: Any) -> dict[str, Any]:
    if isinstance(request, dict):
        source_value = request.get("source")
        destination_value = request.get("destination")
    else:
        source_value = destination_value = None
    safe = _safe_request(request)
    if isinstance(safe, str):
        return _result(source_value, destination_value, "rejected", safe)

    source, destination = safe
    directory_error = _directory_check(root)
    if directory_error:
        return _result(source, destination, "rejected", directory_error)

    source_path = root / source
    destination_path = root / destination
    try:
        source_mode = os.lstat(source_path).st_mode
        source_exists = True
    except FileNotFoundError:
        source_mode = None
        source_exists = False
    except OSError as error:
        return _result(source, destination, "rejected", str(error))
    try:
        destination_mode = os.lstat(destination_path).st_mode
        destination_exists = True
    except FileNotFoundError:
        destination_mode = None
        destination_exists = False
    except OSError as error:
        return _result(source, destination, "rejected", str(error))

    if source_exists and not stat.S_ISREG(source_mode):
        return _result(source, destination, "rejected", "source is not a regular file")
    if not source_exists and destination_exists and stat.S_ISREG(destination_mode):
        return _result(source, destination, "already-archived")
    if source_exists and destination_exists:
        return _result(source, destination, "conflict", "source and destination both exist")
    if not source_exists and not destination_exists:
        return _result(source, destination, "missing", "source and destination are missing")
    try:
        os.rename(source_path, destination_path)
    except OSError as error:
        return _result(source, destination, "rejected", str(error))
    return _result(source, destination, "moved")


def route(envelope: dict[str, Any], root: Path) -> dict[str, Any]:
    messages = [
        message for message in messages_from(envelope)
        if message.get("fromStepId") == STEP8 and isinstance(message.get("payload"), dict)
    ]
    if not messages:
        raise ValueError("plan-archive requires a step8-docs-refresh message")
    latest_payload = messages[-1]["payload"]
    requests = latest_payload.get("archiveRequests")
    if not isinstance(requests, list):
        results = [_result(None, None, "rejected", "archiveRequests must be an array")]
    else:
        results = [_apply_request(root, request) for request in requests]

    archived_paths = [
        result["destination"] for result in results
        if result["status"] in {"moved", "already-archived"}
    ]
    docs_refresh_round = len(messages)
    completion_blocked = docs_refresh_round > MAX_DOCS_REFRESH_ROUNDS
    payload = {
        **latest_payload,
        "archiveResults": results,
        "archivedImplPlanPaths": archived_paths,
        "docsRefreshRound": docs_refresh_round,
        "completion_blocked": completion_blocked,
    }
    if completion_blocked:
        unresolved = [result for result in results if result["status"] not in {"moved", "already-archived"}]
        unresolved_sources = [result["source"] for result in unresolved if isinstance(result.get("source"), str)]
        payload.update({
            "implementation_blocked": True,
            "status": "blocked",
            "blockedStepId": "step9-commit-message",
            "blockedPlanIds": sorted({PurePosixPath(source).stem for source in unresolved_sources}),
            "successfulPlanIds": [],
            "blockers": [{
                "type": "completion-archive-loop",
                "dependency": ACTIVE,
                "paths": unresolved_sources,
                "results": unresolved,
                "message": "Step 9 rejected completion three times; plan archiving or index updates still need operator action.",
            }],
            "resumeCriteria": [
                "Operator: move the listed plans from impl-plans/active to impl-plans/completed, update impl-plans/README.md, then rerun from step9-commit-message."
            ],
            "nextStep": (
                "Operator: resolve archive requests for " + ", ".join(unresolved_sources)
                if unresolved_sources else "review the Step 9 completion findings"
            ),
        })
    return {"when": {"completion_blocked": completion_blocked}, "payload": payload}


def main() -> int:
    try:
        envelope = json.loads(sys.stdin.readline())
        if not isinstance(envelope, dict):
            raise ValueError("stdio envelope must be an object")
        print(json.dumps(route(envelope, Path.cwd().resolve()), separators=(",", ":"), ensure_ascii=False))
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, separators=(",", ":"), ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
