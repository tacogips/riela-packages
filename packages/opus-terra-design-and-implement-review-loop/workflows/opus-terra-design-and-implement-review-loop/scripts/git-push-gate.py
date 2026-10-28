#!/usr/bin/env python3
"""Route an accepted riela/git-commit result to publication or a local-only finish.

`workflowInput.gitPush` (default true) decides whether the commit is pushed and
integrated into the base branch. With `gitPush: false` the run commits locally
only: the gate forwards the commit payload unchanged so downstream steps keep
the same `git` evidence, and its `local_only` branch skips riela/git-push and
base-branch integration.
"""
import json
import sys
from typing import Any

COMMIT_STEPS = {"plan-git-commit", "step10-git-commit"}


def workflow_inputs(variables: dict[str, Any]) -> list[Any]:
    # A cross-workflow call's own input takes precedence over parent defaults.
    call = variables.get("workflowCall")
    call_input = call.get("input") if isinstance(call, dict) else None
    called = call_input.get("workflowInput") if isinstance(call_input, dict) else None
    return [called, variables.get("workflowInput")]


def push_enabled(variables: dict[str, Any]) -> bool:
    for workflow_input in workflow_inputs(variables):
        if not isinstance(workflow_input, dict) or "gitPush" not in workflow_input:
            continue
        value = workflow_input["gitPush"]
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lower() in {"true", "false"}:
            return value.strip().lower() == "true"
        raise ValueError("workflowInput.gitPush must be a boolean")
    return True


def latest_commit(envelope: dict[str, Any]) -> dict[str, Any]:
    input_payload = envelope.get("input")
    metadata = input_payload.get("_rielaInput") if isinstance(input_payload, dict) else None
    messages = metadata.get("messages") if isinstance(metadata, dict) else None
    commits = [
        message
        for message in (messages if isinstance(messages, list) else [])
        if isinstance(message, dict)
        and message.get("fromStepId") in COMMIT_STEPS
        and isinstance(message.get("payload"), dict)
        and isinstance(message["payload"].get("git"), dict)
        and message["payload"]["git"].get("operation") == "commit"
    ]
    if not commits:
        raise ValueError("git-push-gate requires an accepted riela/git-commit message")
    return max(commits, key=lambda message: message.get("createdOrder", 0))["payload"]


def route(envelope: dict[str, Any]) -> dict[str, Any]:
    variables = envelope.get("variables")
    push = push_enabled(variables if isinstance(variables, dict) else {})
    payload = dict(latest_commit(envelope))
    payload["gitPush"] = push
    # Command-node routing reads top-level payload booleans; `when` is kept for adapters that honor it.
    payload["push"] = push
    payload["local_only"] = not push
    return {"when": {"push": push, "local_only": not push}, "payload": payload}


def main() -> int:
    try:
        envelope = json.loads(sys.stdin.readline())
        if not isinstance(envelope, dict):
            raise ValueError("stdio envelope must be an object")
        print(json.dumps(route(envelope), separators=(",", ":"), ensure_ascii=False))
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, separators=(",", ":")), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
