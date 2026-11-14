---
name: fable-and-improve-opus
description: Run the fable-and-improve-opus Riela workflow when Fable should author design/plans and own integration and goal acceptance, while Opus 5.5 independently reviews planning, implements, and runs test-integrity and adversarial review gates.
---

# Fable And Improve Opus

Run the installed workflow instead of manually emulating its orchestration.

## Responsibility split

- Fable `claude-fable-5`: analysis, design/plan authoring and revision,
  integration review, goal acceptance, knowledge-base self-review, final output
- Opus `claude-opus-5-5`: independent design and plan review, implementation,
  tests, bounded continuation, reconciliation, documentation and Git finalization
- Independent Opus `claude-opus-5-5`: read-only test-integrity and adversarial
  implementation review

Design or plan findings loop back to the Fable author. Test-integrity and
adversarial findings loop back to the owning Opus implementation session.
Fable integration findings distinguish serial repair from selective redispatch.
Blocked-only waves terminate without accepted Git finalization; productive
partial success continues with successful plan IDs preserved.

## Knowledge base

The workflow reads and maintains a durable knowledge base on kaiba long-term
memory. Before design, it recalls prior knowledge for the analysis topic and
carries the applicable items into the design and plan artifacts. After Fable
accepts the goal, it self-reviews the run and creates, merges (rewrites an
existing note instead of appending), or skips at most one durable lesson.
When several existing notes overlap a merged topic, it also tidies the base
by collapsing the redundant note to a one-line superseded pointer.
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

Design and implementation planning run together in `fable-design`, followed by
independent `step3-design-review` and `step5-impl-plan-review` gates. Each
fanout branch runs `step6-implement`, deterministic
`implementation-progress-check`, `step6-test-integrity-check`, and
`step7-adversarial-review` before immutable branch evidence. Integration and
goal review, E2E evidence, documentation, completion and Git gates all remain
mandatory before accepted final output.

Use `--scope user` for a user-scope install. Report the final artifacts,
changed files, verification, independent review evidence, residual risks, and
`goalAchieved` status.

## Maintainer notes

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve-opus
task check
```
