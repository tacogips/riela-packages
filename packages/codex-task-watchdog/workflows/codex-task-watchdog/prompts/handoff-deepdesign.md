You are preparing a dependency workflow call to `codex-deepdesign`.

Read the latest `claim-next-task` output and use its `payload.task` as the source of truth.

Task fields:
- `prompt` describes the feature or design question.
- `workflowInput` may already contain fields accepted by `codex-deepdesign`; preserve it.
- `targetDesignDoc`, `constraints`, and `acceptanceCriteria` should be carried through when present.

Build a design request:
- `feature`: `task.workflowInput.feature`, else `task.title`, else `task.prompt`.
- `targetDesignDoc`: from task or task.workflowInput when present.
- `constraints`: combine task constraints and workflowInput constraints when present.
- `acceptanceCriteria`: preserve when present.
- `taskId`: the task id.

Return JSON with:
- `workflowInput`
- `task`
- `handoffSummary`
