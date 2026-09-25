# d4-opus-contracts: migrate fable-and-improve-opus

```json
{
  "planId": "d4-opus-contracts",
  "planPath": "impl-plans/active/d4-opus-contracts.md",
  "dependsOn": [],
  "writePaths": [
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-fable-analysis.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-fable-design.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-opus-implementation.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-opus-review.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-fable-goal-review.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-kb-self-review.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-kb-merge-judge.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-kb-archive-brief.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-final-output.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-plan-checkpoint.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-dispatch-plans.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-branch-evidence.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-reconcile-implementations.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-integration-review.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-step9-commit-message.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/nodes/node-base-branch-integrate.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/prompts/fable-goal-review.md",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/prompts/plan-checkpoint.md",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/prompts/step9-commit-message.md",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/prompts/kb-merge-judge.md",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/prompts/kb-archive-brief.md",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/mock-scenario.json",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus/EXPECTED_RESULTS.md",
    "packages/fable-and-improve-opus/tests/check-output-contract.ts",
    "impl-plans/active/d4-opus-contracts.md"
  ],
  "sharedPaths": []
}
```

## Intent, authority and limits

Workflow mode: `issue-resolution`. Issue repository: `tacogips/riela-packages`; title: “Migrate fable-and-improve bundles to the agent-node output contract”; number/URL: not supplied. Step 3 accepted the design without findings. Source of truth: `design-docs/specs/design-fable-output-contract-d4.md` and its linked user-QA. No codex-agent reference input, Cursor mapping or intentional reference divergence applies.

Riela core already implements the contract. Modify only the named package artifacts to preserve behavior under mandatory sandboxes and required producer schemas. Do not edit Riela core, unrelated packages, the dirty main checkout, other worktrees, models/backends/effort/session policies, workflow routing/fanout, or Git add-on behavior. Do not create the absent `packages/fable-and-improve` package. Its scope question remains in user-QA; do not mark three-package acceptance satisfied. Do not rediscover the executing workflow's registry/provenance. No release publication, new abstraction or cleanup work.

## Shared-workspace execution and evidence

The checkpoint step must commit the accepted design, all three plans and dispatch manifest before implementation fanout. Work on the existing `feat/output-contract-d4` branch and worktree; no worker Git mutation, private branches or worktrees. Treat checkpointCommit and this run's evidenceRoot from runtime input as authoritative. Each plan owns only its listed paths and progress file. Shared indexes, manifests and global plan archiving belong to serial reconciliation/finalization.

Before EACH edit, freshly read the path and compare SHA-256 with the last recorded version. Save immutable before/after contents and hashes under evidenceRoot/planId/attempt-N; use unique filenames, never replace snapshots. Before first edit also save accepted plan/design intent and a baseline file inventory. Missing files have an explicit absent marker. Compare completed intended edits against fresh contents before handoff and again after the join. Native fanout change tracking is additional evidence, not permission to overwrite drift. If another writer changed a path, preserve both versions and report drift; serial reconciliation repairs only the lost intended edits after all workers stop. Never restore a whole old file blindly.

Run all shell/verification commands in foreground. Retain/poll yielded sessions through exit. For each command record exact expanded argv, cwd, complete stdout/stderr log, final exit, test/scenario/assertion count and observed session result. Keep scratch, logs, caches and isolated mock state under the worktree's tmp/. Use a unique evidenceRoot/planId/attempt-N directory (E below); do not share mock stores between scenarios or attempts. A truncated log, missing exit or missing assertion is not a pass. Progress goes only in this plan's Progress log; report task statuses, changed paths, commands, logs, counts, findings and residual gaps. Do not mark later review/commit/push gates complete from a worker.

## Tasks and precise deliverables

1. **Inventory before edits.** Fresh-read `packages/fable-and-improve-opus/workflows/fable-and-improve-opus/workflow.json`, every node and referenced prompt, including add-on config/inputs and mock payloads. Save a table identifying each missing sandbox, conditional label, consumed template field, producer and current schema. Follow incoming edges through forwarding add-ons with cycle protection; do not mistake runtime context references for payload requirements. Baseline: 16 agents, 11 missing sandboxes, 8 existing schemas. Investigate drift instead of forcing historical counts.
2. **Sandbox declarations (node files only).** Preserve all existing values. Add `workspace-write` on missing implementation, checkpoint, branch-evidence, reconciliation, Step 9 and base-branch-integration nodes. Add `read-only` on missing implementation reviewer, integration-review, dispatch-plans, knowledge self-review/judge/archive-brief and final-output nodes. Existing Fable design/goal-review declarations stay unchanged. Confirm all 16 sandbox-consuming agents have supported explicit values. No workflow.json edits.
3. **Minimal schemas and budgets.** Add schemas to `node-plan-checkpoint.json`, `node-step9-commit-message.json` and `node-fable-goal-review.json`. Preserve existing review, analysis, knowledge, dispatch, reconciliation and integration schemas; strengthen conditional knowledge fields only as specified below. Set `output.maxValidationAttempts: 2` on required payload/label producers. Do not add schemas to unconditional implementation/design/reporting nodes without a concrete consumer requirement. Do not remove existing schemas. Keep noncontract node fields unchanged.
4. **Prompt/schema compatibility.** Read `packages/fable-and-improve-opus/workflows/fable-and-improve-opus/prompts/fable-goal-review.md` for this bundle's exact business fields. Its routing flags stay in `when`; do not require new payload copies. If prose is ambiguous, clarify only the listed relevant prompt, maintaining the existing business output. Checkpoint requires nonempty `commitMessage`, path-string array `committedFiles`, string `manifestPath` and string `evidenceRoot`. Step 9 requires shared completion fields actually emitted by its prompt; use `anyOf`/`oneOf` and `const` to distinguish revision from accepted output. Revision has `decision: needs-revision`, `needs_revision: true` and need not contain commit fields. Acceptance has `decision: accepted`, `needs_revision: false`, `accepted: true`, empty findings, nonempty commitMessage (`minLength: 1`) and path-string committedFiles. Planning-only remains valid. Keep `when.needs_revision` consistent with payload. Do not use unsupported schema keywords. Declare `git` object shape if the forwarding walk requires it, but never require the agent to fabricate the add-on-produced git.commitHash.
5. **Knowledge compatibility.** On merge, require actual `mergeNoteId` and `mergedBody`; skip/create must not need them. On `archive_note: true`, require actual archive ID/body; false must remain valid without them. Preserve `candidateContent` string and `candidateTags` array types. Keep root properties discoverable to static validation even when branch-specific required lists live in schema combinators. Retain additional evidence fields permitted by current prompts.
6. **Reproducible tests and docs.** Update `packages/fable-and-improve-opus/workflows/fable-and-improve-opus/mock-scenario.json` only to align actual payload contracts. Add `packages/fable-and-improve-opus/tests/check-output-contract.ts`, a small Bun regression runner using installed `riela` and built-in assertions/process/file APIs, following the existing repository mock pattern without changing its shared runner. Accept `--evidence-root <absolute path>`; write all generated scenarios and copied probe bundles there. Record complete child stdout/stderr and exit for each invocation. Use `spawnSync` or fully awaited foreground child processes; no live providers or real git/knowledge actions. Update EXPECTED_RESULTS with commands, scenario names and expected results; replace its source-build advice with installed CLI target checks.

## Test matrix and required assertions

The package runner must cover these 10 named cases, plus static invariants:

1. `happy`: original complete workflow succeeds; checkpoint precedes fanout, reconciliation/review precede final git steps and knowledge work.
2. `completion-revision`: revision without commit fields routes to Fable goal review, then a subsequent accepted answer reaches git-commit exactly once.
3. `planning-only`: valid accepted completion without archive cleanup.
4. `checkpoint-empty-message`: empty checkpoint message is rejected at producer, before plan-git-commit.
5. `commit-missing-message`: accepted Step 9 missing message is rejected before step10-git-commit.
6. `commit-empty-message`: accepted Step 9 empty message is rejected before step10-git-commit.
7. `knowledge-create`: create path succeeds without merge-only fields.
8. `knowledge-merge-archive`: merge and archive selected with required values, expected add-ons reached in order.
9. `knowledge-merge-no-archive`: merge succeeds, archive false omits archive-only fields and bypasses archive add-on.
10. `knowledge-skip`: skip needs no merge/archive fields and bypasses write add-ons.

Use actual published envelope payloads and execution records as assertions, not fixture intent. For focused cases, copy the authored bundle under E and alter only the probe entry step/fixture there, following the existing compact-workflow test pattern; keep at least happy and completion-revision exercising production routing. Never edit the production graph for tests. All agent and add-on steps must be mocked. Negative cases must prove schema rejection at the intended producer, not failure from unrelated validation/loop limits. If mock execution bypasses contract validation, report that gap and use an existing installed-runtime validation entry point if available; do not claim rejection/retry coverage from structural assertions. No Riela core changes or new generic validator.

Static assertions: 16 supported sandboxes; expected required-producer coverage and budgets; schema permits branch outputs; workflow.json, backend/model/effort/session/fanout settings equal checkpoint baseline; no new schemas on unrequired producers. Compare graph/settings with `git show <checkpointCommit>:<path>` read-only. Print actual scenario/assertion totals. Runtime schema validation and JSON parsing are the appropriate checks for these JSON/prompt changes; no application typecheck is applicable. Bun executes the small test runner.

## Exact verification commands

Run from repository root, assigning E to the absolute runtime evidenceRoot/d4-opus-contracts/attempt-N path and creating it before execution. Capture each command separately with its true exit; do not mask failure with tee.

```sh
riela workflow validate fable-and-improve-opus --workflow-definition-dir packages/fable-and-improve-opus/workflows --output json
riela workflow run fable-and-improve-opus --workflow-definition-dir packages/fable-and-improve-opus/workflows --mock-scenario packages/fable-and-improve-opus/workflows/fable-and-improve-opus/mock-scenario.json --session-store "$E/happy/sessions" --artifact-root "$E/happy/artifacts" --output json
bun packages/fable-and-improve-opus/tests/check-output-contract.ts --evidence-root "$E/regressions"
git diff --check
```

The test runner must additionally run installed validation and mock commands with fully expanded paths in its command journal; each mock needs isolated sessions/artifacts and any knowledge roots. CLI success must match completed session status and assertions. Record expected nonzero negative-case exits as successful assertions only after checking the intended schema diagnostic and absence of consumer execution.

## Acceptance and completion

All tasks above complete, 16/16 sandbox declarations, required producers covered without blanket additions, nonempty accepted commit fields, valid revision/knowledge branches, unchanged graph/settings, passing target validation and all 10 cases with complete logs and counts. No unresolved high/mid implementation finding. Package manifests and shared indexes remain untouched for serial reconciliation. Handoff exact changed files, immutable intent snapshots, pre/post hashes and evidence paths. A missing test or unrelated failure must be stated explicitly; do not mark passed.

## Progress log

- Plan authored after Step 3 acceptance; implementation not started.
- Tasks 1–6: pending. Verification: pending. Independent review: pending.
