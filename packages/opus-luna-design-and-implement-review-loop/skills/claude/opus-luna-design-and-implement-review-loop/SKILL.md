---
name: opus-luna-design-and-implement-review-loop
description: Run the opus-luna-design-and-implement-review-loop Riela workflow when Claude Opus 5.5 should design, write detailed implementation plans, review, and do the final integration review, while Codex GPT-6 Luna implements every plan in maximum-parallel fanout and Opus reviewers repair findings through Sonnet subagents.
---

# Opus Luna Design And Implement Review Loop

Run the installed workflow instead of manually emulating its orchestration.

## Responsibility split

- Opus `claude-opus-5-5`: intake, design, implementation plans, design and
  plan review, test-integrity and adversarial review, reconciliation,
  integration review, documentation, completion and Git handoff
- Codex `gpt-6-luna` (high effort, fast tier): implementation of each plan in
  its own native fanout branch; all dependency-ready plans run at once
- Sonnet subagents (`model: "sonnet"`): launched by the Opus reviewers to repair
  high/mid findings, after which the reviewer re-reviews and reruns verification

Findings that survive two repair rounds or need out-of-scope changes route back
to the Opus author (design/plan) or to GPT-6 Luna (implementation). Integration
findings distinguish serial repair from selective redispatch. Blocked-only waves
terminate without accepted Git finalization.

## Run

```bash
riela workflow validate opus-luna-design-and-implement-review-loop
riela workflow inspect opus-luna-design-and-implement-review-loop --output json
riela workflow run opus-luna-design-and-implement-review-loop \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the target scope.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

Use `--max-concurrency <n>` only when the host cannot sustain every ready Luna
branch at once. Use `--scope user` for a user-scope install. Report the final
artifacts, changed files, verification, review evidence including
`selfRepairs`, residual risks, and the final Git or PR handoff status.

## Maintainer notes

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-luna-design-and-implement-review-loop
mise run check
```
