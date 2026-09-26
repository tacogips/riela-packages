# compat-assets

Status: proposed for Step 5 review.

```json
{
  "planId": "compat-assets",
  "planPath": "impl-plans/active/compat-assets.md",
  "dependsOn": [],
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
  "progressFile": "tmp/registry-contract-migration/verification/compat-assets/continuation-35d1e6a/attempt-1/progress.json",
  "verification": [
    "\"$RIELA_COMPAT_CLI\" --version",
    "shasum -a 256 \"$RIELA_COMPAT_CLI\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root \"$COMPAT_ATTEMPT/audit\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root \"$COMPAT_ATTEMPT/installed-workflows\"",
    "mise run package:check-container-images",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "All add-ons, skills and examples have a recorded disposition and existing relevant package tests/typechecks are executed.",
    "YouTube resolved-install evidence is explicit; no live network service tests or widened grants.",
    "Manifest/digest intents are delivered to the serial owner.",
    "Owned source verification passes; later-wave failures retain exact evidence and assigned repair owners. Final reconciliation permits no historical #117 waiver or unresolved required check.",
    "Each applicable package-local behavioral command has its own actual exitCode, positive passing test count and complete logPath; no combined prose/semicolon evidence."
  ]
}
```

## Intent, context and non-goals

Continue https://github.com/tacogips/riela-packages/issues/14 from `35d1e6acf3399d31fafc886bbed441b20530afaa` on `fix/registry-contract-migration` for Draft PR #15 in `issue-resolution` mode. Step 3 comm-000004 accepted `design-docs/specs/design-riela-021-package-compat.md` with no findings. Preserve all five plans and checkpointed source work. Scope remains 65 packages, 59 workflows, deterministic packaged examples and validation evidence for all 75 Riela core examples. Intake reports 14 Codex/four supporting mocks, two new fixtures and asset audit passing with #117; recheck affected inputs and final integration. The installed-owner helper fix `e9b5869` is integrated: YouTube install/validate/inspect pass per effective input. Preserve their source-matched closure receipts. The remaining 48 failed commands belong to 24 Claude/Cursor wrappers; keep actual nonzero outcomes until repaired. The historical 50-command cohort remains evidence, not 50 current failures or distinct workflows.

`codexAgentReferences: []`. Preserve Cursor/Claude adaptations in existing extends patches/replacement maps, including backend/model overrides. No reference checkout or new adapters. No graph/model/session redesign, broad formatting, new frameworks, unrelated cleanup, live providers, release or merge to main. Do not change sibling repositories or rediscover the running workflow's registry/provenance. Runtime input is authoritative. Do not create worktrees/private branches or perform concurrent Git operations. Read applicable subtree AGENTS.md before editing. Preserve unrelated D4 records.

## Completed prerequisite and CLI setup

`compat-verification` remains completed prerequisite evidence (historical 17/17 accepted regressions); never redispatch its implementation. Preserve old receipts and prior progress. The contract split already exists; continue the five existing owners. Run required checks in the foreground from repository root, retaining terminal handles through exit. Record actual executable version/hash, exact argv/cwd, source hashes, final exit and complete stdout/stderr logs. No zero-test, truncated-log or missing-command result is a pass.

Use this package-check executable exactly; the separate #118 runner is `/Users/taco/gits/tacogips/riela-worktrees/fanout-directory-change-tracking/.build/debug/riela` and is not the package verifier:

```sh
export RIELA_COMPAT_CLI=/Users/taco/gits/tacogips/riela-worktrees/remaining-impl-plans/.build/debug/riela
export RIELA_BIN="$RIELA_COMPAT_CLI"
"$RIELA_COMPAT_CLI" --version
shasum -a 256 "$RIELA_COMPAT_CLI"
```

Set `COMPAT_ATTEMPT` to the absolute repository root plus `tmp/registry-contract-migration/verification/compat-assets/continuation-35d1e6a/attempt-1`; if it already exists use the next unused attempt number and record the effective progressFile. Preserve the prior canonical progress log as historical evidence. Create `bin/riela` there as a symlink to `$RIELA_COMPAT_CLI`, prepend that bin directory to PATH and record `command -v riela` plus its resolved target so subprocesses use #117 too. Do not overwrite previous attempts, change HOME, build core or silently substitute a binary. Missing executables block dependent checks only. Canonical command paths below must be expanded consistently to the new attempt path and recorded in `commands.json`.

## Continuation and failure accounting

Riela https://github.com/tacogips/riela/issues/117 is the related fix reference, not a presumed outstanding blocker or acceptance waiver. Diagnose fresh failures using the supplied #117 executable. Keep failing commands in `verification` with their nonzero exits; preserve historical comparisons in `baselineDiagnostics`. Use `externalBlockers` only for newly demonstrated external defects with exact command/log/exit evidence. Every reported command failure relevant to this owner must map to a workflow, diagnosis, owner and final result in `failure-accounting.json`; never discard inventory entries, weaken validation or convert aggregate failure to success.

An earlier wave may finish its owned source tasks while documented later-wave repairs remain pending: assign each pending wrapper defect to compat-inheritance and each manifest/dependency-lock defect to compat-reconcile, with exact paths and field-level intent. An owned contract failure or missing owned material verification blocks that owner. Full-catalog aggregate failures remain failed even when an owner's individual checks pass. The final reconciliation gate requires all requested checks passing; a historical failure or baseline reproduction grants no exception. This permits dependency-ready progress without claiming compatibility completion early.

Reuse receipts only after matching audited file hashes, CLI hash/version, dependencies, effective arguments, final exit and complete logs; record comparisons and original receipt paths. If mismatch or incomplete, rerun affected checks. Baseline copies, if needed, use checkpoint 35d1e6a under repository tmp; no extra worktrees. Preserve the two checkpointed fixtures and all existing route assertions. The 12 fixtureless supporting workflows require validate/inspect receipts, never a manufactured scenario requirement. All packaged examples require deterministic checks or explicit static invocation/asset coverage where live execution is excluded. Serial reconciliation additionally records validation for each of the 75 core examples; static audits cannot replace those validation results.

Formal independent reviews, checkpoint/publication and final commit/push are later Riela gates. Step 6 completion covers assigned source tasks and their verification, not those later gates. Report source status and final-verification status separately. No unresolved high/mid owned finding is complete; no final acceptance while required checks fail or are blocked.

The previous Step 6 stop was an evidence-format blocker, not a test failure. For EVERY package-local behavioral command, write a separate `verification` record containing the exact command/cwd, actual numeric `exitCode`, positive `testsRun` or `testCount` for a passing behavioral check, complete `logPath`, and source/CLI hashes. Copy only source-matched complete receipts or rerun the command. Do not use a prose summary, semicolon-combined command, assumed zero exit, or aggregate test count. Preserve nonzero results until a separately recorded rerun passes. Keep whole-catalog failures as separate nonzero records assigned to downstream owners; structural checks report actual coverage, not invented test counts.

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

The original contract owner is now `compat-agent-contracts` plus `compat-agent-contracts-supporting`. Preserve this plan's task IDs and write/shared ownership; apply the current design's final-verification criteria. This plan runs alongside both disjoint contract owners. The completed `compat-verification` result is reused, never dispatched. Serial reconciliation joins both contract selections and rechecks all 65 packages / 59 workflows; no worker edits another worker's progress.

## Ordered tasks and deliverables

1. Audit every assigned non-workflow payload path and associated read-only manifests: add-on source/descriptors, capability grants, environment mappings, packaged skill frontmatter/vendor placement/referenced files, README commands and examples. Record exact files and compatible/changed/failing dispositions in `assets.json`. Inspect source to determine required package-focused commands; run declared test commands where present, recording exact argv, positive counts and typecheck/build requirements from their own configuration. Do not install unrelated toolchains or refactor working assets.
2. Fix only confirmed 0.2.1 incompatibilities in owned paths. Keep add-on inputs/outputs/capability scope stable. For skill changes preserve backend identifiers and appropriate vendor directories; align concrete obsolete invocations with supported installed CLI help. Read nested packaged AGENTS.md before editing. Manifest incompatibilities and dependency-lock changes are handed to serial reconciliation as exact proposed field patches, not edited here.
3. Verify the three YouTube dependency add-ons from local payloads through isolated installed-package resolution using the helper. Record resolved executable availability, download-to-audio-to-transcription handoff contracts and deterministic responses; no live service credentials/calls. If a workflow fixture correction is needed, send exact intent to its workflow owner or serial reconciliation; do not overwrite that workflow. Distinguish a raw catalog omission from the installed host-resolution defect tracked by #117. Recheck installed behavior with #117; retain failed exits and send exact dependency-lock repairs to reconciliation. Do not repair core or presume its historical failure remains.
4. For `packages/youtube-mp4-to-text-workflow/riela-package.json`, check whether any of the three local-command dependency locks still mismatch with `packages/youtube-mp4-download-addon/riela-package.json`, `packages/mp4-audio-extract-addon/riela-package.json`, `packages/google-speech-to-text-addon/riela-package.json` and their add-on descriptors. If a mismatch remains, deliver exact field-level lock migration intent to compat-reconcile; otherwise record compatible unchanged with the integrated helper closure; do not write manifests. Confirm replacement fields against the supplied #117 executable and actual descriptors; record unsupported behavior as a failed check, never guessed values. Preserve canonical IDs, capability grants and source content locks.
5. Deliver `assets.json`, proposed manifest patches and source-changed add-on IDs needing content digest updates. If no asset incompatibility exists, retain sources unchanged and deliver audit/test evidence rather than cosmetic edits.

## Verification result interpretation

The workflows helper validates and inspects the full 59-workflow catalog; `--workflow-list` selects scenarios only and does not filter workflows mode. Read `<validation-evidence>/commands.json` and `coverage.json`: require both `validate-<workflowId>` and `inspect-<workflowId>` exit 0 for every owned workflow, except an exact dependency-lock defect assigned to the serial owner as pending final verification. Retain the full helper exit even when only later-wave failures remain. In scenarios mode require every selected case's CLI exit and `scenario-assert-<workflowId>` result to pass, with completed status, exact expected route and matching payload assertions. Do not use an empty selection or CLI exit alone as success.

For each required command, capture complete stdout/stderr plus final exit in the attempt's commands.json; record source hashes and test/assertion counts. A passing structural check cannot replace an applicable behavioral check. Run existing configured typecheck/build for code actually changed; document no configured check where applicable. Inventory and verify examples from owned README/skill/add-on paths; no live providers. Every own progress update preserves earlier attempt receipts; handoff includes changed paths, pre/post hashes, immutable intent, findings, ownership transfers and next action.

The supporting owner supplies the Claude worker, Fable Astra and Fable output-contract behavioral receipts. Consume their source-matched handoff without editing or claiming ownership of those tests; this asset owner records its own declared asset tests separately.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root "$COMPAT_ATTEMPT/audit"
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root "$COMPAT_ATTEMPT/installed-workflows"
mise run package:check-container-images
git diff --check
```

## Completion criteria

- Owned source verification passes; later-wave failures retain exact evidence and assigned repair owners. Final reconciliation permits no historical #117 waiver or unresolved required check.
- All add-ons, skills and examples have a recorded disposition and existing relevant package tests/typechecks are executed.
- YouTube resolved-install evidence is explicit; no live network service tests or widened grants.
- Manifest/digest intents are delivered to the serial owner.

Run any existing configured typecheck/build for changed code and record its exact command/result; if none is configured, state that limit without inventing a project. Update affected documentation/EXPECTED_RESULTS.md only for changed behavior.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.

## Author review handoff

Step 3 accepted the design in comm-000004 with no findings. Step 5 review of these revised plan instructions is pending. Preserve prior plan receipts and the source-matched supporting implementation review; reuse only evidence whose audited inputs still match. Current author checks and ownership enumeration are recorded in `tmp/registry-contract-migration/verification/step4-plans-35d1e6a/commands.json`. Package implementation/verification remains downstream; the author does not claim those commands have passed.
