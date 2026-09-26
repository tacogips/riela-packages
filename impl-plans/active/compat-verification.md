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
    ".agents/skills/riela-package-release/scripts/check-package-compat.test.ts"
  ],
  "sharedPaths": [],
  "progressFile": "tmp/registry-contract-migration/verification/compat-verification/progress.json",
  "verification": [
    "riela --version",
    "riela package install --help",
    "riela workflow run --help",
    "bun test .agents/skills/riela-package-release/scripts/check-package-compat.test.ts",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode manifests --source-root tmp/registry-contract-migration/verification/compat-verification/baseline --evidence-root tmp/registry-contract-migration/verification/compat-verification/baseline-manifests",
    "bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --source-root tmp/registry-contract-migration/verification/compat-verification/baseline --evidence-root tmp/registry-contract-migration/verification/compat-verification/baseline-workflows",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "Inventory includes every repository package; baseline failures are preserved with source identity.",
    "Existing mise validation tasks use installed 0.2.1, isolated dependencies and repository-local scratch.",
    "Harness tests demonstrate coverage and failure propagation; no user registry writes or sibling writes."
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

1. Inventory every package from `impl-plans/active/riela-021-inventory.json`; detect drift with the current tree. Record manifests, concrete/extended graphs, callees, add-ons, examples and skill files in `coverage.json`. Save a baseline source archive with `git archive --format=tar --output=tmp/registry-contract-migration/verification/compat-verification/baseline.tar b3bbf8c15760a56423b0d58120fc11f72280381a`, extracting into your evidence directory (no checkout/worktree).
2. Read `riela package install --help`, `riela workflow run --help` and related target-validation help to establish isolated installation flags. This is CLI syntax research for repository package tests, not lookup of the running workflow. Set the isolated install root explicitly below tmp and fail closed if a command would use the real project/user registry. Do not repurpose HOME. Record resolved local payload paths and dependency versions/digests. Preserve canonical dependency package IDs, including scoped IDs.
3. Implement the narrowly scoped `check-package-compat.ts` with `--mode manifests|workflows|scenarios|assets` and optional `--source-root`/`--evidence-root`. Defaults use this checkout and a fresh tmp evidence directory. Wire existing `package:validate` and `workflow:validate` tasks to its first two modes, replacing sibling Swift invocation. Manifests mode validates every local manifest through installed CLI with source paths; workflows mode installs the local dependency closure into an isolated root, exposes bases/callees, detects duplicate workflow IDs and validates/inspects all concrete and effective inherited workflows. Never skip wrappers or externally dependent workflows. Record expanded commands and per-package outcomes; nonzero validation or unresolved dependencies cause nonzero exit. Do not edit package payloads in this plan.
4. Scenarios mode accepts `--workflow-list <JSON-array-file>` (omission means every packaged scenario) and uses existing fixture files in an isolated, dependency-resolved catalog, unique sessions/artifacts, verifying final status and expected routes/payloads. Honor relative fixture paths by selecting the proper cwd or absolute expansion. Include inherited fixtures from resolved bases. Assets mode accepts `--source-root`, audits all tracked skill/frontmatter/reference files and add-on descriptors, checks documented example syntax against installed CLI help, and records coverage/exclusions; do not execute credentialed/live examples. Keep checks focused, no generic framework. This helper centralizes existing check commands and evidence only; it must not reinterpret agent outputs or replace runtime validation.
5. Add focused Bun tests in `check-package-compat.test.ts` for omitted inventory entries, duplicate IDs, dependency failures, inherited inclusion, nonzero exits and scenario assertion failure. Use local fixture roots/CLI stubs for harness tests and at least one installed-runtime smoke check. Before releasing dependent workers, run the new helper on the untouched baseline source, capture actual legacy failures, missing tool limits, and every component of `mise run check` that is runnable without out-of-tree writes. For original full-check comparison, run the intake tree's unchanged `mise run check` in the disposable copy with any required source/build inputs also isolated under tmp; unavailable inputs are a recorded baseline gap, not proof that a new failure is pre-existing. Never run the original sibling-source command against a real sibling checkout.
6. Deliver baseline.json, coverage.json and commands.json with all failures and complete receipts. Payload validation failures expected at baseline do not block finishing this verification infrastructure plan when the harness tests pass and failures are accurately reported; unavailable installed CLI or inability to isolate target installation does block dependent behavioral verification.

## Verification commands and required evidence

Run from repository root unless an explicit cwd is stated. The commands below are mandatory when their affected inputs exist; record unsupported CLI behavior as a blocked check, never silently skip it.

```sh
riela --version
riela package install --help
riela workflow run --help
bun test .agents/skills/riela-package-release/scripts/check-package-compat.test.ts
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode manifests --source-root tmp/registry-contract-migration/verification/compat-verification/baseline --evidence-root tmp/registry-contract-migration/verification/compat-verification/baseline-manifests
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --source-root tmp/registry-contract-migration/verification/compat-verification/baseline --evidence-root tmp/registry-contract-migration/verification/compat-verification/baseline-workflows
git diff --check
```

## Completion criteria

- Inventory includes every repository package; baseline failures are preserved with source identity.
- Existing mise validation tasks use installed 0.2.1, isolated dependencies and repository-local scratch.
- Harness tests demonstrate coverage and failure propagation; no user registry writes or sibling writes.

Complete your progress log and handoff only after each owned task has evidence or an explicitly blocked outcome. No unresolved high/mid finding may be marked complete. Independent implementation review remains a later gate.
