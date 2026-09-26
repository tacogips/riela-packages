# compat-inheritance

Status: proposed for Step 5 review.

```json
{
  "planId": "compat-inheritance",
  "planPath": "impl-plans/active/compat-inheritance.md",
  "dependsOn": [
    "compat-agent-contracts",
    "compat-assets"
  ],
  "writePaths": [
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
  "sharedPaths": [],
  "progressFile": "tmp/registry-contract-migration/verification/compat-inheritance/progress.json",
  "verification": [
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root tmp/registry-contract-migration/verification/compat-inheritance/validation",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --workflow-list tmp/registry-contract-migration/verification/compat-inheritance/workflows.json --evidence-root tmp/registry-contract-migration/verification/compat-inheritance/scenarios",
    "mise run workflow:check-compact",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "Every inherited workflow validates after base migration and has effective contract/authority/backend evidence.",
    "No inheritance flattening or duplicate base edits; wrapper release impact is reported.",
    "Any outstanding base defect is explicitly handed to serial reconciliation.",
    "Source work may be accepted with an explicitly evidenced core #117 final installed YouTube blocker; raw failures remain failures and all-green completion/release stays blocked."
  ]
}
```

## Intent, context and non-goals

Resolve https://github.com/tacogips/riela-packages/issues/14 in `issue-resolution` mode using accepted `design-docs/specs/design-riela-021-package-compat.md` (continuation update accepted by Step 3, comm-000004, no findings). All packages are in scope; the intake's 39 failures are a diagnostic cohort, not an inventory limit. `codexAgentReferences: []`; preserve existing Cursor/Claude wrapper adaptations rather than introducing adapters. Issue title/body were unavailable; do not infer #114 from scratch directory names.

Use installed Riela 0.2.1 on `fix/registry-contract-migration`. Do not inspect the running workflow's registry/provenance, change sibling repositories, create worktrees/private branches, run concurrent Git mutations, release or merge. No graph/model/session redesign, broad formatting, vacuous schemas, permission escalation for review-only agents or unrelated cleanup. Review existing subtree AGENTS.md before editing. Do not modify unrelated D4 records.

## Continuation and #117 boundary

Continue from `ae365081721dde884ac212b9c691427272790ff1`, covering 65 packages / 59 workflows. Reuse the checkpointed harness and source-matched receipts; repair concrete gaps only. Riela core https://github.com/tacogips/riela/issues/117 tracks installed YouTube `unresolvedAddonExecutable`. Its repair is not a prerequisite for source edits, acceptance of usable verification infrastructure, or dependency-ready source-plan dispatch. Do not modify sibling repositories or installed user-scope packages; make no live model/provider calls.

Keep command exit status separate from plan readiness: record the exact failing command, complete log, source/tool identity, affected workflow and #117 attribution. Never convert a nonzero result to a pass, skip the affected inventory entry, weaken validation or classify unrelated failures as #117. Owned changed-package tests and deterministic mock assertions must pass; record the specifically blocked installed YouTube check separately. Missing material source verification or unresolved high/mid source defects still block source acceptance. Core #117 alone does not block independent review, accepted source commit or non-force push; full all-green compatibility and release remain blocked.

The plan's command lists specify required evidence collection; do not copy aggregate command results blindly into Step 6 output. Its `verification` array contains changed-source acceptance checks expected to pass, with any genuine changed-source failure retained as failing and blocking. Untouched pre-migration failures belong in `baselineDiagnostics`; the exact installed YouTube #117 failure belongs in `externalBlockers`. Keep complete aggregate logs and nonzero exits in `commands.json`, and link individual passing source-check receipts separately; never report a failing aggregate as passing. Any other residual failure requires exact baseline reproduction and a separate issue reference. Whole-catalog failures belonging to later dependency waves remain explicit pending owner tasks, not completed fixes or blanket #117 exceptions; serial reconciliation must account for every failure before source delivery.

Reuse a preserved baseline only when its audited source SHA-256 values, CLI executable hash/version, effective command arguments and dependency inputs match the intended baseline, and the original final exit and complete log are available. Record the old receipt paths and the hash comparison in the new attempt's `baseline.json`/`commands.json`; keep the receipt's original commit identity. Commit-label differences alone do not invalidate identical audited inputs. Do not rerun the 59-workflow baseline when this comparison passes. If hashes differ or required evidence is incomplete, regenerate only the affected baseline evidence from the intake commit under a fresh `tmp/` attempt. This reuse rule applies to every baseline command below and does not waive inventory drift detection or changed-source verification.

Each progress/handoff records source-task status separately from final-verification status, including `externalBlockers` with issue URL, command/exit/log evidence and follow-up. Formal downstream review, commit and push remain later workflow gates, not missing worker implementation tasks. After the core fix, serial finalization records the fixed CLI identity and reruns installed YouTube validation/scenarios and the full suite; preserve this pending obligation in plan status until it passes.

## Execution, drift and progress contract

This plan and the accepted design are committed and non-force pushed with the dispatch manifest by the later Riela checkpoint step before native fanout (a failed checkpoint push stops dispatch); this authoring step does not commit. Wait for every dependsOn plan's accepted source/infrastructure output under the #117 boundary above; do not wait for final all-green verification. All workers share this branch and directory. Write only the listed paths; only the reconciliation plan may repair shared paths after all other workers join. Do not edit this plan or another worker's progress log during execution.

Before each edit, freshly read the file and consumers. Save its bytes and SHA-256 plus an immutable intent record naming the requirement, proposed fields and expected behavior in your own evidence directory under `attempt-N/intent/`. Recheck the hash immediately before writing; on drift, re-read and reconcile the intended patch instead of overwriting. Save post-edit bytes/hash, exact changed paths and tests tied to those hashes. Check hashes again at handoff. Record any mismatch and pause the conflicting edit for serial reconciliation; never discard another worker's change. This detects non-atomic overwrite races but does not pretend to prevent them.

Use a new attempt directory; preserve old receipts. Command examples below name canonical evidence paths: expand each to a fresh attempt path consistently (including workflow-list/baseline inputs) before execution and record the exact argv. Never overwrite an earlier attempt. Maintain your own `progress.json` with task IDs, pending/running/passed/blocked status, source hashes, changed paths, exact argv/cwd, final exit, complete log path, case/assertion counts, findings and next action. Also write `handoff.json` with requirements-to-files/tests mapping, remaining failures, review decision and post-hashes. Run commands foreground; poll yielded processes until exit. Capture stdout/stderr without losing the command exit. `git diff --check` supplements behavioral checks, never substitutes for them.

Do not regenerate manifests, versions, dependency locks or registry-index.json in a parallel payload worker. Do not archive plans or run git add/commit/push in any worker. Serial finalization prepares an exact file list for Riela publication steps. Every changed input invalidates affected verification and review receipts.

## Shared invariants and evidence rules

Preserve agent output envelope routing (`when`) separately from business `payload` schemas. Trace consumed fields through forwarding add-ons and cross-workflow calls; do not require an agent to invent a later add-on's Git result. Require concrete prompt-compatible types and branch-aware required fields. Keep legitimate failure/revision/planning/skip outputs valid. Use read-only for JSON-only reviews/reporting and workspace-write for file writers; justify any existing broader authority individually. Preserve routing, models, backend overrides and session policy unless a proven compatibility defect demands a scoped correction.

All evidence, catalogs, installations, session stores and artifacts stay under repository-root `tmp/registry-contract-migration/verification/`. Record tool versions and source identity. Assert mock terminal state, observed payloads and branch traces, not fixture intent or CLI exit alone. Mocks do not prove actual sandbox enforcement. If mocks bypass schema rejection, use a supported installed validation entry point and state coverage limits. Missing dependencies/network and incomplete logs are blocked checks, not passes. Core #117 is already accepted by intake as an external final-verification blocker; preserve reproduction evidence without requiring its repair for source delivery. Other residual failures require independent baseline reproduction and a separately tracked issue; unexplained failures are blocking.

## Ordered tasks and deliverables

1. After bases and asset payloads join, inspect every assigned `workflow.json` against its listed extends base. Use resolved target-package inspect output to compare effective nodes, schemas, sandbox declarations, property replacement names, models, callees and session policies to the accepted base plus original override. Record this matrix in `inheritance.json`.
2. Change wrapper workflow.json only for a demonstrated incompatibility after base migration. Preserve extends inheritance, Claude/Cursor backend/model patches and string replacement maps, including composer-2.5 on the Cursor implementation node. Do not duplicate base nodes/prompts into wrappers. Inherited effective behavior changes still go on the serial owner's release-impact list even if wrapper source is unchanged.
3. Run existing resolved base fixtures with each effective wrapper, adapting only scratch fixture node IDs/backend field names when inheritance requires it. Validate and inspect every wrapper with bases/callees/add-ons resolved. Assert acceptance/revision routes and the effective schema/authority contracts; record legitimate backend-specific divergences. Write `workflows.json` for helper scenario selection, using `{workflowId, expectedRoute}` entries where a base route is not reliable for the effective wrapper. Derive each route from the resolved graph, selected fixture and available expected-results documentation; preserve repeated steps and account for replacements. Confirm missing metadata and incompatible base routes fail, never disable route assertions. Include fixture identity and derivation evidence in `inheritance.json`. Send persistent map corrections to serial reconciliation; this worker does not edit expected-routes.json. Any producer issue found in a base is an exact repair request for serial reconciliation, not a concurrent base edit.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root tmp/registry-contract-migration/verification/compat-inheritance/validation
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --workflow-list tmp/registry-contract-migration/verification/compat-inheritance/workflows.json --evidence-root tmp/registry-contract-migration/verification/compat-inheritance/scenarios
mise run workflow:check-compact
git diff --check
```

## Completion criteria

- Source work may be accepted with an explicitly evidenced core #117 final installed YouTube blocker; raw failures remain failures and all-green completion/release stays blocked.
- Every inherited workflow validates after base migration and has effective contract/authority/backend evidence.
- No inheritance flattening or duplicate base edits; wrapper release impact is reported.
- Any outstanding base defect is explicitly handed to serial reconciliation.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.
