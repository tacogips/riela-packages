# fable-and-improve-opus

Claude Code Fable researches the request and maintains the goal and plan.
Claude Opus 5 implements the plan, a separate Opus 5 session reviews the
result, and Fable verifies completion and routes any remaining work.

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
