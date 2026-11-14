# Expected Results

`mock-scenario.json` verifies the wrapper graph without calling live models:

- `fable-goal-plan` creates markdown `goalMarkdown` and `planMarkdown`.
- `codex-implementation-handoff` emits a `payload.workflowInput` for
  `codex-design-and-implement-review-loop`.
- The child Codex workflow mock completes an issue-resolution path.
- `fable-goal-review` returns `needs_replan: false` and `needs_todo: false`.
- `final-output` returns `status: completed` and `goalAchieved: true`.

Stable assertions:

```json
{
  "workflowId": "fable-and-improve",
  "status": "completed",
  "rootOutput": {
    "status": "completed",
    "goalAchieved": true,
    "delegatedWorkflowRuns": [
      "codex-design-and-implement-review-loop"
    ]
  }
}
```
