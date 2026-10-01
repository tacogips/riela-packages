#!/usr/bin/env python3
"""Validate the written, not yet committed, dispatch manifest before the plan checkpoint commit.

The gate reuses the exact tracking-contract and preflight rules of
dispatch-plans.py. A valid contract passes the checkpoint commit request
through unchanged to plan-git-commit; an invalid contract routes back to the
plan author with structured findings. It never converts a policy rejection
into acceptance.
"""

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
        raise ValueError(f"cannot load dispatch contract helpers from {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dispatch = load_dispatch_module()

PASS_THROUGH_KEYS = ("checkpoint_blocked", "status", "commitMessage", "committedFiles", "evidenceRoot", "blockers")
TARGET_STEP = "step4-impl-plan-create"


def latest_checkpoint(messages: list[dict[str, Any]]) -> dict[str, Any]:
    for message in reversed(messages):
        if message.get("fromStepId") != "plan-checkpoint":
            continue
        payload = message.get("payload")
        if isinstance(payload, dict):
            return payload
    raise ValueError("plan-contract-validate requires a plan-checkpoint message in its direct inbox")


def manifest_path_from(checkpoint: dict[str, Any], root: Path) -> str:
    value = checkpoint.get("manifestPath")
    if value is not None:
        return dispatch.safe_relative_path(value, "plan-checkpoint.manifestPath", root)
    committed = checkpoint.get("committedFiles")
    if not isinstance(committed, list):
        raise ValueError("plan-checkpoint must return manifestPath or committedFiles")
    candidates: list[str] = []
    for entry in committed:
        relative = dispatch.safe_relative_path(entry, "plan-checkpoint.committedFiles[]", root)
        path = root / relative
        if path.suffix != ".json" or path.is_symlink() or not path.is_file():
            continue
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("plans"), list):
            candidates.append(relative)
    if len(candidates) != 1:
        raise ValueError("plan-checkpoint must identify exactly one dispatch manifest")
    return candidates[0]


def finding(message: str, file: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {"severity": "high", "targetStep": TARGET_STEP, "message": message}
    if file:
        result["file"] = file
    return result


def validate(envelope: dict[str, Any]) -> dict[str, Any]:
    root = Path.cwd().resolve()
    messages = dispatch.messages_from(envelope)
    checkpoint = latest_checkpoint(messages)
    manifest_path: str | None = None
    try:
        manifest_path = manifest_path_from(checkpoint, root)
        manifest_file = root / manifest_path
        if manifest_file.is_symlink() or not manifest_file.is_file():
            raise ValueError(f"dispatch manifest {manifest_path} must be a regular non-symlink file")
        try:
            manifest = json.loads(manifest_file.read_text())
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"cannot read dispatch manifest {manifest_path}: {error}") from error
        report = dispatch.validate_manifest_contract(manifest, root)
    except ValueError as error:
        report = {"valid": False, "limits": dispatch.tracking_limits(), "plans": [], "errors": [str(error)]}
    report = {"manifestPath": manifest_path, **report}
    contract_valid = report["valid"] is True
    # report["errors"] already aggregates every per-plan error in order.
    findings = [finding(error, manifest_path) for error in report["errors"]]
    payload: dict[str, Any] = {"contract_valid": contract_valid, "report": report, "findings": findings}
    if manifest_path is not None:
        payload["manifestPath"] = manifest_path
    if contract_valid:
        # plan-git-commit renders its commit request from this node's payload.
        for key in PASS_THROUGH_KEYS:
            if key in checkpoint:
                payload[key] = checkpoint[key]
    else:
        payload["needs_revision"] = True
        payload["resumeCriteria"] = [
            "Amend the plans and dispatch manifest: declare generated tool installs, caches and binaries in "
            "artifactRoots (each also a writePaths entry), keep an authored audit manifest in writePaths, or "
            "narrow writePaths; then repeat plan review and the checkpoint."
        ]
    return {"when": {"contract_valid": contract_valid}, "payload": payload}


def main() -> int:
    try:
        envelope = json.loads(sys.stdin.readline())
        if not isinstance(envelope, dict):
            raise ValueError("stdio envelope must be an object")
        print(json.dumps(validate(envelope), separators=(",", ":"), ensure_ascii=False))
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, separators=(",", ":")), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
