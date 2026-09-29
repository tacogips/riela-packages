# fable-and-improve-opus

Claude Fable analyzes the request, authors the design and implementation plans,
reviews the reconciled integration, and verifies completion. Independent Claude
Opus 5.5 sessions review the design and plans, implement dependency-ready work,
check test integrity, run adversarial implementation review, and repair retained
shared-tree behavior.

The workflow also maintains a durable, cross-workflow knowledge base on kaiba
long-term memory. Analysis names a `knowledgeQuery` keyword and prior
knowledge is recalled (`kaiba/memory-recall`) into the design step; the
applicable items are carried into the design and plan artifacts so the
implementation and review sessions see them. After Fable accepts the goal, a
self-review step extracts at most one durable lesson from the run, recalls
related notes, and a merge judge decides to `create` a new note, `merge` it
into an existing note by rewriting it (compaction, no append growth), or
`skip` it (the default when uncertain, so the base does not overfit to single
runs). When several existing notes overlap a merged topic, the judge also
tidies the base: the redundant note is collapsed to a one-line superseded
pointer (`kb-archive`), so the base absorbs lessons while shrinking. All runs
sharing the same kaiba note root share the knowledge base;
set the `noteRoot` runtime variable to select a different base.

- Package id: `fable-and-improve-opus`
- Backend: `claude-code-agent`
- Models: `claude-fable-5`, `claude-opus-5-5`
- Workflow: `fable-and-improve-opus`
- Skill: Claude Code

## Install

```bash
riela package install fable-and-improve-opus \
  --source <riela-packages-checkout>/packages/fable-and-improve-opus \
  --scope user
```

The graph has 32 steps. Design and implementation planning share one Fable
author session, while separate Opus design-review and implementation-plan-review
gates must accept before checkpointing. Each implementation branch then passes
the same bounded progress, test-integrity, and adversarial-review sequence as
the Codex design-and-implement workflow. Blocked-only waves terminate with an
actionable handoff; partial-success waves preserve successful evidence and
redispatch only pending plans. Fable integration review distinguishes
repair-in-place from redispatch, and final goal review precedes advisory E2E,
documentation, completion, commit, push, base integration, and knowledge-base
self-review.

## Run

```bash
riela workflow validate fable-and-improve-opus --scope user
riela workflow run fable-and-improve-opus \
  --scope user \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the feature area.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

## Shared-branch implementation

Design and all implementation plans are authored by a single author node per phase. Accepted designs/plans are committed before implementation. Native Riela fanout runs dependency-ready implementation/review branches in the same working directory and Git branch (default concurrency 4; --max-concurrency can lower it). No worktrees are created.

The runtime calls each parallel execution a **fanout branch**, its input an **item**, and the aggregation a **join**. This is separate from a Git branch. Built-in fanout.dependencies selects ready branches from stable IDs and accepted dependencies. Built-in fanout.changeTracking captures immutable file content, hashes and modes at node boundaries, and reports drift candidates at join. No workflow-local evidence script is needed.

After all branches stop, a wave-outcome gate separates blocked-only waves from
partial success. Serial reconciliation repairs missing/overwritten behavior and
Fable integration review checks the combined tree against every plan and the
design. Review findings route either to in-place reconciliation or selective
redispatch. Failed branches stay pending; already accepted branch IDs are
skipped on subsequent dispatch. Preserve original evidence and existing user
changes. Node-boundary snapshots cannot detect every transient overwrite inside
an agent call, so per-edit intention records and behavior tests remain required.

Agents that read or write the workspace declare an explicit sandbox. Required producer outputs have JSON schemas and validation budgets, so malformed checkpoint or accepted completion messages are rejected before Git steps. A revision completion can omit commit fields; an accepted completion requires a nonempty commit message. Knowledge create, merge, archive and skip routes retain their conditional fields and existing routing. The deterministic ten-case contract suite is documented in `workflows/fable-and-improve-opus/EXPECTED_RESULTS.md` and runs with `bun tests/check-output-contract.ts --evidence-root <absolute-path>` from this package directory.

Git operations are serialized: planning checkpoint, final implementation commit/push, and base-branch integration. workflowInput.baseBranch defaults to the current branch; an explicit different base is merged only after combined verification. No force push or automatic discard of unrelated edits. A blocked merge/push prevents completion.

Requires a Riela build with fanout.dependencies, fanout.changeTracking and shared-branch finalization evidence support. The explicit shared-workspace ownership mode makes older runners reject the new bundle instead of silently ignoring its dependency/tracking fields. Use the paired Riela source changes before installing this update.
