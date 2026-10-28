# Opus Luna gate and routing fixes (0.1.10)

Issues: tacogips/riela #125, #126, #128, #129, #132, #134 (local texts
`tmp/run/issue-<N>.md`).
Package: `packages/opus-terra-design-and-implement-review-loop` (0.1.9 -> 0.1.10).
Workflow root below: `packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/`
(scripts live in `<workflow root>/scripts/`, not in the package root).

Baseline: no existing design covers these six failure modes.
`design-docs/specs/design-opus-terra-wave-input-compaction.md` (wave summary)
is unrelated and stays unchanged; its bounds and rules still apply.

## Problem

Each issue ends a long live run with `failed`/`blocked` even though the work is
correct, or loops until an operator steps in:

| Issue | Where | Failure |
| --- | --- | --- |
| #125 | `implementation-progress-check.py` `behavioral_kind()` | A structured passing record from a runner outside the regex allowlist (`node tmp/.../smoke.mjs`, `testsRun: 2`, `failureCount: 0`) is not behavioral evidence, so the branch is `implementation-materially-unverified`. The resume text does not say what would be accepted. |
| #126 | same script, `classify()` | Any non-empty `blockers` gives `implementation-dependency`. That includes a workspace-wide `cargo fmt --check` that failed only on a file owned by a concurrently running sibling plan. |
| #128 | `dispatch-plans` | The 512-entry snapshot check runs only when a wave is dispatched. By then the manifest is committed and immutable, so the session fails (`provider_error`, or runtime `policyBlocked`) with no recovery. |
| #129 | `step8-docs-refresh` / `step9-commit-message` | Step 8's sandbox denies `mv`/`git mv`. Step 9 rejects because plans are still in `impl-plans/active`, and the loop step8 -> step9 -> step8 never ends. |
| #132 | `dispatch-plans.py` `project()` lines 740-745 | Integration-review findings on files outside every pending plan's `writePaths` raise `ValueError`. The command exits 1 and the session fails as `provider_error` with no `nextStep`. |
| #134 | `implementation-progress-check.py` `verification_succeeded()` / `has_failed_behavioral_evidence()` | Intentional mutation runs (`negativeControl: true`, exit 100) count as failed tests. Green records whose exit status appears only as `outcome: "exit 0 in 1010s"` fall through to `return False`. |

## Repository facts this design relies on

- `packages/codex-design-and-implement-review-loop/tests/test_artifact_roots.py::test_dispatch_scripts_stay_identical`
  requires this package's `scripts/dispatch-plans.py` to stay byte-identical to
  the Codex base. `test_dispatch_evidence_root.py::test_integration_revision_outside_ownership_requires_amendment`
  expects `project()` to *raise* the amendment `ValueError` for this package's
  copy. Both test files are outside targetScope. **Therefore `dispatch-plans.py`
  is not edited.** #128/#132 routing goes in a wrapper (D5).
- `packages/codex-design-and-implement-review-loop/tests/test_implementation_progress_check.py`
  runs its behavior cases against this package's `implementation-progress-check.py`
  (the files already differ, and no identity check exists). Every change to the
  progress check must keep those cases green: an explicit blocker without a
  sibling-owned path still blocks, custom runners without structured counts
  still do not pass, and failed required gates still block.
- `.agents/skills/riela-package-release/scripts/check-compact-workflows.ts:392-397`
  asserts that the `dispatch-plans` step's `transitions[0].fanout` exists with
  `changeTracking {pathsFrom:/trackedPaths, artifactRootsFrom:/artifactRoots}`,
  and that `node-dispatch-plans.json` keeps
  `output.jsonSchema.properties.implementationItems.items.required` with
  `artifactRoots`. The fanout transition must stay first, and that schema path
  must stay.
- The Codex base already has the pre-commit gate that #128 asks for:
  `nodes/node-plan-contract-validate.json` + `scripts/validate-plan-contract.py`
  (uses `dispatch-plans.py` `validate_manifest_contract`), wired
  `plan-checkpoint -> plan-contract-validate -> plan-git-commit | step4-impl-plan-create`.
  `step4-impl-plan-create.md:25` of the Codex base has the matching author rule.
- Command nodes receive one stdin line `{"input": runtimeVariables, "variables": ...}`
  with the repository as cwd. They print `{"when": {...}, "payload": {...}}`.
  Direct-inbox history accumulates across loop visits (progress check reads
  `messages[-2]`; dispatch notes "Inbox history retains earlier reviewed
  checkpoints").
- Labeled fanout transitions are supported
  (`codex-refactoring-divide-and-conquer` `label: "implementation_ready"` + `fanout`).
- `plan-checkpoint.md` already promises "a deterministic contract check
  validates the written manifest ... before commit". This workflow has no such
  node yet (EXPECTED_RESULTS.md line 46).

## Decisions

### D1 (#125). Structured behavioral records from any runner

In `implementation-progress-check.py`:

1. `behavioral_kind(record)` keeps the existing allowlist and discovery
   exclusion unchanged. It also returns `"test"` when
   `record.get("kind")` is a string equal to `behavioral-test` (strip, lower)
   **and** the command matches no non-test pattern (D1.3).
2. A record that is behavioral only through `kind` (no allowlist match) counts
   as successful only when all of these hold:
   - the exit status from `record_exit_status()` (D2.1) is the integer `0`;
   - `testsRun` is an `int` (not `bool`) > 0;
   - `failureCount` is an `int` (not `bool`) == 0;
   - the existing `verification_succeeded()` and `positive_test_count()` also pass.

   If it fails any of these, it is failed behavioral evidence and blocks
   through `has_failed_behavioral_evidence()`. Allowlist-matched records keep
   their current semantics, so existing codex/opus tests are unaffected.
3. `NON_TEST_COMMAND_PATTERNS` is matched case-insensitively against the
   whole command. It applies only to the `kind` path:
   - `cargo (build|check|clippy|fmt|doc)`, `go (build|vet|fmt)`, `swift build`
   - `(npm|pnpm|yarn|bun) run (build|lint|format|fmt|typecheck|check)`
   - `make (build|lint|fmt|format|check)`, `tsc`, `eslint`, `prettier`,
     `rustfmt`, `gofmt`, `swiftlint`, `swiftformat`, `ruff`, `black`, `mypy`,
     `shellcheck`
   - `git (diff|status|log|show)`, a bare `diff`, `wasm-pack build`,
     `tree-sitter generate`, `python3? -m (json.tool|py_compile|compileall)`

   A compound command containing any of these is rejected. The bias is
   fail-closed: a false rejection only means the implementer must split the
   command.
4. `plan_requires_behavioral_tests()` is unchanged. It reads committed command
   strings, which carry no `kind`.
5. The `implementation-materially-unverified` resume criterion names the
   accepted forms: the allowlisted runners (swift test, cargo test, cargo
   nextest run, go test, pytest, python -m unittest, ctest, bun test, vitest
   run, npm/pnpm/yarn test, tree-sitter test, deno test, node --test, and
   task/mise run/make/npm|pnpm|yarn|bun run `<name containing test>`), or any
   runner reported as `{"kind":"behavioral-test", "exitStatus":0,
   "testsRun":>0, "failureCount":0}`. It also states that build, lint, format
   and diff commands never count.
6. `prompts/step6-implement.md` requires integer `exitStatus`, `testsRun` and
   `failureCount` on every verification record. It requires
   `kind: "behavioral-test"` for test runs whose runner is not in the allowlist.

Out of scope: `verificationDeferredTo` (the issue's second suggestion). It is
not in the accepted intake, and the structured record covers the FST-22 smoke
case.

### D2 (#134). Exit-status parsing and negative controls

1. New `record_exit_status(record) -> int | None`:
   - Use `exitStatus`, then `exitCode`, when the value is an `int` (not
     `bool`) or a decimal string.
   - Otherwise, parse a leading `^\s*exit(?:\s+(?:status|code))?\s*[=:]?\s*(-?\d+)\b`
     (case-insensitive) from `outcome`. This matches `exit=0`, `exit 0 in
     1010.466 seconds`, `exit: 1` and `exit code 2`.
   - When a structured value and a parsed `outcome` value both exist and
     differ, the record is not successful (fail closed).

   `verification_succeeded()` uses this helper in place of its current
   `exitStatus`/`exitCode` loop. A parsed `0` therefore counts as a seen exit
   status, and a parsed nonzero value fails. Failure-count, failed/skipped text
   and `environmentBlocked` checks keep running first.
2. A verification record is a **valid negative control** only when all of
   these hold:
   - `negativeControl is True` (a JSON boolean);
   - `record_exit_status()` is a nonzero integer;
   - `expectedExitStatus`, when present, is an integer equal to the actual
     exit status;
   - the whitespace-normalized command is not one of the committed
     `variables.implementation.verification` commands. Final-source gates are
     never exempt.
3. In `classify()`, valid negative controls are removed from the record set
   used by `has_failed_behavioral_evidence()`, `has_behavioral_evidence()` and
   the static-plan success check. They never count as positive evidence: the
   plan still needs its own successful positive-count record.
   A record flagged `negativeControl: true` that is *not* valid (exit 0,
   missing exit status, mismatched expectation, or a committed command)
   returns `implementation-materially-unverified` with the message
   `Step 6 reported a negative-control record that did not fail as declared or names a committed verification command.`
   The fingerprint still covers every record, and
   `concrete_verification()` is unchanged.
4. The ready payload forwards `negativeControlEvidence` (the valid records),
   so test-integrity and adversarial review can check that each control
   failed for the intended reason.
5. Every `implementation-materially-unverified` blocker gains
   `failingCommands`: up to 5 command strings of the records that caused the
   block.
6. `prompts/step6-implement.md` tells the implementer to report mutation and
   expected-failure runs with `negativeControl: true` and
   `expectedExitStatus`, and to keep superseded attempts out of
   `verification[]`.

Out of scope: "latest record per command" de-duplication. `priorVerification[]`
is already ignored by the gate.

### D3 (#126). Sibling-owned blockers do not block a finished plan

In `implementation-progress-check.py`, before the `implementation-dependency`
check:

1. **Inputs.** Take `planId`, `writePaths`, `acceptedPlanIds`, `manifestPath`,
   `checkpointCommit` and `evidenceRoot` from `envelope.variables.implementation`.
   Read the immutable manifest with
   `git show <checkpointCommit>:<manifestPath>` (cwd repository root, no
   shell). Plans whose IDs are in `acceptedPlanIds` or equal `planId` are not
   sibling candidates.
2. **Classification.** A blocker is **sibling-owned** only when all of these
   hold:
   - it is an object naming `path` (string) or `paths` (non-empty string list);
   - every named path is a safe repository-relative path (no absolute path, no
     `..`, no `.git`);
   - no named path is owned by this plan's `writePaths`. Ownership means equal
     to, or under, a `writePaths` entry, the same semantics as dispatch
     `path_is_owned`;
   - every named path is owned by the `writePaths` of at least one other
     manifest plan that is not accepted. The `owner` text in the blocker is
     ignored.
3. **Fail closed.** These keep today's `implementation-dependency` block:
   - a missing implementation item;
   - a `git show` failure or a non-JSON manifest;
   - any blocker that is not sibling-owned, including string blockers;
   - `implementation_blocked: true` with no blockers.
4. **When every blocker is sibling-owned.**
   - The plan continues through the remaining gates unchanged: findings,
     behavioral evidence, incomplete, no-progress and verification gaps. A
     branch whose own required tests did not produce positive-count success
     is still blocked. This covers the Rust shared-test-binary case in the
     #126 third occurrence; that branch recovers through the existing
     partial-success redispatch.
   - On the ready outcome, the payload has `blockers: []` and
     `siblingOwnedBlockers: [{paths, ownerPlanIds, command?, message?}]`.
   - The gate writes the same list atomically to
     `<evidenceRoot>/<planId>/sibling-owned-blockers.json`, after checking that
     `evidenceRoot` is a safe path under `tmp/`. If the write fails, the plan is
     blocked as `implementation-dependency`.
   - On a blocked outcome, the original blockers stay in `blockers` (current
     `blocked_result` behavior).
5. **Integration review re-checks deferred blockers.**
   `prompts/integration-review.md` states that, for every candidate plan with
   that file, the reviewer re-runs each recorded command (or the equivalent
   workspace gate) on the reconciled combined tree. A remaining failure is a
   material finding owned by the plan that owns the path. A candidate is
   never accepted while a deferred gate fails.
6. **Prompts.**
   - `step6-implement.md`: scope fmt/lint/test gates to the plan's own
     `writePaths` while siblings run. Report a failure caused only by another
     plan's file as a blocker object `{path|paths, command, exitStatus,
     message}`, and never edit that file.
   - `step4-impl-plan-create.md` and `step5-impl-plan-review.md`: per-plan
     `verification` must not contain workspace-wide format, lint or full-build
     commands when sibling plans share a wave. Those belong to reconcile and
     integration review. Step 5 reports such a plan as a mid finding.

### D4 (#128). Pre-commit manifest gate, ported from the Codex base

1. Add `nodes/node-plan-contract-validate.json` and
   `scripts/validate-plan-contract.py` as **byte-identical copies** of the
   Codex base files. The script imports this package's unchanged
   `dispatch-plans.py`.
2. `workflow.json`:
   - add node `plan-contract-validate`;
   - change `plan-checkpoint` `!(checkpoint_blocked)` to point at
     `plan-contract-validate`;
   - `plan-contract-validate` routes `contract_valid` -> `plan-git-commit` and
     `!(contract_valid)` -> `step4-impl-plan-create`.

   On acceptance the gate passes `commitMessage`/`committedFiles` through
   unchanged, so `plan-git-commit` still renders from
   `inbox.latest.output.payload`. The `checkpoint_blocked: true` behavior is
   unchanged.
3. Port the Codex `step4-impl-plan-create.md:25` rule (address every
   `contract_valid: false` finding by narrowing paths or declaring
   `artifactRoots`, and never raise limits) into this package's Step 4 prompt.
4. Step 4 and Step 5 rules:
   - prefer concrete files to broad directories in `sharedPaths`, and account
     for growth across waves;
   - plans never list `impl-plans/active` or `impl-plans/completed` in
     `writePaths`/`sharedPaths`, because plan archiving belongs to D6. This
     removes the session-226 CMP-40 cause.

   Step 5 reports violations as mid findings.
5. Dispatch-time violations (a directory that grew between checkpoint and a
   later wave) no longer fail the session. They take the D5 amendment route.

Out of scope: closeout-wave exemption, digest-tracked directories, and
`session continue` after a runtime `policyBlocked`. All three are runtime
changes. D5 covers every violation that the dispatch preflight detects
in-session.

### D5 (#132, #128 at dispatch time). Routed dispatch wrapper

1. New `scripts/dispatch-wave.py`. `node-dispatch-plans.json` `command.scriptPath`
   points to it. It loads `dispatch-plans.py` through `importlib`, the same
   pattern as `validate-plan-contract.py`, and calls `project(envelope)`.
   `dispatch-plans.py` stays byte-identical to the Codex base.
2. **Normal projection.** The wrapper returns `project()`'s payload unchanged
   plus `dispatch_ready: true, amendment_required: false,
   amendment_blocked: false`, with the same three booleans in `when`.
3. **Amendment.** A `ValueError` whose text starts with
   `dispatch.AMENDMENT` (`bounded checkpoint amendment required`) covers both
   cases:
   - tracking-contract or preflight violations of pending plans (#128);
   - integration-review paths outside `writePaths` (#132).

   The wrapper then exits 0 with a routed payload containing:
   - `checkpointAmendment`:
     - `reason`: `tracking-contract` or `integration-paths-outside-writePaths`
     - `error`: the full text
     - `unmatchedPaths`: parsed from the text after `outside manifest writePaths: `
     - `ownerCandidates`: for each unmatched path, the manifest plans whose
       `writePaths` own it, each with an `accepted` flag
     - `findings`: the integration findings naming those paths (at most 20)
     - `manifestPath` and `previousCheckpointCommit`, from `dispatch.checkpoint_source`
     - `amendmentRound` and `maxAmendmentRounds`
   - `acceptedPlanIds`, `pendingPlanIds`, `issueReference` (from the manifest
     `reviewContext`)
   - `blockedPlanIds`: the pending manifest plan IDs, never empty
   - `successfulPlanIds`: the accepted IDs
   - `blockers`, `resumeCriteria` and `nextStep`

   Every other `ValueError` keeps exit 1 (fail closed). This covers a
   malformed inbox, a checkpoint mismatch and unknown accepted IDs.
4. **Bound.** `amendmentRound` is the number of distinct `git.commitHash`
   values in the direct inbox messages from `plan-git-push`, `plan-git-commit`
   and `plan-push-gate`, minus 1. `MAX_CHECKPOINT_AMENDMENTS = 2`.
   - Below the bound: `when.amendment_required: true`.
   - At or above it: `when.amendment_blocked: true`. The `nextStep` names the
     unmatched paths and the operator action: amend the manifest, commit, and
     start a resume run.
5. **`workflow.json` `dispatch-plans` transitions**, in this order:
   1. the existing fanout transition (still `transitions[0]`) with
      `label: "dispatch_ready"`;
   2. `amendment_required` -> `step4-impl-plan-create`;
   3. `amendment_blocked` -> `implementation-blocked-output`.
6. **`node-dispatch-plans.json` output schema.** Keep
   `properties.implementationItems` with its item schema and `minItems: 1`.
   Remove `implementationItems` from top-level `required` (it is absent on
   amendment routes). Add properties `dispatch_ready`, `amendment_required`,
   `amendment_blocked`, `checkpointAmendment`, `pendingPlanIds`,
   `blockedPlanIds`, `successfulPlanIds`, `issueReference`, `blockers`,
   `resumeCriteria` and `nextStep`. Keep `additionalProperties: false`. The
   three booleans plus `acceptedPlanIds`, `manifestPath` and
   `checkpointCommit` are required.
7. **Amendment loop:** step4 -> step5 -> plan-checkpoint ->
   plan-contract-validate -> plan-git-commit -> plan-push-gate
   (-> plan-git-push) -> dispatch-plans.
   - `step4-impl-plan-create.md`: on `amendment_required`, perform only the
     bounded amendment. Assign each unmatched path to a pending owning plan's
     `writePaths`, or narrow and reclassify paths for `tracking-contract`. Keep
     plan IDs and accepted plans unchanged, and carry `checkpointAmendment`
     verbatim in the output.
   - `step5-impl-plan-review.md`: review only the amendment's scope, and carry
     `checkpointAmendment` forward.
   - `plan-checkpoint.md`: update the existing manifest in place. Require HEAD
     to equal `checkpointAmendment.previousCheckpointCommit` instead of the
     intake HEAD. Commit only the changed manifest and plan files; the
     uncommitted implementation work stays unstaged.

   The redispatch reuses the latest integration-review feedback. Its paths are
   now owned, so `project()` assigns them to the amended plan. The Step 4 and
   Step 5 output schemas already use `additionalProperties: true`, so
   `checkpointAmendment` needs no schema change.
8. **`implementation-blocked-output`.**
   - The prompt copies issue reference, blocked/successful IDs, blockers,
     resume criteria and `nextStep` from whichever direct predecessor
     delivered the blocked payload: `implementation-wave-outcome`,
     `dispatch-plans` (`amendment_blocked`) or `plan-archive`
     (`completion_blocked`, D6).
   - Its schema relaxes `blockedPlanIds` `minItems` from 1 to 0, because the
     completion-loop block may have no plan ID. The prompt still requires a
     non-empty list for wave and dispatch blocks.
   - The schema adds an optional `blockedStepId` string.

### D6 (#129). Deterministic plan archiving and a bounded completion loop

1. **Step 8 requests moves.** `prompts/step8-docs-refresh.md` no longer
   moves files. For each completed plan it returns
   `archiveRequests: [{source: "impl-plans/active/<name>", destination: "impl-plans/completed/<name>"}]`.
   It still edits `impl-plans/README.md` and links to point at the destination
   paths, and never runs `mv`/`git mv`. `node-step8-docs-refresh.json` adds
   the optional `archiveRequests` property.
2. **New command node `plan-archive`** (`nodes/node-plan-archive.json`,
   `scripts/plan-archive.py`). `workflow.json` routes:
   - `step8-docs-refresh` -> `plan-archive`;
   - `plan-archive` `!(completion_blocked)` -> `step9-commit-message`;
   - `plan-archive` `completion_blocked` -> `implementation-blocked-output`.

   `step9-commit-message` `needs_revision` -> `step8-docs-refresh` is unchanged.
3. **Script rules.** The script reads the latest `step8-docs-refresh` payload
   from its direct inbox. For each request:
   - **Rejected** (no filesystem change) when:
     - `source` is not directly under `impl-plans/active/`;
     - `destination` is not `impl-plans/completed/<same basename>`;
     - either path is unsafe (absolute, `..`, `.git`);
     - `source` is a symlink, a directory or a special file.
   - **`already-archived`**: the source is absent and the destination exists
     as a regular file.
   - **`conflict`**: the source and destination both exist. Neither is changed.
   - **`moved`**: `os.rename` after creating `impl-plans/completed/` if needed.
     The script runs no `git` command and does not touch the index. Step 9
     lists both source and destination in `committedFiles`, which the
     existing prompt already requires, and `riela/git-commit` stages the
     rename.
   - **`missing`**: neither path exists.

   The payload forwards every Step 8 key plus:
   - `archiveResults: [{source, destination, status, message}]`;
   - `archivedImplPlanPaths`: the destinations with status `moved` or
     `already-archived`;
   - `docsRefreshRound`;
   - `completion_blocked`, mirrored in `when`.
4. **Bound.** `docsRefreshRound` is the number of `step8-docs-refresh`
   messages in the direct inbox. `MAX_DOCS_REFRESH_ROUNDS = 3`. When the
   round exceeds 3 (Step 9 has already rejected three times), the script still
   applies the requests, which is idempotent, and then returns
   `completion_blocked: true` with:
   - `implementation_blocked: true`, `status: "blocked"`, `blockedStepId: "step9-commit-message"`;
   - `blockedPlanIds`: the basenames of unresolved request sources, which may
     be empty;
   - `successfulPlanIds: []`;
   - a `completion-archive-loop` blocker that lists the non-`moved`/`already-archived`
     results;
   - `resumeCriteria`, and a `nextStep` naming the operator move or index edit.
5. **Step 9.** `prompts/step9-commit-message.md` reads `archiveResults` from
   its direct inbox. It treats `rejected`/`conflict`/`missing` results as
   `needs_revision` with the exact paths, and accepts `already-archived`.
   It still never moves files.

### D7. Fixtures, docs, release

- Mock scenarios. Command nodes are answered by node id, and the response
  `model` names the script, following the `plan-push-gate` convention.
  - In `mock-scenario.json`, `mock-scenario-fanout.json` and
    `mock-scenario-local.json`:
    - add `plan-contract-validate` (`contract_valid: true`, passing through
      the checkpoint `commitMessage`/`committedFiles`);
    - add `plan-archive` (`completion_blocked: false`, `archiveResults`);
    - give every `dispatch-plans` response `when`/payload
      `dispatch_ready: true, amendment_required: false, amendment_blocked: false`;
    - add `archiveRequests` to the `step8-docs-refresh` payloads.
  - `mock-scenario-planning-only.json` never reaches these nodes. Check that
    and leave it unchanged.
  - No new mock scenario: the amendment, contract-rejection and
    completion-block routes are covered by script unit tests and a graph test
    (Verification 7).
- `EXPECTED_RESULTS.md`:
  - line 5 and the route description gain `plan-contract-validate` and
    `plan-archive`;
  - line 7 execution counts: re-measure from the mock runs;
  - line 12: Step 8 requests moves and `plan-archive` performs them, with the
    3-round bound;
  - line 18: the pre-commit gate exists;
  - line 30: the dispatch command is a routing wrapper around the
    byte-identical projection;
  - lines 34-40: sibling-owned blockers, negative controls, structured
    `kind`, and `exit=N` parsing;
  - line 46: remove "no pre-commit plan-contract-validate gate", keep
    "dispatch-plans is byte-identical", and add the amendment routes.
- Package `README.md`: under "Review revision routing", add three sentences
  covering the pre-commit gate, the amendment route and deterministic plan
  archiving. Update the skill `SKILL.md` only if it describes Step 8 moving
  files.
- Release, as the last edit:
  1. Set `riela-package.json` version to `0.1.10`.
  2. Run `bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-terra-design-and-implement-review-loop`
     (this refreshes the package and `registry-index.json` digests).
  3. Run `mise run package:check-digests`.
- **Plan ordering.** The Step 4 author decides, but the intake's
  same-file rule implies this chain:
  - `implementation-progress-check.py`: D2 (#134, adds `record_exit_status`)
    -> D1 (#125, uses it) -> D3 (#126);
  - `dispatch-plans` node/schema and `workflow.json`: D4 -> D5 -> D6. All three
    edit `workflow.json`, so they are serialized or owned by one plan;
  - prompts are split by file owner;
  - D7 fixtures/docs/release runs last.

## Verification

Each issue gets regression tests under
`packages/opus-terra-design-and-implement-review-loop/tests/`, loading scripts
with `importlib`. Run them with `unittest` only, and write temporary git repos
and files under the test's temp dir.

1. `test_progress_structured_runner.py` (#125)
   - **Accepted:** the session-222 record
     `{"command":"node tmp/fst/FST-22/wasm-smoke-rerun.mjs","kind":"behavioral-test","exitStatus":0,"testsRun":2,"testsPassed":2,"failureCount":0}`
     is behavioral, and `classify()` reaches `ready-for-test-integrity`.
   - **Still not behavioral:** the same record without `kind`.
   - **Failed evidence (blocks):** a `kind` record with `testsRun` 0 or
     missing, `failureCount` 1, `exitStatus` 1, or bool/str counts.
   - **Not behavioral when declared with `kind`:** `cargo build`,
     `cargo clippy --all-targets`, `cargo fmt --check`, `npm run lint`,
     `git diff --stat`, and `tsc --noEmit`.
   - **Resume text:** the resume criterion lists the runner forms and the
     structured form.
2. `test_progress_negative_control.py` (#134)
   - **Accepted:**
     - the session-282 shape: passing nextest/vitest records plus two
       `negativeControl:true` records with exit 100 and `expectedExitStatus`
       100;
     - the session-283 record `outcome: "exit 0 in 1010.466 seconds; 3 skipped"`
       with counts and no `exitStatus`.
   - **Blocked:**
     - a negative control with exit 0;
     - a negative control with no exit status;
     - a mismatched `expectedExitStatus`;
     - a negative control whose command equals a committed verification command;
     - an unflagged failing record;
     - a negative control as the only behavioral record (no positive evidence).
   - **Parsing:** `exit=1` fails, and structured `0` with parsed `1` fails.
3. `test_progress_sibling_blockers.py` (#126). The fixture is a temp git repo
   with a committed manifest: FST-22 owns its files, and FST-20 owns
   `src/cli/tests/fmt.rs`.
   - **Accepted:** a Step 6 blocker on that path, plus passing own tests,
     reaches ready. `siblingOwnedBlockers` names FST-20, and the evidence file
     exists.
   - **Blocked:** the path is owned by this plan; the path is unowned; the
     owner is accepted; the blocker has no path or is a string; one sibling
     and one unowned path; the `git show` fails; a sibling-only blocker
     without behavioral evidence.
4. `test_plan_contract_gate.py` (#128)
   - The copied script and node are byte-identical to the Codex files.
   - A plan whose `sharedPaths` directory expands past 512 entries gives
     `contract_valid:false`, and the findings name the plan and the path.
   - A valid manifest passes `commitMessage`/`committedFiles` through.
   - `dispatch-wave.py` turns the same over-cap preflight at dispatch time
     into `amendment_required` with exit 0.
5. `test_dispatch_amendment.py` (#132)
   - The session-271 shape (findings on `editor/src/code/pointer.ts`, ...
     outside `writePaths`) gives `amendment_required` with `unmatchedPaths`,
     `findings`, `manifestPath`, `previousCheckpointCommit` and
     `amendmentRound` 0.
   - With 3 distinct checkpoint commits in the inbox, it gives
     `amendment_blocked` with non-empty `blockedPlanIds`, `blockers`,
     `resumeCriteria` and `nextStep`.
   - Unknown accepted IDs or a bad push receipt still exit 1.
   - A normal projection equals `project()`'s payload plus the three booleans.
   - `dispatch-plans.py` is byte-identical to the Codex base.
6. `test_plan_archive.py` (#129)
   - Statuses: `moved`, idempotent `already-archived`, `conflict` (both left
     intact), `missing`, and `rejected` for each unsafe or ineligible form.
   - The script never invokes `git`: patch `subprocess` to fail on use.
   - Step 8 keys are forwarded.
   - The 4th Step 8 message gives `completion_blocked` with the blocker,
     `nextStep` and `resumeCriteria`.
7. `test_workflow_routing.py`
   - It asserts every new or changed edge in D4-D6. `dispatch-plans`
     `transitions[0]` keeps its fanout, `changeTracking` and the
     `dispatch_ready` label, and its node `scriptPath` is
     `scripts/dispatch-wave.py`.
   - The node schemas accept the routed payload keys.
   - Prompt anchors:
     - `step8-docs-refresh.md` mentions `archiveRequests` and has no move
       instruction;
     - `step6-implement.md` mentions `negativeControl`, `behavioral-test`
       and own-path gate scoping;
     - `step4-impl-plan-create.md` handles `contract_valid: false` and
       `amendment_required`;
     - `integration-review.md` re-checks `sibling-owned-blockers.json`.

Commands. Record each exit status and the complete log path under
`tmp/opus-terra-issue-sweep/`:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests`.
  This runs read-only: those tests load this package's `dispatch-plans.py`
  and `implementation-progress-check.py`, and they must stay green.
- `riela workflow validate opus-terra-design-and-implement-review-loop --workflow-definition-dir packages/opus-terra-design-and-implement-review-loop/workflows`
- `riela workflow run` with `--mock-scenario` for all four scenarios (local
  with `--variables '{"workflowInput":{"gitPush":false}}'`), using an
  isolated `--session-store` and `--artifact-root`
- `mise run workflow:check-compact`
- `bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-terra-design-and-implement-review-loop`,
  then `mise run package:check-digests`
- `mise run workflow:check-scenarios`. Expected result: the opus-terra route
  assertion is stale because the route fixture is out of scope. See
  `design-docs/user-qa/opus-terra-gate-routing-0110.md`.

## Constraints and boundaries

- Edit only `packages/opus-terra-design-and-implement-review-loop/**` and
  `registry-index.json`.
  - `dispatch-plans.py` stays byte-identical to the Codex base.
  - `validate-plan-contract.py` and its node are byte-identical copies.
  - Codex tests and `.agents/**` are not edited.
- Gates stay fail-closed:
  - failed, zero-count, missing-count and non-test evidence is rejected;
  - an invalid negative control blocks;
  - unclassifiable blockers block;
  - non-amendment dispatch errors still exit 1.
- No git index mutation in `plan-archive`. No push, merge or base integration
  (`gitPush=false`).
- Run Python with `PYTHONDONTWRITEBYTECODE=1`. Refresh digests last.
