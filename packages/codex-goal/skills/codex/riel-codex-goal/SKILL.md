---
name: riel-codex-goal
description: Use when running a generic Codex GPT-5.5 workflow that first creates a goal, then creates an in-session plan without plan files, performs the work, and reviews whether the goal is achieved before looping back to work or planning.
---

# Riel Codex Goal

Use this skill when the user asks for a generic Codex workflow that should
define the goal, plan internally, do the work, and review completion before
finishing.

## Workflow Bundle

- Workflow id: `codex-goal`
- Package id: `codex-goal`
- Backend: `codex-agent`
- Model: `gpt-5.5`
- Effort: `high`
- Goal review rule: after `goal`, `goal-quality-review` routes back to `goal`
  until the goal is clear, testable, scoped, and has workflow routing guidance
  when a specialized Riela workflow is a better fit
- Plan review rule: after `plan`, `plan-quality-review` routes back to `plan`
  until the plan is actionable, scoped, verifiable, avoids plan files, and has
  workflow dispatch guidance when a specialized Riela workflow is a better
  fit
- Completion loop rule: `goal-review` routes back to `plan` when replanning is
  required, routes back to `work` when implementation is incomplete, and
  finishes only when both flags are false
- Plan persistence: the plan is held only in workflow session/output data; the
  workflow must not create plan files
- Delegation rule: goal, planning, work, and review steps may call or recommend
  a more specific Riela workflow when that workflow is a better fit than the
  generic loop
- Workflow discovery rule: every goal, review, planning, and work step should
  actively inspect available project/user workflows, installed packages,
  package metadata, relevant skills, or workflow usage/inspect output when the
  runtime permits it, then record the discovery evidence and delegation decision

## Standard Run

Run from the repository root after checkout or installation:

```bash
riela workflow run codex-goal \
  --variables '{"workflowInput":{"requestedOutcome":"Describe the desired outcome.","targetScope":"path or project scope","constraints":["Do not create plan files."],"acceptanceCriteria":["The goal review reports the goal achieved."]}}' \
  --output json --no-auto-improve
```

Adjust `requestedOutcome`, `targetScope`, `constraints`, `acceptanceCriteria`,
and `verificationHint` to the user's request.

## Scope

Prefer this workflow for broad generic work where no more specialized workflow
is a better fit and the user wants an explicit goal, internal plan, execution,
and goal-completion review loop.

Use a dedicated workflow instead when the task clearly needs deep design,
implementation-plan files, source security checks, task watchdog dispatch,
website generation, or refactoring decomposition.

The worker should not create commits or pushes unless the user explicitly asks
for them.

## Verification

Validate the package workflow after edits:

```bash
riela workflow validate codex-goal \
  --workflow-definition-dir ./packages/codex-goal/workflows
```

Refresh `riela-package.json` digests after changing the workflow or packaged
skill:

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts codex-goal
```
