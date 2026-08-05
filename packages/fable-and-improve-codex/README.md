# fable-and-improve-codex

Claude Fable analyzes the request, authors the design and implementation plan,
and verifies completion. Codex GPT-5.6 Terra implements the plan, and an
independent Codex GPT-5.6 SOL session reviews the result.

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
