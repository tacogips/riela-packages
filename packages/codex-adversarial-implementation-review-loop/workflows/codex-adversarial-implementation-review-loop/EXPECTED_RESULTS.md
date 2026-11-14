# Expected Results

Stable assertions for deterministic verification with the bundled mock scenario.
Ignore `sessionId`, timestamps, and artifact paths.

The mock scenario covers the explicit-target review acceptance path with
`skipInitialImplementation` behavior. Normal implementation runs first dispatch
`codex-design-and-implement-review-loop`, then adversarially review and delegate
blocking fixes until no high or medium findings remain.
The final `workflow-output` step must base acceptance on the latest direct
runtime input from `adversarial-review` (`_rielaInput.latest.payload`), not on
older sessions, cached root outputs, or a broad recent-change review.

## Validate

Command:

```bash
riela workflow validate codex-adversarial-implementation-review-loop
```

Expected result: the workflow is valid when this package and
`codex-design-and-implement-review-loop` are installed or otherwise visible to
the workflow loader.

## Run

Command:

```bash
riela workflow run codex-adversarial-implementation-review-loop \
  --mock-scenario .riela/workflows/codex-adversarial-implementation-review-loop/mock-scenario.json \
  --output json
```

Expected stable run summary:

```json
{
  "status": "completed",
  "workflowName": "codex-adversarial-implementation-review-loop",
  "workflowId": "codex-adversarial-implementation-review-loop",
  "nodeExecutions": 3,
  "transitions": 2,
  "exitCode": 0
}
```

Expected path: `riela-manager` -> `adversarial-review` -> `workflow-output`

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
