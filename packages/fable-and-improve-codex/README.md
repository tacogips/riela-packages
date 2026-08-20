# fable-and-improve-codex

Claude Fable analyzes the request, authors the design and implementation plan,
and verifies completion. Codex GPT-5.6 Terra implements the plan, and an
independent Codex GPT-5.6 SOL session reviews the result.

The workflow also maintains a durable, cross-workflow knowledge base on kaiba
long-term memory. Analysis names a `knowledgeQuery` keyword and prior
knowledge is recalled (`kaiba/memory-recall`) into the design step; the
applicable items are carried into the design and plan artifacts so Terra and
SOL see them. After Fable accepts the goal, a self-review step extracts at
most one durable lesson from the run, recalls related notes, and a merge
judge decides to `create` a new note, `merge` it into an existing note by
rewriting it (compaction, no append growth), or `skip` it (the default when
uncertain, so the base does not overfit to single runs). All runs sharing the
same kaiba note root share the knowledge base; set the `noteRoot` runtime
variable to select a different base.

- Package id: `fable-and-improve-codex`
- Backends: `claude-code-agent`, `codex-agent`
- Models: `claude-fable-5`, `gpt-5.6-terra`, `gpt-5.6-sol`
- Workflow: `fable-and-improve-codex`
- Skills: Claude Code, Codex

## Install

```bash
riela package install fable-and-improve-codex \
  --source <riela-packages-checkout>/packages/fable-and-improve-codex
```

Add `--scope user` for a user-scope install.

## Run

```bash
riela workflow validate fable-and-improve-codex
riela workflow run fable-and-improve-codex \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the feature area.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```
