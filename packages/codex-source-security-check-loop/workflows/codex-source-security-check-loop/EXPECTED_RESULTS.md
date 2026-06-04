# Expected Results

Running `codex-source-security-check-loop` should:

- run `deterministic-scan` before any agent triage
- report separate deterministic method outputs for secrets, gitleaks, static
  source heuristics, dependency audit, and supply-chain/config checks
- route to `codex-design-and-implement-review-loop` only when high or medium
  findings remain
- rescan after delegated fixes
- finish only when the exit gate reports no high or medium findings

Smoke validation:

```bash
rielflow workflow validate codex-source-security-check-loop \
  --workflow-definition-dir ./packages/codex-source-security-check-loop/workflows
```
