# Expected Results

Stable assertions for deterministic verification with the bundled mock scenario.
Ignore `sessionId`, timestamps, and artifact paths.
Use the available `rielflow` command. Add `--scope user` for a user-scope
install, or validate through the registry-wide package checks when testing this
source repository.

## Validate

Command:

```bash
rielflow workflow validate codex-impl-plan-completion-review-loop
```

Expected result: the workflow is valid when this package and its dependencies
are installed or otherwise visible to the workflow loader.

## Run

Command:

```bash
rielflow workflow run codex-impl-plan-completion-review-loop \
  --mock-scenario .rielflow/workflows/codex-impl-plan-completion-review-loop/mock-scenario.json \
  --output json
```

Expected stable run summary:

```json
{
  "status": "completed",
  "workflowName": "codex-impl-plan-completion-review-loop",
  "workflowId": "codex-impl-plan-completion-review-loop",
  "nodeExecutions": 6,
  "transitions": 5,
  "exitCode": 0
}
```

Expected final output node: `final-output`

Expected stable workflow-call facts:

- the parent session first calls `codex-impl-plan-completion-loop`
- the parent session resumes at `impl-loop-result`
- the parent session then calls `codex-recent-change-quality-loop`
- the parent session resumes at `review-loop-result`

Expected final output payload:

```json
{
  "status": "accepted",
  "workflowId": "codex-impl-plan-completion-review-loop",
  "childWorkflowRuns": [
    {
      "workflowId": "codex-impl-plan-completion-loop",
      "status": "completed"
    },
    {
      "workflowId": "codex-recent-change-quality-loop",
      "status": "accepted"
    }
  ],
  "completedPlans": ["impl-plans/completed/example-complete-plan.md"],
  "activePlansRemaining": [],
  "reviewedRange": "HEAD~1..HEAD plus clean working tree",
  "finalFindings": [],
  "fixIterations": 0,
  "changedFiles": [
    "impl-plans/completed/example-complete-plan.md",
    "impl-plans/README.md"
  ],
  "verification": [
    {
      "command": "mock implementation-plan completion verification",
      "result": "passed"
    },
    "mock recent-change review verification"
  ],
  "residualRisks": [],
  "operatorNotes": [
    "Implementation-plan completion ran before recent-change review."
  ]
}
```
