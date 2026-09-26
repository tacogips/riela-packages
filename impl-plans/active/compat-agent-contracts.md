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
  "progressFile": "tmp/registry-contract-migration/verification/compat-agent-contracts/continuation-b212240/attempt-1/progress.json",
  "verification": [
    "\"$RIELA_COMPAT_CLI\" --version",
    "shasum -a 256 \"$RIELA_COMPAT_CLI\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root \"$COMPAT_ATTEMPT/validation\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --workflow-list \"$COMPAT_ATTEMPT/workflows.json\" --evidence-root \"$COMPAT_ATTEMPT/scenarios\"",
    "mise run workflow:check-codex-dispatch",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "Every concrete agent has required authority and meaningful consumer-compatible output contracts.",
    "Every changed base has observed positive/negative behavioral coverage; no graph/model/session regression.",
    "Whole-catalog failures outside this owner are listed for wrapper/asset/finalization owners rather than hidden.",
    "Owned source verification passes; later-wave failures retain exact evidence and assigned repair owners. Final reconciliation permits no historical #117 waiver or unresolved required check."
  ]
}
```

## Intent, context and non-goals

Continue https://github.com/tacogips/riela-packages/issues/14 from `b212240228ca02d9532d442bcf454b320e4affe3` on `fix/registry-contract-migration` for Draft PR #15 in `issue-resolution` mode. Step 3 comm-000004 accepted `design-docs/specs/design-riela-021-package-compat.md` with no findings. Preserve all five plans and checkpointed source work. Scope remains 65 packages, 59 workflows and all examples. Intake reports 14 Codex/four supporting mocks, two new fixtures and asset audit passing with #117; recheck affected inputs and final integration. The 50 reported validation-command failures (mainly 24 inherited wrappers and YouTube) are actual failures, not passing baseline checks or 50 unique workflows.

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

Set `COMPAT_ATTEMPT` to the absolute repository root plus `tmp/registry-contract-migration/verification/compat-agent-contracts/continuation-b212240/attempt-1`; if it already exists use the next unused attempt number and record the effective progressFile. Preserve the prior canonical progress log as historical evidence. Create `bin/riela` there as a symlink to `$RIELA_COMPAT_CLI`, prepend that bin directory to PATH and record `command -v riela` plus its resolved target so subprocesses use #117 too. Do not overwrite previous attempts, change HOME, build core or silently substitute a binary. Missing executables block dependent checks only. Canonical command paths below must be expanded consistently to the new attempt path and recorded in `commands.json`.

## Continuation and failure accounting

Riela https://github.com/tacogips/riela/issues/117 is the related fix reference, not a presumed outstanding blocker or acceptance waiver. Diagnose fresh failures using the supplied #117 executable. Keep failing commands in `verification` with their nonzero exits; preserve historical comparisons in `baselineDiagnostics`. Use `externalBlockers` only for newly demonstrated external defects with exact command/log/exit evidence. Every reported command failure relevant to this owner must map to a workflow, diagnosis, owner and final result in `failure-accounting.json`; never discard inventory entries, weaken validation or convert aggregate failure to success.

An earlier wave may finish its owned source tasks while documented later-wave repairs remain pending: assign each pending wrapper defect to compat-inheritance and each manifest/dependency-lock defect to compat-reconcile, with exact paths and field-level intent. An owned contract failure or missing owned material verification blocks that owner. Full-catalog aggregate failures remain failed even when an owner's individual checks pass. The final reconciliation gate requires all requested checks passing; a historical failure or baseline reproduction grants no exception. This permits dependency-ready progress without claiming compatibility completion early.

Reuse receipts only after matching audited file hashes, CLI hash/version, dependencies, effective arguments, final exit and complete logs; record comparisons and original receipt paths. If mismatch or incomplete, rerun affected checks. Baseline copies, if needed, use checkpoint b212240 under repository tmp; no extra worktrees. Preserve the two checkpointed fixtures and all existing route assertions. The 12 fixtureless supporting workflows require validate/inspect receipts, never a manufactured scenario requirement. All examples require a recorded deterministic check or static invocation/asset verification where live execution is excluded, with the limit stated.

Formal independent reviews, checkpoint/publication and final commit/push are later Riela gates. Step 6 completion covers assigned source tasks and their verification, not those later gates. Report source status and final-verification status separately. No unresolved high/mid owned finding is complete; no final acceptance while required checks fail or are blocked.

For the Step 6 progress gate, report each executed `bun packages/<owned-package>/tests/check-compat.ts` separately in the `verification` array with its actual `exitCode: 0`, a positive `testsRun` or `testCount`, and the complete log path. A combined semicolon-separated command or a prose summary is not a substitute for these command receipts. Keep the failed whole-catalog workflow check as a separate nonzero diagnostic with its downstream owner; never mark it passed.

## Execution, drift and progress contract

This plan and the accepted design are committed and non-force pushed with the dispatch manifest by the later Riela checkpoint step before native fanout (a failed checkpoint push stops dispatch); this authoring step does not commit. Wait for every dependsOn plan's accepted source/infrastructure output under the ownership/failure-accounting rules above; do not wait for downstream review/publication. All workers share this branch and directory. Write only the listed paths; only the reconciliation plan may repair shared paths after all other workers join. Do not edit this plan or another worker's progress log during execution.

Before each edit, freshly read the file and consumers. Save its bytes and SHA-256 plus an immutable intent record naming the requirement, proposed fields and expected behavior in your own evidence directory under `attempt-N/intent/`. Recheck the hash immediately before writing; on drift, re-read and reconcile the intended patch instead of overwriting. Save post-edit bytes/hash, exact changed paths and tests tied to those hashes. Check hashes again at handoff. Record any mismatch and pause the conflicting edit for serial reconciliation; never discard another worker's change. This detects non-atomic overwrite races but does not pretend to prevent them.

Use a new attempt directory; preserve old receipts. Command examples below name canonical evidence paths: expand each to a fresh attempt path consistently (including workflow-list/baseline inputs) before execution and record the exact argv. Never overwrite an earlier attempt. Maintain your own `progress.json` with task IDs, pending/running/passed/blocked status, source hashes, changed paths, exact argv/cwd, final exit, complete log path, case/assertion counts, findings and next action. Also write `handoff.json` with requirements-to-files/tests mapping, remaining failures, review decision and post-hashes. Run commands foreground; poll yielded processes until exit. Capture stdout/stderr without losing the command exit. `git diff --check` supplements behavioral checks, never substitutes for them.

Only compat-reconcile may regenerate manifests, versions, dependency locks or registry-index.json, after all payload workers join. Do not archive plans or run git add/commit/push in any worker. Serial finalization prepares an exact file list for Riela publication steps. Every changed input invalidates affected verification and review receipts.

## Shared invariants and evidence rules

Preserve agent output envelope routing (`when`) separately from business `payload` schemas. Trace consumed fields through forwarding add-ons and cross-workflow calls; do not require an agent to invent a later add-on's Git result. Require concrete prompt-compatible types and branch-aware required fields. Keep legitimate failure/revision/planning/skip outputs valid. Use read-only for JSON-only reviews/reporting and workspace-write for file writers; justify any existing broader authority individually. Preserve routing, models, backend overrides and session policy unless a proven compatibility defect demands a scoped correction.

All evidence, catalogs, installations, session stores and artifacts stay under repository-root `tmp/registry-contract-migration/verification/`. Record tool versions and source identity. Assert mock terminal state, observed payloads and branch traces, not fixture intent or CLI exit alone. Mocks do not prove actual sandbox enforcement. If mocks bypass schema rejection, use a supported installed validation entry point and state coverage limits. Missing dependencies/network and incomplete logs are blocked checks, not passes. Historical #117 failures confer no waiver. Record fresh failures explicitly; owned defects block owner acceptance and any required final failure blocks completion.

## Split ownership and retained task mapping

Current planning sizing receipt: `tmp/registry-contract-migration/verification/step4-plans-b212240/ownership.json`; historical receipts remain under `step4-plans-78445b4/`. Refresh sizing before checkpoint after any ownership or test-path change.

The original contract is `impl-plans/active/compat-agent-contracts.md` at `78445b4919ce337cae550855431ec6bc21577265`. This plan owns exactly the 28 original paths listed above (Codex workflow families). Its peer is `compat-agent-contracts-supporting`. The two plans have no dependency on each other and share no writes; both reuse completed `compat-verification`. Scope every task below to owned paths. Named examples for an unowned workflow are contract guidance and read-only consumer references, never edit authorization.

| Original task | Retained obligation | Execution/evidence owner |
| --- | --- | --- |
| 1 | Producer/consumer inventory and authority rationale | Both plans for their own producers; `<planId>:1` |
| 2 | Concrete node schemas, budgets and role-correct sandbox | Both plans for their own nodes; `<planId>:2` |
| 3 | Affected prompts, mocks and expected results | Both plans within their workflow roots; `<planId>:3` |
| 4 | Positive/negative package-local behavioral coverage | Both plans within their test roots; `<planId>:4` |
| 5 | Workflow selection, source-backed routes and handoff | Both plans with separate evidence roots; `<planId>:5` |

Retain original task IDs and contract obligations; continuation acceptance now removes the historical #117 waiver in accordance with the accepted design. Existing source changes and passing evidence are preserved, not restarted. Both own CLI identity checks, whole-catalog diagnostics, selected scenarios and diff checks. The supporting plan owns the two Fable output-contract commands; the Codex plan owns `mise run workflow:check-codex-dispatch`. Whole-catalog diagnostics remain visible without treating a peer's pending work as this branch's completed result. Reconciliation joins both selections and every contract receipt to retain complete coverage.

Keep existing cross-group call signatures and graph semantics fixed. Read external consumers freshly; record each cross-group handoff field and expected schema in `contracts.json`. Do not depend on an unaccepted peer edit. Missing peer-independent behavioral verification blocks branch acceptance; send an exact repair intent for serial integration without marking an unverified contract complete. Existing callee/base ordering within each owned family remains task 1's responsibility.

Before Step 5 acceptance and checkpoint, run `python3 tmp/registry-contract-migration/verification/step4-plans-b212240/check-plans.py`; retain ownership.json, complete log and final exit. This source-backed enumerator checks core #118 directory semantics, unchanged checkpoint ownership, manifest/header equality, DAG, no concurrent ancestor overlaps, and contract counts including reserved tests. Both contracts must remain at most 400 expanded entries before dispatch, with the 512-entry runtime ceiling retained. Do not drop paths/tests to make counts fit; any ownership change needs renewed plan review. If the scratch checker is unavailable in a later environment, reproduce those stated checks against the plan headers and runner source; absence is not a workflow-provenance blocker.

## Ordered tasks and deliverables

1. Order concrete changes by existing callee/base dependencies; keep a single owner for coupled producer/consumer contracts. Use the inventory's exact `agentNodes` nodePath/promptPath/conditionalConsumers as the starting file list. Re-read every concrete graph and producer prompt, including already migrated Fable/Codex orchestration nodes; do not assume existing contracts are wrong. Record in `contracts.json` each producer path, prompt path, downstream step/template reference, payload fields/types/required conditions, current/proposed authority and reason, plus affected fixtures. Include a compatible-unchanged disposition. Trace add-on forwarding and cross-workflow consumers beyond local conditional edges before choosing fields.
2. In the assigned workflow directories edit only `nodes/*.json` (and nested node files if present) for missing/incorrect agentSandbox and concrete output.jsonSchema/required validation budget. Keep unconditional terminal nodes schema-free unless a real consumer requires a contract. Use existing supported authored sandbox spellings. Preserve valid schemas; do not replace them with generic object contracts. The simple-work reviewer must describe needs_revision, findings severity/file/line/message, feedback strings and accepted; its when routing stays outside the payload schema. Check branch-specific commit requirements and existing relay fields.
3. Adjust only affected `prompts/*.md`, `mock-scenario.json` and `EXPECTED_RESULTS.md` where needed to align with existing intended contracts. Preserve concrete non-agent workflows unless a verified contract issue affects them. If graph changes appear necessary, surface the contradiction for review rather than inventing architecture. Do not change models/backends/session reuse.
4. Extend package-local `tests/` (existing runners first) for each materially changed base family: accepted and revision routes, missing/malformed consumed fields, conditional commit fields and cross-workflow output handoffs. Add package-local `tests/check-compat.ts` only where no appropriate runner exists; invoke each with `bun packages/<package>/tests/check-compat.ts` and record expanded command. Use the installed helper scenarios mode for existing mocks and runtime assertions. Reuse Fable output-contract tests unchanged if their contract already passes. Preserve negative-test integrity: malformed output must reach the actual validating producer.
5. Write `workflows.json` as the exact JSON array of owned concrete workflow IDs (or selection objects with explicit `expectedRoute` when needed) and `contracts.json` with cases mapped to each changed producer. Deliver file hashes, acceptance traces, rejection evidence and unchanged graph/model comparisons against baseline. For every selected fixture, derive the route from the graph, fixture and available expected-results documentation; use the accepted map/fixture route or an explicit selection route, never an observed-only oracle. Hand any required map correction to serial reconciliation; do not write the completed verification map. Missing external dependency resolution is handled through the helper, never by deleting an add-on.

## Verification result interpretation

The workflows helper validates and inspects the full 59-workflow catalog; `--workflow-list` selects scenarios only and does not filter workflows mode. Read `<validation-evidence>/commands.json` and `coverage.json`: require both `validate-<workflowId>` and `inspect-<workflowId>` exit 0 for every owned workflow, except an exact dependency-lock defect assigned to the serial owner as pending final verification. Retain the full helper exit even when only later-wave failures remain. In scenarios mode require every selected case's CLI exit and `scenario-assert-<workflowId>` result to pass, with completed status, exact expected route and matching payload assertions. Do not use an empty selection or CLI exit alone as success.

For each required command, capture complete stdout/stderr plus final exit in the attempt's commands.json; record source hashes and test/assertion counts. A passing structural check cannot replace an applicable behavioral check. Run existing configured typecheck/build for code actually changed; document no configured check where applicable. Inventory and verify examples from owned README/skill/add-on paths; no live providers. Every own progress update preserves earlier attempt receipts; handoff includes changed paths, pre/post hashes, immutable intent, findings, ownership transfers and next action.

Preserve and explicitly recheck the two checkpointed fixture paths:

- `packages/codex-source-security-check-loop/workflows/codex-source-security-check-loop/mock-scenario.json`
- `packages/codex-task-watchdog/workflows/codex-task-watchdog/mock-scenario.json`

The owned selection contains all 14 workflow IDs from this plan's workflow-directory writePaths; all have fixtures. Preserve existing source-backed routes and record individual receipts.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root "$COMPAT_ATTEMPT/validation"
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --workflow-list "$COMPAT_ATTEMPT/workflows.json" --evidence-root "$COMPAT_ATTEMPT/scenarios"
mise run workflow:check-codex-dispatch
git diff --check
```

## Completion criteria

- Owned source verification passes; later-wave failures retain exact evidence and assigned repair owners. Final reconciliation permits no historical #117 waiver or unresolved required check.
- Every concrete agent has required authority and meaningful consumer-compatible output contracts.
- Every changed base has observed positive/negative behavioral coverage; no graph/model/session regression.
- Whole-catalog failures outside this owner are listed for wrapper/asset/finalization owners rather than hidden.

Run any existing configured typecheck/build for changed code and record its exact command/result; if none is configured, state that limit without inventing a project. Update affected documentation/EXPECTED_RESULTS.md only for changed behavior.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.

## Author review handoff

Step 3 accepted the design in comm-000004 with no findings. Step 5 review of this continuation is pending; prior plan acceptance is historical. Current author checks and ownership enumeration are recorded in `tmp/registry-contract-migration/verification/step4-plans-b212240/commands.json`. Package implementation/verification remains downstream; the author does not claim those commands have passed.
