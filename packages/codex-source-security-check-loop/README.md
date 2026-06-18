# Codex Source Security Check Loop

Runs deterministic source-code security checks, derives harness-style
attack-surface focus areas, asks Codex to triage the evidence, adversarially
verifies candidate findings, delegates blocking fixes to
`codex-design-and-implement-review-loop`, and rescans until no verified high or
medium findings remain.

The deterministic scan includes:

- secret-pattern checks
- `gitleaks detect --no-git --redact` when `gitleaks` is available
- static source heuristics for risky code patterns
- dependency manifest inspection and optional package-manager audits
- supply-chain and configuration heuristics

The agent review stages incorporate read-only logic from Anthropic's
`defending-code-reference-harness`:

- threat-model and recon-style focus area partitioning before triage
- independent adversarial verification before fix routing
- semantic dedupe and report-quality scoring for high and medium candidates
- explicit coverage gaps for deferred execution-only harness behavior such as
  ASAN PoC reproduction in a fresh sandbox

Run from a repository root:

```bash
riela workflow run codex-source-security-check-loop \
  --from-registry \
  --registry default \
  --variables '{"workflowInput":{"targetPath":".","runNetworkAudits":"false","maxFindings":50}}'
```

Set `workflowInput.runNetworkAudits` to `"true"` only when dependency audit
commands may access the network.
