# compat-agent-contracts

Status: proposed for Step 5 review.

```json
{
  "planId": "compat-agent-contracts",
  "planPath": "impl-plans/active/compat-agent-contracts.md",
  "dependsOn": [],
  "writePaths": [
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
    "packages/codex-website-builder/tests"
  ],
  "sharedPaths": [],
  "progressFile": "tmp/registry-contract-migration/verification/compat-agent-contracts/progress.json",
  "verification": [
    "\"$RIELA_COMPAT_CLI\" --version",
    "shasum -a 256 \"$RIELA_COMPAT_CLI\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root tmp/registry-contract-migration/verification/compat-agent-contracts/validation",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --workflow-list tmp/registry-contract-migration/verification/compat-agent-contracts/workflows.json --evidence-root tmp/registry-contract-migration/verification/compat-agent-contracts/scenarios",
    "mise run workflow:check-codex-dispatch",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "Every concrete agent has required authority and meaningful consumer-compatible output contracts.",
    "Every changed base has observed positive/negative behavioral coverage; no graph/model/session regression.",
    "Whole-catalog failures outside this owner are listed for wrapper/asset/finalization owners rather than hidden.",
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

## Split ownership and retained task mapping

Step 4 source-backed sizing passed: 348 current expanded entries, 362 including reserved new test files, and 150 entries remaining below 512 after reservations. Full enumeration and original-task comparisons are in `tmp/registry-contract-migration/verification/step4-plans-78445b4/ownership.json`; sizing command exited 0 with complete `06.log`. The current unsplit tree enumerates 541 entries; retain the intake's 514 as historical evidence, not a fresh count. Both splits meet 400 without dropping any original path.

The original contract is `impl-plans/active/compat-agent-contracts.md` at `78445b4919ce337cae550855431ec6bc21577265`. This plan owns exactly the 28 original paths listed above (Codex workflow families). Its peer is `compat-agent-contracts-supporting`. The two plans have no dependency on each other and share no writes; both reuse completed `compat-verification`. Scope every task below to owned paths. Named examples for an unowned workflow are contract guidance and read-only consumer references, never edit authorization.

| Original task | Retained obligation | Execution/evidence owner |
| --- | --- | --- |
| 1 | Producer/consumer inventory and authority rationale | Both plans for their own producers; `<planId>:1` |
| 2 | Concrete node schemas, budgets and role-correct sandbox | Both plans for their own nodes; `<planId>:2` |
| 3 | Affected prompts, mocks and expected results | Both plans within their workflow roots; `<planId>:3` |
| 4 | Positive/negative package-local behavioral coverage | Both plans within their test roots; `<planId>:4` |
| 5 | Workflow selection, source-backed routes and handoff | Both plans with separate evidence roots; `<planId>:5` |

All four original JSON acceptance criteria and completion bullets remain verbatim in both plans. All original invariants and ordered-task text remain below. Both own CLI identity checks, whole-catalog diagnostics, selected scenarios and diff checks. The supporting plan owns the two Fable output-contract commands; the Codex plan owns `mise run workflow:check-codex-dispatch`. Whole-catalog diagnostics remain visible without treating a peer's pending work as this branch's completed result. Reconciliation joins both selections and every contract receipt to retain complete coverage.

Keep existing cross-group call signatures and graph semantics fixed. Read external consumers freshly; record each cross-group handoff field and expected schema in `contracts.json`. Do not depend on an unaccepted peer edit. Missing peer-independent behavioral verification blocks branch acceptance; send an exact repair intent for serial integration without marking an unverified contract complete. Existing callee/base ordering within each owned family remains task 1's responsibility.

Before Step 5 acceptance and the checkpoint, run `python3 tmp/registry-contract-migration/verification/step4-plans-78445b4/check-plans.py` and retain its `ownership.json`, complete log and final exit. This source-backed sizing checker enumerates declared roots (including missing roots), every directory and descendant, deduplicates entries, rejects symlinks/special entries and enforces file/aggregate byte limits using core #118 `WorkflowFanoutChangeEvidence.swift:94-163`. It compares the original 60-path union, tasks, criteria, concurrent ancestor overlaps, manifest/header equality and DAG. Each split must remain at most 400 expanded entries, including known new-file reservations. It reserves one new `tests/check-compat.ts` per owned workflow when absent; additional planned files require a refreshed count before checkpoint. Never discard original paths or tests to reduce size. Recheck after input changes and before dispatch. After checkpoint, do not exceed the 512-entry runtime ceiling as tests are added. Only the plan author may rebalance whole workflow/test pairs before renewed plan review if the 400 bound fails.

## Ordered tasks and deliverables

1. Order concrete changes by existing callee/base dependencies; keep a single owner for coupled producer/consumer contracts. Use the inventory's exact `agentNodes` nodePath/promptPath/conditionalConsumers as the starting file list. Re-read every concrete graph and producer prompt, including already migrated Fable/Codex orchestration nodes; do not assume existing contracts are wrong. Record in `contracts.json` each producer path, prompt path, downstream step/template reference, payload fields/types/required conditions, current/proposed authority and reason, plus affected fixtures. Include a compatible-unchanged disposition. Trace add-on forwarding and cross-workflow consumers beyond local conditional edges before choosing fields.
2. In the assigned workflow directories edit only `nodes/*.json` (and nested node files if present) for missing/incorrect agentSandbox and concrete output.jsonSchema/required validation budget. Keep unconditional terminal nodes schema-free unless a real consumer requires a contract. Use existing supported authored sandbox spellings. Preserve valid schemas; do not replace them with generic object contracts. The simple-work reviewer must describe needs_revision, findings severity/file/line/message, feedback strings and accepted; its when routing stays outside the payload schema. Check branch-specific commit requirements and existing relay fields.
3. Adjust only affected `prompts/*.md`, `mock-scenario.json` and `EXPECTED_RESULTS.md` where needed to align with existing intended contracts. Preserve concrete non-agent workflows unless a verified contract issue affects them. If graph changes appear necessary, surface the contradiction for review rather than inventing architecture. Do not change models/backends/session reuse.
4. Extend package-local `tests/` (existing runners first) for each materially changed base family: accepted and revision routes, missing/malformed consumed fields, conditional commit fields and cross-workflow output handoffs. Add package-local `tests/check-compat.ts` only where no appropriate runner exists; invoke each with `bun packages/<package>/tests/check-compat.ts` and record expanded command. Use the installed helper scenarios mode for existing mocks and runtime assertions. Reuse Fable output-contract tests unchanged if their contract already passes. Preserve negative-test integrity: malformed output must reach the actual validating producer.
5. Write `workflows.json` as the exact JSON array of owned concrete workflow IDs (or selection objects with explicit `expectedRoute` when needed) and `contracts.json` with cases mapped to each changed producer. Deliver file hashes, acceptance traces, rejection evidence and unchanged graph/model comparisons against baseline. For every selected fixture, derive the route from the graph, fixture and available expected-results documentation; use the accepted map/fixture route or an explicit selection route, never an observed-only oracle. Hand any required map correction to serial reconciliation; do not write the completed verification map. Missing external dependency resolution is handled through the helper, never by deleting an add-on.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root tmp/registry-contract-migration/verification/compat-agent-contracts/validation
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --workflow-list tmp/registry-contract-migration/verification/compat-agent-contracts/workflows.json --evidence-root tmp/registry-contract-migration/verification/compat-agent-contracts/scenarios
mise run workflow:check-codex-dispatch
git diff --check
```

## Completion criteria

- Source work may be accepted with an explicitly evidenced core #117 final installed YouTube blocker; raw failures remain failures and all-green completion/release stays blocked.
- Every concrete agent has required authority and meaningful consumer-compatible output contracts.
- Every changed base has observed positive/negative behavioral coverage; no graph/model/session regression.
- Whole-catalog failures outside this owner are listed for wrapper/asset/finalization owners rather than hidden.

Run any existing configured typecheck/build for changed code and record its exact command/result; if none is configured, state that limit without inventing a project. Update affected documentation/EXPECTED_RESULTS.md only for changed behavior.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.
