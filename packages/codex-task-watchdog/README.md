# codex-task-watchdog

`codex-task-watchdog` is a rielflow event-source package for watching
`./tasks/list.jsonl` and processing newly added Codex tasks one at a time.

It runs under `rielflow events serve` with a cron source. Each scheduled tick is
one watchdog polling pass:

1. Skips when any task is already `running`.
2. Skips when the queue is missing, empty, all `done`, or has no `active` task.
3. Marks the first `active` task as `running`.
4. Dispatches by `kind`:
   - `design-and-impl` -> `codex-design-and-implement-review-loop`
   - `design-deepthin`, `design-deepthink`, `deepdesign`, `design` -> `codex-deepdesign`
   - `review` -> `codex-recent-change-quality-loop`
   - `adhoc` -> local Codex worker
5. Marks the running task `done` after delegated or ad hoc completion.

The package includes `codex-task-queue` and `codex-task-watchdog` skills for queue
management and background event-server operation.
