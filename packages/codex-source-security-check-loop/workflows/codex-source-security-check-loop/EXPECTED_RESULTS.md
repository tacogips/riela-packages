# Expected Results

The deterministic scanner and harness recon must emit complete attack-surface
review items. Riela dispatches 3–8 read-only security reviews concurrently, then
the serial triage and adversarial verification steps fail closed on missing or
failed branch coverage before any remediation is accepted.

Running `codex-source-security-check-loop` should:

- run `deterministic-scan` before any agent triage
- run `harness-recon` after deterministic scanning to derive attack-surface
  focus areas, threat classes, and verifier rubric
- report separate deterministic method outputs for secrets, gitleaks, static
  source heuristics, dependency audit, and supply-chain/config checks
- run `adversarial-verification` before the exit gate to verify, dedupe, and
  rerank triaged findings
- route to `codex-design-and-implement-review-loop` only when adversarially
  verified high or medium findings remain
- rescan after delegated fixes
- finish only when the exit gate reports no verified high or medium findings

Smoke validation:

```bash
riela workflow validate codex-source-security-check-loop \
  --workflow-definition-dir ./packages/codex-source-security-check-loop/workflows
```
