---
name: fable-and-improve-codex
description: Run the fable-and-improve-codex Riela workflow when Fable should analyze, design, and author the implementation plan, Codex Terra should implement, Codex SOL should independently review, and Fable should verify completion.
---

# Fable And Improve Codex

Run the installed `fable-and-improve-codex` workflow instead of emulating its
orchestration manually.

## Responsibility split

- Fable `claude-fable-5`: analysis, design, implementation plan, replanning, final acceptance
- Codex `gpt-5.6-terra`: implementation, tests, verification, and improvements
- Codex `gpt-5.6-sol`: independent read-only implementation review

The workflow loops SOL findings back to Terra. Fable sends invalid analysis,
design, or plans back through its own authoring sequence and sends valid-plan
TODOs directly to Terra.

## Run

```bash
riela workflow validate fable-and-improve-codex
riela workflow inspect fable-and-improve-codex --output json
riela workflow run fable-and-improve-codex \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the target scope.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

Add `--scope user` for a user-scope install. Preserve the operator's actual
constraints and acceptance criteria. Report artifacts, changed files,
verification, review evidence, residual risks, and `goalAchieved`.

## Maintainer notes

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve-codex
task check
```
