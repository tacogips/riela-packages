# bwa-prompts

Status: active. Wave 1. Issue: `local:tacogips/riela-packages#opus-terra-blocked-wave-amendment`.
Design: `design-docs/specs/design-opus-terra-blocked-wave-amendment.md`, section D6.

```json
{
  "planId": "bwa-prompts",
  "planPath": "impl-plans/active/bwa-prompts.md",
  "dependsOn": [],
  "writePaths": [
    "impl-plans/active/bwa-prompts.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/step4-impl-plan-create.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/plan-checkpoint.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/step5-impl-plan-review.md",
    "packages/opus-terra-design-and-implement-review-loop/tests/test_planning_prompts.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_planning_prompts.py packages/opus-terra-design-and-implement-review-loop/tests/test_runtime_prompts.py -v",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "step4-impl-plan-create.md accepts checkpointAmendment from dispatch-plans or implementation-wave-outcome. For reason blocked-wave-scope-or-contract it requires the D6 conservative decisions: exact writePaths, an additive contract, one owner per file without same-level write clashes, and a dated '## Amendment <YYYY-MM-DD> (blocked-wave-scope-or-contract, round N)' section in each affected plan. It also requires no redesign (a design gap becomes a Step 5 blocker), stable plan IDs, acceptedDependencies, and checkpointAmendment carried verbatim. It states that the two-amendment bound is shared across dispatch and blocked-wave amendments, and it still contains the phrase 'After two amendments'.",
    "For any checkpointAmendment, plan-checkpoint.md keeps manifest originalHead, taskId and evidenceRoot unchanged. For blocked-wave-scope-or-contract it appends one dated reviewContext.designDecisionsAndRationale entry so the manifest always changes and appears once in committedFiles, and it keeps blocked plans' uncommitted implementation changes unstaged. The existing rule HEAD == checkpointAmendment.previousCheckpointCommit is unchanged.",
    "step5-impl-plan-review.md amendment scope covers the new reason: per-blocker decisions, no redesign, and no same-level write clash.",
    "Every existing assertion in test_planning_prompts.py and test_runtime_prompts.py still passes, and new assertions cover the new text."
  ]
}
```

## Intent and context

The design's D6 asks Opus to resolve blocked-wave scope and contract gaps the same way the existing bounded checkpoint amendment does.

Abbreviations: `W` = `packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop`, `T` = `packages/opus-terra-design-and-implement-review-loop/tests`.

Prompt sentences to imitate:
- `W/prompts/step4-impl-plan-create.md`, the "Plan and dispatch recovery rules" bullet that starts "If `dispatch-plans` returns `amendment_required`".
- `W/prompts/plan-checkpoint.md`, the paragraph that starts "If the checkpoint input carries `checkpointAmendment`".
- `W/prompts/step5-impl-plan-review.md`, line 23.

Test structure to imitate: `T/test_planning_prompts.py`, which uses `assertIn` on fixed phrases.

## Non-goals

- Do not touch any other prompt. In particular, `implementation-blocked-output.md` stays unchanged (design D5).
- Do not touch scripts, workflow.json, nodes, mocks or docs.
- Do not rewrite unrelated prompt text. Edit only the amendment sentences.
- Do not remove or reword any phrase that `T/test_planning_prompts.py` or `T/test_runtime_prompts.py` already asserts. Grep for them before editing.

## File-level changes

1. Step 4 prompt. Extend the existing amendment bullet (or add one sub-bullet right after it) with:
   - the source `implementation-wave-outcome`;
   - the `reason: blocked-wave-scope-or-contract` rules from D6, citing `checkpointAmendment.blockers[]` fields `paths`, `dependency`, `evidence`, `resumeCriterion`/`resumeCriteria`;
   - the dated section heading format;
   - the instruction that a gap needing design change is reported as a Step 5 blocker instead of being decided.

   Replace "After two amendments, dispatch blocks for the operator." with a sentence that keeps "After two amendments" and says the budget is shared by dispatch and blocked-wave amendments. Exhaustion then ends at implementation-blocked-output.
2. `plan-checkpoint.md`. Add three short rules to the amendment paragraph. Keep the existing sentence `HEAD` == `checkpointAmendment.previousCheckpointCommit` verbatim.
   - (a) For any `checkpointAmendment`, keep the manifest's `originalHead`, `taskId` and `evidenceRoot` exactly as committed. Never rewrite `originalHead` to `previousCheckpointCommit` or to the current HEAD. The shared amendment round is counted from `originalHead` (design D2). Clarify that the existing "supersedes the intake `originalHead` check" applies only to the HEAD verification, not to the manifest field.
   - (b) For `reason: blocked-wave-scope-or-contract`, always append one dated entry to the manifest's existing `reviewContext.designDecisionsAndRationale` array, using the shape `{decision: "Amendment <YYYY-MM-DD> round <N>: <summary>", rationale: "<blocked plan ids and resolved gaps>"}`. `dispatch-plans.py` already accepts `{decision, rationale}` items. The entry guarantees that the manifest differs from HEAD and is listed exactly once in `committedFiles`, even when only plan markdown changed. Do not add new manifest top-level keys.
   - (c) Blocked plans' uncommitted implementation changes in the working tree stay unstaged and are never listed in `committedFiles`.
3. `step5-impl-plan-review.md`. Add one sentence to the line-23 bullet: for `blocked-wave-scope-or-contract`, verify that each listed blocker has a recorded decision in a dated amendment section, that there is no redesign, and that plans at the same dependency level have no write clash.
4. `T/test_planning_prompts.py`. Add test methods that assert these strings in the step4 prompt:
   - `blocked-wave-scope-or-contract`
   - `implementation-wave-outcome`
   - `## Amendment`
   - `After two amendments`
   - `shared`

   Also add these assertions:
   - In the checkpoint prompt: `blocked-wave-scope-or-contract`, `committedFiles` and `designDecisionsAndRationale`.
   - Also in the checkpoint prompt: `originalHead` inside the amendment paragraph. That paragraph is the slice from the index of `checkpointAmendment.previousCheckpointCommit` to the next blank line `\n\n`.
   - In the step5 prompt: `blocked-wave-scope-or-contract`.

## Pitfalls

- The prompts are runtime contracts. Keep the additions short (a few sentences) and imperative.
- Do not invite redesign or plan-ID churn. Stable plan IDs and `acceptedDependencies` must stay explicit.
- Two failure modes that the new rules prevent:
  - Missing manifest. If a blocked-wave amendment checkpoint leaves the manifest unchanged, `committedFiles` cannot list it, because unchanged files are forbidden. `dispatch-plans.py:checkpoint_source` then raises `checkpoint must contain exactly one dispatch manifest`, and `dispatch-wave.py` exits 1. Rule (b) prevents this.
  - Rewritten originalHead. If `originalHead` is rewritten, every later blocked wave computes round 0 and the shared bound stops working. Rule (a) prevents this.

## Test cases

- step4 prompt -> contains each new phrase, and every existing assertion still passes.
- plan-checkpoint prompt -> contains each of the following, and still contains `checkpointAmendment.previousCheckpointCommit`:
  - the new reason;
  - the unstaged rule;
  - the `designDecisionsAndRationale` append;
  - `originalHead` preservation inside the amendment paragraph.
- step5 prompt -> mentions the new reason, and still contains "review only the amendment's scope" and "Carry `checkpointAmendment` forward unchanged".

## Done criteria

- The verification commands exit 0.
- A dated `## Progress` section in this file records the changed files and each command's exit status.

## Progress (2026-11-03)

- Implemented the blocked-wave amendment rules in `step4-impl-plan-create.md`, `plan-checkpoint.md`, and `step5-impl-plan-review.md`; added focused assertions in `tests/test_planning_prompts.py`, including the unique “Never rewrite `originalHead`” preservation rule.
- Completion criteria: prompt changes and assigned tests implemented; formal review and release-wide checks remain downstream.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_planning_prompts.py packages/opus-terra-design-and-implement-review-loop/tests/test_runtime_prompts.py -v`: exit 0, 9 tests passed; log `tmp/blocked-wave-amendment/bwa-prompts/attempt-1/unittest.log`.
- `git diff --check`: exit 0; log `tmp/blocked-wave-amendment/bwa-prompts/attempt-1/diff-check.log`.
