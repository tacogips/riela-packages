---
name: fable-and-improve
description: Use when a Codex session should run the fable-and-improve Riela workflow so Claude Fable researches and plans the goal, delegates implementation, review, and improvement to the Codex design-and-implement workflow, then verifies completion and loops on remaining TODOs.
---

# Fable And Improve

Run the `fable-and-improve` Riela workflow when the user explicitly requests
it or asks for Fable-led planning and verification with Codex implementation
and review. Do not emulate the orchestration manually when the installed
workflow is available.

## Package

- Package id: `fable-and-improve`
- Workflow id: `fable-and-improve`
- Parent backend: `claude-code-agent`
- Parent model: `claude-fable-5`
- Child workflow: `codex-design-and-implement-review-loop`
- Required dependency package: `codex-design-and-implement-review-loop`

The workflow starts from Codex, but its parent planning and verification nodes
run on Claude Fable. Its delegated implementation and review run through the
Codex child workflow.

## Install

Install both packages from a local `riela-packages` checkout:

```bash
riela package install codex-design-and-implement-review-loop --source <riela-packages-checkout>/packages/codex-design-and-implement-review-loop
riela package install fable-and-improve --source <riela-packages-checkout>/packages/fable-and-improve
```

For user scope, add `--scope user` to both commands.

## Validate

Project scope:

```bash
riela workflow validate fable-and-improve
riela workflow inspect fable-and-improve --output json
```

User scope:

```bash
riela workflow validate fable-and-improve --scope user
riela workflow inspect fable-and-improve --scope user --output json
```

Confirm that inspection resolves the Fable parent nodes and the
`codex-design-and-implement-review-loop` child workflow before starting a
non-trivial run.

## Run

Encode the user's request as a concise `workflowInput`:

```bash
riela workflow run fable-and-improve \
  --variables '{"workflowInput":{"requestedOutcome":"Implement the requested change, review it, and verify completion.","targetScope":"Describe the target files or feature area.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

Use `--scope user` when the packages were installed in user scope. Preserve the
user's acceptance criteria and constraints rather than replacing them with the
generic example. Monitor the JSONL session until it finishes; if it pauses or
fails, inspect and resume it with the Riela workflow-run and troubleshooting
commands available in the environment.

For a cheap connectivity check before using Fable, patch the parent Fable nodes
to a less expensive Claude Code model:

```bash
riela workflow run fable-and-improve \
  --node-patch '{"fable-goal-plan":{"model":"claude-sonnet-4-5"},"codex-implementation-handoff":{"model":"claude-sonnet-4-5"},"codex-implementation-result":{"model":"claude-sonnet-4-5"},"fable-goal-review":{"model":"claude-sonnet-4-5"},"final-output":{"model":"claude-sonnet-4-5"}}' \
  --variables '{"workflowInput":{"requestedOutcome":"Connectivity smoke test only.","targetScope":"No repository changes.","constraints":["Do not edit files."],"acceptanceCriteria":["The workflow starts and delegates correctly."],"verificationHint":"No-op smoke check."}}' \
  --output jsonl
```

Use the model patch only for a smoke test. Run the normal workflow with Fable
for the actual task.

## Output

Verify that the final output includes:

- `status`
- `goalAchieved`
- `goalMarkdown`
- `planMarkdown`
- `delegatedWorkflowRuns`
- `changedFiles`
- `verificationEvidence`
- `reviewEvidence`
- `commitStatus`
- `pushStatus`
- `residualRisks`

Report the session id, final status, changed files, verification and review
evidence, and any residual risks. Do not claim completion unless
`goalAchieved` is true and the evidence supports it.

## Maintainer Notes

After changing workflow files, prompts, mock scenarios, or either packaged
skill payload, refresh digests and validate the registry:

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve
task check
```
