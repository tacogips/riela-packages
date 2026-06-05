---
name: riel-codex-deepdesign
description: Use when running, editing, or troubleshooting the packaged codex-deepdesign rielflow workflow for design-doc specification authoring with deep and broad review loops.
---

# Riel Codex Deepdesign

Use this skill when the user asks Codex to create or refine design-doc specifications through the packaged `codex-deepdesign` workflow, or when maintaining that workflow package.

## Workflow Bundle

- Workflow id: `codex-deepdesign`
- Package id: `codex-deepdesign`
- Backend: `codex-agent`
- Primary output: accepted `design-docs/` specification plus deep, broad, and adversarial review summaries
- Loop rule: Node 2, Node 3, and Node 4 route back to Node 1 until no review reports `high` or `middle` findings

## Standard Run

Run from the repository root after checkout or installation:

```bash
bun run packages/rielflow/src/bin.ts workflow run codex-deepdesign \
  --variables '{"workflowInput":{"feature":"Describe the feature to design.","targetDesignDoc":"design-docs/specs/design-example.md","constraints":["Design documentation only."],"acceptanceCriteria":["Deep review has no high or middle findings.","Broad review has no high or middle findings.","Adversarial review has no high or middle findings."]}}' \
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

Node 4 adversarial review checks failure modes, misuse paths, misleading success states, implementation loopholes, overconfident assumptions, and verification that could pass while material behavior remains broken.

All reviewers must return adapter JSON with `when.needs_revision` and `payload.needs_revision`. Set those booleans to `true` only when any `high` or `middle` finding exists.

## Verification

Validate the package workflow after edits:

```bash
bun run packages/rielflow/src/bin.ts workflow validate codex-deepdesign \
  --workflow-definition-dir ./packages/codex-deepdesign/workflows
```

Run the bundled mock scenario when prompts, transitions, or review payloads change:

```bash
bun run packages/rielflow/src/bin.ts workflow run codex-deepdesign \
  --workflow-definition-dir ./packages/codex-deepdesign/workflows \
  --mock-scenario ./packages/codex-deepdesign/workflows/codex-deepdesign/mock-scenario.json \
  --output json
```

Refresh `rielflow-package.json` digests after changing the workflow or packaged skill:

```bash
bun .agents/skills/rielflow-package-release/scripts/update-package-digests.ts codex-deepdesign
```
