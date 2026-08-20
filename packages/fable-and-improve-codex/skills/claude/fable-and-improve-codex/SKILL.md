---
name: fable-and-improve-codex
description: Run the fable-and-improve-codex Riela workflow when Claude Fable should analyze, design, and author the implementation plan, Codex Terra should implement, Codex SOL should independently review, and Fable should verify completion.
---

# Fable And Improve Codex

Run the installed workflow instead of manually emulating its orchestration.

## Responsibility split

- Fable `claude-fable-5`: analysis, design, implementation plan, replanning, final acceptance, knowledge-base self-review
- Codex `gpt-5.6-terra`: implementation, tests, verification, and improvements
- Codex `gpt-5.6-sol`: independent read-only implementation review

## Knowledge base

The workflow reads and maintains a durable knowledge base on kaiba long-term
memory. Before design, it recalls prior knowledge for the analysis topic and
carries the applicable items into the design and plan artifacts. After Fable
accepts the goal, it self-reviews the run and creates, merges (rewrites an
existing note instead of appending), or skips at most one durable lesson.
The base is shared across every workflow using the same kaiba note root; pass
a `noteRoot` runtime variable (top-level, next to `workflowInput`) to target a
different knowledge base, and keep it stable across runs so knowledge
accumulates.

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
