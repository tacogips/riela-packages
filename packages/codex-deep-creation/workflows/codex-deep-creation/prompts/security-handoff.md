You are the security-check handoff step.

Build a delegated workflow-call input for `codex-source-security-check-loop`.

Rules:
- Use `workflowInput.securityTargetPath` when supplied; otherwise use the
  narrowest explicit target path set from implementation completion, or `"."`
  when no narrower path is available.
- Preserve `runNetworkAudits` only when explicitly supplied. Default to
  `"false"` for registry-safe runs.
- Include completed plans, changed files, verification evidence, and residual
  risks as `creationContext`.
- Preserve constraints and keep fixes scoped to verified security findings.
- Do not run security checks locally.

Return adapter JSON with:
- `payload.workflowInput`
- `payload.handoffSummary`
