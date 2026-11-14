You are the final output step for `codex-impl-plan-completion-review-loop`.

Read the implementation-loop result and review-loop result.

Return JSON with:
- `status`: `accepted` only when the implementation loop completed and the review loop returned accepted
- `workflowId`: `codex-impl-plan-completion-review-loop`
- `childWorkflowRuns`
- `completedPlans`
- `activePlansRemaining`
- `reviewedRange`
- `finalFindings`
- `fixIterations`
- `changedFiles`
- `verification`
- `residualRisks`
- `operatorNotes`

If either child workflow failed or returned unresolved blocking work, set `status` to `blocked` and include the child workflow id and blocking reason.
