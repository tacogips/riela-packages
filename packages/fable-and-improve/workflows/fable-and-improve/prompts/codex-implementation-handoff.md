You are the Codex implementation handoff step for `fable-and-improve`.

Prepare a delegated workflow-call input for `codex-design-and-implement-review-loop`. Do not implement locally in this wrapper workflow.

Rules:
- Read the latest Fable goal/plan output and, when this is a follow-up loop, the latest Fable goal-review TODOs.
- Preserve the Fable `goalMarkdown` and `planMarkdown` in the child workflow input.
- Convert the Fable plan into a concrete `workflowInput` that `codex-design-and-implement-review-loop` can intake.
- Use `executionMode: "issue-resolution"` unless Fable explicitly chose planning-only.
- Set `issueTitle` to a short actionable title.
- Set `requestedBehavior` to a concise instruction that includes the markdown plan and any follow-up TODOs.
- Preserve constraints, acceptance criteria, target scope, review mode, risk level, and verification hints.
- Make clear that the child workflow owns implementation, review, improvement, verification, documentation refresh, and any commit/push behavior already defined by that child workflow.

Return adapter JSON shaped like (the `when` envelope keeps the accepted
payload identical between live and mock runs — without it the `payload`
wrapper would itself become the accepted payload):

```json
{
  "when": {
    "always": true
  },
  "payload": {
    "workflowInput": {
      "executionMode": "issue-resolution",
      "issueTitle": "Short title",
      "requestedBehavior": "Implement the Fable plan...",
      "targetFeatureArea": "Relevant area",
      "constraints": [],
      "acceptanceCriteria": [],
      "verificationHint": "",
      "reviewMode": "standard",
      "riskLevel": "normal",
      "fableGoalMarkdown": "## Goal\n...",
      "fablePlanMarkdown": "## Plan\n...",
      "fableFollowUpTodos": []
    },
    "fableContext": {
      "sourceWorkflowId": "fable-and-improve",
      "nextStep": "codex-implementation-result"
    },
    "handoffSummary": "Delegating the Fable plan to Codex for implementation and review."
  }
}
```
