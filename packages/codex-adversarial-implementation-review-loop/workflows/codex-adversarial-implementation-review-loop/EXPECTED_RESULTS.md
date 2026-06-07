# Expected Results

Stable assertions for deterministic verification with the bundled mock scenario.
Ignore `sessionId`, timestamps, and artifact paths.

The mock scenario covers the explicit-target review acceptance path with
`skipInitialImplementation` behavior. Normal implementation runs first dispatch
`codex-design-and-implement-review-loop`, then adversarially review and delegate
blocking fixes until no high or medium findings remain.

## Validate

Command:

```bash
rielflow workflow validate codex-adversarial-implementation-review-loop
```

Expected result: the workflow is valid when this package and
`codex-design-and-implement-review-loop` are installed or otherwise visible to
the workflow loader.

## Run

Command:

```bash
rielflow workflow run codex-adversarial-implementation-review-loop \
  --mock-scenario .rielflow/workflows/codex-adversarial-implementation-review-loop/mock-scenario.json \
  --output json
```

Expected stable run summary:

```json
{
  "status": "completed",
  "workflowName": "codex-adversarial-implementation-review-loop",
  "workflowId": "codex-adversarial-implementation-review-loop",
  "nodeExecutions": 4,
  "transitions": 3,
  "exitCode": 0
}
```

Expected path: `rielflow-manager` -> `adversarial-review` -> `exit-gate` -> `workflow-output`

Expected final output node: `workflow-output`

Expected final output payload:

```json
{
  "status": "accepted",
  "workflowId": "codex-adversarial-implementation-review-loop",
  "reviewSubject": "Adversarially review completed active plan implementation.",
  "finalFindings": [],
  "residualRisks": []
}
```
