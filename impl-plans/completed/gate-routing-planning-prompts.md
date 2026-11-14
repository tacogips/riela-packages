# gate-routing-planning-prompts

Status: completed. Wave 1. Issues tacogips/riela#126, #128 and #132 (planning-side prompt rules). Implementation accepted by test-integrity, adversarial and integration review in opus-terra-design-and-implement-review-loop-session-1 (integration-review-attempt-1-exec-93). Archived from `impl-plans/active/gate-routing-planning-prompts.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "gate-routing-planning-prompts",
  "planPath": "impl-plans/active/gate-routing-planning-prompts.md",
  "dependsOn": [],
  "writePaths": [
    "impl-plans/active/gate-routing-planning-prompts.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/step4-impl-plan-create.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/step5-impl-plan-review.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/plan-checkpoint.md",
    "packages/opus-terra-design-and-implement-review-loop/tests/test_planning_prompts.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_planning_prompts.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'",
    "find packages/opus-terra-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "step4-impl-plan-create.md has four rules: (a) the ported Codex rule for plan-contract-validate output with `contract_valid: false`; (b) an `amendment_required` rule for dispatch-plans output (bounded checkpoint amendment, stable plan IDs, accepted plans kept as acceptedDependencies, checkpointAmendment carried verbatim); (c) never list `impl-plans/active` or `impl-plans/completed` in writePaths/sharedPaths, prefer concrete files, and budget snapshot growth across waves; (d) per-plan verification is scoped to the plan's own writePaths, with no workspace-wide format, lint or full-build gates when sibling plans share a wave.",
    "step5-impl-plan-review.md reports violations of (c) and (d) as mid findings, limits an amendment review to the amendment's scope, and carries checkpointAmendment forward.",
    "plan-checkpoint.md has an amendment-checkpoint rule: when checkpointAmendment is present, update the existing manifest in place, verify HEAD equals checkpointAmendment.previousCheckpointCommit instead of the intake originalHead, record previously accepted plans as acceptedDependencies, commit only changed manifest/plan/design files, and leave implementation changes unstaged.",
    "test_planning_prompts.py asserts the anchors listed below. All opus-terra package tests and codex package tests (test_authoring_model_policy reads node-step4 JSON only) pass, and no __pycache__ remains."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-terra-gate-routing-0110.md`, D3.6 (#126), D4.3-D4.4 (#128) and D5.7 (#132). `W`/`T` as in `impl-plans/active/gate-routing-negative-control.md`.

- **#126.** In session 226, Step 4 wrote a workspace-wide `cargo clippy --all-targets` into FST-50's per-plan verification, and a sibling's half-written file blocked it.
- **#128.** In session 226, CMP-40 listed `src`, `editor/src`, `editor/test`, `impl-plans/active` and `impl-plans/completed`, about 978 entries.
- **#132/D5.** The dispatch wrapper routes `amendment_required` back to Step 4. The amendment loop runs step4 -> step5 -> plan-checkpoint -> plan-contract-validate -> plan-git-commit -> plan-push-gate -> dispatch-plans.

Prior art to imitate, adapted to this package's terms:
- `packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/prompts/step4-impl-plan-create.md:25` (contract_valid rule) and `:52` (tracking-contract amendment);
- `packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/prompts/plan-checkpoint.md:12` (amendment checkpoint: verify HEAD against the latest checkpoint, keep accepted plans as acceptedDependencies, preserve unstaged changes).

Keeping accepted plans as `acceptedDependencies` also stops the pre-commit gate from preflighting accepted plans that dispatch would skip. This addresses Step 3 low finding 3.

## Non-goals

- Do not rewrite unrelated prompt text. Add or adjust only the paragraphs named here. Keep the existing "GPT-6 Luna plan contract" section.
- Do not edit step6, step8, step9, integration-review or blocked-output prompts. Those belong to `gate-routing-runtime-prompts`.
- Do not edit nodes, `workflow.json` or scripts.

## File-level changes

1. `W/prompts/step4-impl-plan-create.md`
   - (a) Add a paragraph adapted from the Codex `:25`. It must contain the literal `plan-contract-validate` and `contract_valid: false`, and say: address every finding by narrowing paths or declaring artifactRoots, never raise limits, and report in `addressedFeedback`.
   - (b) Add a paragraph that contains `amendment_required` and `checkpointAmendment`:
     - Perform only the bounded amendment.
     - For `reason: integration-paths-outside-writePaths`, assign each `unmatchedPaths` entry to the `writePaths` of the pending plan that owns the related finding, or to a new small pending plan.
     - For `reason: tracking-contract`, narrow or reclassify tracked paths.
     - Keep plan IDs stable. Record previously accepted plans (`successfulPlanIds`) as `acceptedDependencies`, not as `plans`.
     - Do not redesign. Carry `checkpointAmendment` verbatim in the output.
     - After two amendments, dispatch blocks for the operator.
   - (c) Add to the path-classification bullet: never list `impl-plans/active` or `impl-plans/completed` (completed-plan archiving is performed by the workflow's `plan-archive` node). Prefer concrete files to broad directories in `sharedPaths`, and budget for snapshot growth across waves.
   - (d) Add: per-plan `verification` commands are scoped to the plan's own writePaths (for example `rustfmt --check <owned files>` or a filtered test run). Workspace-wide format, lint or full-build gates belong to reconcile and integration review whenever sibling plans share a wave.
2. `W/prompts/step5-impl-plan-review.md`
   - Add review bullets. Report as `mid`:
     - a plan listing `impl-plans/active` or `impl-plans/completed`;
     - a broad directory likely to exceed the 512-entry snapshot;
     - a workspace-wide format, lint or full-build gate in per-plan verification while sibling plans share a wave.
   - Add: when the input carries `checkpointAmendment`, review only the amendment (ownership of the unmatched paths, stable IDs, acceptedDependencies), and carry `checkpointAmendment` forward in the output.
3. `W/prompts/plan-checkpoint.md`
   - Add the amendment-checkpoint paragraph, adapted from the Codex `plan-checkpoint.md:12`. It must contain `checkpointAmendment.previousCheckpointCommit` and `acceptedDependencies`.
   - The existing "deterministic contract check validates ... before commit" sentence stays. It now names the `plan-contract-validate` node.
4. `T/test_planning_prompts.py`: a new module that reads the three prompt files and asserts the anchors.

## Key points and pitfalls

- Keep the literals exact, because the tests and later steps rely on them: `plan-contract-validate`, `contract_valid: false`, `amendment_required`, `checkpointAmendment`, `checkpointAmendment.previousCheckpointCommit`, `acceptedDependencies`, `impl-plans/active`, `impl-plans/completed`, `workspace-wide`.
- Do not tell the planner to edit `impl-plans/README.md` or to move plans.
- Plain prose only. Do not add JSON code blocks with `when`/`payload` keys.

## Test cases

- step4 contains `plan-contract-validate`, `contract_valid: false`, `amendment_required`, `checkpointAmendment`, `acceptedDependencies`, `impl-plans/completed` and `workspace-wide`.
- step5 contains `checkpointAmendment`, `impl-plans/active`, `512` and `workspace-wide`.
- plan-checkpoint contains `checkpointAmendment.previousCheckpointCommit`, `acceptedDependencies` and `plan-contract-validate`.

## Done criteria

- The prompt and regression-test scope is implemented and all listed verification commands pass on the stable combined tree. Evidence is under `tmp/opus-terra-gate-routing/gate-routing-planning-prompts/`.

## Progress log

- 2026-10-24: Added Step 4 contract-validation, bounded amendment, path-budget, and plan-scoped verification rules; added Step 5 mid-finding and amendment-scope rules; added amendment checkpoint handling; created `tests/test_planning_prompts.py` with 3 anchor/behavior tests. Focused tests passed (3/3, exit 0; `tmp/opus-terra-gate-routing/gate-routing-planning-prompts/focused.log`). Codex tests passed (91/91, exit 0; `.../codex_suite.log`). `git diff --check` passed and `find ... -name __pycache__` found none. The full Opus suite ran 58 tests but remains pending stable-tree rerun: 56 passed, with one error and one failure in dispatch-amendment coverage outside this plan's writePaths (`tests/test_dispatch_amendment.py`: Codex path lookup and amendment round expectation; `.../opus_suite.log`). No prompt-plan tests failed. Do not mark this plan complete until the required full Opus suite passes on the stable combined tree.

- 2026-10-24: Stable combined-tree rerun passed: focused prompt tests 3/3 (exit 0, `tmp/opus-terra-gate-routing/gate-routing-planning-prompts/focused-final.log`); full Opus suite 86/86 (exit 0, `tmp/opus-terra-gate-routing/gate-routing-planning-prompts/opus-suite-final.log`); Codex suite 91/91 (exit 0, `tmp/opus-terra-gate-routing/gate-routing-planning-prompts/codex-suite-final.log`). Removed the generated `scripts/__pycache__` directory found after tests; final `find ... -name __pycache__` is empty (exit 0, `tmp/opus-terra-gate-routing/gate-routing-planning-prompts/pycache-clean-final.log`). Final `git diff --check` passed (exit 0, `tmp/opus-terra-gate-routing/gate-routing-planning-prompts/diff-check-final.log`).
