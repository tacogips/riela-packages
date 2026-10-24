# gate-routing-plan-archive

Status: active. Wave 1. Issue tacogips/riela#129.

```json
{
  "planId": "gate-routing-plan-archive",
  "planPath": "impl-plans/active/gate-routing-plan-archive.md",
  "dependsOn": [],
  "writePaths": [
    "impl-plans/active/gate-routing-plan-archive.md",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/scripts/plan-archive.py",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/nodes/node-plan-archive.json",
    "packages/opus-luna-design-and-implement-review-loop/tests/test_plan_archive.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "test -x packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/scripts/plan-archive.py",
    "python3 -m json.tool packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/nodes/node-plan-archive.json",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-luna-design-and-implement-review-loop/tests/test_plan_archive.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-luna-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "find packages/opus-luna-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "New executable W/scripts/plan-archive.py reads the latest step8-docs-refresh payload's archiveRequests and applies each request with os.rename. It assigns statuses moved, already-archived, conflict, missing or rejected per design D6.3, never invokes git, and forwards every Step 8 key plus archiveResults, archivedImplPlanPaths, docsRefreshRound and completion_blocked, with the same boolean in when.",
    "When the step8-docs-refresh message count exceeds MAX_DOCS_REFRESH_ROUNDS (3), the script still applies the requests and returns completion_blocked true with implementation_blocked true, status blocked, blockedStepId step9-commit-message, blockedPlanIds, successfulPlanIds [], a completion-archive-loop blocker, resumeCriteria, nextStep, and the forwarded Step 8 issueReference (never fabricated or replaced).",
    "New W/nodes/node-plan-archive.json is a command node with scriptPath scripts/plan-archive.py and an output jsonSchema that requires completion_blocked, archiveResults and docsRefreshRound, with additionalProperties true.",
    "test_plan_archive.py covers design Verification 6 and passes. Opus-luna package tests pass and no __pycache__ remains."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-luna-gate-routing-0110.md` D6. `W`/`T` as in `impl-plans/active/gate-routing-negative-control.md`.

Session 232 looped through step8 -> step9 -> step8 (executions 1338-1342). Step 8's sandbox denied `mv`/`git mv` for archiving `impl-plans/active/*` to `impl-plans/completed/`, and read-only Step 9 kept rejecting the result. This plan provides the deterministic mover and the round bound.

- `gate-routing-graph` wires `step8-docs-refresh -> plan-archive -> step9-commit-message | implementation-blocked-output`.
- `gate-routing-runtime-prompts` changes the Step 8, Step 9 and blocked-output prompts.

## Non-goals

- Do not stage, commit or call `git`/`subprocess` at all. Step 9 lists source and destination in `committedFiles`, and `riela/git-commit` stages them.
- Do not decide which plans are complete. Step 8 decides. Do not edit `impl-plans/README.md`.
- Do not edit `workflow.json`, prompts or other nodes.

## File-level changes

1. `W/scripts/plan-archive.py`: a new file, mode 755, standard library only (`json`, `os`, `stat`, `sys`, `pathlib`, `typing`).
   - Pinned constants: `ACTIVE = "impl-plans/active"`, `COMPLETED = "impl-plans/completed"`, `STEP8 = "step8-docs-refresh"`, `MAX_DOCS_REFRESH_ROUNDS = 3`.
   - Pinned `route(envelope: dict, root: Path) -> dict`. `main()` calls it with `Path.cwd().resolve()`.
   - **Messages.** Copy the `messages_from` pattern from `W/scripts/dispatch-plans.py:messages_from`. Do not import that module. Take the `fromStepId == STEP8` messages with a dict payload. None -> `ValueError` (exit 1). The latest by `createdOrder` is the request source.
   - **Requests.** `archiveRequests` that is not a list -> one result `{"source": None, "destination": None, "status": "rejected", "message": "archiveRequests must be an array"}`. Each item must be a dict with str `source` and `destination`.
   - **Per request, in order:**
     1. **Path checks.** Reject when the path is absolute, has an empty part, contains `..`, `.git` or a backslash, `PurePosixPath(source).parent != PurePosixPath(ACTIVE)`, or `destination != f"{COMPLETED}/{basename}"`.
     2. **Directory checks.** `os.lstat` each of `impl-plans`, `impl-plans/active` and `impl-plans/completed` that exists. A symlink -> rejected. `impl-plans/completed` absent -> `os.mkdir`, but only if `impl-plans` is a real directory.
     3. **Source state.** Source exists and is not a regular file (symlink, dir or special; use `stat.S_ISREG` on `lstat`) -> rejected.
     4. **Destination state.**
        - Source absent and destination a regular file -> `already-archived`.
        - Both exist -> `conflict` (touch neither).
        - Neither exists -> `missing`.
        - Otherwise `os.rename(root/source, root/destination)` -> `moved`. An `OSError` -> `rejected` with the error text.
   - **Output.**
     - `archivedImplPlanPaths` = destinations whose status is `moved` or `already-archived`.
     - `docsRefreshRound` = the count of step8 messages.
     - `completion_blocked = docsRefreshRound > MAX_DOCS_REFRESH_ROUNDS`.
     - `payload = {**latest_step8_payload, "archiveResults": results, "archivedImplPlanPaths": ..., "docsRefreshRound": n, "completion_blocked": flag}`.
   - **When blocked**, also set:
     - `implementation_blocked: True`, `status: "blocked"`, `blockedStepId: "step9-commit-message"`;
     - `blockedPlanIds` = sorted `PurePosixPath(source).stem` of unresolved results (status not moved or already-archived), skipping None;
     - `successfulPlanIds: []`;
     - `blockers: [{"type": "completion-archive-loop", "dependency": "impl-plans/active", "paths": [...unresolved sources], "results": unresolved, "message": "Step 9 rejected completion three times; plan archiving or index updates still need operator action."}]`;
     - `resumeCriteria: ["Operator: move the listed plans from impl-plans/active to impl-plans/completed, update impl-plans/README.md, then rerun from step9-commit-message."]`;
     - `nextStep` naming the unresolved paths, or "review the Step 9 completion findings" when there are none.
     - `issueReference` is the latest Step 8 payload's `issueReference`, carried through by the `**latest_step8_payload` spread. Never overwrite it, default it, or synthesize a placeholder: the Step 8 node schema (owned by `gate-routing-graph`) makes it a required non-empty string, and `implementation-blocked-output` requires it. This addresses Step 5 finding S5-F1.
   - Return `{"when": {"completion_blocked": flag}, "payload": payload}`.
2. `W/nodes/node-plan-archive.json`.
   - Imitate `W/nodes/node-plan-push-gate.json`: `id "plan-archive"`, `description`, `nodeType "command"`, `command.scriptPath "scripts/plan-archive.py"`, `variables {}`.
   - `output.description` plus `jsonSchema {type:"object", properties:{completion_blocked:{type:"boolean"}, archiveResults:{type:"array",items:{type:"object"}}, archivedImplPlanPaths:{type:"array",items:{type:"string"}}, docsRefreshRound:{type:"integer"}}, required:["completion_blocked","archiveResults","docsRefreshRound"], additionalProperties:true}`.
3. `T/test_plan_archive.py`: a new module.
   - Load the script with `importlib`, and call `route(envelope, root)` with a temp dir root.
   - Patch `subprocess.run` and `subprocess.Popen` (`unittest.mock.patch`) to raise if called.

## Key points and pitfalls

- Use `os.lstat`, never `os.stat`: symlinks must be detected, not followed.
- A conflict must leave both files byte-identical.
- The round count includes the current message. The 4th Step 8 message is the first blocked run.
- Results keep request order. Duplicate requests: the second becomes `already-archived`.

## Test cases

- `impl-plans/active/a.md` exists, and request a -> completed/a.md -> `moved`. The file now lives at the destination, and `archivedImplPlanPaths == ["impl-plans/completed/a.md"]`.
- The same request again (source gone, destination present) -> `already-archived`.
- Both present -> `conflict`, both unchanged.
- Neither present -> `missing`.
- Rejected forms:
  - source `impl-plans/a.md`;
  - destination `impl-plans/completed/b.md` for source a.md;
  - `../x.md`;
  - an absolute path;
  - a source symlink;
  - a source directory;
  - a symlinked `impl-plans/completed`;
  - `archiveRequests: "x"`.
- Step 8 keys (`documentationFiles`, `workflowMode`) are forwarded.
- 4 step8 messages, each payload carrying `issueReference: "tacogips/riela#129"`, with an unresolved `missing` request for `impl-plans/active/p.md` -> `when == {"completion_blocked": True}`, `blockedPlanIds == ["p"]`, `payload.issueReference == "tacogips/riela#129"`, and non-empty `blockers`, `resumeCriteria` and `nextStep`.
- 3 step8 messages -> `completion_blocked` False.
- No step8 message -> `ValueError`.
- The patched subprocess is never called.

## Done criteria

- All verification commands exit 0. Evidence is under `tmp/opus-luna-gate-routing/gate-routing-plan-archive/`.

## Progress log

- (implementer appends dated entries)
