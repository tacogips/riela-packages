---
name: codex-task-queue
description: Use when adding, deleting, listing, showing, or editing codex task queue items in ./tasks/list.jsonl for the packaged codex-task-watchdog workflow.
user-invocable: true
---

# Codex Task Queue

Use this skill to manage the `./tasks/list.jsonl` queue consumed by the
packaged `codex-task-watchdog` workflow.

## Invocation Phrases

Treat these user requests as requests to add an `active` item to the watchdog
task queue:

- `watchdog taskを追加せよ`
- `watchdog taskを追加して`
- `Codex watchdogにタスクを積んで`
- `codex-task-watchdogにこの作業を予約して`
- `tasks/list.jsonlにwatchdog用タスクを追加して`

When the user says `watchdog task`, assume they mean a task queue item for
`codex-task-watchdog`, not starting or stopping the background watcher, unless
they explicitly mention daemon setup, cron/event serving, start, stop, or
status inspection.

## Queue File

Default path: `./tasks/list.jsonl`.

Each line is one JSON object. Recommended fields:

```json
{
  "id": "task-20260604-001",
  "status": "active",
  "kind": "design-and-impl",
  "title": "Short task title",
  "prompt": "Concrete work request for Codex or a dependency workflow.",
  "workflowInput": {},
  "constraints": [],
  "acceptanceCriteria": [],
  "createdAt": "2026-06-04T00:00:00.000Z"
}
```

Statuses:
- `active`: runnable by the next watchdog polling pass.
- `running`: claimed by the workflow; later polling passes skip while this exists.
- `done`: completed; when every task is done, polling passes skip.
- `failed` or `cancelled`: ignored by automatic selection.

Kinds:
- `design-and-impl`: dispatches `codex-design-and-implement-review-loop`.
- `design-deepthin`, `design-deepthink`, `deepdesign`, or `design`: dispatches `codex-deepdesign`.
- `review`: dispatches `codex-recent-change-quality-loop`.
- `adhoc`: runs the prompt in the local Codex worker step.

## Add A Task

1. Ensure `tasks/` exists.
2. Append one compact JSON object to `tasks/list.jsonl`.
3. Generate a stable `id`; use timestamp ids when the user does not specify one.
4. Set `status` to `active` unless the user explicitly asks otherwise.
5. Put dependency-workflow-specific inputs under `workflowInput` instead of inventing top-level fields.

Example:

```bash
mkdir -p tasks
printf '%s\n' '{"id":"task-20260604-001","status":"active","kind":"adhoc","title":"Update docs","prompt":"Refresh README for the new option.","workflowInput":{},"createdAt":"2026-06-04T00:00:00.000Z"}' >> tasks/list.jsonl
```

## List Tasks

Use `jq` when available:

```bash
jq -c . tasks/list.jsonl
```

Fallback:

```bash
sed -n '1,200p' tasks/list.jsonl
```

## Show A Task

```bash
jq -c 'select(.id == "task-20260604-001")' tasks/list.jsonl
```

## Delete A Task

Rewrite the JSONL file without the matching id:

```bash
tmp="$(mktemp)"
jq -c 'select(.id != "task-20260604-001")' tasks/list.jsonl > "$tmp"
mv "$tmp" tasks/list.jsonl
```

Do not delete a `running` task unless the user explicitly asks to recover or
cancel the active run. Prefer changing it to `failed` or `cancelled` with a
short `result.note`.

## Recovery

If a workflow run died and left a stale `running` task, inspect the rielflow
session artifacts first. Then either:
- set `status` back to `active` to retry, or
- set `status` to `failed` with `result.reason`.

After a successful run, `codex-task-watchdog` may also create or update
project-scope skills under `.agents/skills` based on the completed Codex log and
commit the accepted task queue and skill changes.
