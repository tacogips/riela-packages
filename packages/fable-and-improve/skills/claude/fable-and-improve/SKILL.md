---
name: fable-and-improve
description: Use when a Claude Code session should let Claude Fable plan and manage the goal, delegate implementation/review/improvement to the Codex design-and-implement workflow, then have Fable verify completion and loop on remaining TODOs.
metadata:
  short-description: Fable plans, Codex implements, Fable verifies
---

# Fable And Improve

Use this skill when the user explicitly wants the `fable-and-improve` Riela
workflow or asks for a Fable-led plan with Codex implementation and review.

## Package

- Package id: `fable-and-improve`
- Workflow id: `fable-and-improve`
- Parent backend: `claude-code-agent`
- Parent model: `claude-fable-5`
- Child workflow: `codex-design-and-implement-review-loop`
- Required dependency package: `codex-design-and-implement-review-loop`

This package intentionally provides only a Claude skill. It does not project a
Codex or Cursor usage skill.

## Install

From a local `riela-packages` checkout:

```bash
riela package install fable-and-improve --source <riela-packages-checkout>/packages/fable-and-improve
```

User scope:

```bash
riela package install fable-and-improve --source <riela-packages-checkout>/packages/fable-and-improve --scope user
```

## Validate

Project scope:

```bash
riela workflow validate fable-and-improve
riela workflow inspect fable-and-improve --output json
```

User scope:

```bash
riela workflow validate fable-and-improve --scope user
riela workflow inspect fable-and-improve --scope user --output json
```

## Run

Use a concise `workflowInput`:

```bash
riela workflow run fable-and-improve \
  --variables '{"workflowInput":{"requestedOutcome":"Implement the requested change, review it, and verify completion.","targetScope":"Describe the target files or feature area.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

For a cheap connectivity check before using Fable, patch the parent Fable nodes
to a less expensive Claude Code model:

```bash
riela workflow run fable-and-improve \
  --node-patch '{"fable-goal-plan":{"model":"claude-sonnet-4-5"},"codex-implementation-handoff":{"model":"claude-sonnet-4-5"},"codex-implementation-result":{"model":"claude-sonnet-4-5"},"fable-goal-review":{"model":"claude-sonnet-4-5"},"final-output":{"model":"claude-sonnet-4-5"}}' \
  --variables '{"workflowInput":{"requestedOutcome":"Connectivity smoke test only.","targetScope":"No repository changes.","constraints":["Do not edit files."],"acceptanceCriteria":["The workflow starts and delegates correctly."],"verificationHint":"No-op smoke check."}}' \
  --output jsonl
```

Then run the normal workflow with Fable for a small real task.

## Output

Expect the final output to include:

- `status`
- `goalAchieved`
- `goalMarkdown`
- `planMarkdown`
- `delegatedWorkflowRuns`
- `changedFiles`
- `verificationEvidence`
- `reviewEvidence`
- `commitStatus`
- `pushStatus`
- `residualRisks`

## Maintainer Notes

After changing workflow files, prompts, mock scenarios, or this skill payload,
refresh digests:

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve
```
