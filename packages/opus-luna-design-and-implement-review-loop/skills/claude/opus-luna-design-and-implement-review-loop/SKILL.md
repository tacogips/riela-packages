---
name: opus-luna-design-and-implement-review-loop
description: Run the opus-luna-design-and-implement-review-loop Riela workflow when Claude Opus 5.5 should design, write detailed implementation plans, review, and do the final integration review, while Codex GPT-6 Luna implements every plan in maximum-parallel fanout and read-only Opus reviews return detailed correction instructions to the owning Luna implementer.
---

# Opus Luna Design And Implement Review Loop

Run the installed workflow instead of manually emulating its orchestration.

## Responsibility split

- Opus `claude-opus-5-5`: intake, design, implementation plans, design and
  plan review, test-integrity and adversarial review, reconciliation,
  integration review, documentation, completion and Git handoff
- Codex `gpt-6-luna` (high effort, fast tier): implementation of each plan in
  its own native fanout branch; all dependency-ready plans run at once
Reviewers do not edit or delegate repairs. Design/plan findings return to the
Opus author; implementation findings return immediately to the original Luna
step, then pass both independent reviews again. Integration findings selectively
redispatch the owning Luna plans. Detailed repairRequests and feedback must
include location, intent, reproduction, root cause, authorized scope, ordered
changes, exact verification and completion criteria. Blocked-only waves terminate
without accepted Git finalization.

## GPT-6 Luna fanout

The `implementation-wave-outcome` command stores `fanout-join.json` and `wave-summary.json` under `tmp/opus-luna-waves/<workflowExecutionId>/wave-NNN/`; the summary plus verdict is bounded to 64 KiB. Reconciliation and integration review locate the highest wave and require verdict equality before using the summary. Inspect `wave-summary.json` when reporting a wave; mock scenarios do not execute the command. Riela 0.2.34 still renders the persistent `fanoutJoin` request variable into later agent prompts; this is the open Q1 limitation.

## Run

```bash
riela workflow validate opus-luna-design-and-implement-review-loop
riela workflow inspect opus-luna-design-and-implement-review-loop --output json
riela workflow run opus-luna-design-and-implement-review-loop \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the target scope.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

To keep every commit local, add `"gitPush":false` to `workflowInput`. The run
still commits the plan checkpoint and the final change, but skips `riela/git-push`
and base-branch integration, accepts unpushed base-branch commits, and reports
`mergeStatus: local-only`. Push or open a PR yourself afterwards.

Use `--max-concurrency <n>` only when the host cannot sustain every ready Luna
branch at once. Use `--scope user` for a user-scope install. Report the final
artifacts, changed files, verification, review evidence and per-finding Luna correction evidence, residual risks, and the final Git or PR handoff status.

## Maintainer notes

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-luna-design-and-implement-review-loop
mise run check
```
