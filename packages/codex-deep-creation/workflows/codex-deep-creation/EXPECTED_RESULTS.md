# Expected Results

Stable assertions for deterministic verification with the bundled mock scenario.
Ignore `sessionId`, timestamps, and artifact paths.

## Validate

Command:

```bash
rielflow workflow validate codex-deep-creation
```

Expected result: the workflow is valid when this package and its dependencies
are installed or otherwise visible to the workflow loader.

## Run

Command:

```bash
rielflow workflow run codex-deep-creation \
  --mock-scenario .rielflow/workflows/codex-deep-creation/mock-scenario.json \
  --output json
```

Expected stable run summary:

```json
{
  "status": "completed",
  "workflowName": "codex-deep-creation",
  "workflowId": "codex-deep-creation",
  "nodeExecutions": 8,
  "transitions": 7,
  "exitCode": 0
}
```

Expected path: `creation-manager` -> `deepdesign-handoff` -> `deepdesign-result` -> `impl-completion-handoff` -> `impl-completion-result` -> `security-handoff` -> `security-result` -> `workflow-output`

Expected final output node: `workflow-output`

Expected final output payload:

```json
{
  "status": "accepted",
  "workflowId": "codex-deep-creation",
  "childWorkflowRuns": [
    {
      "workflowId": "codex-deepdesign",
      "status": "accepted"
    },
    {
      "workflowId": "codex-impl-plan-completion-loop",
      "status": "completed"
    },
    {
      "workflowId": "codex-source-security-check-loop",
      "status": "accepted"
    }
  ],
  "securityStatus": "accepted",
  "residualRisks": []
}
```
