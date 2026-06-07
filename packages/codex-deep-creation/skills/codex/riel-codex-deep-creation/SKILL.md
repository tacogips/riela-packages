---
name: riel-codex-deep-creation
description: Use when the user asks Codex for deep creation: deep design, adversarial implementation-plan completion, and source security checks in one Rielflow workflow.
---

# Riel Codex Deep Creation

Use this skill when the user asks for `deep creation`, `rielflow deep creation`,
`deep-impl-plan-completion` followed by security checks, or a full creation flow
that must run deep design, adversarial implementation, and security checking.

## Workflow

- Package id: `codex-deep-creation`
- Workflow id: `codex-deep-creation`
- Sequence:
  1. `codex-deepdesign`
  2. `codex-impl-plan-completion-loop` as the deep implementation-plan
     completion phase
  3. `codex-source-security-check-loop`

`codex-impl-plan-completion-loop` delegates active implementation plans through
`codex-adversarial-implementation-review-loop`, so the implementation phase is
not the recent-change review loop.

## Standard Run

```bash
rielflow workflow run codex-deep-creation \
  --variables '{"workflowInput":{"feature":"Describe the feature to create.","targetDesignDoc":"design-docs/specs/example.md","targetPaths":["src"],"securityTargetPath":"src","constraints":["Do not revert unrelated dirty worktree changes."]}}' \
  --output json --no-auto-improve
```

## Expected Output

The final output reports accepted design docs, completed implementation plans,
security status, child workflow runs, changed files, verification, and residual
risks.

## Verification

```bash
task check
```

Refresh package digests after workflow or skill changes:

```bash
bun .agents/skills/rielflow-package-release/scripts/update-package-digests.ts codex-deep-creation
```
