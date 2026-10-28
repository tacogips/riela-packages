# Opus Luna wave input compaction

Issue: `workflowInput:opus-terra-wave-input-compaction` (no GitHub issue).
Package: `packages/opus-terra-design-and-implement-review-loop` (0.1.8 -> 0.1.9).

## Problem

Session-471 (2026-10-22) failed at `implementation-wave-outcome` with
`Prompt is too long (~1.25M tokens)`. That step is the native fanout join
(`dispatch-plans` fanout `shared-branch-implementation`, `joinStepId:
implementation-wave-outcome`, `failurePolicy: collect-partial`). It was a
`claude-code-agent` Opus step with `variables: {}`, so its prompt carried the
whole raw `fanoutJoin`: every branch output plus unbounded
`changeEvidence.observations` (~8 MB). The step only aggregates
classifications that the branch-local `implementation-progress-check` has
already made, so the work is mechanical.

## Runtime delivery facts this design relies on

Riela source evidence (riela `3f921eb4`, installed 0.2.34). These lines were
cited by the Step 3 design review. This design step's sandbox cannot read
`/Users/taco/gits/tacogips/riela`, so they were not re-run here (see
Verification gaps).

- **Persistent request variable.** `Sources/RielaCore/DeterministicWorkflowRunner.swift:426`
  runs `effectiveRequest.variables["fanoutJoin"] = .object(fanoutJoin)` after
  `dispatchFanout` returns. The runner keeps that request for every later
  step, and no code removes the key. The only other `fanoutJoin` reference is
  the join message publication at `DeterministicWorkflowRunner+Fanout.swift:442`.
- **Rendered into every agent prompt.** `DeterministicWorkflowRunner+Prompting.swift:60-101`
  builds `runtimeVariables` from the request variables, with the step's
  resolved direct-inbox payload keys overlaid on top (`:96-101`).
  `:154-165` renders the whole object into the agent system prompt as compact
  JSON. There is no size cap, key filter or per-node variables policy.
- **Inherited by later fanout branches.** `DeterministicWorkflowRunner+Fanout.swift:242`
  runs `var branchVariables = request.variables`, so every branch of wave N+1
  carries wave N's raw join.
- **Direct-inbox payloads do not accumulate.** In session-476 the step2 input
  has the step1 payload but none of the `riela-manager` keys recorded in
  `tmp/wave-compaction/run.jsonl`. The join *message* goes only to the join
  step. The *request variable* is what persists.
- Command nodes receive one JSON line on stdin (`{"input": runtimeVariables}`),
  run with the repository working directory as cwd, and print
  `{"when": {...}, "payload": {...}}` (`dispatch-plans.py`,
  `implementation-progress-check.py`). They have no prompt, so a raw join in
  their `runtimeVariables` cannot overflow a model context.
- Mock scenarios answer every node by node id, command nodes included. Scripts
  are not executed and prompts are not rendered by `--mock-scenario` runs.

Consequences:

1. Compacting the join step (D1-D4) is necessary but not sufficient. If only
   the join step changes, the session-471 overflow moves to the first later
   agent step (`reconcile-implementations`, or `implementation-blocked-output`
   on the blocked path). The full list of affected steps is in D5.
2. No package-local change can remove the request variable. A package can only
   *shadow* it for one step at a time: the direct predecessor's payload must
   carry a top-level `fanoutJoin` key (`Prompting.swift:96-101`). D7 evaluates
   this and the upstream alternative. The scope decision is recorded in
   `design-docs/user-qa/opus-terra-wave-input-compaction.md`.
3. `reconcile-implementations` and `integration-review` still need an explicit
   bounded data path (the wave summary, D3-D5), whichever D7 option is chosen.

## Decisions

### D1. The join step becomes a deterministic command

`implementation-wave-outcome` keeps its step id, node id, `joinStepId` role,
incoming edges (`branch-evidence`, `implementation-progress-check`
`implementation_blocked`), transitions and output `jsonSchema` (the six
fields, `additionalProperties: false`), with the schema bytes unchanged.
`nodes/node-implementation-wave-outcome.json` becomes
`nodeType: "command"`, `command.scriptPath:
"scripts/implementation-wave-outcome.py"`, `variables: {}`,
`modelFreeze: false`, with no `executionBackend`, `model`, `effort`,
`agentSandbox` or `promptTemplateFile`. The node keeps `output.description`
and `output.jsonSchema`. `prompts/implementation-wave-outcome.md` is deleted
and its rules move into the script.

Rejected alternative: a new command join step in front of the Opus
`implementation-wave-outcome`. It adds a route step (the
`.agents/.../expected-routes.json` map is outside this package's scope), keeps
an Opus call with no judgment left to make, and still cannot hand the summary
to reconciliation, because the closed six-field contract drops it.

### D2. The script's deterministic classification

The script reproduces the deleted prompt's rules. It reads branches in input
order. `planId` is `branchId`, falling back to `output.planId`, and
`output` is the branch's terminal payload.

| Branch condition | Classification | Verdict effect |
| --- | --- | --- |
| `failureReason` starts with `policy_blocked: fanout snapshot`, `policy_blocked: fanout change tracking` or `policy_blocked: fanout artifact` | `tracking-rejected` | blocked. Resume criterion is exactly `amend checkpoint: declare artifactRoots / narrow writePaths`. |
| Plan is named by a `changeEvidence.captureFailures`/`reduceFailures` diagnostic `branchId`, or `changeEvidence.complete === false` with no attributable `branchId` (then every dispatched branch) | `evidence-incomplete` | blocked, same resume criterion |
| `output.implementation_blocked === true` or `output.status === "blocked"` | `blocked` | blocked. Uses the output's `blockerType`/`blockers`/`resumeCriteria`. |
| Status is `completed`/`succeeded`/`success`, not blocked, `output.evidencePaths` is a non-empty array, and `output.changedFiles` is an array | `successful` | goes in `successfulPlanIds` |
| Status is `failed`/`cancelled`/other, or a completed branch with missing evidence | `failed` / `cancelled` / `evidence-missing` | none. The plan stays for reconciliation and selective redispatch. |
| Listed in `pendingBranchIds` and never dispatched | `pending` | none |

The verdict fields are computed as follows:

- `implementation_blocked` is true when any plan is blocked.
- `partial_success` is `implementation_blocked && successfulPlanIds.length > 0`.
- When the wave is unblocked, the verdict is `partial_success:false` with
  empty `blockedPlanIds`, `blockers` and `resumeCriteria`.
- A blocked plan always gets at least one blocker and one resume criterion,
  because `implementation-blocked-output` requires `minItems: 1`. If the
  branch supplied none, the default is `"<planId>: resolve the <blockerType>
  blockers recorded in <summaryPath> and redispatch"`.
- Each diagnostic keeps only `branchId, node, phase, selection, root, path,
  observed, limit`. File contents are never copied.
- stdout is `{"when": {"implementation_blocked": B, "partial_success": P},
  "payload": verdict}`.

Standalone fallback: with no `fanoutJoin` but a direct
`implementation-progress-check` or `branch-evidence` message (a session
resume), the script classifies that payload as a one-branch wave. This matches
the Codex tracking gate. Otherwise it exits 1 with a JSON error (fail closed).

### D3. Raw join and summary storage

- The run's wave evidence root is
  `tmp/opus-terra-waves/<workflowExecutionId>/`. It sits under the workflow's
  declared `scratchRoot: tmp` and is keyed by the runtime-owned
  `_rielaInput.workflowExecutionId`, which every step receives. The manifest
  `evidenceRoot` is not used because the join carries no dispatch item or
  manifest, so neither the join step nor reconciliation could locate it
  without the raw join.
- Each join execution creates a new immutable `wave-<NNN>/` (3-digit ordinal,
  next free number, `mkdir(exist_ok=False)`). It writes `fanout-join.json`
  (the exact join, compact UTF-8 JSON) and `wave-summary.json`, each through a
  temp file plus `os.replace`. Earlier waves are never overwritten. A resumed
  or retried join gets a new ordinal.
- The script fails closed (exit 1) in these cases: `workflowExecutionId` is
  missing or does not match `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$` or contains
  `..`; `tmp`, `tmp/opus-terra-waves` or the session directory is a symlink or
  not a directory; or a write fails.
- Locator rule, shared by the script, reconciliation and integration review:
  the current wave is the highest `wave-NNN` under
  `tmp/opus-terra-waves/<own workflowExecutionId>/`. Waves are strictly serial
  within a session (dispatch -> join -> reconcile -> integration review ->
  dispatch), so the highest ordinal is the current wave.
  `wave-summary.json.verdict` must deep-equal the wave-outcome payload.

### D4. Bounded wave summary (`wave-summary.json`, schemaVersion 1)

```
{schemaVersion, generatedBy:"implementation-wave-outcome.py", workflowExecutionId,
 waveOrdinal, summaryPath, rawJoinPath, rawJoinBytes, rawJoinSha256,
 verdict:{<the six fields>},
 dispatchedBranchIds, pendingBranchIds, completedBranchIds,
 plans:[{planId, status, classification, rawPointer:"/branches/<i>", sessionId,
   failureReason, blockerType, blockers[], blockersTotal, resumeCriteria[],
   changedFiles[], changedFilesTotal, evidencePaths[], evidencePathsTotal,
   reviewDecisions, checkpointProvenance, baselineReviewPending}],
 changeEvidence:{complete, hasDrift, observationTotal, pathTotal,
   bySelection:{source, artifact, other}, byKind:{...}, kindsOmitted,
   captureFailuresTotal, reduceFailuresTotal, captureFailures[], reduceFailures[],
   artifactPaths[], artifactPathsTotal,
   paths:[{path, selection, observationCount, kinds[], branchIds[]}], pathsOmitted},
 truncation:{level, truncatedFieldCount}}
```

- Field rules:
  - Branch id lists are kept in full. They are plan ids, bounded by plan
    count.
  - `hasDrift` is the native boolean when present, otherwise
    `observationTotal > 0`.
  - An observation's kind is `kind`, falling back to `type` and then
    `"unknown"`. Its path is `path`, falling back to `root`. Its selection is
    `selection`, defaulting to `"other"`, never assumed `source`.
  - `reviewDecisions` and `checkpointProvenance` use a generic bounded
    projection: depth, list-item and string caps. A cut string ends with
    `…[truncated N chars; see rawJoinPath#<pointer>]`.
- Drift-first ordering of `paths` is deterministic:
  1. Kind severity: deleted/removed/overwrite, then content, then
     added/new/membership, then mode/kind, then other. (Operator amendment
     2026-10-22 after session-477: a removed path outranks content drift
     regardless of observation count, matching the adversarial regression
     `test_runtime_reason_observations_rank_removed_first`.)
  2. Selection: `source`, then `artifact`, then other.
  3. `observationCount`, descending.
  4. Path, ascending.

  Blocked plans' blockers come first within lists.
- Bounds:
  - `SUMMARY_BYTE_LIMIT = 49152` (`wave-summary.json`) and
    `VERDICT_BYTE_LIMIT = 16384` (payload), both counted as compact UTF-8
    JSON. The Opus-bound input after the join is at most 64 KiB in total.
  - The script tries levels in order and stops at the first that fits. If no
    level fits, it exits 1 with an error naming the plan count. It never
    emits an oversized or silently cut summary.

| Level | paths | kinds/path | branchIds/path | changedFiles | evidencePaths | blockers | resumeCriteria | diagnostics, artifactPaths, byKind | generic items/depth | string |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 40 | 3 | 5 | 50 | 20 | 10 | 10 | 20 | 10 / 4 | 300 |
| 1 | 20 | 2 | 3 | 20 | 10 | 5 | 5 | 10 | 5 / 3 | 160 |
| 2 | 5 | 1 | 2 | 5 | 5 | 3 | 3 | 5 | 3 / 2 | 80 |
| 3 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | key names only | 80 |

  Totals are always exact. In the verdict, each blocked plan keeps at most 3
  blockers plus one `additional-blockers-omitted` marker carrying
  `omittedCount` and `summaryPath`, at most 3 deduplicated resume criteria,
  and 300-character strings. The verdict fallback is 1/1/120, then exit 1.
- The summary has no timestamps or random values. The same join produces
  byte-identical output apart from `waveOrdinal`, `summaryPath` and
  `rawJoinPath`.

### D5. Downstream Opus steps

- `reconcile-implementations`: the prompt replaces the raw-join instructions
  with these:
  1. Use the inbox verdict.
  2. Locate the current wave summary (D3) and verify `workflowExecutionId`
     and the `verdict` deep-equality. A mismatch or missing file is a
     blocking evidence gap.
  3. Take these from the summary: `plans[]`, `dispatchedBranchIds`,
     `pendingBranchIds`, `checkpointProvenance`, `reviewDecisions`,
     `changedFiles`, `evidencePaths`, the `changeEvidence` aggregates and the
     capped drift paths with their `selection: "source"` vs
     `selection: "artifact"` classification.
  4. Never load `fanout-join.json` whole. When a needed field is truncated,
     or a total exceeds the listed items, extract only that record by
     `rawPointer` (for example
     `jq '.branches[2].output.reviewDecisions' <rawJoinPath>`).
  5. Return `waveSummaryPath` and `rawJoinPath` in the payload. The schema
     already allows additional properties.

  The existing semantics remain: checkpoint provenance agreement, artifact
  drift is not a source overwrite, `complete:false` is a blocking evidence
  gap, partial-success handling, and the Luna ownership of corrections.
- `integration-review`: the prompt reads the summary at the reconcile-supplied
  `waveSummaryPath` and requires it to equal the D3 locator result for its own
  `workflowExecutionId`. It replaces "native `fanoutJoin.dispatchedBranchIds`
  and branchId records" with the summary's `dispatchedBranchIds` and
  `plans[]`, and it uses the same targeted-extraction rule. All acceptance
  rules are otherwise unchanged.
- Audit of raw-join exposure. Every agent step that runs after a join carries
  `runtimeVariables.fanoutJoin` through the persistent request variable,
  whatever its direct inbox holds. Command nodes and add-ons have no prompt.

| Step (backend) | Reached after a join | Direct predecessor | Raw join in prompt today |
| --- | --- | --- | --- |
| `implementation-blocked-output` (Opus) | blocked-only wave | `implementation-wave-outcome` (command) | yes |
| `reconcile-implementations` (Opus) | every non-blocked wave | `implementation-wave-outcome` | yes |
| `integration-review` (Opus) | every wave | `reconcile-implementations` | yes |
| `step7b-e2e-evidence` (Opus) | final | `integration-review` | yes |
| `step8-docs-refresh` (Opus) | final | `step7b-e2e-evidence` / `step9-commit-message` | yes |
| `step9-commit-message` (Opus) | final | `step8-docs-refresh` | yes |
| `base-branch-integrate` (Opus) | push mode | `step11-git-push` (riela/git-push add-on) | yes |
| `workflow-output` (Opus) | final | `base-branch-integrate`, or `final-push-gate` (command) in local-only mode | yes |
| next-wave and redispatch branch steps `step6-implement` (Luna), `step6-test-integrity-check`, `step7-adversarial-review`, `branch-evidence` (Opus) | every wave after the first, including selective redispatch after an integration revision | fanout item, `implementation-progress-check` (command), the preceding gate | yes (`Fanout.swift:242`) |
| `dispatch-plans`, `implementation-progress-check`, `implementation-wave-outcome`, `final-push-gate`, `plan-push-gate` (command); `step10-git-commit`, `step11-git-push` (add-ons) | n/a | n/a | no prompt |

  D7 decides how these steps are bounded. D1-D5 do not bound them by
  themselves.
- Session reuse (`reconcile-implementations` reuse and `integration-review`
  inheriting the `step2-design-doc-update` session) grows with wave and
  revision visits. It is bounded by gate convergence (`maxGateVisits: 4`) and
  `maxLoopIterations: 30`. No change; recorded as a residual risk.

### D7. Bounding the persistent request variable (scope decision required)

The package cannot delete `request.variables["fanoutJoin"]`. Riela has no
runtime filter for this: Step 3 searched for runtimeVariables
omit/exclude/variablesPolicy options and found none. Options:

- **A. Upstream riela change (recommended).** Scope `fanoutJoin` to the join
  step: deliver it through the join message and the join step's
  `runtimeVariables` only, do not persist it in the run request after the join
  step, and do not copy it into later branch variables
  (`DeterministicWorkflowRunner.swift:426`, `+Fanout.swift:242`).
  - Coverage: every row of the D5 table, including push mode and every
    next-wave and redispatch branch.
  - Package side: D1-D6 unchanged, plus the minimum riela version stated in
    the package `README.md` and `EXPECTED_RESULTS.md`.
  - Out of targetScope (riela repository and release). It needs the user
    decision recorded in `design-docs/user-qa/opus-terra-wave-input-compaction.md`.
- **B. In-package shadow.** Each predecessor payload carries a bounded
  top-level `fanoutJoin` stub `{compacted:true, waveSummaryPath, rawJoinPath}`.
  The stub overrides the request variable for its direct successor only
  (`Prompting.swift:96-101`). Requirements:
  - Add the stub as a declared property to the `implementation-wave-outcome`
    schema. This changes the closed six-field contract named in acceptance
    signal 3, which needs a user decision.
  - Make the stub required in the `reconcile-implementations`,
    `integration-review`, `step7b-e2e-evidence`, `step8-docs-refresh` and
    `step9-commit-message` output schemas.
  - Have `final-push-gate` emit a constant stub so local-only
    `workflow-output` is covered.

  Uncovered: `base-branch-integrate` (its predecessor is an add-on), push-mode
  `workflow-output` (behind an overflowing `base-branch-integrate`), and every
  next-wave or redispatch branch step. Covering those would need byte-identical
  shared scripts changed (`dispatch-plans.py`, `implementation-progress-check.py`).
  Push-mode runs and multi-wave or redispatch runs can therefore still
  overflow.
- **C. Ship D1-D6 only.** The join step no longer overflows, but the failure
  moves to `reconcile-implementations` and the requested outcome is not met.
  This is not acceptable as a final state.

Rejected: isolating the fanout in a called child workflow. The propagation of
request variables across a cross-workflow transition is not verified, the
graph and route would be restructured, and `expected-routes.json` is out of
scope.

Rollout:

- D1-D6 are required under A and B and proceed now.
- Until the user picks A or B, the prompt-level part of acceptance signal 1
  and the requested outcome ("the run proceeds to reconciliation/integration")
  stay **blocked**. Do not report them as met on the strength of the
  projection test alone.
- If B is chosen, its schema/stub work is added as a plan that depends on the
  D1-D6 plans. If A is chosen, the package plans add only the riela minimum
  version note once the upstream release exists.

### D6. Fixtures, docs, release

- In `mock-scenario.json`, `mock-scenario-fanout.json` and
  `mock-scenario-local.json`, the `implementation-wave-outcome` responses set
  `model: "scripts/implementation-wave-outcome.py"` (the convention used by
  `plan-push-gate`) and `when` includes `partial_success:false`. Payloads and
  routes are unchanged, so `.agents/skills/riela-package-release/fixtures/expected-routes.json`
  needs no edit. `mock-scenario-planning-only.json` has no implementation
  wave; check it and run it unchanged.
- `EXPECTED_RESULTS.md`:
  - Line 28: every agent node except `step6-implement` uses Opus, and
    `implementation-wave-outcome` is now a deterministic command.
  - Line 42: the shared-with-Codex statement excludes `implementation-wave-outcome` and
    the reconcile and integration-review prompts.
  - New paragraph: the wave summary path, bounds and verdict binding.
- Package `README.md`: add a node-table row for the command and a short
  "Compact wave summary" section with the storage path. The skill `SKILL.md`
  "GPT-6 Luna fanout" section gets a matching paragraph.
- Release: set `riela-package.json` to `0.1.9`, then run
  `bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-terra-design-and-implement-review-loop`
  and regenerate `registry-index.json` (`mise run package:generate-index`).
  Update the root `README.md` listing text only if its description changes.

## Verification

New `packages/opus-terra-design-and-implement-review-loop/tests/test_wave_outcome.py`
uses `unittest` (it must run under both `unittest` and `pytest`). It loads the
script with `importlib`, calls `classify(envelope, root)` with a temporary
root, and covers these cases:

1. Synthetic join of at least 8 MiB: 4 branches (3 successful with long
   continuation outputs and long review feedback, 1 progress-blocked), at
   least 5,000 observations over at least 1,000 paths in both selections, and
   capture/reduce diagnostics. Assertions:
   - The serialized join is at least 8 MiB.
   - `wave-summary.json` bytes plus the payload bytes are at most 65,536.
   - The raw file's sha256 equals the input's and `rawJoinBytes` is correct.
   - Per-plan status/classification, blockers and resume criteria are
     present, and the verdict is correct.
   - `hasDrift`, `complete`, `captureFailuresTotal`, `reduceFailuresTotal`
     and `observationTotal` are exact.
   - Source content-drift paths rank first.
2. Each policy prefix gives `tracking-rejected` with the exact resume
   criterion, and diagnostics drop `contents`. A successful sibling gives
   `partial_success:true`.
3. `complete:false`, attributable vs unattributable.
4. A blocked-only wave gives `partial_success:false`.
5. Ordinary failed/cancelled branches leave `implementation_blocked:false`.
6. The unblocked verdict has empty lists.
7. The payload keys equal the node schema properties, and the
   `workflow.json` transitions of `implementation-wave-outcome` are unchanged.
8. Successive calls create `wave-001` and `wave-002` with nothing
   overwritten. Unsafe `workflowExecutionId` and symlinked `tmp` fail closed.
9. Determinism: the same input gives the same summary bytes, apart from the
   ordinal and path fields.
10. A minimal-level overflow exits with an error.

Case 1 bounds the *projection*: the summary plus the verdict. It does not
bound the rendered prompt while the request variable persists (D7).

Prompt-level checks for `reconcile-implementations`, `integration-review` and
`implementation-blocked-output`:

11. In-package, a static test: those three prompt files do not instruct
    reading `runtimeVariables.fanoutJoin` or `fanoutJoin.branches`, and
    `reconcile-implementations.md` and `integration-review.md` reference the
    wave summary locator and the `rawPointer` extraction rule.
12. Rendered-prompt bound, an explicit owned gap. Mock scenarios render no
    prompts and the package cannot run the riela runner.
    - Under option A, the upstream riela change must include a runner test
      proving that a post-join step's `runtimeVariables` and next-wave branch
      variables lack the raw `fanoutJoin`. Owner: riela maintainer (user).
    - Under either option, the operator confirms on the first live
      multi-branch wave that the `reconcile-implementations` node execution
      record's prompt holds no raw join and stays within context. Owner:
      operator (user).
    - Until then, the prompt-level part of acceptance signal 1 is reported
      as blocked.

Commands (record exit status and complete log paths under `tmp/wave-compaction/`):

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -p 'test_*.py' -v`
  (and `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest packages/opus-terra-design-and-implement-review-loop/tests` when pytest is installed)
- `riela workflow validate --workflow-definition-dir packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop`
- `riela workflow run` with `--mock-scenario` for each of the four scenarios
  (`mock-scenario-local.json` with `--variables '{"workflowInput":{"gitPush":false}}'`),
  using an isolated `--session-store` and `--artifact-root`
- `riela package validate packages/opus-terra-design-and-implement-review-loop`
- `mise run check` (includes `workflow:check-scenarios` route assertions and
  the Codex tests that load this package's unchanged `dispatch-plans.py` and
  `implementation-progress-check.py`)

## Constraints and boundaries

- Do not modify `dispatch-plans.py`, `implementation-progress-check.py`,
  other packages, `.agents/`, or riela runtime sources. `git-push-gate.py`
  changes only if the user selects D7 option B.
- The design is limited to the targetScope paths, `registry-index.json` and
  the root `README.md` listing.
- gitPush=false: commits stay local and unpublished.
