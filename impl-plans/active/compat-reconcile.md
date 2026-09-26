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
  "progressFile": "tmp/registry-contract-migration/verification/compat-reconcile/progress.json",
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
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode manifests --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/manifests",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/workflows",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/scenarios",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/assets",
    "mise run check",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "All package manifests and effective workflows pass supplied source CLI validation with dependencies except the explicitly evidenced core #117 installed YouTube blocker; all other source verification passes.",
    "Relevant behavioral/package tests pass; each permitted residual check failure is reproduced and separately tracked.",
    "Combined hashes preserve all worker intent; versions/digests/index are consistent.",
    "Review-ready exact file set and release evidence are complete; final commit/push remain explicit later gates.",
    "Source work may be accepted with an explicitly evidenced core #117 final installed YouTube blocker; raw failures remain failures and all-green completion/release stays blocked."
  ]
}
```

## Intent, context and non-goals

Resolve https://github.com/tacogips/riela-packages/issues/14 in `issue-resolution` mode using accepted `design-docs/specs/design-riela-021-package-compat.md` (bounded contract-plan split accepted by Step 3, comm-000004, no findings). All packages are in scope; the intake's 39 failures are a diagnostic cohort, not an inventory limit. `codexAgentReferences: []`; preserve existing Cursor/Claude wrapper adaptations rather than introducing adapters. Issue title/body were unavailable; do not infer #114 from scratch directory names.

Use the runner-supplied source Riela binary containing core #118 on `fix/registry-contract-migration`. Do not inspect the running workflow's registry/provenance, change sibling repositories, create worktrees/private branches, run concurrent Git mutations, release or merge. No graph/model/session redesign, broad formatting, vacuous schemas, permission escalation for review-only agents or unrelated cleanup. Review existing subtree AGENTS.md before editing. Do not modify unrelated D4 records.

## Completed prerequisite and CLI setup

The accepted design and Step 3 comm-000004 authorize exactly these five remaining plans after splitting only the original contract plan. `compat-verification` is completed at `75f371f80d30ee69c17193121111972fc65a68db`, with 17/17 tests and integration review accepted by intake. It is not dispatched again. The current continuation checkpoint is `78445b4919ce337cae550855431ec6bc21577265`; the older hash records completed prerequisite evidence only. Source-matched evidence is reusable after comparing audited source, CLI, dependency inputs, final exits and complete logs. Final integration reruns remain required. The source inventory is 65 packages / 59 workflows; repair the reported 39 legacy agent-contract and 47 asset/README failures without treating these diagnostic counts as coverage limits.

Before the commands below, bind `RIELA_COMPAT_CLI` and `RIELA_BIN` to the same absolute, runner-supplied source executable containing core #118. Record the expanded executable path, `"$RIELA_COMPAT_CLI" --version` and `shasum -a 256 "$RIELA_COMPAT_CLI"` with final exit and complete logs. For tests that spawn literal `riela`, prepend a directory under the worker's fresh `tmp/` attempt containing a `riela` symlink to that executable to PATH; verify `command -v riela` resolves there. Do not change HOME, build core, or infer #117 support from #118. Do not substitute a different installed binary silently. No executable location is invented by this plan; absence of the supplied executable blocks its dependent checks only.

Step 4 identified the repaired source executable at `/Users/taco/gits/tacogips/riela-worktrees/fanout-directory-change-tracking/.build/debug/riela`: version `0.2.1`, source HEAD `b83887ac08c9585641008fc8ebf128eaa1d8aa9c`, executable SHA-256 `1c56cdd80ed47cbb7a739e6bc521cf1cf7268b2a817761821a534aced61e2ab5`. The source checkout was clean. Identity receipts are `tmp/registry-contract-migration/verification/step4-plans-78445b4/commands.json` (commands 2–5, all exit 0). Set both CLI variables to this absolute executable for this checkout and re-record identity in each attempt; if the runner explicitly supplies a newer repaired source binary, record that replacement and invalidate affected receipts. This identity does not establish #117 availability. Do not use `/opt/homebrew/bin/riela` as an implicit fallback.

## Continuation and #117 boundary

Continue from `78445b4919ce337cae550855431ec6bc21577265`, covering 65 packages / 59 workflows. Reuse the checkpointed harness and source-matched receipts; repair concrete gaps only. Riela core https://github.com/tacogips/riela/issues/117 tracks installed YouTube `unresolvedAddonExecutable`. Its repair is not a prerequisite for source edits, acceptance of usable verification infrastructure, or dependency-ready source-plan dispatch. Do not modify sibling repositories or installed user-scope packages; make no live model/provider calls.

Keep command exit status separate from plan readiness: record the exact failing command, complete log, source/tool identity, affected workflow and #117 attribution. Never convert a nonzero result to a pass, skip the affected inventory entry, weaken validation or classify unrelated failures as #117. Owned changed-package tests and deterministic mock assertions must pass; record the specifically blocked installed YouTube check separately. Missing material source verification or unresolved high/mid source defects still block source acceptance. Core #117 alone does not block independent review, accepted source commit or non-force push; full all-green compatibility and release remain blocked.

The plan's command lists specify required evidence collection; do not copy aggregate command results blindly into Step 6 output. Its `verification` array contains changed-source acceptance checks expected to pass, with any genuine changed-source failure retained as failing and blocking. Untouched pre-migration failures belong in `baselineDiagnostics`; the exact installed YouTube #117 failure belongs in `externalBlockers`. Keep complete aggregate logs and nonzero exits in `commands.json`, and link individual passing source-check receipts separately; never report a failing aggregate as passing. Any other residual failure requires exact baseline reproduction and a separate issue reference. Whole-catalog failures belonging to later dependency waves remain explicit pending owner tasks, not completed fixes or blanket #117 exceptions; serial reconciliation must account for every failure before source delivery.

Reuse a preserved baseline only when its audited source SHA-256 values, CLI executable hash/version, effective command arguments and dependency inputs match the intended baseline, and the original final exit and complete log are available. Record the old receipt paths and the hash comparison in the new attempt's `baseline.json`/`commands.json`; keep the receipt's original commit identity. Commit-label differences alone do not invalidate identical audited inputs. Do not rerun the 59-workflow baseline when this comparison passes. If hashes differ or required evidence is incomplete, regenerate only the affected baseline evidence from the intake commit under a fresh `tmp/` attempt. This reuse rule applies to every baseline command below and does not waive inventory drift detection or changed-source verification.

Each progress/handoff records source-task status separately from final-verification status, including `externalBlockers` with issue URL, command/exit/log evidence and follow-up. Formal downstream review, commit and push remain later workflow gates, not missing worker implementation tasks. After the core fix, serial finalization records the fixed CLI identity and reruns installed YouTube validation/scenarios and the full suite; preserve this pending obligation in plan status until it passes.

## Execution, drift and progress contract

This plan and the accepted design are committed and non-force pushed with the dispatch manifest by the later Riela checkpoint step before native fanout (a failed checkpoint push stops dispatch); this authoring step does not commit. Wait for every dependsOn plan's accepted source/infrastructure output under the #117 boundary above; do not wait for final all-green verification. All workers share this branch and directory. Write only the listed paths; only the reconciliation plan may repair shared paths after all other workers join. Do not edit this plan or another worker's progress log during execution.

Before each edit, freshly read the file and consumers. Save its bytes and SHA-256 plus an immutable intent record naming the requirement, proposed fields and expected behavior in your own evidence directory under `attempt-N/intent/`. Recheck the hash immediately before writing; on drift, re-read and reconcile the intended patch instead of overwriting. Save post-edit bytes/hash, exact changed paths and tests tied to those hashes. Check hashes again at handoff. Record any mismatch and pause the conflicting edit for serial reconciliation; never discard another worker's change. This detects non-atomic overwrite races but does not pretend to prevent them.

Use a new attempt directory; preserve old receipts. Command examples below name canonical evidence paths: expand each to a fresh attempt path consistently (including workflow-list/baseline inputs) before execution and record the exact argv. Never overwrite an earlier attempt. Maintain your own `progress.json` with task IDs, pending/running/passed/blocked status, source hashes, changed paths, exact argv/cwd, final exit, complete log path, case/assertion counts, findings and next action. Also write `handoff.json` with requirements-to-files/tests mapping, remaining failures, review decision and post-hashes. Run commands foreground; poll yielded processes until exit. Capture stdout/stderr without losing the command exit. `git diff --check` supplements behavioral checks, never substitutes for them.

Only compat-reconcile may regenerate manifests, versions, dependency locks or registry-index.json, after all payload workers join. Do not archive plans or run git add/commit/push in any worker. Serial finalization prepares an exact file list for Riela publication steps. Every changed input invalidates affected verification and review receipts.

## Shared invariants and evidence rules

Preserve agent output envelope routing (`when`) separately from business `payload` schemas. Trace consumed fields through forwarding add-ons and cross-workflow calls; do not require an agent to invent a later add-on's Git result. Require concrete prompt-compatible types and branch-aware required fields. Keep legitimate failure/revision/planning/skip outputs valid. Use read-only for JSON-only reviews/reporting and workspace-write for file writers; justify any existing broader authority individually. Preserve routing, models, backend overrides and session policy unless a proven compatibility defect demands a scoped correction.

All evidence, catalogs, installations, session stores and artifacts stay under repository-root `tmp/registry-contract-migration/verification/`. Record tool versions and source identity. Assert mock terminal state, observed payloads and branch traces, not fixture intent or CLI exit alone. Mocks do not prove actual sandbox enforcement. If mocks bypass schema rejection, use a supported installed validation entry point and state coverage limits. Missing dependencies/network and incomplete logs are blocked checks, not passes. Core #117 is already accepted by intake as an external final-verification blocker; preserve reproduction evidence without requiring its repair for source delivery. Other residual failures require independent baseline reproduction and a separately tracked issue; unexplained failures are blocking.

## Split continuation

The original contract owner is now `compat-agent-contracts` plus `compat-agent-contracts-supporting`. Preserve this plan's original tasks, acceptance criteria and write/shared ownership. Both contract handoffs must be accepted before this plan starts. The completed `compat-verification` result is reused, never dispatched. Serial reconciliation joins both contract selections and rechecks all 65 packages / 59 workflows; no worker edits another worker's progress.

## Ordered tasks and deliverables

1. Join every handoff and compare current file hashes to worker post-hashes and immutable intent snapshots. Repair any overwritten requirement serially with fresh reads; document each drift and its chosen resolution. Review complete combined diff and rerun every affected check. Shared writePaths are repair authority only, not permission for optional refactoring. Reconcile package/producer coverage matrices so no package or changed producer lacks an owner/result. Reconcile expected-routes.json only after joining downstream route intents against the completed verification checkpoint: retain effective workflow/fixture identities, graph/fixture/document derivation evidence and mandatory route checks. Rerun all 17 accepted harness regressions after any repair. Final scenarios mode without --workflow-list must exercise mandatory routes for every default-selected fixture; explicitly selected inherited cases must also retain effective-wrapper route assertions.
2. Apply concrete manifest corrections requested by workers. After core #117 support is available, migrate the old local-command dependency locks in `packages/youtube-mp4-to-text-workflow/riela-package.json` against its three actual add-on descriptors and the fixed CLI contract. Preserve canonical IDs/capabilities/content digests; update dependent manifest metadata where required. Record before/after lock fields and validate the isolated installed dependency closure. If the fix is unavailable, retain the pending lock migration and installed validation in externalBlockers with exact known failure evidence; do not mark either complete. Unrelated accepted source delivery may proceed under the design boundary. Bump changed package versions according to existing version policy; review effective wrapper impact and update necessary version/dependency pins. For each source-changed add-on run `bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts <package-directory-id>` with the recorded exact ID, recomputing its content digest and synchronized dependency locks FIRST, then package checksum/integrity for all affected packages, then registry-index.json. Use --all digest refresh only after recording the affected set and review every unexpected change. Update root/package README metadata only where displayed information changes; preserve package inventory.
3. Run the compatibility helper in manifests, workflows, scenarios and assets modes, then full `mise run check` and focused suites on final source. Core #117 remains an explicit final-verification blocker, not a source-delivery veto. Any other residual failure is not accepted unless reproduced at intake HEAD in the isolated baseline copy with the same effective inputs/command, exact final exit/log comparison and a separately tracked issue reference. Record baseline tool gaps honestly; they do not prove pre-existence. New or unexplained failures block delivery. If a tracked residual issue must be created, hand the concrete report to the authorized workflow publication/control step; do not fabricate a URL.
4. Run structural/typechecking required by changed TS/Python/add-on code using its existing configured checks; Bun tests alone are not a claimed static typecheck. Do not introduce a TypeScript project solely for this migration. Repeat package-specific behavioral regressions and all relevant scenario cases after repairs/metadata updates as needed; report unchanged input evidence reuse explicitly.
5. Write `release-evidence.json` containing every package disposition, changed versions/digests, validation results, all exact logs/exits/counts, baseline comparisons, unresolved findings and review source hashes. Prepare exact intended commit paths and a safety-reviewed diff. Record `sourceDelivery` and `finalVerification` separately, with #117 command/exit/log evidence and the pending post-fix rerun. Update impl-plans/README.md to list this migration's source status and pending final verification; global plan archiving remains a later completion-step operation, not a payload-worker action.
6. Hand off for independent test-integrity/adversarial/integration review. Only when no high/mid findings remain, Riela later completion/publication steps archive these plans if appropriate, commit the reviewed design/plans/payloads/metadata and non-force push `origin fix/registry-contract-migration`. They must report resulting commit and push result, retain the #117 follow-up in active tracking, and not archive or describe the migration as fully complete while final verification is blocked. This worker does not run Git mutations, release, merge, or claim publication is already complete.

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
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode manifests --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/manifests
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/workflows
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/scenarios
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/assets
mise run check
git diff --check
```

## Post-core-fix verification handoff

The later serial finalization owner reruns `riela --version`, `mise run package:validate`, `mise run workflow:validate`, `bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --evidence-root tmp/registry-contract-migration/verification/compat-reconcile/post-core-fix-scenarios`, and `mise run check`, plus every affected package test listed in worker receipts. Use fresh attempt paths. The workflow validation/scenario evidence must explicitly include installed `youtube-mp4-to-text` with its three resolved add-on dependencies, terminal state and observed handoffs. Only passing complete receipts on final source remove the external final-verification blocker; this handoff does not authorize a release.

## Completion criteria

- Source work may be accepted with an explicitly evidenced core #117 final installed YouTube blocker; raw failures remain failures and all-green completion/release stays blocked.
- All package manifests and effective workflows pass supplied source CLI validation with dependencies except the explicitly evidenced core #117 installed YouTube blocker; all other source verification passes.
- Relevant behavioral/package tests pass; each permitted residual check failure is reproduced and separately tracked.
- Combined hashes preserve all worker intent; versions/digests/index are consistent.
- Review-ready exact file set and release evidence are complete; final commit/push remain explicit later gates.

Run any existing configured typecheck/build for changed code and record its exact command/result; if none is configured, state that limit without inventing a project. Update affected documentation/EXPECTED_RESULTS.md only for changed behavior.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.
