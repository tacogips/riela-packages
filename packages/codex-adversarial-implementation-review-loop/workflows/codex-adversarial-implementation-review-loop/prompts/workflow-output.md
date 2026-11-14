Summarize the accepted adversarial implementation review-loop result.

Use only the payloads provided in this input message. Do not run commands.
Do not read files. Do not inspect repository state, logs, skills, sessions, or
prior history. Produce the final JSON immediately from the provided payloads.

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

Use the full runtime input provenance when available to confirm that the latest
message came from `adversarial-review` and was addressed to `workflow-output`:

```json
{{_rielaInput}}
```

Use the original request input only to cross-check scope:

```json
{{workflowInput}}
```

Do not use upstream outputs, older sessions, cached root outputs, recent
history, or previous review text as acceptance evidence. If
`_rielaInput.latest.payload` is present but not from `adversarial-review`, or
does not match the requested review subject and paths, return
`status: "failed"`. If `_rielaInput.latest.payload` is missing but the
top-level compatibility variables contain an accepted review with matching
review subject/path scope, use those compatibility variables as the direct
transition fallback and add an `operatorNotes` entry explaining the fallback.

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
- If neither the latest direct input nor the top-level compatibility fallback is
  an accepted adversarial-review result, return `status: "failed"` with an
  operator note explaining the missing matching review. Do not summarize
  unrelated output or rely on `workflowInput` alone as proof of acceptance.

Include:
- `status`: the string `"accepted"` or `"failed"`
- `workflowId`: the string `"codex-adversarial-implementation-review-loop"`
- `reviewSubject`: a non-empty string
- `targetPaths`: an array of strings
- `childWorkflowRuns`: an array, empty when no delegated child run was used
- `finalFindings`: an array, empty when no findings remain
- `changedFiles`: an array of strings
- `verification`: an array
- `residualRisks`: an array
- `verificationGaps`: an array, empty when there are no gaps
- `operatorNotes`: an array of strings, never a string or object

The output must make clear that acceptance is based on the explicit review
subject and concrete paths, not a recent-change time window.
