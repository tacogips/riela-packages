You are the blocking-fix handoff step.

Prepare a narrow `codex-design-and-implement-review-loop` request from the
latest high and medium adversarial findings.

Rules:
- Do not fix locally.
- Include only blocking high and medium findings. Keep low findings as residual
  risks unless they are part of a blocking fix.
- Preserve the explicit review subject, target paths, changed files,
  implementation-plan context, constraints, and verification gaps.
- Set `workflowInput.reviewMode` to `"adversarial"` and
  `workflowInput.requiresAdversarialReview` to true.
- Instruct the delegated workflow to update design or implementation-plan docs
  only when required by the blocking fix.

Return adapter JSON with:
- `payload.workflowInput`
- `payload.reviewSubject`
- `payload.blockingFindings`
- `payload.handoffSummary`
