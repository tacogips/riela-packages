# fable-and-improve-codex

Claude Fable analyzes the request, authors the design and implementation plan,
and verifies completion. Codex GPT-5.6 SOL low effort implements the plan, and
an independent Codex GPT-5.6 SOL medium-effort session reviews the result.

The workflow also maintains a durable, cross-workflow knowledge base on kaiba
long-term memory. Analysis names a `knowledgeQuery` keyword and prior
knowledge is recalled (`kaiba/memory-recall`) into the design step; the
applicable items are carried into the design and plan artifacts so the SOL
implementer and independent reviewer see them. After Fable accepts the goal, a self-review step extracts at
most one durable lesson from the run, recalls related notes, and a merge
judge decides to `create` a new note, `merge` it into an existing note by
rewriting it (compaction, no append growth), or `skip` it (the default when
uncertain, so the base does not overfit to single runs). When several
existing notes overlap a merged topic, the judge also tidies the base: the
redundant note is collapsed to a one-line superseded pointer (`kb-archive`),
so the base absorbs lessons while shrinking. All runs sharing the
same kaiba note root share the knowledge base; set the `noteRoot` runtime
variable to select a different base.

- Package id: `fable-and-improve-codex`
- Backends: `claude-code-agent`, `codex-agent`
- Models: `claude-fable-5`, `gpt-5.6-sol`
- Workflow: `fable-and-improve-codex`
- Skills: Claude Code

## Install

```bash
riela package install fable-and-improve-codex \
  --source <riela-packages-checkout>/packages/fable-and-improve-codex
```

The compact graph has 14 steps: design and implementation planning share one Fable execution, with both artifacts and their consistency evidence retained. Independent implementation review, goal acceptance, and knowledge-base operations remain separate.

Codex review feedback is limited to concrete security, functionality, data-integrity, regression, acceptance, lost-work, or severe code-quality risks. Speculative optimization, optional abstraction, and other overengineering are excluded.

Add `--scope user` for a user-scope install.

## Run

```bash
riela workflow validate fable-and-improve-codex
riela workflow run fable-and-improve-codex \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the feature area.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

## Shared-branch implementation

Design and all implementation plans are authored by a single author node per phase. Accepted designs/plans are committed before implementation. Native Riela fanout runs dependency-ready implementation/review branches in the same working directory and Git branch (default concurrency 4; --max-concurrency can lower it). No worktrees are created.

The runtime calls each parallel execution a **fanout branch**, its input an **item**, and the aggregation a **join**. This is separate from a Git branch. Built-in fanout.dependencies selects ready branches from stable IDs and accepted dependencies. Built-in fanout.changeTracking captures immutable file content, hashes and modes at node boundaries, and reports drift candidates at join. No workflow-local evidence script is needed.

After all branches stop, serial reconciliation repairs missing/overwritten behavior and independent integration review checks the combined tree against every plan and the design. Failed branches stay pending; already accepted branch IDs are skipped on subsequent dispatch. Preserve original evidence and existing user changes. Node-boundary snapshots cannot detect every transient overwrite inside an agent call, so per-edit intention records and behavior tests remain required.

Git operations are serialized: planning checkpoint, final implementation commit/push, and base-branch integration. workflowInput.baseBranch defaults to the current branch; an explicit different base is merged only after combined verification. No force push or automatic discard of unrelated edits. A blocked merge/push prevents completion.

Requires a Riela build with fanout.dependencies, fanout.changeTracking and shared-branch finalization evidence support. The explicit shared-workspace ownership mode makes older runners reject the new bundle instead of silently ignoring its dependency/tracking fields. Use the paired Riela source changes before installing this update.
