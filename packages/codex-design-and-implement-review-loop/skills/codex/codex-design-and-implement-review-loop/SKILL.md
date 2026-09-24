---
name: codex-design-and-implement-review-loop
description: Run the all-Codex Riela workflow for analysis, design, implementation planning, implementation, independent review, verification, documentation, and completion checks. Use for issue resolution or planning-only handoff when Codex should own every agent role; do not use when Claude or Fable should participate.
---

# Codex Design And Implement Review Loop

Run the installed `codex-design-and-implement-review-loop` workflow instead of
manually emulating its orchestration.

## Responsibility split

- Codex `gpt-6-astra` medium effort: design documentation, implementation-plan authoring, and final combined-tree integration review
- Codex `gpt-6-sol` medium effort: implementation, revisions, overwrite repair, test-integrity, and the single adversarial implementation review
- Repeated implementation, reconciliation, and review attempts reuse their role-local backend session. Astra implementation-plan authoring and integration review inherit the Astra design session so accepted intent stays available without merging implementation and adversarial-review contexts.
- Other coordination uses Codex `gpt-6-sol`. The adversarial gate accepts only material spec violations, correctness/data-loss/security risks, likely regressions, or missing material verification; it rejects style nits, naming-only feedback, speculative refactors, and overengineering.

Every agent node uses low or medium effort. Do not raise any node, especially an Astra node, to high, xhigh, or extra-high effort.

Design and planning each use one author node. Astra plans must state intent/context, non-goals, exact file-level changes, invariants, acceptance criteria, and evidence-producing verification commands so even a lower-capability implementation model could execute without inventing scope. Commit and non-force push accepted plans before native same-branch implementation/review fanout; a blocked checkpoint push stops dispatch. This leaves only the final implementation commit unpublished for the built-in push gate. Sol implementation and test-integrity maximize safely independent delegated investigation and verification while retaining a single integration owner and avoiding overlapping edits. The join aggregates runtime-owned change evidence; serial repair and independent combined review are mandatory before final commit, push and base integration. No worktrees. Failed branches remain pending; accepted IDs feed native dependency scheduling. Requires the matching Riela fanout.dependencies/changeTracking support.

An incomplete Step 6 attempt with concrete new change, plan-progress, and passing behavioral-test evidence may continue in the same branch at most twice without repeating design and planning. External blockers, repeated evidence, missing material verification, and a third consecutive incomplete attempt terminate with an actionable handoff; incomplete work never enters review or Git finalization.
Step 6 completeness covers its assigned implementation and behavioral verification, not formal downstream reviews, review-dependent documentation, commit, or push. A plan task expressly ordered after formal review remains pending for those later steps and must not make Step 6 self-block; the workflow must still report and perform it before final completion.

## Run

```bash
riela workflow validate codex-design-and-implement-review-loop
riela workflow inspect codex-design-and-implement-review-loop --output json
riela workflow run codex-design-and-implement-review-loop \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the target scope.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

Use `--scope user` for a user-scope install. Preserve the operator's requested
mode, constraints, authorization boundaries, and acceptance criteria. The
workflow may prepare a commit and push near completion, so do not run it unless
those repository mutations are authorized; otherwise use inspection or
validation without starting the workflow.

Report the resulting artifacts, changed files, verification evidence, review
decisions, residual risks, and final workflow status.

## Maintainer verification

After changing this packaged workflow or skill in the registry checkout, run:

```bash
riela workflow validate codex-design-and-implement-review-loop \
  --workflow-definition-dir ./packages/codex-design-and-implement-review-loop/workflows
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts \
  codex-design-and-implement-review-loop
```
