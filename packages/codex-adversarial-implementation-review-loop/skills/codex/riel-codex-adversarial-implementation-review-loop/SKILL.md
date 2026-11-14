---
name: riel-codex-adversarial-implementation-review-loop
description: Use when the user asks Codex to run a scoped implementation request with adversarial implementation review, fix blocking findings, and repeat until no high or medium findings remain.
---

# Riel Codex Adversarial Implementation Review Loop

Use this skill when the user wants an explicit implementation subject reviewed
adversarially while blocking fixes are delegated and re-reviewed.

This is distinct from `codex-recent-change-quality-loop`: scope is provided by
`reviewSubject`, `targetPaths`, changed files, implementation evidence, or an
implementation-plan path, not by a recent time window.

## Workflow

- Package id: `codex-adversarial-implementation-review-loop`
- Workflow id: `codex-adversarial-implementation-review-loop`
- Dependency: `codex-design-and-implement-review-loop`

## Standard Run

```bash
riela workflow run codex-adversarial-implementation-review-loop \
  --variables '{"workflowInput":{"reviewSubject":"Describe the implementation result to review.","targetPaths":["src"],"constraints":["Do not revert unrelated dirty worktree changes."]}}' \
  --output json --no-auto-improve
```

To review existing work without first dispatching implementation:

```bash
riela workflow run codex-adversarial-implementation-review-loop \
  --variables '{"workflowInput":{"skipInitialImplementation":true,"reviewSubject":"Review the completed implementation for the described feature.","targetPaths":["src"],"changedFiles":[]}}' \
  --output json --no-auto-improve
```

## Expected Output

The final output reports the accepted review subject, target paths, delegated
workflow runs, final findings, changed files, verification, and residual risks.

## Verification

```bash
task check
```

Refresh package digests after workflow or skill changes:

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts codex-adversarial-implementation-review-loop
```
