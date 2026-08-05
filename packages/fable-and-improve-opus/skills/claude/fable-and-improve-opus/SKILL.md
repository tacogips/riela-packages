---
name: fable-and-improve-opus
description: Use when Claude Code should run a Riela workflow in which Claude Fable researches and plans the goal, Claude Opus 5 implements and independently reviews the work, and Fable verifies completion and loops on remaining work.
metadata:
  short-description: Fable plans, Opus 5 develops, Fable verifies
---

# Fable And Improve Opus

Use this skill when the user explicitly requests `fable-and-improve-opus` or
wants Fable-led planning and acceptance with Opus 5 implementation and review.
Run the installed workflow instead of emulating its orchestration manually.

## Package

- Package id: `fable-and-improve-opus`
- Workflow id: `fable-and-improve-opus`
- Backend: `claude-code-agent`
- Planning and acceptance model: `claude-fable-5`
- Implementation and independent review model: `claude-opus-5`
- Required variables: `workflowInput.requestedOutcome`; optional `targetScope`, `constraints`, `acceptanceCriteria`, and `verificationHint`
- Project-scope skill: `.claude/skills/fable-and-improve-opus/SKILL.md`
- User-scope skill: `~/.claude/skills/fable-and-improve-opus/SKILL.md`

## Install

Project scope:

```bash
riela package install fable-and-improve-opus \
  --source <riela-packages-checkout>/packages/fable-and-improve-opus
```

User scope:

```bash
riela package install fable-and-improve-opus \
  --source <riela-packages-checkout>/packages/fable-and-improve-opus \
  --scope user
```

## Validate

Project scope:

```bash
riela workflow validate fable-and-improve-opus
riela workflow inspect fable-and-improve-opus --output json
```

User scope:

```bash
riela workflow validate fable-and-improve-opus --scope user
riela workflow inspect fable-and-improve-opus --scope user --output json
```

Confirm that Fable nodes resolve to `claude-fable-5` and the implementation and
review nodes resolve to the frozen `claude-opus-5` model.

## Run

```bash
riela workflow run fable-and-improve-opus \
  --scope user \
  --variables '{"workflowInput":{"requestedOutcome":"Implement the requested change and verify completion.","targetScope":"Describe the target files or feature area.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

Preserve the user's actual constraints and acceptance criteria. Monitor JSONL
until completion, and use Riela session status/progress/resume commands if the
workflow pauses or fails.

## Output

Expect:

- `status`
- `goalAchieved`
- `goalMarkdown`
- `planMarkdown`
- `changedFiles`
- `implementationEvidence`
- `reviewEvidence`
- `verificationEvidence`
- `commitStatus`
- `pushStatus`
- `residualRisks`
- `operatorNotes`

Report the session id, final status, changed files, verification and review
evidence, and residual risks. Do not claim completion unless `goalAchieved` is
true and the evidence supports it.

## Maintainer Notes

After changing any packaged payload, refresh digests and validate the registry:

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve-opus
task check
```
