---
name: riel-codex-simple-work-package
description: Use when making small code or documentation changes under a directory and no more specialized rielflow workflow applies. Runs the packaged codex-simple-work-package workflow with Codex GPT-5.5 high-effort implementation and high-effort review, looping back only for high or middle findings.
---

# Riel Codex Simple Work Package

Use this skill when the user asks for a small code or documentation change under
a directory or file scope and no dedicated workflow is a better fit.

## Workflow Bundle

- Workflow id: `codex-simple-work-package`
- Package id: `codex-simple-work-package`
- Backend: `codex-agent`
- Model: `gpt-5.5`
- Effort: `high` for both implementation and review
- Loop rule: the review step routes back to implementation only for `high` or
  `middle` findings

## Standard Run

Run from the repository root after checkout or installation:

```bash
rielflow workflow run codex-simple-work-package \
  --variables '{"workflowInput":{"targetDirectory":"path/to/dir","requestedChange":"Describe the small code or documentation change.","acceptanceCriteria":["Review has no high or middle findings."]}}' \
  --output json --no-auto-improve
```

Adjust `targetDirectory`, `requestedChange`, `constraints`,
`acceptanceCriteria`, and `verificationHint` to the user's request.

## Scope

Prefer this workflow for lightweight edits inside a requested directory or file
scope. Do not use it for changes that need design documents, implementation
plans, refactoring decomposition, recent-change quality loops, task watchdog
dispatch, or other dedicated workflows.

The implementer should not create commits or pushes unless the user explicitly
asks for them.

## Verification

Validate the package workflow after edits:

```bash
rielflow workflow validate codex-simple-work-package \
  --workflow-definition-dir ./packages/codex-simple-work-package/workflows
```

Refresh `rielflow-package.json` digests after changing the workflow or packaged
skill:

```bash
bun .agents/skills/rielflow-package-release/scripts/update-package-digests.ts codex-simple-work-package
```
