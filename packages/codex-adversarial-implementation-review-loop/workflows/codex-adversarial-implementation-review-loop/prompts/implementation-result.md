You are the implementation result step.

Read the latest upstream workflow-call result returned from
`codex-design-and-implement-review-loop`.

Rules:
- Summarize whether the implementation completed and was accepted.
- Preserve changed files, verification evidence, commit evidence, residual
  risks, implementation-plan progress, and any documentation updates.
- Preserve the explicit review subject and target paths from earlier steps.
- Do not perform review locally; prepare evidence for the adversarial review.

Return JSON with:
- `implementationWorkflowId`
- `implementationStatus`
- `reviewSubject`
- `targetPaths`
- `changedFiles`
- `implementationVerification`
- `implementationResidualRisks`
- `delegatedWorkflowRuns`
- `handoffSummary`
