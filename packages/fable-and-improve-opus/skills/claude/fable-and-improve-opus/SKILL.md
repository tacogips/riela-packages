---
name: fable-and-improve-opus
description: Run the fable-and-improve-opus Riela workflow when Claude Fable should analyze, design, and author the implementation plan, Claude Opus 5 should implement and independently review, and Fable should verify completion.
---

# Fable And Improve Opus

Run the installed workflow instead of manually emulating its orchestration.

## Responsibility split

- Fable `claude-fable-5`: analysis, design, implementation plan, replanning, final acceptance, knowledge-base self-review
- Opus `claude-opus-5`: implementation, tests, verification, and improvements
- Independent Opus `claude-opus-5`: read-only implementation review

Review findings loop back to the implementation session. Fable sends invalid
analysis, design, or plans back through its authoring sequence and sends
valid-plan TODOs directly to implementation.

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
riela workflow validate fable-and-improve-opus
riela workflow inspect fable-and-improve-opus --output json
riela workflow run fable-and-improve-opus \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the target scope.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

Use `--scope user` for a user-scope install. Report the final artifacts,
changed files, verification, independent review evidence, residual risks, and
`goalAchieved` status.

## Maintainer notes

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve-opus
task check
```
