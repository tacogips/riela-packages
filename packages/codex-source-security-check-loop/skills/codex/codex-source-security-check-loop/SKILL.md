---
name: codex-source-security-check-loop
description: Use when the user asks Codex to security-check source code, run secure code review, find or fix source security issues, run deterministic SAST or dependency/security scans, or loop fixes until security findings are resolved through the packaged codex-source-security-check-loop Rielflow workflow.
---

# Codex Source Security Check Loop

Use this skill when the user asks for a source-code security check with deterministic verification and fix follow-up.

## Workflow

- Package id: `codex-source-security-check-loop`
- Workflow id: `codex-source-security-check-loop`
- Dependency: `codex-design-and-implement-review-loop`

## Standard Run

Run from the repository root:

```bash
rielflow package install codex-source-security-check-loop
rielflow package install codex-design-and-implement-review-loop
rielflow workflow run codex-source-security-check-loop \
  --variables '{"workflowInput":{"targetPath":".","runNetworkAudits":"false","maxFindings":50,"constraints":["Do not stage, commit, or push unless the user explicitly asks.","Do not revert unrelated dirty worktree changes.","Keep fixes narrowly scoped to verified security findings."]}}' \
  --output json --verbose --no-auto-improve
```

For registry-backed one-off runs:

```bash
rielflow workflow run codex-source-security-check-loop \
  --from-registry \
  --registry default \
  --variables '{"workflowInput":{"targetPath":".","runNetworkAudits":"false","maxFindings":50}}' \
  --output json --verbose --no-auto-improve
```

Set `workflowInput.runNetworkAudits` to `"true"` only when dependency audit commands may use network access.

## What The Workflow Checks

The workflow runs separate deterministic vulnerability-check methods before agent triage:

- Secret scan: high-confidence secret patterns and private keys.
- Gitleaks scan: runs `gitleaks detect --no-git --redact` when the executable is available, otherwise records a missing-tool coverage gap.
- Static source/SAST scan: risky-code heuristics and optional local evidence.
- Dependency audit scan: manifests and optional npm, pnpm, yarn, Bun, Python, Ruby, Rust, and Go audit commands when network audits are allowed.
- Supply-chain/config scan: risky package scripts, build-chain indicators, Docker/container config, CI, and infrastructure-as-code heuristics.
- Agent triage: repository-specific exploitability review using the deterministic evidence.

The design borrows useful patterns from Claude Code and Codex security skills: scoped review modes, security-area checklists, automated checks, OWASP framing, and findings with severity, location, and remediation.

## Operating Rules

- Do not rely on agent judgment alone; use deterministic method output as routing evidence.
- Keep method outputs separate so a finding can be traced to secrets, gitleaks, static analysis, dependency audit, supply-chain/config, or agent triage.
- Delegate high and medium fixes through `codex-design-and-implement-review-loop`.
- Rerun all deterministic methods after fixes.
- Accept low findings only as documented residual risk.
- Preserve user constraints about dirty worktrees, staging, commits, and pushes.
