You are preparing a dependency workflow call to `codex-recent-change-quality-loop`.

Read the latest `claim-next-task` output and use its `payload.task` as the source of truth.

Task fields:
- `prompt` describes the review scope.
- `workflowInput` may already contain fields accepted by `codex-recent-change-quality-loop`; preserve it.
- `hours`, `targetPaths`, `constraints`, and `reviewFocus` should be carried through when present.

Build a review request:
- `hours`: `task.workflowInput.hours` or `task.hours` or `24`.
- `request`: `task.prompt`.
- `targetPaths`: preserve when present.
- `constraints`: preserve when present.
- `reviewFocus`: preserve when present.
- `taskId`: the task id.

Return JSON with:
- `workflowInput`
- `task`
- `handoffSummary`
