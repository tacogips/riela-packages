---
name: fable-and-improve-codex
description: Run the fable-and-improve-codex Riela workflow when Claude Fable should analyze, design, and author the implementation plan, Codex Terra should implement, Codex SOL should independently review, and Fable should verify completion.
---

# Fable And Improve Codex

Run the installed workflow instead of manually emulating its orchestration.

## Responsibility split

- Fable `claude-fable-5`: analysis, design, implementation plan, replanning, final acceptance
- Codex `gpt-5.6-terra`: implementation, tests, verification, and improvements
- Codex `gpt-5.6-sol`: independent read-only implementation review

## Run

```bash
riela workflow validate fable-and-improve-codex
riela workflow inspect fable-and-improve-codex --output json
riela workflow run fable-and-improve-codex \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the target scope.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

Use `--scope user` for a user-scope install. Report the final artifacts,
changed files, verification, review evidence, residual risks, and
`goalAchieved` status.
