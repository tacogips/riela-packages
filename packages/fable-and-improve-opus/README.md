# fable-and-improve-opus

Claude Fable analyzes the request, authors the design and implementation plan,
and verifies completion. Claude Opus 5 implements the plan, and a separate
Opus 5 session independently reviews the result.

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
