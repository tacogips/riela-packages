# Codex Source Security Check Loop

Runs deterministic source-code security checks, asks Codex to triage the
evidence, delegates blocking fixes to `codex-design-and-implement-review-loop`,
and rescans until no high or medium findings remain.

The deterministic scan includes:

- secret-pattern checks
- `gitleaks detect --no-git --redact` when `gitleaks` is available
- static source heuristics for risky code patterns
- dependency manifest inspection and optional package-manager audits
- supply-chain and configuration heuristics

Run from a repository root:

```bash
rielflow workflow run codex-source-security-check-loop \
  --from-registry \
  --registry default \
  --variables '{"workflowInput":{"targetPath":".","runNetworkAudits":"false","maxFindings":50}}'
```

Set `workflowInput.runNetworkAudits` to `"true"` only when dependency audit
commands may access the network.
