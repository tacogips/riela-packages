---
name: riel-claude-code-deepdesign
description: Use when running, editing, or troubleshooting the packaged claude-code-deepdesign riela workflow for design-doc specification authoring with deep and broad review loops.
---

# Riel Claude Code Deepdesign

Use this skill when the user asks Claude Code to create or refine design-doc specifications through the packaged `claude-code-deepdesign` workflow, or when maintaining that workflow package.

## Workflow Bundle

- Workflow id: `claude-code-deepdesign`
- Package id: `claude-code-deepdesign`
- Backend: `claude-code-agent`
- Primary output: accepted `design-docs/` specification plus deep and broad review summaries
- Loop rule: Node 2 and Node 3 route back to Node 1 until neither review reports `high` or `middle` findings

## Standard Run

Run from the repository root after checkout or installation:

```bash
riela workflow run claude-code-deepdesign \
  --variables '{"workflowInput":{"feature":"Describe the feature to design.","targetDesignDoc":"design-docs/specs/design-example.md","constraints":["Design documentation only."],"acceptanceCriteria":["Deep review has no high or middle findings.","Broad review has no high or middle findings."]}}' \
  --output json --no-auto-improve
```

Adjust `feature`, `targetDesignDoc`, `targetScope`, `constraints`, `acceptanceCriteria`, and `nonGoals` to the user's request.

## Provisional Decisions

The workflow should not stop for user confirmation. When a user decision would normally be required, Node 1 must choose the generally preferable, conservative specification and document it as a provisional decision.

Each provisional decision should include:

- the chosen provisional specification
- why user confirmation would normally be needed
- why this provisional choice is preferable
- what should change if the user later disagrees

Prefer recording these decisions in a clearly named `Provisional Decisions` section of the target design document. Use `design-docs/user-qa/` when the decision needs a separate follow-up note.

## Review Expectations

Node 2 deep review checks assumptions, prerequisites, irregular states, lifecycle edge cases, recovery paths, malformed inputs, permissions, privacy, observability, and testability.

Node 3 broad review checks existing similar features, duplication risk, adjacent workflow behavior, package and installation impacts, combined use cases, compatibility, migration, docs, and repository conventions.

Both reviewers must return adapter JSON with `when.needs_revision` and `payload.needs_revision`. Set those booleans to `true` only when any `high` or `middle` finding exists.

## Verification

Validate the package workflow after edits:

```bash
riela workflow validate claude-code-deepdesign \
  --workflow-definition-dir ./packages/claude-code-deepdesign/workflows
```

Run the bundled mock scenario when prompts, transitions, or review payloads change:

```bash
riela workflow run claude-code-deepdesign \
  --workflow-definition-dir ./packages/claude-code-deepdesign/workflows \
  --mock-scenario ./packages/claude-code-deepdesign/workflows/claude-code-deepdesign/mock-scenario.json \
  --output json
```

Refresh `riela-package.json` digests after changing the workflow or packaged skill:

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts claude-code-deepdesign
```
