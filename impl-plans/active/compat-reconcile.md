# compat-reconcile

Status: proposed for Step 5 review.

```json
{
  "planId": "compat-reconcile",
  "planPath": "impl-plans/active/compat-reconcile.md",
  "dependsOn": [
    "compat-agent-contracts",
    "compat-assets",
    "compat-inheritance"
  ],
  "writePaths": [
    "packages/claude-code-adversarial-implementation-review-loop/riela-package.json",
    "packages/claude-code-deepdesign/riela-package.json",
    "packages/claude-code-design-and-implement-review-loop/riela-package.json",
    "packages/claude-code-goal/riela-package.json",
    "packages/claude-code-impl-plan-completion-loop/riela-package.json",
    "packages/claude-code-impl-plan-completion-review-loop/riela-package.json",
    "packages/claude-code-recent-change-quality-loop/riela-package.json",
    "packages/claude-code-refactoring-divide-and-conquer/riela-package.json",
    "packages/claude-code-refactoring-slice-review/riela-package.json",
    "packages/claude-code-simple-work-package/riela-package.json",
    "packages/claude-code-source-security-check-loop/riela-package.json",
    "packages/claude-code-task-watchdog/riela-package.json",
    "packages/claude-code-website-builder/riela-package.json",
    "packages/claude-code-worker-only-single-step/riela-package.json",
    "packages/codex-adversarial-implementation-review-loop/riela-package.json",
    "packages/codex-deep-creation/riela-package.json",
    "packages/codex-deepdesign/riela-package.json",
    "packages/codex-design-and-implement-review-loop/riela-package.json",
    "packages/codex-goal/riela-package.json",
    "packages/codex-impl-plan-completion-loop/riela-package.json",
    "packages/codex-impl-plan-completion-review-loop/riela-package.json",
    "packages/codex-recent-change-quality-loop/riela-package.json",
    "packages/codex-refactoring-divide-and-conquer/riela-package.json",
    "packages/codex-refactoring-slice-review/riela-package.json",
    "packages/codex-simple-work-package/riela-package.json",
    "packages/codex-source-security-check-loop/riela-package.json",
    "packages/codex-task-watchdog/riela-package.json",
    "packages/codex-website-builder/riela-package.json",
    "packages/cursor-cli-adversarial-implementation-review-loop/riela-package.json",
    "packages/cursor-cli-deepdesign/riela-package.json",
    "packages/cursor-cli-design-and-implement-review-loop/riela-package.json",
    "packages/cursor-cli-developer-workflows/riela-package.json",
    "packages/cursor-cli-fable-design-and-implement-review-loop/riela-package.json",
    "packages/cursor-cli-goal/riela-package.json",
    "packages/cursor-cli-hydra-claude-design-and-implement-review-loop/riela-package.json",
    "packages/cursor-cli-hydra-codex-design-and-implement-review-loop/riela-package.json",
    "packages/cursor-cli-impl-plan-completion-loop/riela-package.json",
    "packages/cursor-cli-impl-plan-completion-review-loop/riela-package.json",
    "packages/cursor-cli-recent-change-quality-loop/riela-package.json",
    "packages/cursor-cli-refactoring-divide-and-conquer/riela-package.json",
    "packages/cursor-cli-refactoring-slice-review/riela-package.json",
    "packages/cursor-cli-simple-work-package/riela-package.json",
    "packages/cursor-cli-source-security-check-loop/riela-package.json",
    "packages/cursor-cli-task-watchdog/riela-package.json",
    "packages/cursor-cli-website-builder/riela-package.json",
    "packages/fable-and-improve-codex/riela-package.json",
    "packages/fable-and-improve-opus/riela-package.json",
    "packages/fable-astra-design-plan-review-loop/riela-package.json",
    "packages/google-speech-to-text-addon/riela-package.json",
    "packages/greeting-container/riela-package.json",
    "packages/greeting-node-addon/riela-package.json",
    "packages/greeting-shell/riela-package.json",
    "packages/mp4-audio-extract-addon/riela-package.json",
    "packages/pdf-to-images-addon/riela-package.json",
    "packages/release-note-node-addon/riela-package.json",
    "packages/riela-package-installer-skill/riela-package.json",
    "packages/riela-package-manager-skill/riela-package.json",
    "packages/riela-package-release-skill/riela-package.json",
    "packages/riela-project-workflow-skill/riela-package.json",
    "packages/riela-temporary-workflow-skill/riela-package.json",
    "packages/riela-workflow-creator-skill/riela-package.json",
    "packages/riela-workflow-skill-creator-skill/riela-package.json",
    "packages/youtube-mp4-download-addon/riela-package.json",
    "packages/youtube-mp4-to-text-workflow/riela-package.json",
    "packages/youtube-shorts-to-text-container/riela-package.json",
    "registry-index.json",
    "README.md",
    "impl-plans/README.md"
  ],
  "sharedPaths": [
    "mise.toml",
    ".agents/skills/riela-package-release/scripts/check-package-compat.ts",
    ".agents/skills/riela-package-release/scripts/check-package-compat.test.ts",
    "packages/claude-code-worker-only-single-step/workflows/claude-code-worker-only-single-step",
    "packages/codex-adversarial-implementation-review-loop/workflows/codex-adversarial-implementation-review-loop",
    "packages/codex-deep-creation/workflows/codex-deep-creation",
    "packages/codex-deepdesign/workflows/codex-deepdesign",
    "packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop",
    "packages/codex-goal/workflows/codex-goal",
    "packages/codex-impl-plan-completion-loop/workflows/codex-impl-plan-completion-loop",
    "packages/codex-impl-plan-completion-review-loop/workflows/codex-impl-plan-completion-review-loop",
    "packages/codex-recent-change-quality-loop/workflows/codex-recent-change-quality-loop",
    "packages/codex-refactoring-divide-and-conquer/workflows/codex-refactoring-divide-and-conquer",
    "packages/codex-refactoring-slice-review/workflows/codex-refactoring-slice-review",
    "packages/codex-simple-work-package/workflows/codex-simple-work-package",
    "packages/codex-source-security-check-loop/workflows/codex-source-security-check-loop",
    "packages/codex-task-watchdog/workflows/codex-task-watchdog",
    "packages/codex-website-builder/workflows/codex-website-builder",
    "packages/cursor-cli-developer-workflows/workflows/cursor-cli-developer-workflows",
    "packages/fable-and-improve-codex/workflows/fable-and-improve-codex",
    "packages/fable-and-improve-opus/workflows/fable-and-improve-opus",
    "packages/fable-astra-design-plan-review-loop/workflows/fable-astra-design-plan-review-loop",
    "packages/greeting-container/workflows/greeting-container",
    "packages/greeting-shell/workflows/greeting-shell",
    "packages/riela-package-installer-skill/workflows/riela-package-installer-skill",
    "packages/riela-package-manager-skill/workflows/riela-package-manager-skill",
    "packages/riela-package-release-skill/workflows/riela-package-release-skill",
    "packages/riela-project-workflow-skill/workflows/riela-project-workflow-skill",
    "packages/riela-temporary-workflow-skill/workflows/riela-temporary-workflow-skill",
    "packages/riela-workflow-creator-skill/workflows/riela-workflow-creator-skill",
    "packages/riela-workflow-skill-creator-skill/workflows/riela-workflow-skill-creator-skill",
    "packages/youtube-mp4-to-text-workflow/workflows/youtube-mp4-to-text",
    "packages/youtube-shorts-to-text-container/workflows/youtube-shorts-to-text-container",
    "packages/claude-code-worker-only-single-step/tests",
    "packages/codex-adversarial-implementation-review-loop/tests",
    "packages/codex-deep-creation/tests",
    "packages/codex-deepdesign/tests",
    "packages/codex-design-and-implement-review-loop/tests",
    "packages/codex-goal/tests",
    "packages/codex-impl-plan-completion-loop/tests",
    "packages/codex-impl-plan-completion-review-loop/tests",
    "packages/codex-recent-change-quality-loop/tests",
    "packages/codex-refactoring-divide-and-conquer/tests",
    "packages/codex-refactoring-slice-review/tests",
    "packages/codex-simple-work-package/tests",
    "packages/codex-source-security-check-loop/tests",
    "packages/codex-task-watchdog/tests",
    "packages/codex-website-builder/tests",
    "packages/cursor-cli-developer-workflows/tests",
    "packages/fable-and-improve-codex/tests",
    "packages/fable-and-improve-opus/tests",
    "packages/fable-astra-design-plan-review-loop/tests",
    "packages/greeting-container/tests",
    "packages/greeting-shell/tests",
    "packages/riela-package-installer-skill/tests",
    "packages/riela-package-manager-skill/tests",
    "packages/riela-package-release-skill/tests",
    "packages/riela-project-workflow-skill/tests",
    "packages/riela-temporary-workflow-skill/tests",
    "packages/riela-workflow-creator-skill/tests",
    "packages/riela-workflow-skill-creator-skill/tests",
    "packages/youtube-mp4-to-text-workflow/tests",
    "packages/youtube-shorts-to-text-container/tests",
    "packages/claude-code-adversarial-implementation-review-loop/README.md",
    "packages/claude-code-deepdesign/README.md",
    "packages/claude-code-design-and-implement-review-loop/README.md",
    "packages/claude-code-design-and-implement-review-loop/skills",
    "packages/claude-code-goal/README.md",
    "packages/claude-code-impl-plan-completion-loop/README.md",
    "packages/claude-code-impl-plan-completion-review-loop/README.md",
    "packages/claude-code-recent-change-quality-loop/README.md",
    "packages/claude-code-refactoring-divide-and-conquer/README.md",
    "packages/claude-code-refactoring-slice-review/README.md",
    "packages/claude-code-simple-work-package/README.md",
    "packages/claude-code-source-security-check-loop/README.md",
    "packages/claude-code-source-security-check-loop/skills",
    "packages/claude-code-task-watchdog/README.md",
    "packages/claude-code-task-watchdog/skills",
    "packages/claude-code-website-builder/README.md",
    "packages/claude-code-worker-only-single-step/README.md",
    "packages/codex-adversarial-implementation-review-loop/README.md",
    "packages/codex-deep-creation/README.md",
    "packages/codex-deepdesign/README.md",
    "packages/codex-design-and-implement-review-loop/README.md",
    "packages/codex-design-and-implement-review-loop/skills",
    "packages/codex-goal/README.md",
    "packages/codex-impl-plan-completion-loop/README.md",
    "packages/codex-impl-plan-completion-review-loop/README.md",
    "packages/codex-recent-change-quality-loop/README.md",
    "packages/codex-refactoring-divide-and-conquer/README.md",
    "packages/codex-refactoring-slice-review/README.md",
    "packages/codex-simple-work-package/README.md",
    "packages/codex-source-security-check-loop/README.md",
    "packages/codex-source-security-check-loop/skills",
    "packages/codex-task-watchdog/README.md",
    "packages/codex-task-watchdog/skills",
    "packages/codex-website-builder/README.md",
    "packages/cursor-cli-adversarial-implementation-review-loop/README.md",
    "packages/cursor-cli-deepdesign/README.md",
    "packages/cursor-cli-design-and-implement-review-loop/README.md",
    "packages/cursor-cli-design-and-implement-review-loop/skills",
    "packages/cursor-cli-developer-workflows/README.md",
    "packages/cursor-cli-developer-workflows/skills",
    "packages/cursor-cli-fable-design-and-implement-review-loop/README.md",
    "packages/cursor-cli-goal/README.md",
    "packages/cursor-cli-hydra-claude-design-and-implement-review-loop/README.md",
    "packages/cursor-cli-hydra-codex-design-and-implement-review-loop/README.md",
    "packages/cursor-cli-impl-plan-completion-loop/README.md",
    "packages/cursor-cli-impl-plan-completion-review-loop/README.md",
    "packages/cursor-cli-recent-change-quality-loop/README.md",
    "packages/cursor-cli-refactoring-divide-and-conquer/README.md",
    "packages/cursor-cli-refactoring-slice-review/README.md",
    "packages/cursor-cli-simple-work-package/README.md",
    "packages/cursor-cli-source-security-check-loop/README.md",
    "packages/cursor-cli-source-security-check-loop/skills",
    "packages/cursor-cli-task-watchdog/README.md",
    "packages/cursor-cli-task-watchdog/skills",
    "packages/cursor-cli-website-builder/README.md",
    "packages/fable-and-improve-codex/README.md",
    "packages/fable-and-improve-codex/skills",
    "packages/fable-and-improve-opus/README.md",
    "packages/fable-and-improve-opus/skills",
    "packages/fable-astra-design-plan-review-loop/README.md",
    "packages/fable-astra-design-plan-review-loop/skills",
    "packages/google-speech-to-text-addon/README.md",
    "packages/google-speech-to-text-addon/addons",
    "packages/google-speech-to-text-addon/skills",
    "packages/greeting-container/README.md",
    "packages/greeting-node-addon/README.md",
    "packages/greeting-node-addon/addons",
    "packages/greeting-shell/README.md",
    "packages/mp4-audio-extract-addon/README.md",
    "packages/mp4-audio-extract-addon/addons",
    "packages/pdf-to-images-addon/README.md",
    "packages/pdf-to-images-addon/addons",
    "packages/release-note-node-addon/README.md",
    "packages/release-note-node-addon/addons",
    "packages/riela-package-installer-skill/README.md",
    "packages/riela-package-installer-skill/skills",
    "packages/riela-package-manager-skill/README.md",
    "packages/riela-package-manager-skill/skills",
    "packages/riela-package-release-skill/README.md",
    "packages/riela-package-release-skill/skills",
    "packages/riela-project-workflow-skill/README.md",
    "packages/riela-project-workflow-skill/skills",
    "packages/riela-temporary-workflow-skill/README.md",
    "packages/riela-temporary-workflow-skill/skills",
    "packages/riela-workflow-creator-skill/README.md",
    "packages/riela-workflow-creator-skill/skills",
    "packages/riela-workflow-skill-creator-skill/README.md",
    "packages/riela-workflow-skill-creator-skill/skills",
    "packages/youtube-mp4-download-addon/README.md",
    "packages/youtube-mp4-download-addon/addons",
    "packages/youtube-mp4-to-text-workflow/README.md",
    "packages/youtube-shorts-to-text-container/README.md",
    "packages/claude-code-adversarial-implementation-review-loop/workflows/claude-code-adversarial-implementation-review-loop",
    "packages/claude-code-deepdesign/workflows/claude-code-deepdesign",
    "packages/claude-code-design-and-implement-review-loop/workflows/claude-code-design-and-implement-review-loop",
    "packages/claude-code-goal/workflows/claude-code-goal",
    "packages/claude-code-impl-plan-completion-loop/workflows/claude-code-impl-plan-completion-loop",
    "packages/claude-code-impl-plan-completion-review-loop/workflows/claude-code-impl-plan-completion-review-loop",
    "packages/claude-code-recent-change-quality-loop/workflows/claude-code-recent-change-quality-loop",
    "packages/claude-code-refactoring-divide-and-conquer/workflows/claude-code-refactoring-divide-and-conquer",
    "packages/claude-code-refactoring-slice-review/workflows/claude-code-refactoring-slice-review",
    "packages/claude-code-simple-work-package/workflows/claude-code-simple-work-package",
    "packages/claude-code-source-security-check-loop/workflows/claude-code-source-security-check-loop",
    "packages/claude-code-task-watchdog/workflows/claude-code-task-watchdog",
    "packages/claude-code-website-builder/workflows/claude-code-website-builder",
    "packages/cursor-cli-adversarial-implementation-review-loop/workflows/cursor-cli-adversarial-implementation-review-loop",
    "packages/cursor-cli-deepdesign/workflows/cursor-cli-deepdesign",
    "packages/cursor-cli-design-and-implement-review-loop/workflows/cursor-cli-design-and-implement-review-loop",
    "packages/cursor-cli-fable-design-and-implement-review-loop/workflows/cursor-cli-fable-design-and-implement-review-loop",
    "packages/cursor-cli-goal/workflows/cursor-cli-goal",
    "packages/cursor-cli-hydra-claude-design-and-implement-review-loop/workflows/cursor-cli-hydra-claude-design-and-implement-review-loop",
    "packages/cursor-cli-hydra-codex-design-and-implement-review-loop/workflows/cursor-cli-hydra-codex-design-and-implement-review-loop",
    "packages/cursor-cli-impl-plan-completion-loop/workflows/cursor-cli-impl-plan-completion-loop",
    "packages/cursor-cli-impl-plan-completion-review-loop/workflows/cursor-cli-impl-plan-completion-review-loop",
    "packages/cursor-cli-recent-change-quality-loop/workflows/cursor-cli-recent-change-quality-loop",
    "packages/cursor-cli-refactoring-divide-and-conquer/workflows/cursor-cli-refactoring-divide-and-conquer",
    "packages/cursor-cli-refactoring-slice-review/workflows/cursor-cli-refactoring-slice-review",
    "packages/cursor-cli-simple-work-package/workflows/cursor-cli-simple-work-package",
    "packages/cursor-cli-source-security-check-loop/workflows/cursor-cli-source-security-check-loop",
    "packages/cursor-cli-task-watchdog/workflows/cursor-cli-task-watchdog",
    "packages/cursor-cli-website-builder/workflows/cursor-cli-website-builder"
  ],
  "progressFile": "tmp/registry-contract-migration/verification/compat-reconcile/progress.json",
  "verification": [
    "bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts --all --check",
    "bun .agents/skills/riela-package-release/scripts/update-package-digests.ts --all",
    "mise run package:generate-index",
    "mise run package:check-digests",
    "mise run package:check-addon-digests",
    "mise run package:check-index",
    "bun test .agents/skills/riela-package-release/scripts/check-package-compat.test.ts",
    "mise run check",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/scenarios",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/assets",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "All package manifests and effective workflows pass installed 0.2.1 validation with dependencies.",
    "Relevant behavioral/package tests pass; each permitted residual check failure is reproduced and separately tracked.",
    "Combined hashes preserve all worker intent; versions/digests/index are consistent.",
    "Review-ready exact file set and release evidence are complete; final commit/push remain explicit later gates."
  ]
}
```

## Intent, context and non-goals

Resolve https://github.com/tacogips/riela-packages/issues/14 in `issue-resolution` mode using accepted `design-docs/specs/design-riela-021-package-compat.md` (Step 3 accepted, comm-000004, no findings). All packages are in scope; the intake's 39 failures are a diagnostic cohort, not an inventory limit. `codexAgentReferences: []`; preserve existing Cursor/Claude wrapper adaptations rather than introducing adapters. Issue title/body were unavailable; do not infer #114 from scratch directory names.

Use installed Riela 0.2.1 on `fix/registry-contract-migration`. Do not inspect the running workflow's registry/provenance, change sibling repositories, create worktrees/private branches, run concurrent Git mutations, release or merge. No graph/model/session redesign, broad formatting, vacuous schemas, permission escalation for review-only agents or unrelated cleanup. Review existing subtree AGENTS.md before editing. Do not modify unrelated D4 records.

## Execution, drift and progress contract

This plan and the accepted design are checkpointed with the dispatch manifest by the later Riela checkpoint step before native fanout; this authoring step does not commit. Wait for every dependsOn plan's accepted output. All workers share this branch and directory. Write only the listed paths; only the reconciliation plan may repair shared paths after all other workers join. Do not edit this plan or another worker's progress log during execution.

Before each edit, freshly read the file and consumers. Save its bytes and SHA-256 plus an immutable intent record naming the requirement, proposed fields and expected behavior in your own evidence directory under `attempt-N/intent/`. Recheck the hash immediately before writing; on drift, re-read and reconcile the intended patch instead of overwriting. Save post-edit bytes/hash, exact changed paths and tests tied to those hashes. Check hashes again at handoff. Record any mismatch and pause the conflicting edit for serial reconciliation; never discard another worker's change. This detects non-atomic overwrite races but does not pretend to prevent them.

Use a new attempt directory; preserve old receipts. Maintain your own `progress.json` with task IDs, pending/running/passed/blocked status, source hashes, changed paths, exact argv/cwd, final exit, complete log path, case/assertion counts, findings and next action. Also write `handoff.json` with requirements-to-files/tests mapping, remaining failures, review decision and post-hashes. Run commands foreground; poll yielded processes until exit. Capture stdout/stderr without losing the command exit. `git diff --check` supplements behavioral checks, never substitutes for them.

Do not regenerate manifests, versions, dependency locks or registry-index.json in a parallel payload worker. Do not archive plans or run git add/commit/push in any worker. Serial finalization prepares an exact file list for Riela publication steps. Every changed input invalidates affected verification and review receipts.

## Shared invariants and evidence rules

Preserve agent output envelope routing (`when`) separately from business `payload` schemas. Trace consumed fields through forwarding add-ons and cross-workflow calls; do not require an agent to invent a later add-on's Git result. Require concrete prompt-compatible types and branch-aware required fields. Keep legitimate failure/revision/planning/skip outputs valid. Use read-only for JSON-only reviews/reporting and workspace-write for file writers; justify any existing broader authority individually. Preserve routing, models, backend overrides and session policy unless a proven compatibility defect demands a scoped correction.

All evidence, catalogs, installations, session stores and artifacts stay under repository-root `tmp/registry-contract-migration/verification/`. Record tool versions and source identity. Assert mock terminal state, observed payloads and branch traces, not fixture intent or CLI exit alone. Mocks do not prove actual sandbox enforcement. If mocks bypass schema rejection, use a supported installed validation entry point and state coverage limits. Missing dependencies/network and incomplete logs are blocked checks, not passes. Only independently reproduced and separately tracked pre-existing failures may remain at delivery.

## Ordered tasks and deliverables

1. Join every handoff and compare current file hashes to worker post-hashes and immutable intent snapshots. Repair any overwritten requirement serially with fresh reads; document each drift and its chosen resolution. Review complete combined diff and rerun every affected check. Shared writePaths are repair authority only, not permission for optional refactoring. Reconcile package/producer coverage matrices so no package or changed producer lacks an owner/result.
2. Apply concrete manifest corrections requested by workers. Bump changed package versions according to existing version policy; review effective wrapper impact and update necessary version/dependency pins. For each source-changed add-on run `bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts <package-directory-id>` with the recorded exact ID, recomputing its content digest and synchronized dependency locks FIRST, then package checksum/integrity for all affected packages, then registry-index.json. Use --all digest refresh only after recording the affected set and review every unexpected change. Update root/package README metadata only where displayed information changes; preserve package inventory.
3. Run full `mise run check` and focused suites on final source. A failure is not waived unless reproduced at intake HEAD in the isolated baseline copy with the same effective inputs/command, exact final exit/log comparison and a separately tracked issue reference. Record baseline tool gaps honestly; they do not prove pre-existence. New or unexplained failures block delivery. If a tracked residual issue must be created, hand the concrete report to the authorized workflow publication/control step; do not fabricate a URL.
4. Run structural/typechecking required by changed TS/Python/add-on code using its existing configured checks; Bun tests alone are not a claimed static typecheck. Do not introduce a TypeScript project solely for this migration. Repeat package-specific behavioral regressions and all relevant scenario cases after repairs/metadata updates as needed; report unchanged input evidence reuse explicitly.
5. Write `release-evidence.json` containing every package disposition, changed versions/digests, validation results, all exact logs/exits/counts, baseline comparisons, unresolved findings and review source hashes. Prepare exact intended commit paths and a safety-reviewed diff. Update impl-plans/README.md to list this migration's plan status; global plan archiving remains a later completion-step operation, not a payload-worker action.
6. Hand off for independent test-integrity/adversarial/integration review. Only when no high/mid findings remain, Riela later completion/publication steps archive these plans if appropriate, commit the reviewed design/plans/payloads/metadata and non-force push `origin fix/registry-contract-migration`. They must report resulting commit and push result. This worker does not run Git mutations, release, merge, or claim publication is already complete.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts --all --check
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts --all
mise run package:generate-index
mise run package:check-digests
mise run package:check-addon-digests
mise run package:check-index
bun test .agents/skills/riela-package-release/scripts/check-package-compat.test.ts
mise run check
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/scenarios
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/assets
git diff --check
```

## Completion criteria

- All package manifests and effective workflows pass installed 0.2.1 validation with dependencies.
- Relevant behavioral/package tests pass; each permitted residual check failure is reproduced and separately tracked.
- Combined hashes preserve all worker intent; versions/digests/index are consistent.
- Review-ready exact file set and release evidence are complete; final commit/push remain explicit later gates.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.
