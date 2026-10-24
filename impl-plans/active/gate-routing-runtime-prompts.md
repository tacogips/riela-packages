# gate-routing-runtime-prompts

Status: active. Wave 1. Issues tacogips/riela#125, #126, #129, #132 and #134 (implementation and finalization prompt rules).

```json
{
  "planId": "gate-routing-runtime-prompts",
  "planPath": "impl-plans/active/gate-routing-runtime-prompts.md",
  "dependsOn": [],
  "writePaths": [
    "impl-plans/active/gate-routing-runtime-prompts.md",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/prompts/step6-implement.md",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/prompts/integration-review.md",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/prompts/step8-docs-refresh.md",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/prompts/step9-commit-message.md",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/prompts/implementation-blocked-output.md",
    "packages/opus-luna-design-and-implement-review-loop/tests/test_runtime_prompts.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-luna-design-and-implement-review-loop/tests/test_runtime_prompts.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-luna-design-and-implement-review-loop/tests/test_wave_summary_prompts.py packages/opus-luna-design-and-implement-review-loop/tests/test_progress_gate.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-luna-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "find packages/opus-luna-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "step6-implement.md requires integer exitStatus, testsRun and failureCount on every verification record, and `kind: \"behavioral-test\"` for test runners outside the allowlist (never for build, lint, format or diff commands). Mutation and expected-failure runs carry `negativeControl: true` with `expectedExitStatus`, never reuse a committed verification command, and are never positive evidence. Superseded attempts stay out of verification[]. During fanout, format, lint and test gates are scoped to the plan's own writePaths, and a failure caused only by another plan's file is reported as a blocker object {paths, command, exitStatus, message} without editing that file.",
    "integration-review.md requires that, for every candidate plan with `<evidenceRoot>/<planId>/sibling-owned-blockers.json`, each recorded command (or the equivalent workspace gate) is re-run on the reconciled combined tree, a remaining failure becomes a material finding owned by the path's owning plan, and the candidate is not accepted while a deferred gate fails.",
    "step8-docs-refresh.md no longer instructs moving files. It returns archiveRequests [{source, destination}] for completed plans, updates impl-plans/README.md and links to the destination paths, and never runs mv, git mv, rename helpers or scripts that move files. It also returns a non-empty issueReference copied verbatim from the committed dispatch manifest reviewContext.issueReference under impl-plans/active, or from the accepted upstream payload when that payload carries one. It never invents a placeholder.",
    "step9-commit-message.md reads archiveResults from the plan-archive payload. It returns needs_revision with exact paths for rejected, conflict or missing results, accepts moved and already-archived, lists both source and destination of each such result in committedFiles, and still never moves files.",
    "implementation-blocked-output.md copies the issue reference, blockedPlanIds, successfulPlanIds, blockers, resumeCriteria, nextStep and blockedStepId from whichever direct predecessor delivered the blocked payload (implementation-wave-outcome, dispatch-plans amendment_blocked, or plan-archive completion_blocked). blockedPlanIds is non-empty for wave and dispatch blocks and may be empty for the completion-loop block. For the plan-archive source, the issue reference is the plan-archive payload's forwarded issueReference.",
    "test_runtime_prompts.py asserts the anchors below. The existing test_wave_summary_prompts.py and test_progress_gate.py prompt assertions still pass, and all opus-luna tests pass."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-luna-gate-routing-0110.md`, D1.6, D2.6, D3.5-D3.6, D5.8 and D6.1/D6.5. `W`/`T` as in `impl-plans/active/gate-routing-negative-control.md`.

These prompts tell the agents how to produce, and how to consume, the deterministic contracts implemented by the script plans:
- structured records for #125;
- negative controls for #134;
- sibling-owned blockers for #126, with the path pinned to `<evidenceRoot>/<planId>/sibling-owned-blockers.json`;
- archive requests and results for #129;
- the generic blocked handoff for #132 and #129.

## Non-goals

- Do not edit step4, step5 or plan-checkpoint prompts. Those belong to `gate-routing-planning-prompts`.
- Do not edit nodes, `workflow.json` or scripts.
- Do not remove the existing wave-summary, rawPointer, fanoutJoin-ignore, baseline-review and envelope wording in `integration-review.md`. `T/test_wave_summary_prompts.py` and `T/test_progress_gate.py::IntegrationReviewEnvelopeTests` assert them.

## File-level changes

1. `W/prompts/step6-implement.md`: add a "Verification record contract" bullet group and a concurrent-fanout gate bullet.
   - The record contract lists the allowlisted runner forms, using the same list as the progress-check resume text: swift test, cargo test, cargo nextest run, go test, pytest, python -m unittest, ctest, bun test, vitest run, npm/pnpm/yarn test, tree-sitter test, deno test, node --test, and task/mise run/make/npm|pnpm|yarn|bun run `<name containing test>`.
   - The fanout bullet is an addition to, not a replacement for, the existing "Do not run broad formatters ... concurrently" line.
2. `W/prompts/integration-review.md`: add one paragraph near the acceptance rules. It must contain `sibling-owned-blockers.json` and `siblingOwnedBlockers`. Do not add JSON code blocks.
3. `W/prompts/step8-docs-refresh.md`
   - Replace the "Move only plans ... to `impl-plans/completed/<same-name>.md`" sentence, and the related failure sentence, with the archiveRequests rule. The deterministic `plan-archive` node performs the moves before Step 9, and its `archiveResults` decide.
   - Change the return list: `archivedImplPlanPaths` becomes `archiveRequests` (keep `updatedIndexFiles`).
   - Add `issueReference` to the return list. Copy it verbatim from the committed dispatch manifest's `reviewContext.issueReference` (the `impl-plans/active/*-dispatch.json` named by the accepted checkpoint), or from the accepted upstream payload when one carries it.
     - The value must be a non-empty string; never write a placeholder.
     - If the manifest stores an object, use the same string form that dispatch projects: `repository#issueNumber`, otherwise the identifier, title and URL joined with `: `.
     - Why this is needed: `plan-archive` forwards this key into the `completion_blocked` handoff, and `implementation-blocked-output` requires `issueReference` (minLength 1). This addresses Step 5 finding S5-F1.
   - The words `mv` and `git mv` may appear only in a "never run" instruction.
4. `W/prompts/step9-commit-message.md`
   - Replace "Verify that Step 8 moved completed implementation plans" with "Verify, from `archiveResults` in the direct `plan-archive` payload, that completed plans were moved".
   - Add the status handling rule.
   - Extend the `committedFiles` rule: for every `archiveResults` entry with status `moved` or `already-archived`, include both `source` and `destination`.
5. `W/prompts/implementation-blocked-output.md`
   - Replace "Copy ... from implementation-wave-outcome" and "This step is only reachable for a blocked-only wave" with a generic source rule that names all three predecessors and their flags.
   - Keep the "Do not claim test-integrity review, ..." sentence.
   - Add `blockedStepId` to the returned JSON field list.
   - State that for the `plan-archive` (`completion_blocked`) source, `issueReference` is the plan-archive payload's forwarded `issueReference`. Copy it verbatim and never fabricate one.
   - Do not mention `runtimeVariables.fanoutJoin` or `fanoutJoin.branches`.
6. `T/test_runtime_prompts.py`: a new module that reads the five prompts.

## Key points and pitfalls

- Keep these exact literals: `issueReference`, `reviewContext.issueReference`, `negativeControl`, `expectedExitStatus`, `behavioral-test`, `sibling-owned-blockers.json`, `archiveRequests`, `archiveResults`, `plan-archive`, `amendment_blocked`, `completion_blocked`, `blockedStepId`.
- Step 8 must still own README/index edits. Only the filesystem move moves to the node.
- Step 9 stays read-only. Its "Never attempt the move or index edit" sentence remains.

## Test cases

- step6 contains `negativeControl`, `expectedExitStatus`, `behavioral-test`, `exitStatus`, `testsRun`, `failureCount` and `writePaths`.
- integration-review contains `sibling-owned-blockers.json`, and still contains `rawJoinPath` and `## Output envelope`.
- step8 contains `archiveRequests`, `plan-archive`, `issueReference` and `reviewContext.issueReference`. It does not contain `Move only plans`. Every line containing `git mv` also contains `never` (case-insensitive).
- step9 contains `archiveResults`, `already-archived` and `conflict`.
- implementation-blocked-output contains `dispatch-plans`, `amendment_blocked`, `plan-archive`, `completion_blocked`, `blockedStepId` and `issueReference`. It does not contain `runtimeVariables.fanoutJoin` or `fanoutJoin.branches`.

## Done criteria

- All verification commands exit 0. Evidence is under `tmp/opus-luna-gate-routing/gate-routing-runtime-prompts/`.

## Progress log

- (implementer appends dated entries)
