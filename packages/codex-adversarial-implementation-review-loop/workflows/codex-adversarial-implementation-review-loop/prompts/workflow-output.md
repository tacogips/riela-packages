Summarize the accepted adversarial implementation review-loop result.

Use the runtime-provided latest direct input from the immediately preceding
`adversarial-review` step as the authoritative source of the accepted review:

```json
{{_rielaInput.latest.payload}}
```

Riela also exposes the same direct transition payload as top-level prompt
variables for compatibility:

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

Use the full runtime input provenance only to confirm that the latest message
came from `adversarial-review` and was addressed to `workflow-output`:

```json
{{_rielaInput}}
```

Use the original request input only to cross-check scope:

```json
{{workflowInput}}
```

Do not use upstream outputs, older sessions, cached root outputs, recent
history, or previous review text as acceptance evidence. If
`_rielaInput.latest.payload` is missing, not from `adversarial-review`, or does
not match the requested review subject and paths, return `status: "failed"`.

Accept the latest direct input only when `accepted` is true and there are no
high or medium findings. Ignore any payload whose `reviewSubject` or concrete
paths conflict with the original request input.

Rules:
- Copy `reviewSubject` from `_rielaInput.latest.payload.reviewSubject`.
- Copy `targetPaths` from `_rielaInput.latest.payload.reviewedPaths` or the
  original request input for this same review subject.
- Copy `finalFindings` from `_rielaInput.latest.payload.findings`; do not
  invent or import findings from other sessions.
- Copy `changedFiles`, `verification`, `residualRisks`, and `verificationGaps`
  from `_rielaInput.latest.payload`.
- If the latest direct input is not an accepted adversarial-review result,
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
