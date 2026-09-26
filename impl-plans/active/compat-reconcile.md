# compat-reconcile

Status: proposed for Step 5 review.

```json
{
  "planId": "compat-reconcile",
  "planPath": "impl-plans/active/compat-reconcile.md",
  "dependsOn": [
    "compat-agent-contracts",
    "compat-agent-contracts-supporting",
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
    ".agents/skills/riela-package-release/fixtures/expected-routes.json",
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
  "progressFile": "tmp/registry-contract-migration/verification/compat-reconcile/continuation-3ec4863/attempt-1/progress.json",
  "verification": [
    "\"$RIELA_COMPAT_CLI\" --version",
    "shasum -a 256 \"$RIELA_COMPAT_CLI\"",
    "bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts --all --check",
    "bun .agents/skills/riela-package-release/scripts/update-package-digests.ts --all",
    "mise run package:generate-index",
    "mise run package:check-digests",
    "mise run package:check-addon-digests",
    "mise run package:check-index",
    "bun test ./.agents/skills/riela-package-release/scripts/check-package-compat.test.ts",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode manifests --evidence-root \"$COMPAT_ATTEMPT/manifests\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root \"$COMPAT_ATTEMPT/workflows\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --evidence-root \"$COMPAT_ATTEMPT/scenarios\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root \"$COMPAT_ATTEMPT/assets\"",
    "mise run check",
    "git diff --check",
    "mise run package:validate",
    "mise run workflow:validate",
    "mise run workflow:check-compact",
    "mise run workflow:check-codex-dispatch",
    "\"$RIELA_COMPAT_CLI\" workflow validate <each of the 75 listed workflow IDs> --workflow-definition-dir \"$COMPAT_ATTEMPT/core-examples/catalog\" --output json"
  ],
  "acceptanceCriteria": [
    "All 65 package manifests and 59 effective workflows pass supplied corrected CLI validation/inspection with resolved dependencies; all required final checks pass.",
    "Relevant behavioral/package tests pass; no required residual check failure is permitted at final acceptance.",
    "Combined hashes preserve all worker intent; versions/digests/index are consistent.",
    "Review-ready exact file set and release evidence are complete; final commit/push remain explicit later gates.",
    "Owned source verification passes; later-wave failures retain exact evidence and assigned repair owners. Final reconciliation permits no historical #117 waiver or unresolved required check.",
    "Each applicable package-local behavioral command has its own actual exitCode, positive passing test count and complete logPath; no combined prose/semicolon evidence.",
    "All 75 listed core examples have individual passing validation receipts; deterministic packaged examples retain outcome assertions."
  ]
}
```

## Intent, context and non-goals

Continue https://github.com/tacogips/riela-packages/issues/14 from `3ec4863c61bec4d65e52c2410cf086183882c0f3` on `fix/registry-contract-migration` for Draft PR #15 in `issue-resolution` mode. Step 3 comm-000004 accepted `design-docs/specs/design-riela-021-package-compat.md` with no findings. Preserve all five plans and checkpointed source work. Scope remains 65 packages, 59 workflows, deterministic packaged examples and validation evidence for all 75 Riela core examples. Reassess the three previously accepted first-wave plans with the supplied corrected CLI, preserving 14 Codex/four supporting mocks, two fixtures, asset audit, historical YouTube closure (`e9b5869`) and all prior failures. Their old aggregate exit 1 and the 24-wrapper/48-command failure cohort are historical, not current failures. Core fix `6844d28` in https://github.com/tacogips/riela/pull/121 resolves inherited bases from the explicit catalog first; the old child's field-loss diagnosis does not justify wrapper duplication. Effective input establishes workflow package `0.3.46` as correcting integration-review recoveryDiagnostic dispatch. No orchestration repair or provenance rediscovery is required.

`codexAgentReferences: []`. Preserve Cursor/Claude adaptations in existing extends patches/replacement maps, including backend/model overrides. No reference checkout or new adapters. No graph/model/session redesign, broad formatting, new frameworks, unrelated cleanup, live providers, release or merge to main. Do not change sibling repositories or rediscover the running workflow's registry/provenance. Runtime input is authoritative. Do not create worktrees/private branches or perform concurrent Git operations. Read applicable subtree AGENTS.md before editing. Preserve unrelated D4 records.

## Completed prerequisite and CLI setup

`compat-verification` remains completed prerequisite evidence (historical 17/17 accepted regressions); never redispatch its implementation. Preserve old receipts and prior progress. The contract split already exists; continue the five existing owners. Run required checks in the foreground from repository root, retaining terminal handles through exit. Record actual executable version/hash, exact argv/cwd, source hashes, final exit and complete stdout/stderr logs. No zero-test, truncated-log or missing-command result is a pass.

Use this package-check executable exactly; runtime-resolved orchestration provenance is authoritative and independent of package-payload verification:

```sh
export RIELA_COMPAT_CLI=/Users/taco/gits/tacogips/riela-worktrees/direct-inheritance-catalog/.build/debug/riela
export RIELA_BIN="$RIELA_COMPAT_CLI"
"$RIELA_COMPAT_CLI" --version
shasum -a 256 "$RIELA_COMPAT_CLI"
```

Set `COMPAT_ATTEMPT` to the absolute repository root plus `tmp/registry-contract-migration/verification/compat-reconcile/continuation-3ec4863/attempt-1`; if it already exists use the next unused attempt number and record the effective progressFile. Preserve the prior canonical progress log as historical evidence. Create `bin/riela` there as a symlink to `$RIELA_COMPAT_CLI`, prepend that bin directory to PATH and record `command -v riela` plus its resolved target so subprocesses use the same corrected CLI. Do not overwrite previous attempts, change HOME, build core or silently substitute a binary. Missing executables block dependent checks only. Canonical command paths below must be expanded consistently to the new attempt path and recorded in `commands.json`.

## Continuation and failure accounting

Existing workflows-mode receipts at `tmp/registry-contract-migration/verification/direct-inheritance-catalog-1/commands.json` and `coverage.json` contain 65 inventory packages, 59 workflows and 118 validate/inspect passes (126 command receipts, all exit 0). Record a `reassessment.json` mapping prior receipts to the new CLI/source identities, reused or rerun checks and current status. Compare source/tool hashes, dependencies, arguments and complete logs before reuse; historical HEAD alone does not invalidate source-matched evidence. This receipt is not evidence of manifest, scenario or core-example completion. Old-CLI results remain historical even if the source is unchanged; rerun applicable behavioral commands affected by the CLI change. Reconciliation reruns required final combined-tree checks after payload/metadata updates. Preserve old aggregate exit 1 records verbatim; never carry them forward as current failures or rewrite them as zero.

Riela https://github.com/tacogips/riela/issues/117 is the related fix reference, not a presumed outstanding blocker or acceptance waiver. Diagnose fresh failures using the supplied corrected CLI. Keep failing commands in `verification` with their nonzero exits; preserve historical comparisons in `baselineDiagnostics`. Use `externalBlockers` only for newly demonstrated external defects with exact command/log/exit evidence. Every reported command failure relevant to this owner must map to a workflow, diagnosis, owner and final result in `failure-accounting.json`; never discard inventory entries, weaken validation or convert aggregate failure to success.

An earlier wave may finish its owned source tasks while documented later-wave repairs remain pending: assign each pending wrapper defect to compat-inheritance and each manifest/dependency-lock defect to compat-reconcile, with exact paths and field-level intent. An owned contract failure or missing owned material verification blocks that owner. Full-catalog aggregate failures remain failed even when an owner's individual checks pass. The final reconciliation gate requires all requested checks passing; a historical failure or baseline reproduction grants no exception. This permits dependency-ready progress without claiming compatibility completion early.

Reuse receipts only after matching audited file hashes, CLI hash/version, dependencies, effective arguments, final exit and complete logs; record comparisons and original receipt paths. If mismatch or incomplete, rerun affected checks. Baseline copies, if needed, use checkpoint 3ec4863 under repository tmp; no extra worktrees. Preserve the two checkpointed fixtures and all existing route assertions. The 12 fixtureless supporting workflows require validate/inspect receipts, never a manufactured scenario requirement. All packaged examples require deterministic checks or explicit static invocation/asset coverage where live execution is excluded. Serial reconciliation additionally records validation for each of the 75 core examples; static audits cannot replace those validation results.

Formal independent reviews, checkpoint/publication and final commit/push are later Riela gates. Step 6 completion covers assigned source tasks and their verification, not those later gates. Report source status and final-verification status separately. No unresolved high/mid owned finding is complete; no final acceptance while required checks fail or are blocked.

Earlier evidence-format failures remain historical. The latest integration-review dispatch stop is resolved by package 0.3.46 per effective input. For EVERY package-local behavioral command, write a separate `verification` record containing the exact command/cwd, actual numeric `exitCode`, positive `testsRun` or `testCount` for a passing behavioral check, complete `logPath`, and source/CLI hashes. Copy only source-matched complete receipts or rerun the command. Do not use a prose summary, semicolon-combined command, assumed zero exit, or aggregate test count. Preserve nonzero results until a separately recorded rerun passes. Keep whole-catalog failures as separate nonzero records assigned to downstream owners; structural checks report actual coverage, not invented test counts.

Preserve the source-matched supporting-plan review supplied by effective input. Retain its original receipt and audited hashes in the continuation handoff; changed plan instructions require Step 5 review but do not erase an unchanged-source implementation review. Complete outstanding first-wave review through Riela's existing review gates before accepting those handoffs; do not rerun accepted source work solely because plan status text was stale.

## Execution, drift and progress contract

This plan and the accepted design are committed and non-force pushed with the dispatch manifest by the later Riela checkpoint step before native fanout (a failed checkpoint push stops dispatch); this authoring step does not commit. Wait for every dependsOn plan's accepted source/infrastructure output under the ownership/failure-accounting rules above; do not wait for downstream review/publication. All workers share this branch and directory. Write only the listed paths; only the reconciliation plan may repair shared paths after all other workers join. Do not edit this plan or another worker's progress log during execution.

Before each edit, freshly read the file and consumers. Save its bytes and SHA-256 plus an immutable intent record naming the requirement, proposed fields and expected behavior in your own evidence directory under `attempt-N/intent/`. Recheck the hash immediately before writing; on drift, re-read and reconcile the intended patch instead of overwriting. Save post-edit bytes/hash, exact changed paths and tests tied to those hashes. Check hashes again at handoff. Record any mismatch and pause the conflicting edit for serial reconciliation; never discard another worker's change. This detects non-atomic overwrite races but does not pretend to prevent them.

Use a new attempt directory; preserve old receipts. Command examples below name canonical evidence paths: expand each to a fresh attempt path consistently (including workflow-list/baseline inputs) before execution and record the exact argv. Never overwrite an earlier attempt. Maintain your own `progress.json` with task IDs, pending/running/passed/blocked status, source hashes, changed paths, exact argv/cwd, final exit, complete log path, case/assertion counts, findings and next action. Also write `handoff.json` with requirements-to-files/tests mapping, remaining failures, review decision and post-hashes. Run commands foreground; poll yielded processes until exit. Capture stdout/stderr without losing the command exit. `git diff --check` supplements behavioral checks, never substitutes for them.

Only compat-reconcile may regenerate manifests, versions, dependency locks or registry-index.json, after all payload workers join. Do not archive plans or run git add/commit/push in any worker. Serial finalization prepares an exact file list for Riela publication steps. Every changed input invalidates affected verification and review receipts.

## Shared invariants and evidence rules

Preserve agent output envelope routing (`when`) separately from business `payload` schemas. Trace consumed fields through forwarding add-ons and cross-workflow calls; do not require an agent to invent a later add-on's Git result. Require concrete prompt-compatible types and branch-aware required fields. Keep legitimate failure/revision/planning/skip outputs valid. Use read-only for JSON-only reviews/reporting and workspace-write for file writers; justify any existing broader authority individually. Preserve routing, models, backend overrides and session policy unless a proven compatibility defect demands a scoped correction.

All evidence, catalogs, installations, session stores and artifacts stay under repository-root `tmp/registry-contract-migration/verification/`. Record tool versions and source identity. Assert mock terminal state, observed payloads and branch traces, not fixture intent or CLI exit alone. Mocks do not prove actual sandbox enforcement. If mocks bypass schema rejection, use a supported installed validation entry point and state coverage limits. Missing dependencies/network and incomplete logs are blocked checks, not passes. Historical #117 failures confer no waiver. Record fresh failures explicitly; owned defects block owner acceptance and any required final failure blocks completion.

## Split continuation

The original contract owner is now `compat-agent-contracts` plus `compat-agent-contracts-supporting`. Preserve this plan's task IDs and write/shared ownership; apply the current design's final-verification criteria. Both contract handoffs must be accepted before this plan starts. The completed `compat-verification` result is reused, never dispatched. Serial reconciliation joins both contract selections and rechecks all 65 packages / 59 workflows; no worker edits another worker's progress.

## Ordered tasks and deliverables

1. Join every handoff and compare current file hashes to worker post-hashes and immutable intent snapshots. Repair any overwritten requirement serially with fresh reads; document each drift and its chosen resolution. Review complete combined diff and rerun every affected check. Shared writePaths are repair authority only, not permission for optional refactoring. Reconcile package/producer coverage matrices so no package or changed producer lacks an owner/result. Reconcile expected-routes.json only after joining downstream route intents against the completed verification checkpoint: retain effective workflow/fixture identities, graph/fixture/document derivation evidence and mandatory route checks. Rerun all 17 accepted harness regressions after any repair. Final scenarios mode without --workflow-list must exercise mandatory routes for every default-selected fixture; explicitly selected inherited cases must also retain effective-wrapper route assertions.
2. Apply concrete manifest corrections requested by workers. Using the supplied corrected CLI, repair any demonstrated remaining mismatch in the local-command dependency locks in `packages/youtube-mp4-to-text-workflow/riela-package.json` against its three actual add-on descriptors and the fixed CLI contract. Preserve canonical IDs/capabilities/content digests; update dependent manifest metadata where required. Record before/after lock fields and validate the isolated installed dependency closure. Any remaining lock or installed-validation failure blocks final acceptance; retain exact fresh evidence and repair before completion. Bump changed package versions according to existing version policy; review effective wrapper impact and update necessary version/dependency pins. For each source-changed add-on run `bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts <package-directory-id>` with the recorded exact ID, recomputing its content digest and synchronized dependency locks FIRST, then package checksum/integrity for all affected packages, then registry-index.json. Use --all digest refresh only after recording the affected set and review every unexpected change. Update root/package README metadata only where displayed information changes; preserve package inventory.
3. Run the compatibility helper in manifests, workflows, scenarios and assets modes, then full `mise run check` and focused suites on final source. All requested checks must pass. Historical baseline failures and #117 attribution do not waive in-scope repairs. Retain any remaining failure or tool gap as blocking, with exact command/log/exit and assigned next action. If a tracked residual issue must be created, hand the concrete report to the authorized workflow publication/control step; do not fabricate a URL.
4. Run structural/typechecking required by changed TS/Python/add-on code using its existing configured checks; Bun tests alone are not a claimed static typecheck. Do not introduce a TypeScript project solely for this migration. Repeat package-specific behavioral regressions and all relevant scenario cases after repairs/metadata updates as needed; report unchanged input evidence reuse explicitly.
5. Write `release-evidence.json` containing every package disposition, changed versions/digests, validation results, all exact logs/exits/counts, baseline comparisons, unresolved findings and review source hashes. Prepare exact intended commit paths and a safety-reviewed diff. Record `sourceDelivery` and `finalVerification` separately, with exact command/exit/log evidence for every result, including historical YouTube closure and final passing receipts for the historical 48 wrapper commands. Update impl-plans/README.md to list this migration's actual source and final-verification status; global plan archiving remains a later completion-step operation, not a payload-worker action.
6. Hand off for independent test-integrity/adversarial/integration review. Only when no high/mid findings remain, Riela later completion/publication steps archive these plans if appropriate, commit the reviewed design/plans/payloads/metadata and non-force push `origin fix/registry-contract-migration`, then update Draft PR #15 with the final review and verification evidence. They must report resulting commit and push result, retain any unresolved failure in active tracking, and not archive or describe the migration as fully complete while final verification is blocked. This worker does not run Git mutations, release, merge, or claim publication is already complete.

## Verification result interpretation

The workflows helper validates and inspects the full 59-workflow catalog; `--workflow-list` selects scenarios only and does not filter workflows mode. Read `<validation-evidence>/commands.json` and `coverage.json`: require both `validate-<workflowId>` and `inspect-<workflowId>` exit 0 for every workflow; this final owner has no later-wave exception. Retain the full helper exit even when only later-wave failures remain. In scenarios mode require every selected case's CLI exit and `scenario-assert-<workflowId>` result to pass, with completed status, exact expected route and matching payload assertions. Do not use an empty selection or CLI exit alone as success.

For each required command, capture complete stdout/stderr plus final exit in the attempt's commands.json; record source hashes and test/assertion counts. A passing structural check cannot replace an applicable behavioral check. Run existing configured typecheck/build for code actually changed; document no configured check where applicable. Inventory and verify examples from owned README/skill/add-on paths; no live providers. Every own progress update preserves earlier attempt receipts; handoff includes changed paths, pre/post hashes, immutable intent, findings, ownership transfers and next action.

After the workflows-mode command creates its isolated project/catalog and all locks/digests are refreshed, install the actual YouTube workflow package into that isolated project and validate/inspect it with its installed dependencies. Set `COMPAT_REPO` to the absolute repository root before changing cwd, and `COMPAT_ATTEMPT` to this attempt's absolute evidence root. The helper already installs the three dependency add-ons from repository sources; confirm their successful install receipts before this command. Use a foreground subshell and log each final exit:

```sh
(cd "$COMPAT_ATTEMPT/workflows/isolated-project" && "$RIELA_COMPAT_CLI" package install @tacogips/youtube-mp4-to-text-workflow --source "$COMPAT_REPO/packages/youtube-mp4-to-text-workflow" --scope project --output json)
(cd "$COMPAT_ATTEMPT/workflows/isolated-project" && "$RIELA_COMPAT_CLI" workflow validate youtube-mp4-to-text --scope project --output json)
(cd "$COMPAT_ATTEMPT/workflows/isolated-project" && "$RIELA_COMPAT_CLI" workflow inspect youtube-mp4-to-text --scope project --output json)
```

These commands verify repository payload installation only; they do not inspect the current orchestration workflow. YouTube has no workflow mock fixture: record static download/audio/transcription field compatibility and existing deterministic add-on tests, without live calls. Final `failure-accounting.json` joins every worker's reported failures (including separate validate/inspect commands), identifies the corrective files and final passing receipts, and retains discrepancies between historical counts and fresh counts without inventing entries. All 65 package dispositions and 59 workflow validation/inspection pairs must be present; every deterministic example and fixture has a result or an explicit non-live coverage limit.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts --all --check
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts --all
mise run package:generate-index
mise run package:check-digests
mise run package:check-addon-digests
mise run package:check-index
bun test ./.agents/skills/riela-package-release/scripts/check-package-compat.test.ts
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode manifests --evidence-root "$COMPAT_ATTEMPT/manifests"
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root "$COMPAT_ATTEMPT/workflows"
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --evidence-root "$COMPAT_ATTEMPT/scenarios"
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root "$COMPAT_ATTEMPT/assets"
mise run check
git diff --check
```

## Final-source verification handoff

Run final checks now with the supplied corrected CLI, not as deferred post-fix work. In addition to the commands above, run `mise run package:validate`, `mise run workflow:validate`, `mise run workflow:check-compact`, `mise run workflow:check-codex-dispatch`, and both Fable `tests/check-output-contract.ts` commands from the supporting handoff in fresh evidence paths. Reuse other complete receipts only when all audited inputs still match. Include explicit installed YouTube dependency closure validation/inspection and deterministic handoff evidence; it has no checkpointed workflow fixture, so do not require a missing mock-scenario file. Use existing add-on tests/static handoff checks without live providers. Never interpret this verification as release authorization.

## Core-example validation under task 3

The following 75 source files are read-only inputs under `/Users/taco/gits/tacogips/riela-worktrees/remaining-impl-plans/examples`. Record their hashes and the sibling source revision. Copy the complete examples tree, retaining supporting assets and callees, to `$COMPAT_ATTEMPT/core-examples/catalog`; record copy/source hashes. Do not run these examples against live providers or write to the sibling checkout. For each table row, run the command below separately, substituting that row's exact workflow ID, from repository root:

```sh
"$RIELA_COMPAT_CLI" workflow validate <workflow-id> --workflow-definition-dir "$COMPAT_ATTEMPT/core-examples/catalog" --output json
```

Write `core-examples/commands.json` with 75 individual expanded commands, source paths/hashes, actual final exits and complete stdout/stderr log paths, plus `core-examples/coverage.json` mapping every row to its receipt. These are validation checks, not 75 behavioral tests: record validation coverage without invented positive test counts. Require all 75 exits to be zero. Preserve and report any genuine failure without modifying core or deleting an example; a required failure blocks final verification. Keep deterministic packaged-example execution receipts separate. If external fixture/tool prerequisites fail, record the concrete failed check and next action; do not relabel missing validation as a static pass.

| Source path relative to examples/ | Workflow ID |
| --- | --- |
| `apple-calendar-fetch/workflow.json` | `apple-calendar-fetch` |
| `apple-clock-alarms-list/workflow.json` | `apple-clock-alarms-list` |
| `apple-gateway-admin/workflow.json` | `apple-gateway-admin` |
| `apple-gateway-packaging-plan/workflow.json` | `apple-gateway-packaging-plan` |
| `apple-mail-list/workflow.json` | `apple-mail-list` |
| `apple-note-create/workflow.json` | `apple-note-create` |
| `apple-note-read/workflow.json` | `apple-note-read` |
| `apple-notes-list/workflow.json` | `apple-notes-list` |
| `apple-notifications/workflow.json` | `apple-notifications` |
| `apple-reminders-list/workflow.json` | `apple-reminders-list` |
| `chat-event-attachment-judgement/workflow.json` | `chat-event-attachment-judgement` |
| `chat-reply-webhook/workflow.json` | `chat-reply-webhook` |
| `chat-supervisor-collaboration/workflow.json` | `chat-supervisor-collaboration` |
| `claude-riela-claude-worker/workflow.json` | `claude-riela-claude-worker` |
| `claude-riela-codex-coding/workflow.json` | `claude-riela-codex-coding` |
| `codex-codex-topic-debate/workflow.json` | `codex-codex-topic-debate` |
| `design-and-implement-review-loop/workflow.json` | `design-and-implement-review-loop` |
| `design-and-implement-review-loop-feature-plan/workflow.json` | `design-and-implement-review-loop-feature-plan` |
| `discord-agent-trio-chat/workflow.json` | `discord-agent-trio-chat` |
| `discord-codex-chat/workflow.json` | `discord-codex-chat` |
| `discord-persona-chat/workflow.json` | `discord-persona-chat` |
| `dispatcher-llm-resolver-stub/workflow.json` | `dispatcher-llm-resolver-stub` |
| `enterprise-matrix-agent-personas/workflow.json` | `enterprise-matrix-agent-personas` |
| `enterprise-matrix-customer-escalation/workflow.json` | `enterprise-matrix-customer-escalation` |
| `enterprise-matrix-security-incident/workflow.json` | `enterprise-matrix-security-incident` |
| `enterprise-matrix-vendor-onboarding/workflow.json` | `enterprise-matrix-vendor-onboarding` |
| `file-markdown-convert/workflow.json` | `file-markdown-convert` |
| `first-four-arithmetic-pipeline/workflow.json` | `first-four-arithmetic-pipeline` |
| `gemini-ocr-worker/workflow.json` | `gemini-ocr-worker` |
| `gemini-sdk-worker/workflow.json` | `gemini-sdk-worker` |
| `gmail-latest-mail-digest-telegram/workflow.json` | `gmail-latest-mail-digest-telegram` |
| `kaiba-document-intake/workflow.json` | `kaiba-document-intake` |
| `loop-baseline-regression-ops/workflow.json` | `loop-baseline-regression-ops` |
| `loop-budget-guard/workflow.json` | `loop-budget-guard` |
| `loop-ci-gate-check/workflow.json` | `loop-ci-gate-check` |
| `loop-concurrency-lease/workflow.json` | `loop-concurrency-lease` |
| `loop-engineer-quality-loop/workflow.json` | `loop-engineer-quality-loop` |
| `loop-outcome-notifications/workflow.json` | `loop-outcome-notifications` |
| `loop-stall-guard/workflow.json` | `loop-stall-guard` |
| `matrix-agent-trio-chat/workflow.json` | `matrix-agent-trio-chat` |
| `matrix-chat-reply/workflow.json` | `matrix-chat-reply` |
| `memory-consolidation/workflow.json` | `memory-consolidation` |
| `monja-agent-collaboration/workflow.json` | `monja-agent-collaboration` |
| `monja-typescript-sdk/workflow.json` | `monja-typescript-sdk` |
| `node-combinations-showcase/workflow.json` | `node-combinations-showcase` |
| `note-agent/workflow.json` | `note-agent` |
| `note-link-extract/workflow.json` | `note-link-extract` |
| `note-rag-retrieval-fusion/workflow.json` | `note-rag-retrieval-fusion` |
| `open-model-provider-codex/workflow.json` | `open-model-provider-codex` |
| `recent-change-quality-loop/workflow.json` | `recent-change-quality-loop` |
| `required-loop-gate-failure/workflow.json` | `required-loop-gate-failure` |
| `riela-default-workflow-supervisor/workflow.json` | `riela-default-workflow-supervisor` |
| `routine-chat-manager/workflow.json` | `routine-chat-manager` |
| `routine-task-runner/workflow.json` | `routine-task-runner` |
| `same-node-session-echo/workflow.json` | `same-node-session-echo` |
| `scheduled-sleep/workflow.json` | `scheduled-sleep` |
| `seatbelt-sandboxed-worker/workflow.json` | `seatbelt-sandboxed-worker` |
| `shared-agent-trio-personas/workflow.json` | `shared-agent-trio-personas` |
| `slack-agent-trio-chat/workflow.json` | `slack-agent-trio-chat` |
| `slack-codex-chat/workflow.json` | `slack-codex-chat` |
| `subworkflow-chained-simple/workflow.json` | `subworkflow-chained-simple` |
| `task-agent-director/workflow.json` | `task-agent-director` |
| `task-repair-loop/workflow.json` | `task-repair-loop` |
| `telegram-agent-trio-chat/workflow.json` | `telegram-agent-trio-chat` |
| `telegram-agent-trio-time-signal/workflow.json` | `telegram-agent-trio-time-signal` |
| `telegram-sdk-trio-chat/workflow.json` | `telegram-sdk-trio-chat` |
| `worker-only-single-step/workflow.json` | `worker-only-single-step` |
| `workflow-call-live-echo/workflow.json` | `workflow-call-live-echo` |
| `workflow-call-live-echo-callee/workflow.json` | `workflow-call-live-echo-callee` |
| `workflow-call-review-target/workflow.json` | `workflow-call-review-target` |
| `workflow-call-simple/workflow.json` | `workflow-call-simple` |
| `workflow-knowledge-base/workflow.json` | `workflow-knowledge-base` |
| `wrike-project-kanban-agent/workflow.json` | `wrike-project-kanban-agent` |
| `x-follower-ai-business-digest/workflow.json` | `x-follower-ai-business-digest` |
| `x-incremental-posts-kv/workflow.json` | `x-incremental-posts-kv` |

## Completion criteria

- Owned source verification passes; later-wave failures retain exact evidence and assigned repair owners. Final reconciliation permits no historical #117 waiver or unresolved required check.
- All 65 package manifests and 59 effective workflows pass supplied corrected CLI validation/inspection with resolved dependencies; all required final checks pass.
- All 75 core-example rows have passing individual validation receipts and every deterministic packaged example has asserted evidence.
- Relevant behavioral/package tests pass; no required residual check failure is permitted at final acceptance.
- Combined hashes preserve all worker intent; versions/digests/index are consistent.
- Review-ready exact file set and release evidence are complete; final commit/push remain explicit later gates.

Run any existing configured typecheck/build for changed code and record its exact command/result; if none is configured, state that limit without inventing a project. Update affected documentation/EXPECTED_RESULTS.md only for changed behavior.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.

## Author review handoff

Step 3 accepted the design in comm-000004 with no findings. Step 5 review of these revised plan instructions is pending. Preserve prior plan receipts and the source-matched supporting implementation review; reuse only evidence whose audited inputs still match. Current author checks and ownership enumeration are recorded in `tmp/registry-contract-migration/verification/step4-plans-3ec4863/commands.json`. Package implementation/verification remains downstream; the author does not claim those commands have passed.
