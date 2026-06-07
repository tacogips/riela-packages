You are the initial implementation handoff step.

Build a delegated workflow-call input for `codex-design-and-implement-review-loop`
from the normalized manager output.

Rules:
- Do not implement locally.
- Preserve all user-supplied implementation fields that
  `codex-design-and-implement-review-loop` can consume.
- Set `workflowInput.reviewMode` to `"adversarial"` unless the user supplied a
  stricter value.
- Set `workflowInput.requiresAdversarialReview` to true.
- Preserve active implementation-plan metadata when present.
- Include an `adversarialReviewContext` with the explicit `reviewSubject`,
  `targetPaths`, and constraints so the delegated workflow knows this run will
  be followed by an independent adversarial review loop.

Return adapter JSON shaped like:

```json
{
  "payload": {
    "workflowInput": {
      "executionMode": "issue-resolution",
      "reviewMode": "adversarial",
      "requiresAdversarialReview": true,
      "requestedBehavior": "Implement the scoped request.",
      "adversarialReviewContext": {
        "reviewSubject": "Explicit subject",
        "targetPaths": [],
        "constraints": []
      }
    },
    "reviewSubject": "Explicit subject",
    "handoffSummary": "Delegating initial implementation before adversarial review."
  }
}
```
