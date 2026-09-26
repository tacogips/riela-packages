# compat-assets

Status: proposed for Step 5 review.

```json
{
  "planId": "compat-assets",
  "planPath": "impl-plans/active/compat-assets.md",
  "dependsOn": [
    "compat-verification"
  ],
  "writePaths": [
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
    "packages/youtube-shorts-to-text-container/README.md"
  ],
  "sharedPaths": [],
  "progressFile": "tmp/registry-contract-migration/verification/compat-assets/progress.json",
  "verification": [
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root tmp/registry-contract-migration/verification/compat-assets/audit",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root tmp/registry-contract-migration/verification/compat-assets/installed-workflows",
    "mise run package:check-container-images",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "All add-ons, skills and examples have a recorded disposition and existing relevant package tests/typechecks are executed.",
    "YouTube resolved-install evidence is explicit; no live network service tests or widened grants.",
    "Manifest/digest intents are delivered to the serial owner."
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

1. Audit every assigned non-workflow payload path and associated read-only manifests: add-on source/descriptors, capability grants, environment mappings, packaged skill frontmatter/vendor placement/referenced files, README commands and examples. Record exact files and compatible/changed/failing dispositions in `assets.json`. Inspect source to determine required package-focused commands; run declared test commands where present, recording exact argv, positive counts and typecheck/build requirements from their own configuration. Do not install unrelated toolchains or refactor working assets.
2. Fix only confirmed 0.2.1 incompatibilities in owned paths. Keep add-on inputs/outputs/capability scope stable. For skill changes preserve backend identifiers and appropriate vendor directories; align concrete obsolete invocations with supported installed CLI help. Read nested packaged AGENTS.md before editing. Manifest incompatibilities and dependency-lock changes are handed to serial reconciliation as exact proposed field patches, not edited here.
3. Verify the three YouTube dependency add-ons from local payloads through isolated installed-package resolution using the helper. Record resolved executable availability, download-to-audio-to-transcription handoff contracts and deterministic responses; no live service credentials/calls. If a workflow fixture correction is needed, send exact intent to its workflow owner or serial reconciliation; do not overwrite that workflow. Distinguish the retained direct-catalog unresolvedAddonExecutable from an actual resolved-install failure.
4. Deliver `assets.json`, proposed manifest patches and source-changed add-on IDs needing content digest updates. If no asset incompatibility exists, retain sources unchanged and deliver audit/test evidence rather than cosmetic edits.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root tmp/registry-contract-migration/verification/compat-assets/audit
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root tmp/registry-contract-migration/verification/compat-assets/installed-workflows
mise run package:check-container-images
git diff --check
```

## Completion criteria

- All add-ons, skills and examples have a recorded disposition and existing relevant package tests/typechecks are executed.
- YouTube resolved-install evidence is explicit; no live network service tests or widened grants.
- Manifest/digest intents are delivered to the serial owner.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.
