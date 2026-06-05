# Expected Results

Stable assertions for deterministic verification with the bundled mock scenario.
Ignore `sessionId`, timestamps, and artifact paths.

## Validate

Command:

```bash
bun run packages/rielflow/src/bin.ts workflow validate codex-deepdesign --workflow-definition-dir ./packages/codex-deepdesign/workflows
```

Expected result: the workflow is valid.

## Run

Command:

```bash
bun run packages/rielflow/src/bin.ts workflow run codex-deepdesign \
  --workflow-definition-dir ./packages/codex-deepdesign/workflows \
  --mock-scenario ./packages/codex-deepdesign/workflows/codex-deepdesign/mock-scenario.json \
  --output json
```

Expected stable run summary:

```json
{
  "status": "completed",
  "workflowName": "codex-deepdesign",
  "workflowId": "codex-deepdesign",
  "nodeExecutions": 8,
  "transitions": 7,
  "exitCode": 0
}
```

Expected final output node: `workflow-output`

Expected final output payload:

```json
{
  "status": "accepted",
  "feature": "Deep design workflow package",
  "designDocPaths": [
    "design-docs/specs/design-codex-deepdesign.md"
  ],
  "designSummary": "Accepted design workflow with one author, one deep reviewer, one broad reviewer, one adversarial reviewer, and revision loops for high or middle findings.",
  "deepReviewSummary": "One middle finding was fixed, then the deep review accepted.",
  "broadReviewSummary": "Broad review accepted with no high or middle findings.",
  "adversarialReviewSummary": "Adversarial review accepted with no high or middle findings.",
  "acceptedFindings": [],
  "provisionalDecisions": [
    {
      "decision": "Low findings do not block final acceptance.",
      "confirmationNeed": "The user did not specify the treatment of low findings.",
      "rationale": "The requested loop only mentions high and middle findings as blockers.",
      "revisitPath": "Promote low findings to blocking if a future run requires exhaustive cleanup."
    }
  ],
  "residualLowRisks": [
    "Future workflows may want a configurable severity threshold."
  ],
  "verificationPlan": [
    "workflow validate",
    "workflow run --mock-scenario"
  ],
  "recommendedNextSteps": [
    "Use the accepted design as input for implementation planning."
  ]
}
```
