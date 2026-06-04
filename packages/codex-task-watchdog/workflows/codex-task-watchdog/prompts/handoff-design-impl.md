You are preparing a dependency workflow call to `codex-design-and-implement-review-loop`.

Read the latest `claim-next-task` output and use its `payload.task` as the source of truth.

Task fields:
- `prompt` is the primary requested behavior.
- `title` is the issue title when present.
- `workflowInput` may already contain fields accepted by `codex-design-and-implement-review-loop`; preserve it.
- `constraints`, `targetFeatureArea`, `referenceRepositoryRoot`, and `referenceRepositoryUrl` should be carried through when present.

Build a narrow issue-resolution request. Prefer explicit `task.workflowInput` values when present, and fill missing fields from the task:
- `executionMode`: default `issue-resolution`.
- `issueTitle`: `task.title` or `task.id`.
- `issueBody`: `task.prompt`.
- `requestedBehavior`: `task.prompt`.
- `targetFeatureArea`: `task.targetFeatureArea` or `task.workflowInput.targetFeatureArea`.
- `referenceRepositoryRoot`: `task.referenceRepositoryRoot` or `task.cwd` when present.

Return JSON with:
- `workflowInput`
- `task`
- `reviewContext`
- `handoffSummary`
