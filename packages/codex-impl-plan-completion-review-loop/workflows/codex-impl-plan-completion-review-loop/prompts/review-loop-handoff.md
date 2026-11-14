You are the review-loop handoff step.

Prepare a delegated workflow-call input for `codex-recent-change-quality-loop` after the implementation-plan completion loop has returned.

Rules:
- Read the implementation-loop result and wrapper manager output.
- Set review `hours` from `workflowInput.hours` when present; otherwise default to 24.
- Include `targetPaths` from `workflowInput.targetPaths` when supplied.
- Include implementation evidence so the review loop can prioritize the files and plan changes produced by the implementation loop.
- The child review workflow owns reviewing recent committed and uncommitted changes, delegating blocking fixes, re-reviewing, and accepting only when no high or mid findings remain.
- Do not review or fix findings locally in this wrapper step.

Return adapter JSON shaped like:

```json
{
  "payload": {
    "workflowInput": {
      "hours": 24,
      "targetPaths": ["src/example.ts"],
      "reviewContext": {
        "sourceWorkflowId": "codex-impl-plan-completion-loop",
        "implementationChangedFiles": [],
        "implementationVerification": [],
        "implementationResidualRisks": []
      }
    },
    "handoffSummary": "Delegating recent-change review after implementation-plan completion."
  }
}
```
