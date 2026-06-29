Summarize the accepted adversarial implementation review-loop result.

Use the direct transition input from the immediately preceding
`adversarial-review` step as the authoritative source of the accepted review.
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

Accept the direct input only when `accepted` is true and there are no high or
medium findings. Ignore older sessions, unrelated workflow output, cached root
outputs, recent history, and any payload whose `reviewSubject` or concrete
paths conflict with the original request input.

Rules:
- Copy `reviewSubject` from the direct adversarial-review input.
- Copy `targetPaths` from `reviewedPaths` or the original request input for
  this same review subject.
- Copy `finalFindings` from the direct input `findings`; do not invent or
  import findings from other sessions.
- Copy `changedFiles`, `verification`, `residualRisks`, and `verificationGaps`
  from the direct input.
- If the direct input is not an accepted adversarial-review result,
  return `status: "failed"` with an operator note explaining the missing
  matching review. Do not summarize unrelated output or rely on `workflowInput`
  alone as proof of acceptance.

Include:
- `status`: `"accepted"`
- `workflowId`
- `reviewSubject`
- `targetPaths`
- `childWorkflowRuns`
- `finalFindings`
- `changedFiles`
- `verification`
- `residualRisks`
- `operatorNotes`

The output must make clear that acceptance is based on the explicit review
subject and concrete paths, not a recent-change time window.
