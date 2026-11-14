# d4-codex-contracts: migrate fable-and-improve-codex

```json
{
  "planId": "d4-codex-contracts",
  "planPath": "impl-plans/completed/d4-codex-contracts.md",
  "dependsOn": [],
  "writePaths": [
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-fable-analysis.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-fable-design.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-codex-implementation.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-codex-review.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-fable-goal-review.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-kb-self-review.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-kb-merge-judge.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-kb-archive-brief.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-final-output.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-plan-checkpoint.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-dispatch-plans.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-branch-evidence.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-reconcile-implementations.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-integration-review.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-step9-commit-message.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/nodes/node-base-branch-integrate.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/prompts/fable-goal-review.md",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/prompts/plan-checkpoint.md",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/prompts/step9-commit-message.md",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/prompts/kb-merge-judge.md",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/prompts/kb-archive-brief.md",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/mock-scenario.json",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex/EXPECTED_RESULTS.md",
    "packages/fable-and-improve-codex/tests/check-output-contract.ts",
    "impl-plans/active/d4-codex-contracts.md"
  ],
  "sharedPaths": []
}
```

## Intent, authority and limits

Workflow mode: `issue-resolution`. Issue repository: `tacogips/riela-packages`; title: “Finish D4 output-contract migration after progress-gate repair”; number/URL: not supplied. Step 3 accepted the design without findings. Source of truth: `design-docs/specs/design-fable-output-contract-d4.md` and its linked user-QA. No codex-agent reference input, Cursor mapping or intentional reference divergence applies.

Riela core already implements the contract. Modify only the named package artifacts to preserve behavior under mandatory sandboxes and required producer schemas. Do not edit Riela core, unrelated packages, the dirty main checkout, other worktrees, models/backends/effort/session policies, workflow routing/fanout, or Git add-on behavior. Do not create the absent `packages/fable-and-improve` package. The effective input resolves that exclusion; no third-package acceptance gap remains. Do not rediscover the executing workflow's registry/provenance. No macOS/package release publication, new abstraction or unrelated cleanup work. The requested branch push and PR handoff remain required.

## Continuation authority

Resume checkpoint `b5cf79770a8c5c218057d470b0b1a68d16c52901`; Step 3 accepted the updated design with no findings in `comm-000004`. Preserve all existing dirty bundle edits and prior progress entries. No reset, stash, blind overwrite or reimplementation of completed changes. The historical Kaiba-client blocker below is superseded: deterministic add-on responses now exist in both mock scenarios and the existing ScenarioWorkflowAddonResolver consumes them. No real Kaiba endpoint, new mock adapter or Riela core change is needed.

Read `tmp/d4-mock-retry-opus.jsonl` and `tmp/d4-mock-retry-codex.jsonl` as existing evidence. Each root session reports exit 0 and 18 executions; distinguish the nested 3-execution completion. Verify source membership and content against captured run snapshots/inputs, correlate session IDs, and compare executed add-on outputs with fixture responses. Current filenames or completion counts alone do not prove source matching. Preserve original logs. Reuse passing validation/mock receipts when the relevant workflow, nodes, prompts, fixture, variables and installed runtime match; renew only affected checks after changes or when that match cannot be established, documenting the reason. No current-workflow provenance rediscovery is part of this task.

The runner-resolved immutable user-scope orchestration package is 0.3.44. Its repaired progress gate accepts direct Bun behavioral runners with positive test counts and success; do not repair or rediscover orchestration provenance. Prior passing branch runs: Opus 10 cases / 799 assertions, Codex 10 cases / 684 assertions, both exit 0. Existing tasks are verification/targeted repair, not permission to redo passing work.

## Shared-workspace execution and evidence

The checkpoint owner must commit and non-force push the accepted updated design, all three plans and refreshed dispatch manifest before continuation fanout. Stage only those reviewed documentation/dispatch paths; preserve dirty implementation files outside that checkpoint. The existing b5cf797 checkpoint is history, not proof that the revised plans are already published. Work on the existing `feat/output-contract-d4` branch and worktree; no worker Git mutation, private branches or worktrees. Treat checkpointCommit and this run's evidenceRoot from runtime input as authoritative. Each plan owns only its listed paths and progress file. Shared indexes, manifests and global plan archiving belong to serial reconciliation/finalization.

Before EACH edit, freshly read the path and compare SHA-256 with the last recorded version. Save immutable before/after contents and hashes under evidenceRoot/planId/attempt-N; use unique filenames, never replace snapshots. Before first edit also save accepted plan/design intent and a baseline file inventory. Missing files have an explicit absent marker. Compare completed intended edits against fresh contents before handoff and again after the join. Native fanout change tracking is additional evidence, not permission to overwrite drift. If another writer changed a path, preserve both versions and report drift; serial reconciliation repairs only the lost intended edits after all workers stop. Never restore a whole old file blindly.

Run all shell/verification commands in foreground. Retain/poll yielded sessions through exit. For each command record exact expanded argv, cwd, complete stdout/stderr log, final exit, test/scenario/assertion count and observed session result. Keep scratch, logs, caches and isolated mock state under the worktree's tmp/. Use a unique evidenceRoot/planId/attempt-N directory (E below); do not share mock stores between scenarios or attempts. A truncated log, missing exit or missing assertion is not a pass. Progress goes only in this plan's Progress log; report task statuses, changed paths, commands, logs, counts, findings and residual gaps. Do not mark later review/commit/push gates complete from a worker.

## Tasks and precise deliverables

Tasks 1–6 have prior implementation and passing behavioral evidence. Fresh-read and source-check them; repair only a demonstrated mismatch. The current deliverable is a source-matched evidence handoff and updated own progress log. No code edit is required when all invariants still hold.

1. **Inventory before edits.** Fresh-read `packages/fable-and-improve-codex/workflows/fable-and-improve-codex/workflow.json`, every node and referenced prompt, including add-on config/inputs and mock payloads. Save a table identifying each missing sandbox, conditional label, consumed template field, producer and current schema. Follow incoming edges through forwarding add-ons with cycle protection; do not mistake runtime context references for payload requirements. Historical pre-implementation baseline: 16 agents, 13 missing sandboxes, 8 existing schemas; these missing declarations have since been implemented. Investigate drift instead of forcing historical counts.
2. **Sandbox declarations (node files only).** Preserve all existing values. Add `workspace-write` on missing implementation, checkpoint, branch-evidence, reconciliation, Step 9 and base-branch-integration nodes. Add `read-only` on missing implementation reviewer, integration-review, dispatch-plans, knowledge self-review/judge/archive-brief and final-output nodes. Existing Fable design/goal-review declarations stay unchanged. Confirm all 16 sandbox-consuming agents have supported explicit values. No workflow.json edits.
3. **Minimal schemas and budgets.** Verify the implemented schemas to `node-plan-checkpoint.json`, `node-step9-commit-message.json` and `node-fable-goal-review.json`. Preserve existing review, analysis, knowledge, dispatch, reconciliation and integration schemas; strengthen conditional knowledge fields only as specified below. Set `output.maxValidationAttempts: 2` on required payload/label producers. Do not add schemas to unconditional implementation/design/reporting nodes without a concrete consumer requirement. Do not remove existing schemas. Keep noncontract node fields unchanged.
4. **Prompt/schema compatibility.** Read `packages/fable-and-improve-codex/workflows/fable-and-improve-codex/prompts/fable-goal-review.md` for this bundle's exact business fields. Its routing flags stay in `when`; do not require new payload copies. If prose is ambiguous, clarify only the listed relevant prompt, maintaining the existing business output. Checkpoint requires nonempty `commitMessage`, path-string array `committedFiles`, string `manifestPath` and string `evidenceRoot`. Step 9 requires shared completion fields actually emitted by its prompt; use `anyOf`/`oneOf` and `const` to distinguish revision from accepted output. Revision has `decision: needs-revision`, `needs_revision: true` and need not contain commit fields. Acceptance has `decision: accepted`, `needs_revision: false`, `accepted: true`, empty findings, nonempty commitMessage (`minLength: 1`) and path-string committedFiles. Planning-only remains valid. Keep `when.needs_revision` consistent with payload. Do not use unsupported schema keywords. Declare `git` object shape if the forwarding walk requires it, but never require the agent to fabricate the add-on-produced git.commitHash.
5. **Knowledge compatibility.** On merge, require actual `mergeNoteId` and `mergedBody`; skip/create must not need them. On `archive_note: true`, require actual archive ID/body; false must remain valid without them. Preserve `candidateContent` string and `candidateTags` array types. Keep root properties discoverable to static validation even when branch-specific required lists live in schema combinators. Retain additional evidence fields permitted by current prompts.
6. **Reproducible tests and docs.** Update `packages/fable-and-improve-codex/workflows/fable-and-improve-codex/mock-scenario.json` only to align actual payload contracts. Preserve `packages/fable-and-improve-codex/tests/check-output-contract.ts`, the existing Bun regression runner using installed `riela` and built-in assertions/process/file APIs, following the existing repository mock pattern without changing its shared runner. Retain its `--evidence-root <absolute path>` interface; do not add receipt-loading features. Reuse complete previous regression evidence externally after source comparison. Any renewed runner invocation writes generated scenarios and copied probe bundles to a new evidence directory. Record complete child stdout/stderr and exit for each invocation. Use `spawnSync` or fully awaited foreground child processes; no live providers or real git/knowledge actions. Update EXPECTED_RESULTS with commands, scenario names and expected results; replace its source-build advice with installed CLI target checks.

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

Receipt reuse must retain complete logs, final CLI outcomes and a new source-match report under E. Begin with `tmp/output-contract-d4-session-1/d4-codex-contracts/attempt-2/regressions-final/summary.json`, its sibling `regressions-final.log`, per-case commands/logs and copied bundles. Compare source membership and content for workflow, nodes, prompts and fixture, plus runner identity and scenario-generation inputs. Explain deliberate probe changes separately from source drift; JSON formatting alone is not behavioral drift. Compare EXPECTED_RESULTS with observed traces/counts. Retain hashes of the evidence and current files. Both prior runners renewed the original happy receipts, so do not pass `--happy-receipt` or build reuse support. If identity is missing or source changed, renew affected checks and document why. Direct Bun counts as behavioral evidence only with positive cases/assertions, zero failures, complete logs and successful final exit; builds/static-only checks do not substitute. Do not count nested completion as root success.

## Exact verification commands

Run from repository root, assigning E to the absolute runtime evidenceRoot/d4-codex-contracts/attempt-N path and creating it before execution. Capture each command separately with its true exit; do not mask failure with tee. The validate/run commands below are renewal commands only: reuse verified existing receipts first, and avoid a second happy run when the regression runner already produces it.

```sh
riela workflow validate fable-and-improve-codex --workflow-definition-dir packages/fable-and-improve-codex/workflows --output json
riela workflow run fable-and-improve-codex --workflow-definition-dir packages/fable-and-improve-codex/workflows --mock-scenario packages/fable-and-improve-codex/workflows/fable-and-improve-codex/mock-scenario.json --session-store "$E/happy/sessions" --artifact-root "$E/happy/artifacts" --output json
bun packages/fable-and-improve-codex/tests/check-output-contract.ts --evidence-root "$E/regressions"
git diff --check
```

Record validation receipt paths and source comparisons; renew only when needed. The regression runner already exercises the full happy path, so the standalone mock command is unnecessary when an accepted regression receipt covers it. If runner source changes, also run `bun build packages/fable-and-improve-codex/tests/check-output-contract.ts --target=bun --outfile "$E/check-output-contract.js"`; record exit and complete log as a syntax/build check, not behavioral evidence. No separate application typecheck applies to bundle JSON/prompts. Each renewed mock uses isolated stores under E. Record expected nonzero negative-case exits as successful assertions only after checking the intended schema diagnostic and absence of consumer execution.

## Acceptance and completion

All tasks above complete, 16/16 sandbox declarations, required producers covered without blanket additions, nonempty accepted commit fields, valid revision/knowledge branches, unchanged graph/settings, passing target validation and all 10 cases with complete logs and counts. No unresolved high/mid implementation finding. Package manifests and shared indexes remain untouched for serial reconciliation. Handoff exact changed files, immutable intent snapshots, pre/post hashes and evidence paths. A missing test or unrelated failure must be stated explicitly; do not mark passed.

## Progress log

Earlier entries below are immutable attempt history, not current blockers. The continuation status appended last supersedes their readiness conclusions.

- Plan authored after Step 3 acceptance; implementation not started.
- Tasks 1–6: pending. Verification: pending. Independent review: pending.
- Attempt 1: inspected 16 codex agents and payload consumers; added 13 missing sandboxes, three required schemas, conditional knowledge requirements, validation budgets, and matching happy-path mock fields. Changed node and mock files are snapshotted with per-edit intent under `tmp/output-contract-d4-session-1/d4-codex-contracts/attempt-1/edits/`.
- Installed `riela workflow validate fable-and-improve-codex --workflow-definition-dir packages/fable-and-improve-codex/workflows --output json` passed (exit 0; `validate.log`). Direct required mock run failed at `kb-recall-prior` with `policyBlocked: kaiba execution requires a resolved client` (exit 1; `happy.log`, complete runtime snapshot under `happy/artifacts`). This is an external Kaiba client prerequisite for the required full routing gate.
- Tasks still pending: ten-case Bun regression runner, EXPECTED_RESULTS update, direct happy-path and focused mock runs, final source-matched validation and self-check. No independent review, shared digest refresh, commit, or push has occurred. Resume when the installed Riela mock can execute Kaiba add-ons with a resolved client or an authorized deterministic mock adapter.
- Final-source evidence: `validate-final.log` exit 0; `static.log` 69/69 assertions passed, exit 0; `happy-final.log` exit 1 at the same unresolved Kaiba client prerequisite; `diff-check.log` exit 0. The mock blocker prevents the assigned behavioral matrix from completing.

- Continuation after Step 3 acceptance (`comm-000004`): tasks 1–5 previously implemented; verify preservation and repair only concrete defects. Corrected add-on fixtures resolve the former Kaiba blocker. Source-match/add-on-consumption verification, ten-case runner, EXPECTED_RESULTS and final worker self-check remain pending. Full retry receipt reports exit 0/18 root executions; this is not yet all-branch acceptance. Formal review and publication remain later gates.

- Attempt 2: preserved all prior Codex bundle edits. Added `tests/check-output-contract.ts` and updated `EXPECTED_RESULTS.md`; per-edit before/after hashes and intentions are under `tmp/output-contract-d4-session-1/d4-codex-contracts/attempt-2/edits/`. The old `tmp/d4-mock-retry-codex.jsonl` has no exact current-input source proof, so the runner executed a fresh happy path. `source-identity-final.json` confirms the fresh happy copy matches all 35 current bundle files by content (the mock JSON was reformatted in the copy) using installed Riela 0.1.55.
- Installed validation passed with exit 0 (`attempt-2/validate.log`). The final ten-case regression run passed 10/10 cases and 684 assertions with zero failures (`attempt-2/regressions-final.log`, `attempt-2/regressions-final/summary.json` and per-case `run.jsonl`/`command.json`). Happy root completed with exit 0/18 executions; revision completed 0/20; planning-only 0/17. Three malformed commit-message cases exited 1 as expected, showed `validationRejected` at the producer after two attempts, and never reached their Git consumer. Knowledge create, merge/archive, merge/no-archive and skip completed with observed payload/route assertions. Earlier partial attempts and their logs remain retained.
- Assigned implementation and behavioral verification are complete. Author self-check: final installed validation, post-edit TypeScript Bun build and `git diff --check` each exited 0 (`attempt-2/validate-final.log`, `bun-build-final.log`, `diff-check-final.log`). No high or mid implementation finding remains. Independent integrity/adversarial/integration review, shared digest/index work, exact-file commit and non-force push are downstream workflow steps and are not claimed here.

- Package 0.3.44 continuation plan update after accepted Step 3 (`comm-000004`): preserve all prior implementation and receipts. Branch tasks now source-check completed work; native join, independent reviews, final digest/index checks and publication remain pending. Historical progress entries remain unchanged. Current Step 5 plan review is pending.

- Step 6 continuation at checkpoint `b9d3263`: confirmed all 35 current Codex bundle files and the Bun runner match the retained attempt-2 source identity; `tmp/output-contract-d4-044-implementation/d4-codex-contracts/attempt-1/source-match.json` records hashes, probe differences and zero unexpected mismatches. The bundle implementation, EXPECTED_RESULTS and ten-case runner were preserved without source edits. Renewed installed-Riela validation exited 0 (`attempt-1/validate.log`). Renewed direct Bun regression exited 0 with 10/10 cases, 684 assertions and zero failures (`attempt-1/regressions.log`, `attempt-1/regressions/summary.json` and per-case logs). The happy root had 18 executions; revision and planning-only roots had 20 and 17. Malformed checkpoint and accepted completion messages were rejected at their producers, and create/merge/archive/skip knowledge routes passed. The plan-local intent and before snapshot for this progress edit are under `attempt-1/`. Assigned implementation and behavioral verification are complete with no high or mid self-check finding; formal reviews, shared digest/index checks and publication remain downstream.

- Step 8 completion-state review (issue `comm-000002`, workflow mode `issue-resolution`): assigned implementation and checklist verification are complete; test-integrity, Sol adversarial and Astra integration reviews accepted all three D4 plans without findings. Archived with the same plan ID and historical progress intact. Exact-file commit, non-force push and PR handoff remain downstream workflow publication steps.
