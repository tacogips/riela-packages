---
name: riel-codex-impl-plan-completion-review-loop
description: Use when the user wants Codex to complete active implementation plans and then run a separate review-and-improve pass. Runs codex-impl-plan-completion-review-loop, which first delegates to codex-impl-plan-completion-loop and then to codex-recent-change-quality-loop.
---

# Riel Codex Impl Plan Completion Review Loop

Use this skill when the user asks to finish implementation work from
`impl-plans/active` and then run review/improve after that implementation work
is complete.

This skill is intentionally distinct from:

- `riel-codex-impl-workflow`, which runs `codex-design-and-implement-review-loop`
  for one issue or plan-driven implementation request.
- `codex-impl-plan-completion-loop`, which completes active implementation
  plans but does not run the separate recent-change review workflow afterward.
- `codex-recent-change-quality-loop`, which reviews recent changes but does not
  first complete active implementation plans.

## Workflow Bundle

- Workflow id: `codex-impl-plan-completion-review-loop`
- Package id: `codex-impl-plan-completion-review-loop`
- Backend: `codex-agent`
- Model: `gpt-5.5`
- Sequence:
  1. `codex-impl-plan-completion-loop`
  2. `codex-recent-change-quality-loop`

## Standard Run

Run from the repository root after checkout or installation:

```bash
rielflow workflow run codex-impl-plan-completion-review-loop \
  --variables '{"workflowInput":{"hours":24,"constraints":["Do not revert unrelated dirty worktree changes."]}}' \
  --output json --no-auto-improve
```

To constrain implementation to one active plan:

```bash
rielflow workflow run codex-impl-plan-completion-review-loop \
  --variables '{"workflowInput":{"planPath":"impl-plans/active/example.md","hours":24,"targetPaths":["impl-plans/active/example.md"],"constraints":["Do not revert unrelated dirty worktree changes."]}}' \
  --output json --no-auto-improve
```

For a source checkout without an installed `rielflow` binary, use the equivalent
checkout command:

```bash
bun run packages/rielflow/src/bin.ts workflow run codex-impl-plan-completion-review-loop \
  --variables '{"workflowInput":{"hours":24}}' \
  --output json --no-auto-improve
```

## Inputs

- `workflowInput.planPath`: optional active implementation plan path.
- `workflowInput.maxIterations`: optional operator loop budget for plan
  completion.
- `workflowInput.hours`: optional recent-change review window. Defaults to 24.
- `workflowInput.targetPaths`: optional paths to prioritize during review.
- `workflowInput.constraints`: optional constraints preserved into child
  workflow handoffs.

## Expected Output

The final output reports:

- whether implementation-plan completion finished
- whether recent-change review returned accepted
- child workflow ids and statuses
- completed plans and remaining active plans
- reviewed range, final findings, fix iterations, verification, changed files,
  residual risks, and operator notes

## Verification

Validate package metadata and all packaged workflows from the registry checkout:

```bash
task check
```

Refresh `rielflow-package.json` digests after changing the workflow or packaged
skill:

```bash
bun .agents/skills/rielflow-package-release/scripts/update-package-digests.ts codex-impl-plan-completion-review-loop
```
