# d4-reconcile-verify: serial integration and release evidence

```json
{
  "planId": "d4-reconcile-verify",
  "planPath": "impl-plans/active/d4-reconcile-verify.md",
  "dependsOn": [
    "d4-opus-contracts",
    "d4-codex-contracts"
  ],
  "writePaths": [
    "packages/fable-and-improve-opus/riela-package.json",
    "packages/fable-and-improve-codex/riela-package.json",
    "registry-index.json",
    "impl-plans/active/d4-reconcile-verify.md"
  ],
  "sharedPaths": [
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
    "packages/fable-and-improve-codex/tests/check-output-contract.ts"
  ]
}
```

## Intent, authority and limits

Workflow mode: `issue-resolution`. Issue repository: `tacogips/riela-packages`; title: “Migrate fable-and-improve bundles to the agent-node output contract”; number/URL: not supplied. Step 3 accepted the design without findings. Source of truth: `design-docs/specs/design-fable-output-contract-d4.md` and its linked user-QA. No codex-agent reference input, Cursor mapping or intentional reference divergence applies.

Riela core already implements the contract. Modify only the named package artifacts to preserve behavior under mandatory sandboxes and required producer schemas. Do not edit Riela core, unrelated packages, the dirty main checkout, other worktrees, models/backends/effort/session policies, workflow routing/fanout, or Git add-on behavior. Do not create the absent `packages/fable-and-improve` package. Its scope question remains in user-QA; do not mark three-package acceptance satisfied. Do not rediscover the executing workflow's registry/provenance. No release publication, new abstraction or cleanup work.

## Shared-workspace execution and evidence

The checkpoint step must commit the accepted design, all three plans and dispatch manifest before implementation fanout. Work on the existing `feat/output-contract-d4` branch and worktree; no worker Git mutation, private branches or worktrees. Treat checkpointCommit and this run's evidenceRoot from runtime input as authoritative. Each plan owns only its listed paths and progress file. Shared indexes, manifests and global plan archiving belong to serial reconciliation/finalization.

Before EACH edit, freshly read the path and compare SHA-256 with the last recorded version. Save immutable before/after contents and hashes under evidenceRoot/planId/attempt-N; use unique filenames, never replace snapshots. Before first edit also save accepted plan/design intent and a baseline file inventory. Missing files have an explicit absent marker. Compare completed intended edits against fresh contents before handoff and again after the join. Native fanout change tracking is additional evidence, not permission to overwrite drift. If another writer changed a path, preserve both versions and report drift; serial reconciliation repairs only the lost intended edits after all workers stop. Never restore a whole old file blindly.

Run all shell/verification commands in foreground. Retain/poll yielded sessions through exit. For each command record exact expanded argv, cwd, complete stdout/stderr log, final exit, test/scenario/assertion count and observed session result. Keep scratch, logs, caches and isolated mock state under the worktree's tmp/. Use a unique evidenceRoot/planId/attempt-N directory (E below); do not share mock stores between scenarios or attempts. A truncated log, missing exit or missing assertion is not a pass. Progress goes only in this plan's Progress log; report task statuses, changed paths, commands, logs, counts, findings and residual gaps. Do not mark later review/commit/push gates complete from a worker.

## Dependencies and task order

Start only after d4-opus-contracts and d4-codex-contracts have finished and their independent branch reviews have accepted. All writers must have stopped. This plan is the sole owner of manifests and generated index. Its sharedPaths permit scoped lost-edit/contract repairs in the two completed bundles, not unrelated changes. Never modify another worker's progress log.

1. Compare every worker's accepted intent and immutable after-hashes with the actual tree. Resolve drift serially, retaining both old evidence and new repair evidence. Recheck all 32 agent declarations, required producers, unchanged graphs/models and branch contracts. Rerun affected tests after repairs; preserve the review basis for combined adversarial review.
2. Run both package regression runners and installed target validation on the combined tree. Update only affected EXPECTED_RESULTS if final behavior/evidence differs. Save commands, scenario counts, complete logs and exits. Package tests are the regression deliverables; do not build a second general test framework.
3. Refresh the two package manifest digests using established tooling after final payload edits. Check generated registry-index consistency, regenerate only if these manifests require it, and inspect the diff to reject unrelated index changes. Do not bump unrelated versions or refresh unrelated package digests to silence baseline failures.
4. Run repository checks. The repository's `mise run check` uses Swift source builds that may write outside this worktree. Prefer the explicit component equivalents below using installed Riela for read-only local package validation and combined-catalog workflow validation; record this substitution instead of claiming literal mise run check passed. Keep all temporary catalogs, mock stores and caches under E. No source checkout builds or registry lookups are needed. Do not alter mise.toml or shared check scripts for this migration.
5. Prepare exact reviewed-file and verification handoff for the independent combined-tree adversarial reviewer. Report third-package scope unresolved until an explicit user decision/source resolves it; do not manufacture a third implementation plan. No unresolved material finding may be described as accepted. Review acceptance and final Git operations belong to later owning workflow steps.

## Exact verification commands

From repository root, E is the absolute evidenceRoot/d4-reconcile-verify/attempt-N directory. Set TMPDIR to an existing E/tmp directory and PYTHONPYCACHEPREFIX to E/pycache for checks that create temp/cache files. Record expanded values and complete logs. Installed RIELA_BIN is the path returned by `command -v riela`.

```sh
riela workflow validate fable-and-improve-opus --workflow-definition-dir packages/fable-and-improve-opus/workflows --output json
riela workflow validate fable-and-improve-codex --workflow-definition-dir packages/fable-and-improve-codex/workflows --output json
bun packages/fable-and-improve-opus/tests/check-output-contract.ts --evidence-root "$E/opus"
bun packages/fable-and-improve-codex/tests/check-output-contract.ts --evidence-root "$E/codex"
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve-opus fable-and-improve-codex
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve-opus fable-and-improve-codex --dry-run
bun .agents/skills/riela-package-release/scripts/generate-registry-index.ts --check
```

If index check fails specifically from these manifests, run `bun .agents/skills/riela-package-release/scripts/generate-registry-index.ts`, review its exact diff and rerun `--check`. Repository component checks:

```sh
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts --all --dry-run
bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts --all --check
bun .agents/skills/riela-package-release/scripts/generate-registry-index.ts --check
bun .agents/skills/riela-package-release/scripts/container-image-matrix.ts --check
bun .agents/skills/riela-package-release/scripts/check-compact-workflows.ts
python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'
git diff --check
```

Continue independent component checks after a failure so the result identifies all actual gaps. For package/workflow validation equivalents, enumerate local repository files only. For every `packages/*/riela-package.json`, run installed `riela package install <directory-basename> --source <package-directory> --dry-run --no-dependencies --output json`. This validates repository payloads; it is not current-workflow provenance lookup. Record each actual argv and exit. Copy each `packages/*/workflows/*` directory into E/catalog, failing explicitly on duplicate names instead of silently overwriting; for each concrete catalog bundle run `riela workflow validate <bundle-name> --workflow-definition-dir "$E/catalog" --output json`. Record validated/skipped/failed counts and reasons. This reproduces cross-workflow visibility without modifying sources. If an installed CLI option is unsupported, record its actual diagnostic and the blocked check; do not assume success or invoke a mutable registry. Global checks may expose unrelated baseline defects; report exact paths and exits and keep scope bounded.

The component equivalents above replace only execution plumbing, not omitted coverage. Broad-suite failures are not passing acceptance and require an explicit disposition at review. No source typecheck is required for the bundle declaration change; both Bun regression runners and existing repository tests must execute successfully.

## Completion and finalization handoff

- Both required upstream plan deliverables survive in the joined tree and independent branch reviews are recorded.
- Combined target validation passes; 10 cases per package (20 total minimum) and static invariants pass with actual counts, session evidence and complete logs. Negative cases prove rejection at producers. All required repository checks have results; unresolved failures/gaps prevent an unqualified completion claim.
- Both manifest checksum/integrity values and derived index verify after the last payload edit.
- Combined independent adversarial review has no unresolved high/mid finding before final commit/push.
- Third-package source question remains explicit; this plan cannot mark the three-package criterion met without resolution.
- Later serial completion step archives completed plans under impl-plans/completed/ using the same filenames, while incomplete/blocked plans remain active. There is no existing impl-plans index, so do not invent one. No worker archives plans or performs Git mutation.
- Later Git owner verifies branch feat/output-contract-d4 and exact reviewed paths, preserves unrelated state, commits only reviewed files and pushes non-force to origin feat/output-contract-d4. Prepare a PR with scope, actual verification, any unresolved third-package limitation and no fabricated issue link. Never touch the dirty main checkout or reset another session's changes.

## Progress log

- Plan authored after Step 3 acceptance; implementation not started.
- Tasks 1–5: pending. Combined checks, digest refresh and independent review: pending.
