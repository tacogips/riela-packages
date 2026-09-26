# compat-agent-contracts-supporting

Status: proposed for Step 5 review.

```json
{
  "planId": "compat-agent-contracts-supporting",
  "planPath": "impl-plans/active/compat-agent-contracts-supporting.md",
  "dependsOn": [],
  "writePaths": [
    "packages/claude-code-worker-only-single-step/workflows/claude-code-worker-only-single-step",
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
    "packages/youtube-shorts-to-text-container/tests"
  ],
  "sharedPaths": [],
  "progressFile": "tmp/registry-contract-migration/verification/compat-agent-contracts-supporting/continuation-35d1e6a/attempt-1/progress.json",
  "verification": [
    "\"$RIELA_COMPAT_CLI\" --version",
    "shasum -a 256 \"$RIELA_COMPAT_CLI\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root \"$COMPAT_ATTEMPT/validation\"",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --workflow-list \"$COMPAT_ATTEMPT/workflows.json\" --evidence-root \"$COMPAT_ATTEMPT/scenarios\"",
    "bun packages/fable-and-improve-opus/tests/check-output-contract.ts --evidence-root \"$COMPAT_ATTEMPT/opus\"",
    "bun packages/fable-and-improve-codex/tests/check-output-contract.ts --evidence-root \"$COMPAT_ATTEMPT/codex\"",
    "bun packages/claude-code-worker-only-single-step/tests/check-compat.ts",
    "bun packages/fable-astra-design-plan-review-loop/tests/check-compat.ts",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "Every concrete agent has required authority and meaningful consumer-compatible output contracts.",
    "Every changed base has observed positive/negative behavioral coverage; no graph/model/session regression.",
    "Whole-catalog failures outside this owner are listed for wrapper/asset/finalization owners rather than hidden.",
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

Set `COMPAT_ATTEMPT` to the absolute repository root plus `tmp/registry-contract-migration/verification/compat-agent-contracts-supporting/continuation-35d1e6a/attempt-1`; if it already exists use the next unused attempt number and record the effective progressFile. Preserve the prior canonical progress log as historical evidence. Create `bin/riela` there as a symlink to `$RIELA_COMPAT_CLI`, prepend that bin directory to PATH and record `command -v riela` plus its resolved target so subprocesses use #117 too. Do not overwrite previous attempts, change HOME, build core or silently substitute a binary. Missing executables block dependent checks only. Canonical command paths below must be expanded consistently to the new attempt path and recorded in `commands.json`.

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

## Split ownership and retained task mapping

Current planning sizing receipt: `tmp/registry-contract-migration/verification/step4-plans-35d1e6a/ownership.json`; historical receipts remain under `step4-plans-78445b4/`. Refresh sizing before checkpoint after any ownership or test-path change.

The original contract is `impl-plans/active/compat-agent-contracts.md` at `78445b4919ce337cae550855431ec6bc21577265`. This plan owns exactly the 32 original paths listed above (all non-Codex workflow families, including Fable, Claude worker, Cursor developer, skills, greeting and YouTube). Its peer is `compat-agent-contracts`. The two plans have no dependency on each other and share no writes; both reuse completed `compat-verification`. Scope every task below to owned paths. Named examples for an unowned workflow are contract guidance and read-only consumer references, never edit authorization.

| Original task | Retained obligation | Execution/evidence owner |
| --- | --- | --- |
| 1 | Producer/consumer inventory and authority rationale | Both plans for their own producers; `<planId>:1` |
| 2 | Concrete node schemas, budgets and role-correct sandbox | Both plans for their own nodes; `<planId>:2` |
| 3 | Affected prompts, mocks and expected results | Both plans within their workflow roots; `<planId>:3` |
| 4 | Positive/negative package-local behavioral coverage | Both plans within their test roots; `<planId>:4` |
| 5 | Workflow selection, source-backed routes and handoff | Both plans with separate evidence roots; `<planId>:5` |

Retain original task IDs and contract obligations; continuation acceptance now removes the historical #117 waiver in accordance with the accepted design. Existing source changes and passing evidence are preserved, not restarted. Both own CLI identity checks, whole-catalog diagnostics, selected scenarios and diff checks. The supporting plan owns the two Fable output-contract commands; the Codex plan owns `mise run workflow:check-codex-dispatch`. Whole-catalog diagnostics remain visible without treating a peer's pending work as this branch's completed result. Reconciliation joins both selections and every contract receipt to retain complete coverage.

Keep existing cross-group call signatures and graph semantics fixed. Read external consumers freshly; record each cross-group handoff field and expected schema in `contracts.json`. Do not depend on an unaccepted peer edit. Missing peer-independent behavioral verification blocks branch acceptance; send an exact repair intent for serial integration without marking an unverified contract complete. Existing callee/base ordering within each owned family remains task 1's responsibility.

Before Step 5 acceptance and checkpoint, run `python3 tmp/registry-contract-migration/verification/step4-plans-35d1e6a/check-plans.py`; retain ownership.json, complete log and final exit. This source-backed enumerator checks core #118 directory semantics, unchanged checkpoint ownership, manifest/header equality, DAG, no concurrent ancestor overlaps, and contract counts including reserved tests. Both contracts must remain at most 400 expanded entries before dispatch, with the 512-entry runtime ceiling retained. Do not drop paths/tests to make counts fit; any ownership change needs renewed plan review. If the scratch checker is unavailable in a later environment, reproduce those stated checks against the plan headers and runner source; absence is not a workflow-provenance blocker.

## Ordered tasks and deliverables

1. Order concrete changes by existing callee/base dependencies; keep a single owner for coupled producer/consumer contracts. Use the inventory's exact `agentNodes` nodePath/promptPath/conditionalConsumers as the starting file list. Re-read every concrete graph and producer prompt, including already migrated Fable/Codex orchestration nodes; do not assume existing contracts are wrong. Record in `contracts.json` each producer path, prompt path, downstream step/template reference, payload fields/types/required conditions, current/proposed authority and reason, plus affected fixtures. Include a compatible-unchanged disposition. Trace add-on forwarding and cross-workflow consumers beyond local conditional edges before choosing fields.
2. In the assigned workflow directories edit only `nodes/*.json` (and nested node files if present) for missing/incorrect agentSandbox and concrete output.jsonSchema/required validation budget. Keep unconditional terminal nodes schema-free unless a real consumer requires a contract. Use existing supported authored sandbox spellings. Preserve valid schemas; do not replace them with generic object contracts. The simple-work reviewer must describe needs_revision, findings severity/file/line/message, feedback strings and accepted; its when routing stays outside the payload schema. Check branch-specific commit requirements and existing relay fields.
3. Adjust only affected `prompts/*.md`, `mock-scenario.json` and `EXPECTED_RESULTS.md` where needed to align with existing intended contracts. Preserve concrete non-agent workflows unless a verified contract issue affects them. If graph changes appear necessary, surface the contradiction for review rather than inventing architecture. Do not change models/backends/session reuse.
4. Extend package-local `tests/` (existing runners first) for each materially changed base family: accepted and revision routes, missing/malformed consumed fields, conditional commit fields and cross-workflow output handoffs. Add package-local `tests/check-compat.ts` only where no appropriate runner exists; invoke each with `bun packages/<package>/tests/check-compat.ts` and record expanded command. Use the installed helper scenarios mode for existing mocks and runtime assertions. Reuse Fable output-contract tests unchanged if their contract already passes. Preserve negative-test integrity: malformed output must reach the actual validating producer.
5. Write `workflows.json` as the exact JSON array of owned workflows with an existing mock fixture (or selection objects with explicit `expectedRoute` when needed): `claude-code-worker-only-single-step`, `fable-and-improve-codex`, `fable-and-improve-opus`, and `fable-astra-design-plan-review-loop`. Do not require a scenario from the other 12 owned workflows without fixtures; validate and inspect them through `--mode workflows` instead, retaining their contract inventory and any package-local tests. Write `contracts.json` with cases mapped to each changed producer. Deliver file hashes, acceptance traces, rejection evidence and unchanged graph/model comparisons against baseline. For every selected fixture, derive the route from the graph, fixture and available expected-results documentation; use the accepted map/fixture route or an explicit selection route, never an observed-only oracle. Hand any required map correction to serial reconciliation; do not write the completed verification map. Missing external dependency resolution is handled through the helper, never by deleting an add-on.

## Verification result interpretation

The workflows helper validates and inspects the full 59-workflow catalog; `--workflow-list` selects scenarios only and does not filter workflows mode. Read `<validation-evidence>/commands.json` and `coverage.json`: require both `validate-<workflowId>` and `inspect-<workflowId>` exit 0 for every owned workflow, except an exact dependency-lock defect assigned to the serial owner as pending final verification. Retain the full helper exit even when only later-wave failures remain. In scenarios mode require every selected case's CLI exit and `scenario-assert-<workflowId>` result to pass, with completed status, exact expected route and matching payload assertions. Do not use an empty selection or CLI exit alone as success.

For each required command, capture complete stdout/stderr plus final exit in the attempt's commands.json; record source hashes and test/assertion counts. A passing structural check cannot replace an applicable behavioral check. Run existing configured typecheck/build for code actually changed; document no configured check where applicable. Inventory and verify examples from owned README/skill/add-on paths; no live providers. Every own progress update preserves earlier attempt receipts; handoff includes changed paths, pre/post hashes, immutable intent, findings, ownership transfers and next action.

The four fixture-bearing IDs are listed in task 5. The following 12 require validate/inspect evidence and explicit `scenario: not-applicable` (no fixture), with all underlying files retained:

| Workflow ID | Definition path |
| --- | --- |
| `cursor-cli-developer-workflows` | `packages/cursor-cli-developer-workflows/workflows/cursor-cli-developer-workflows/workflow.json` |
| `greeting-container` | `packages/greeting-container/workflows/greeting-container/workflow.json` |
| `greeting-shell` | `packages/greeting-shell/workflows/greeting-shell/workflow.json` |
| `riela-package-installer-skill` | `packages/riela-package-installer-skill/workflows/riela-package-installer-skill/workflow.json` |
| `riela-package-manager-skill` | `packages/riela-package-manager-skill/workflows/riela-package-manager-skill/workflow.json` |
| `riela-package-release-skill` | `packages/riela-package-release-skill/workflows/riela-package-release-skill/workflow.json` |
| `riela-project-workflow-skill` | `packages/riela-project-workflow-skill/workflows/riela-project-workflow-skill/workflow.json` |
| `riela-temporary-workflow-skill` | `packages/riela-temporary-workflow-skill/workflows/riela-temporary-workflow-skill/workflow.json` |
| `riela-workflow-creator-skill` | `packages/riela-workflow-creator-skill/workflows/riela-workflow-creator-skill/workflow.json` |
| `riela-workflow-skill-creator-skill` | `packages/riela-workflow-skill-creator-skill/workflows/riela-workflow-skill-creator-skill/workflow.json` |
| `youtube-mp4-to-text` | `packages/youtube-mp4-to-text-workflow/workflows/youtube-mp4-to-text/workflow.json` |
| `youtube-shorts-to-text-container` | `packages/youtube-shorts-to-text-container/workflows/youtube-shorts-to-text-container/workflow.json` |

YouTube workflow source/contract issues remain this owner's responsibility; only manifest/lock writes transfer to compat-reconcile with exact proposed fields. No missing-fixture task is created.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root "$COMPAT_ATTEMPT/validation"
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --workflow-list "$COMPAT_ATTEMPT/workflows.json" --evidence-root "$COMPAT_ATTEMPT/scenarios"
bun packages/fable-and-improve-opus/tests/check-output-contract.ts --evidence-root "$COMPAT_ATTEMPT/opus"
bun packages/fable-and-improve-codex/tests/check-output-contract.ts --evidence-root "$COMPAT_ATTEMPT/codex"
git diff --check
```

Package-local commands below are separate behavioral checks; each needs its own complete receipt. Preserve their current assertions and rerun affected inputs; add a command to this list only when task 4 creates another required test.

```sh
bun packages/claude-code-worker-only-single-step/tests/check-compat.ts
bun packages/fable-astra-design-plan-review-loop/tests/check-compat.ts
```

## Completion criteria

- Owned source verification passes; later-wave failures retain exact evidence and assigned repair owners. Final reconciliation permits no historical #117 waiver or unresolved required check.
- Every concrete agent has required authority and meaningful consumer-compatible output contracts.
- Every changed base has observed positive/negative behavioral coverage; no graph/model/session regression.
- Whole-catalog failures outside this owner are listed for wrapper/asset/finalization owners rather than hidden.

Run any existing configured typecheck/build for changed code and record its exact command/result; if none is configured, state that limit without inventing a project. Update affected documentation/EXPECTED_RESULTS.md only for changed behavior.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.

## Author review handoff

Step 3 accepted the design in comm-000004 with no findings. Step 5 review of these revised plan instructions is pending. Preserve prior plan receipts and the source-matched supporting implementation review; reuse only evidence whose audited inputs still match. Current author checks and ownership enumeration are recorded in `tmp/registry-contract-migration/verification/step4-plans-35d1e6a/commands.json`. Package implementation/verification remains downstream; the author does not claim those commands have passed.
