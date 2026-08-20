# fable-and-improve-opus

Claude Fable analyzes the request, authors the design and implementation plan,
and verifies completion. Claude Opus 5 implements the plan, and a separate
Opus 5 session independently reviews the result.

The workflow also maintains a durable, cross-workflow knowledge base on kaiba
long-term memory. Analysis names a `knowledgeQuery` keyword and prior
knowledge is recalled (`kaiba/memory-recall`) into the design step; the
applicable items are carried into the design and plan artifacts so the
implementation and review sessions see them. After Fable accepts the goal, a
self-review step extracts at most one durable lesson from the run, recalls
related notes, and a merge judge decides to `create` a new note, `merge` it
into an existing note by rewriting it (compaction, no append growth), or
`skip` it (the default when uncertain, so the base does not overfit to single
runs). All runs sharing the same kaiba note root share the knowledge base;
set the `noteRoot` runtime variable to select a different base.

- Package id: `fable-and-improve-opus`
- Backend: `claude-code-agent`
- Models: `claude-fable-5`, `claude-opus-5`
- Workflow: `fable-and-improve-opus`
- Skill: Claude Code

## Install

```bash
riela package install fable-and-improve-opus \
  --source <riela-packages-checkout>/packages/fable-and-improve-opus \
  --scope user
```

## Run

```bash
riela workflow validate fable-and-improve-opus --scope user
riela workflow run fable-and-improve-opus \
  --scope user \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the feature area.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```
