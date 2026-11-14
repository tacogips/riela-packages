---
name: riel-claude-code-goal
description: Use when running a generic Claude Code Opus 4.8 workflow that creates and reviews a goal, creates and reviews an in-session plan without plan files, performs the work, and reviews whether the goal is achieved before looping back to work or planning.
---

# Riel Claude Code Goal

Use this skill when the user asks for a generic Claude Code workflow that
should define the goal, review and improve it, plan internally, review and
improve the plan, do the work, and review completion before finishing.

## Workflow Bundle

- Workflow id: `claude-code-goal`
- Package id: `claude-code-goal`
- Backend: `claude-code-agent`
- Model: `claude-opus-4-8`
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
- Workflow discovery rule: every goal, review, planning, and work step should
  actively inspect available project/user workflows, installed packages,
  package metadata, relevant skills, or workflow usage/inspect output when the
  runtime permits it, then record the discovery evidence and delegation decision

## Standard Run

Run from the repository root after checkout or installation:

```bash
riela workflow run claude-code-goal \
  --variables '{"workflowInput":{"requestedOutcome":"Describe the desired outcome.","targetScope":"path or project scope","constraints":["Do not create plan files."],"acceptanceCriteria":["The goal review reports the goal achieved."]}}' \
  --output json --no-auto-improve
```

## Verification

Validate the package workflow after edits:

```bash
riela workflow validate claude-code-goal \
  --workflow-definition-dir ./packages/claude-code-goal/workflows
```

Refresh digests after changing the workflow or packaged skill:

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts claude-code-goal
```
