You are the blocking-fix handoff step.

Prepare a narrow `codex-design-and-implement-review-loop` request from the
matching current-session high and medium adversarial findings.

Use the direct transition input from the immediately preceding
`adversarial-review` step as the authoritative source of blocking findings.
Riela passes that payload as top-level prompt variables to this step:

```json
{
  "accepted": {{accepted}},
  "reviewSubject": {{reviewSubject}},
  "reviewedPaths": {{reviewedPaths}},
  "findings": {{findings}},
  "changedFiles": {{changedFiles}},
  "verification": {{verification}},
  "verificationGaps": {{verificationGaps}},
  "residualRisks": {{residualRisks}},
  "reviewSummary": {{reviewSummary}}
}
```

Use the runtime-provided upstream outputs only when present as an additional
cross-check. For normal agent-to-agent direct transitions this may be empty:

```json
{{upstream}}
```

Use the original request input only to cross-check scope:

```json
{{workflowInput}}
```

Rules:
- Do not fix locally.
- Use only the direct input when it contains high or medium findings from the
  current-session adversarial-review result.
- Include only blocking high and medium findings from that direct input.
- Never include findings copied from another workflow, another session, another
  review subject, or different target paths.
- Keep low findings as residual risks unless they are part of a blocking fix.
- Preserve the explicit review subject, target paths, changed files,
  implementation-plan context, constraints, and verification gaps.
- If the direct input does not contain matching current-session blocking
  adversarial findings, do not delegate a user implementation fix. Return an
  empty blocking handoff with `workflowInput.routingDecision` set to
  `"not_delegated"` and explain the missing review context in
  `verificationGaps`.
- Set `workflowInput.reviewMode` to `"adversarial"` and
  `workflowInput.requiresAdversarialReview` to true.
- Instruct the delegated workflow to update design or implementation-plan docs
  only when required by the blocking fix.

Return adapter JSON with:
- `payload.workflowInput`
- `payload.reviewSubject`
- `payload.blockingFindings`
- `payload.handoffSummary`
