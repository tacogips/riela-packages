# wave-summary-prompts

Status: completed. Implementation accepted by test-integrity, adversarial and integration review in session-480 (integration-review-attempt-1-exec-7361, comm-008771). Archived from `impl-plans/active/wave-summary-prompts.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "wave-summary-prompts",
  "planPath": "impl-plans/completed/wave-summary-prompts.md",
  "dependsOn": [],
  "writePaths": [
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/reconcile-implementations.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/integration-review.md",
    "packages/opus-terra-design-and-implement-review-loop/tests/test_wave_summary_prompts.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "progressFile": "tmp/wave-compaction/wave-summary-prompts/progress.json",
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_wave_summary_prompts.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "grep -n 'runtimeVariables.fanoutJoin\\|fanoutJoin.branches\\|fanoutJoin.dispatchedBranchIds' packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/reconcile-implementations.md packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/integration-review.md packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/implementation-blocked-output.md",
    "find packages/opus-terra-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "reconcile-implementations.md no longer tells the agent to read runtimeVariables.fanoutJoin or the joined inbox payload. It locates the current wave summary by the design D3 rule (highest tmp/opus-terra-waves/<own _rielaInput.workflowExecutionId>/wave-NNN/wave-summary.json), requires the summary's workflowExecutionId to match and its verdict to deep-equal the inbox implementation-wave-outcome payload, and treats a mismatch or missing file as a blocking evidence gap.",
    "reconcile-implementations.md takes plans[], dispatchedBranchIds/pendingBranchIds, checkpointProvenance, reviewDecisions, changedFiles, evidencePaths, the changeEvidence aggregates and the selection source-vs-artifact drift paths from the summary. It extracts raw records only by rawPointer with a targeted query, never reads fanout-join.json whole, ignores any raw fanoutJoin in runtimeVariables, and returns waveSummaryPath and rawJoinPath in its payload.",
    "integration-review.md reads the summary at the reconcile-supplied waveSummaryPath, requires it to equal the locator result for its own workflowExecutionId, and uses the summary's dispatchedBranchIds and plans[] instead of native fanoutJoin records, with the same targeted-extraction rule.",
    "All other existing semantics of both prompts are preserved verbatim: checkpoint provenance verification, artifact drift is not a source overwrite, complete:false is a blocking gap, partial_success handling, Luna ownership, the detailed revision handoff, the loopGate contract.",
    "test_wave_summary_prompts.py passes (design Verification case 11)."
  ]
}
```

## Intent and context

Issue `workflowInput:opus-terra-wave-input-compaction`, mode `issue-resolution`. Accepted design: `design-docs/specs/design-opus-terra-wave-input-compaction.md` (D3 locator, D4 summary schema, D5 prompt changes, Verification case 11). After the `wave-outcome-script` plan lands, `implementation-wave-outcome` is a deterministic command. It hands `reconcile-implementations` only the six-field verdict and writes the bounded summary to `tmp/opus-terra-waves/<workflowExecutionId>/wave-NNN/`. The two prompts must use that summary as their wave data source.

This plan only changes prompt text, and it does not depend on the script code. The summary schema and locator are pinned by the design. `W` = `packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop`.

The rendered-prompt bound is not delivered here, because riela still renders the persistent `fanoutJoin` request variable. It is pending user decision Q1 in `design-docs/user-qa/opus-terra-wave-input-compaction.md`. The prompts can only tell the agent to ignore that key; do not claim this bounds the prompt.

## Non-goals

- Do not edit node JSON files, output schemas, `workflow.json`, `implementation-blocked-output.md`, other prompts, mocks, docs, scripts, other packages, `.agents/` or the Codex base prompts.
- Do not rewrite or reorder unrelated paragraphs. Only replace the sentences that reference the raw join, and add the summary instructions.
- Do not add the D7 option B `fanoutJoin` stub.

## File-level changes

1. `W/prompts/reconcile-implementations.md`
   - Replace the second sentence block, which begins `Read runtimeVariables.fanoutJoin or the joined inbox payload` and ends `do not run a workflow-local evidence script.`, with the wave-summary instructions:
     - The direct inbox is the deterministic verdict.
     - Locate the summary by the locator rule and verify `workflowExecutionId` and the `verdict` deep-equality.
     - Read the committed manifest and prior accepted waves as before.
     - Ignore any `fanoutJoin` key in runtimeVariables: never read, quote or summarize it.
     - Use `plans[]`, `dispatchedBranchIds` and `pendingBranchIds`.
     - Extract only the needed record by `rawPointer`, for example `jq '.branches[2].output.reviewDecisions' <rawJoinPath>`, when a field ends with the `…[truncated` marker or a `*Total` exceeds the listed items.
   - In the `checkpointProvenance` sentence, change the source from "each successful native fanout branch's `checkpointProvenance`" to "each successful plan's `checkpointProvenance` in the wave summary (extract the full record by `rawPointer` when truncated)". Keep "Require the branches to agree" and every verification clause.
   - In the `Observations carry selection` paragraph, refer to the summary's `changeEvidence.paths[].selection`, `bySelection` and `byKind` counts, and `captureFailures` / `reduceFailures` with their totals. Keep the source-vs-artifact rule and the `complete:false` rule verbatim in meaning.
   - In the `Return payload {...}` sentence, add `waveSummaryPath,rawJoinPath`. Keep every existing field.
2. `W/prompts/integration-review.md`
   - In the paragraph beginning `Use native fanoutJoin.dispatchedBranchIds and branchId records`, replace the data source with the wave summary from the reconcile payload's `waveSummaryPath`. That path must equal the locator result for the reviewer's own `_rielaInput.workflowExecutionId`, and its `verdict` must match the summary's own binding. Use the summary's `dispatchedBranchIds` and `plans[]`.
   - In the `Treat selection: "artifact"` sentence (paragraph 3), reference the summary `changeEvidence`.
   - Add the same ignore-raw-`fanoutJoin` and `rawPointer` targeted-extraction rule as one sentence.
   - Keep every other sentence unchanged.
3. `packages/opus-terra-design-and-implement-review-loop/tests/test_wave_summary_prompts.py`: new `unittest` module. Read the three prompt files as UTF-8 text. Imitate the path constants in `tests/test_review_handoff.py`.

## Key pitfalls

- `check-compact-workflows.ts` regex-tests only the Codex bundle's prompts, so there is no shared-text constraint here. Do not edit the Codex bundle.
- Do not drop the provenance, `baselineReviewPending`, SwiftLint, reviewDecisions, Luna-ownership or loopGate paragraphs. Diff review must show only the targeted replacements.
- Do not instruct `cat` or a full read of `fanout-join.json`. Only pointer-targeted extraction is allowed.
- Use the exact literals `tmp/opus-terra-waves/`, `wave-summary.json`, `rawPointer`, `waveSummaryPath`, `rawJoinPath` and `verdict`; the tests and the script share them.

## Test cases (`situation -> expected`)

1. `reconcile-implementations.md` and `integration-review.md` contain none of `runtimeVariables.fanoutJoin`, `fanoutJoin.branches` or `fanoutJoin.dispatchedBranchIds`.
2. `reconcile-implementations.md` contains `tmp/opus-terra-waves/`, `wave-summary.json`, `rawPointer`, `waveSummaryPath`, `rawJoinPath` and `verdict`.
3. `integration-review.md` contains `waveSummaryPath`, `rawPointer` and `tmp/opus-terra-waves/`.
4. `implementation-blocked-output.md` contains none of `runtimeVariables.fanoutJoin` or `fanoutJoin.branches`. It is unchanged; this asserts the audit.
5. Preserved semantics: reconcile still matches `selection: "artifact"`, `checkpointProvenance`, `reviewDecisions` and `partial_success`. integration-review still matches `loopGate`, `repairInstructions`, `redispatch_required:true and repair_in_place:false` and `partial_success`.

## Execution, drift and progress contract

- Write only the three `writePaths`. Before each edit, freshly read the file. Record its SHA-256 and an immutable intent note under `tmp/wave-compaction/wave-summary-prompts/attempt-N/intent/`, re-check the hash before writing, reconcile on drift, and record post-hashes.
- Maintain `tmp/wave-compaction/wave-summary-prompts/progress.json` and `handoff.json` with commands, cwd, exit codes, complete log paths and test counts.
- Run commands in the foreground from the repository root.
- No git mutations. Do not touch other plans' files.

## Verification and required evidence

- `test_wave_summary_prompts.py`: exit 0 and ≥ 5 tests, 0 failures.
- The package discover: exit 0. The `wave-outcome-script` tests may be absent or present depending on timing; record which.
- The grep command must print nothing, and its exit 1 is the expected "no match" outcome. Record it as such.
- `find ... __pycache__`: no output.
- `git diff --check`: exit 0.
- Save a unified diff of both prompts against `81a4fcb` in the attempt directory for reviewers.

## Completion criteria

All acceptance criteria are evidenced, progress and handoff are complete, and no open high or mid finding remains. Later independent reviews decide acceptance.

## Operator amendment (2026-10-22, rerun after session-476)

Attempt 1 was blocked by workflow bookkeeping, not by this plan's code: the
installed progress gate did not recognize `python3 -m unittest` as a
behavioral test runner. That gate is fixed in cfa5880 and the rerun uses the
fixed gate. The attempt-1 implementation is still in the working tree; reuse
it, re-run this plan's verification, and report each test command with an
integer `exitCode`, `testsRun` and `failureCount`. The package suite currently
passes (31 tests, including `tests/test_progress_check.py`).


## Operator amendment 2 (2026-10-22, rerun after session-477)

The upstream riela change (D7 Option A: stop persisting the raw `fanoutJoin`
as a run-level request variable) is out of scope for this package run and is
tracked in the riela repository as an operator follow-up. It is NOT a blocker
of this plan. This plan's contract is the prompt changes and their tests; when
those pass, report the plan as complete with `implementation_blocked: false`
and no `blockers`. Mention the upstream dependency only in prose (progress
log / handoff notes), never in `blockers`, `findings` or `risks`, and never as
a string starting with a severity word.
