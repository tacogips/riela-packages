# compat-verification

Status: proposed for Step 5 review.

```json
{
  "planId": "compat-verification",
  "planPath": "impl-plans/active/compat-verification.md",
  "dependsOn": [],
  "writePaths": [
    "mise.toml",
    ".agents/skills/riela-package-release/scripts/check-package-compat.ts",
    ".agents/skills/riela-package-release/scripts/check-package-compat.test.ts",
    ".agents/skills/riela-package-release/fixtures/expected-routes.json"
  ],
  "sharedPaths": [],
  "progressFile": "tmp/registry-contract-migration/verification/compat-verification/progress.json",
  "verification": [
    "riela --version",
    "riela package install --help",
    "riela workflow run --help",
    "bun test ./.agents/skills/riela-package-release/scripts/check-package-compat.test.ts",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode manifests --source-root tmp/registry-contract-migration/verification/compat-verification/baseline --evidence-root tmp/registry-contract-migration/verification/compat-verification/baseline-manifests",
    "git diff --check"
  ],
  "baselineDiagnostics": [
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --source-root tmp/registry-contract-migration/verification/compat-verification/baseline --evidence-root tmp/registry-contract-migration/verification/compat-verification/baseline-workflows"
  ],
  "acceptanceCriteria": [
    "Inventory includes every repository package; baseline failures are preserved with source identity.",
    "Existing mise validation tasks use installed 0.2.1, isolated dependencies and repository-local scratch.",
    "Harness tests demonstrate coverage, required route assertions for every selected scenario, and failure propagation; no user registry writes or sibling writes.",
    "Source work may be accepted with an explicitly evidenced core #117 final installed YouTube blocker; raw failures remain failures and all-green completion/release stays blocked."
  ]
}
```

## Intent, context and non-goals

Resolve https://github.com/tacogips/riela-packages/issues/14 in `issue-resolution` mode using accepted `design-docs/specs/design-riela-021-package-compat.md` (Step 3 accepted, comm-000004, no findings). All packages are in scope; the intake's 39 failures are a diagnostic cohort, not an inventory limit. `codexAgentReferences: []`; preserve existing Cursor/Claude wrapper adaptations rather than introducing adapters. Issue title/body were unavailable; do not infer #114 from scratch directory names.

Use installed Riela 0.2.1 on `fix/registry-contract-migration`. Do not inspect the running workflow's registry/provenance, change sibling repositories, create worktrees/private branches, run concurrent Git mutations, release or merge. No graph/model/session redesign, broad formatting, vacuous schemas, permission escalation for review-only agents or unrelated cleanup. Review existing subtree AGENTS.md before editing. Do not modify unrelated D4 records.

## Continuation and #117 boundary

Continue from `475ffde2c35210427b1b92524854de3c8ec0c69e`, covering 65 packages / 59 workflows. Reuse the checkpointed harness and source-matched receipts; repair concrete gaps only. Riela core https://github.com/tacogips/riela/issues/117 tracks installed YouTube `unresolvedAddonExecutable`. Its repair is not a prerequisite for source edits, acceptance of usable verification infrastructure, or dependency-ready source-plan dispatch. Do not modify sibling repositories or installed user-scope packages; make no live model/provider calls.

Keep command exit status separate from plan readiness: record the exact failing command, complete log, source/tool identity, affected workflow and #117 attribution. Never convert a nonzero result to a pass, skip the affected inventory entry, weaken validation or classify unrelated failures as #117. Owned changed-package tests and deterministic mock assertions must pass; record the specifically blocked installed YouTube check separately. Missing material source verification or unresolved high/mid source defects still block source acceptance. Core #117 alone does not block independent review, accepted source commit or non-force push; full all-green compatibility and release remain blocked.

The Step 6 implementation output's `verification` array is for changed-source checks expected to pass. Put the untouched pre-migration workflow baseline, whose failures are the defects being repaired, in `baselineDiagnostics` with exact nonzero exit, count, source identity, and complete log; put the installed YouTube #117 case in `externalBlockers`. Do not report either as a passed check or as a failed changed-source verification. This distinction is required by the workflow's mechanical implementation-progress gate.

The plan's command lists specify required evidence collection; do not copy aggregate command results blindly into Step 6 output. Its `verification` array contains changed-source acceptance checks expected to pass, with any genuine changed-source failure retained as failing and blocking. Untouched pre-migration failures belong in `baselineDiagnostics`; the exact installed YouTube #117 failure belongs in `externalBlockers`. Keep complete aggregate logs and nonzero exits in `commands.json`, and link individual passing source-check receipts separately; never report a failing aggregate as passing. Any other residual failure requires exact baseline reproduction and a separate issue reference. Whole-catalog failures belonging to later dependency waves remain explicit pending owner tasks, not completed fixes or blanket #117 exceptions; serial reconciliation must account for every failure before source delivery.

Reuse a preserved baseline only when its audited source SHA-256 values, CLI executable hash/version, effective command arguments and dependency inputs match the intended baseline, and the original final exit and complete log are available. Record the old receipt paths and the hash comparison in the new attempt's `baseline.json`/`commands.json`; keep the receipt's original commit identity. Commit-label differences alone do not invalidate identical audited inputs. Do not rerun the 59-workflow baseline when this comparison passes. If hashes differ or required evidence is incomplete, regenerate only the affected baseline evidence from the intake commit under a fresh `tmp/` attempt. This reuse rule applies to every baseline command below and does not waive inventory drift detection or changed-source verification.

Each progress/handoff records source-task status separately from final-verification status, including `externalBlockers` with issue URL, command/exit/log evidence and follow-up. Formal downstream review, commit and push remain later workflow gates, not missing worker implementation tasks. After the core fix, serial finalization records the fixed CLI identity and reruns installed YouTube validation/scenarios and the full suite; preserve this pending obligation in plan status until it passes.

## Execution, drift and progress contract

This plan and the accepted design are checkpointed with the dispatch manifest by the later Riela checkpoint step before native fanout; this authoring step does not commit. Wait for every dependsOn plan's accepted source/infrastructure output under the #117 boundary above; do not wait for final all-green verification. All workers share this branch and directory. Write only the listed paths; only the reconciliation plan may repair shared paths after all other workers join. Do not edit this plan or another worker's progress log during execution.

Before each edit, freshly read the file and consumers. Save its bytes and SHA-256 plus an immutable intent record naming the requirement, proposed fields and expected behavior in your own evidence directory under `attempt-N/intent/`. Recheck the hash immediately before writing; on drift, re-read and reconcile the intended patch instead of overwriting. Save post-edit bytes/hash, exact changed paths and tests tied to those hashes. Check hashes again at handoff. Record any mismatch and pause the conflicting edit for serial reconciliation; never discard another worker's change. This detects non-atomic overwrite races but does not pretend to prevent them.

Use a new attempt directory; preserve old receipts. Command examples below name canonical evidence paths: expand each to a fresh attempt path consistently (including workflow-list/baseline inputs) before execution and record the exact argv. Never overwrite an earlier attempt. Maintain your own `progress.json` with task IDs, pending/running/passed/blocked status, source hashes, changed paths, exact argv/cwd, final exit, complete log path, case/assertion counts, findings and next action. Also write `handoff.json` with requirements-to-files/tests mapping, remaining failures, review decision and post-hashes. Run commands foreground; poll yielded processes until exit. Capture stdout/stderr without losing the command exit. `git diff --check` supplements behavioral checks, never substitutes for them.

Do not regenerate manifests, versions, dependency locks or registry-index.json in a parallel payload worker. Do not archive plans or run git add/commit/push in any worker. Serial finalization prepares an exact file list for Riela publication steps. Every changed input invalidates affected verification and review receipts.

## Shared invariants and evidence rules

Preserve agent output envelope routing (`when`) separately from business `payload` schemas. Trace consumed fields through forwarding add-ons and cross-workflow calls; do not require an agent to invent a later add-on's Git result. Require concrete prompt-compatible types and branch-aware required fields. Keep legitimate failure/revision/planning/skip outputs valid. Use read-only for JSON-only reviews/reporting and workspace-write for file writers; justify any existing broader authority individually. Preserve routing, models, backend overrides and session policy unless a proven compatibility defect demands a scoped correction.

All evidence, catalogs, installations, session stores and artifacts stay under repository-root `tmp/registry-contract-migration/verification/`. Record tool versions and source identity. Assert mock terminal state, observed payloads and branch traces, not fixture intent or CLI exit alone. Mocks do not prove actual sandbox enforcement. If mocks bypass schema rejection, use a supported installed validation entry point and state coverage limits. Missing dependencies/network and incomplete logs are blocked checks, not passes. Core #117 is already accepted by intake as an external final-verification blocker; preserve reproduction evidence without requiring its repair for source delivery. Other residual failures require independent baseline reproduction and a separately tracked issue; unexplained failures are blocking.

## Ordered tasks and deliverables

1. Inventory every package from `impl-plans/active/riela-021-inventory.json`; detect drift with the current tree. Record manifests, concrete/extended graphs, callees, add-ons, examples and skill files in `coverage.json`. When matching complete baseline evidence is unavailable, save a baseline source archive with `git archive --format=tar --output=tmp/registry-contract-migration/verification/compat-verification/baseline.tar 475ffde2c35210427b1b92524854de3c8ec0c69e`, extracting into your evidence directory (no checkout/worktree).
2. Read `riela package install --help`, `riela workflow run --help` and related target-validation help to establish isolated installation flags. This is CLI syntax research for repository package tests, not lookup of the running workflow. Set the isolated install root explicitly below tmp and fail closed if a command would use the real project/user registry. Do not repurpose HOME. Record resolved local payload paths and dependency versions/digests. Preserve canonical dependency package IDs, including scoped IDs.
3. Reuse and verify the checkpointed narrowly scoped `check-package-compat.ts` with `--mode manifests|workflows|scenarios|assets` and optional `--source-root`/`--evidence-root`. Defaults use this checkout and a fresh tmp evidence directory. Preserve the existing `package:validate` and `workflow:validate` wiring to its first two modes; repair only demonstrated gaps. Manifests mode validates every local manifest through installed CLI with source paths; workflows mode installs the local dependency closure into an isolated root, exposes bases/callees, detects duplicate workflow IDs and validates/inspects all concrete and effective inherited workflows. Never skip wrappers or externally dependent workflows. Record expanded commands and per-package outcomes; nonzero validation or unresolved dependencies cause nonzero exit. Do not edit package payloads in this plan.
4. Scenarios mode accepts `--workflow-list <JSON-array-file>` (omission means every packaged scenario) and uses existing fixture files in an isolated, dependency-resolved catalog, unique sessions/artifacts, verifying final status and expected routes/payloads. Every selected scenario must have an explicit expected route, either in its selection/fixture or in the repository-owned `.agents/skills/riela-package-release/fixtures/expected-routes.json`; missing route evidence fails closed, including the default selection. Derive the map's entries from each workflow graph, fixture and expected-results document, then verify them against observed mock traces; do not merely copy the observed route. Add a regression where a default-selected packaged fixture follows the wrong route. Honor relative fixture paths by selecting the proper cwd or absolute expansion. Include inherited fixtures from resolved bases; an inherited selection without its own reliable route must supply one explicitly. Assets mode accepts `--source-root`, audits all tracked skill/frontmatter/reference files and add-on descriptors, checks documented example syntax against installed CLI help, and records coverage/exclusions; do not execute credentialed/live examples. Keep checks focused, no generic framework. This helper centralizes existing check commands and evidence only; it must not reinterpret agent outputs or replace runtime validation.
5. Reuse existing tests and fill concrete coverage gaps with focused Bun tests in `check-package-compat.test.ts` for omitted inventory entries, duplicate IDs, dependency failures, inherited inclusion, nonzero exits and scenario assertion failure. Use local fixture roots/CLI stubs for harness tests and at least one installed-runtime smoke check. Before releasing dependent workers, reuse hash-matched complete receipts under the rule above or run the checkpointed helper on the untouched baseline source; account for actual legacy failures, missing tool limits, and every component of `mise run check` that is runnable without out-of-tree writes. For original full-check comparison without matching complete receipts, run the intake tree's unchanged `mise run check` in the disposable copy with any required source/build inputs also isolated under tmp; unavailable inputs are a recorded baseline gap, not proof that a new failure is pre-existing. Never run the original sibling-source command against a real sibling checkout.
6. Deliver baseline.json, coverage.json and commands.json with all failures and complete receipts. Payload validation failures expected at baseline do not block finishing this verification infrastructure plan when the harness tests pass and failures are accurately reported; the specific #117 installed YouTube failure also does not block that acceptance. Unavailable installed CLI or inability to isolate target installation blocks only the dependent behavioral checks that actually require it; report those gaps without manufacturing a running-workflow readiness blocker.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
riela --version
riela package install --help
riela workflow run --help
bun test ./.agents/skills/riela-package-release/scripts/check-package-compat.test.ts
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode manifests --source-root tmp/registry-contract-migration/verification/compat-verification/baseline --evidence-root tmp/registry-contract-migration/verification/compat-verification/baseline-manifests
git diff --check
```

Reuse matching complete receipts or run the `baselineDiagnostics` workflow command above. Preserve its nonzero result and complete log in diagnostic evidence, not in the Step 6 `verification` array.

## Completion criteria

- Source work may be accepted with an explicitly evidenced core #117 final installed YouTube blocker; raw failures remain failures and all-green completion/release stays blocked.
- Inventory includes every repository package; baseline failures are preserved with source identity.
- Existing mise validation tasks use installed 0.2.1, isolated dependencies and repository-local scratch.
- Harness tests demonstrate coverage, required route assertions for every selected scenario, and failure propagation; no user registry writes or sibling writes.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.
