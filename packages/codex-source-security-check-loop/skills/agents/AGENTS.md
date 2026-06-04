# codex-source-security-check-loop

Use the packaged `codex-source-security-check-loop` workflow when source code
needs a deterministic security check, credential scan, SAST-style review,
dependency/security audit, or fix loop for high and medium findings.

Default run:

```bash
rielflow workflow run codex-source-security-check-loop \
  --variables '{"workflowInput":{"targetPath":".","runNetworkAudits":"false","maxFindings":50}}' \
  --output json --no-auto-improve
```

Keep fixes narrowly scoped to verified high or medium findings and preserve
dirty worktree constraints.
