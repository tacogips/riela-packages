# Opus Terra blocked-wave checkpoint amendment

Issue: `local:tacogips/riela-packages#opus-terra-blocked-wave-amendment`
(workflowInput issue; there is no GitHub issue).
Package: `packages/opus-terra-design-and-implement-review-loop` (0.1.15 -> 0.1.16).

## Problem

`implementation-wave-outcome` (command node
`scripts/implementation-wave-outcome.py`) returns
`when: {implementation_blocked, partial_success}`. A fully blocked wave
(`implementation_blocked && !partial_success`) goes straight to the terminal
`implementation-blocked-output` step. In monja security batch 1 (sessions
630-651), almost every such blocker was a scope or contract gap that the plan
owner could decide: a file outside `writePaths`, a missing additive
port/projection field, an unspecified authority/readback rule, or a
fixture/composition file with no owner. Each gap needed a hand-written plan
amendment and a restart from `plan-checkpoint`.

This design adds a bounded, deterministic route from a fully blocked,
amendment-eligible wave to Step 4's existing bounded checkpoint amendment
mode. It reuses `dispatch-wave.py`'s machinery and budget. It adds no new
step, no model call and no new abstraction.

## Baseline reused

- `design-opus-terra-wave-input-compaction.md` D1-D3: the wave outcome is a
  deterministic command join. It writes
  `tmp/opus-terra-waves/<workflowExecutionId>/wave-NNN/{fanout-join.json,wave-summary.json}`
  and has a closed output schema. Those decisions are unchanged. This design
  extends the verdict, the schema and the transitions only.
- `dispatch-wave.py` `amendment_result`: `checkpointAmendment` shape
  (`reason`, `manifestPath`, `previousCheckpointCommit`, `amendmentRound`,
  `maxAmendmentRounds`), `MAX_CHECKPOINT_AMENDMENTS = 2`, and the
  0-based round semantics (`required = amendmentRound < MAX`).
- Step 4 / Step 5 / `plan-checkpoint` already handle `checkpointAmendment`:
  stable plan IDs, `acceptedDependencies`, carrying the amendment verbatim,
  checking HEAD against `previousCheckpointCommit`, and committing only
  manifest/plan/design files.

`scripts/dispatch-plans.py` stays byte-identical (EXPECTED_RESULTS issue #130
contract). The new code only imports its helpers.

## Runtime facts this design relies on

- The join step's inbox holds only the join message and branch messages. It
  does not hold `plan-git-commit`/`plan-git-push`/`plan-push-gate` messages
  (wave-input-compaction doc: "the join carries no dispatch item or
  manifest"). So the wave outcome cannot reuse dispatch-wave's
  inbox-based checkpoint counting.
- Command nodes run with the repository root as cwd.
- During a wave, HEAD is the dispatched plan checkpoint commit. Dispatch
  verifies `checkpointCommit == HEAD` (`dispatch-plans.py` `verify_checkpoint`).
  Fanout branches never commit. Before Step 10, the only commits in a run
  are plan checkpoints created by `plan-git-commit`.
- Blocked branch outputs come from `implementation-progress-check`
  `blocked_result`. Their payload-level `blockerType` is the gate type
  (`implementation-dependency`, `implementation-incomplete`,
  `implementation-material-finding`, `implementation-no-progress`,
  `implementation-materially-unverified`, `implementation-invalid-evidence`).
  Their `blockers` list is Step 6's own blockers followed by one gate marker
  `{type, planId, message, evidenceFingerprint}`. Step 6 blockers are
  free-form objects that carry "the exact dependency and resume criterion"
  (`prompts/step6-implement.md`), and often `paths`/`path`, and `evidence`.
- Mock scenarios answer command nodes by node id. Scripts are not executed
  in `--mock-scenario` runs.

## Decisions

### D1. Eligibility (rule-based, in `implementation-wave-outcome.py`)

The rules are evaluated after `_classify_join`, on the uncapped per-plan
records, and only when `implementation_blocked && !partial_success`. A wave is
**amendment-eligible** only when every rule holds. Any failure makes it
ineligible, and the reason string is recorded in D5.

1. **Wave shape.** Every plan classification is `blocked` or `pending`. Any
   `tracking-rejected`, `evidence-incomplete`, `failed`, `cancelled`,
   `evidence-missing` or other classification makes the wave ineligible.
   Those are runtime/policy failures, not plan-owner decisions.
2. **Plan gate type.** For every blocked plan, `blockerType ==
   "implementation-dependency"` exactly. No other gate type is "equivalent".
   `implementation-material-finding` (review rejection),
   `implementation-materially-unverified` (test integrity/verification),
   `implementation-no-progress`, `implementation-incomplete` and
   `implementation-invalid-evidence` are ineligible.
3. **Environment flag.** The blocked plan output has no
   `environmentBlocked`/`environment_blocked: true`, and its `status` is not
   `environment-blocked`/`blocked-environment`. These are the same predicates
   as `implementation-progress-check.py` `environment_blocked`.
4. **Substantive blockers.** Drop the gate marker (a dict with an
   `evidenceFingerprint` key whose `type` equals the plan `blockerType`).
   Each blocked plan must then have at least one remaining blocker, and
   **every** remaining blocker must be a dict that carries a scope/contract
   signal:
   - a non-empty `paths` list of strings or a non-empty `path` string, or
   - a non-empty `dependency` string, or
   - a `resumeCriterion` string (or a `resumeCriteria` string list) that
     contains, case-insensitively, one of `authoriz`, `amend`, `writepaths`,
     `ownership`, `owner`, `contract`, `scope`.

   A string-only blocker is ineligible because it has no structured
   path/dependency to amend.
5. **Exclusion markers (fail closed).** No substantive blocker may match the
   denylist. Matching uses lowercase containment over the blocker's `type`,
   `blockerType`, `category`, `kind`, `dependency`, `message`, `evidence`
   (stringified when it is not a string) and `resumeCriterion` values, and
   over **every string in the blocker's `resumeCriteria` list**. A
   non-string entry in that list makes the blocker ineligible. The blocked
   plan's own top-level `resumeCriteria` strings are scanned too. Invariant:
   every field that rule 4 accepts as a scope signal is also scanned here,
   so no field can contribute eligibility without also being checked for
   exclusion. Markers:
   - environment/runtime: `environment`, `sandbox`, `network`, `dns`,
     `credential`, `permission denied`, `toolchain`, `timeout`, `timed out`,
     `out of memory`, `disk`
   - external service: `external service`, `external-service`,
     `third-party`, `rate limit`, `service unavailable`, `api key`
   - review rejection: `review rejection`, `review-rejection`,
     `rejected by review`, `needs_revision`
   - test integrity: `test-integrity`, `test integrity`,
     `weakened assertion`, `skipped test`, `flaky`

   Bare words such as `test`, `review` and `fixture` are deliberately not
   markers, because an unowned test fixture is an eligible gap. A false
   match only falls back to today's blocked output, which is safe.
   Unknown blocker shapes are ineligible by rule 4.
6. **Checkpoint resolvable.** D2 resolves `manifestPath`,
   `previousCheckpointCommit` and `amendmentRound` without error.
7. **Size.** The serialized `checkpointAmendment` (D3) is at most
   `AMENDMENT_BYTE_LIMIT = 16384` bytes, and the capped verdict plus the
   amendment still fit the existing 65536-byte payload+summary bound. Values
   are never truncated, because the amendment must be verbatim. An oversize
   amendment is ineligible.

`amendment_required = eligible && amendmentRound < MAX_CHECKPOINT_AMENDMENTS`.

### D2. Shared, bounded round counter

**Definition (both scripts).** `amendmentRound` is the number of plan
checkpoint commits created so far in this run, minus 1. Every bounded
amendment, from either source, produces exactly one new plan checkpoint
commit. A single count therefore bounds dispatch amendments and blocked-wave
amendments together.

- `dispatch-wave.py` keeps its existing evidence: distinct `git.commitHash`
  values from its `plan-git-push`/`plan-git-commit`/`plan-push-gate` inbox
  messages, minus 1. Its behavior is unchanged. Blocked-wave amendment
  checkpoints arrive through `plan-git-commit` (and `plan-git-push`) like any
  checkpoint, so it counts them automatically.
- `implementation-wave-outcome.py` derives the same count from Git, because
  its inbox has no checkpoint messages:
  1. `previousCheckpointCommit = git rev-parse HEAD`.
  2. `manifestPath`: call `dispatch.checkpoint_source` (dispatch-plans
     helpers loaded via importlib, as `dispatch-wave.py` does) with one
     synthesized `plan-git-commit` message
     `{git: {operation: "commit", commitHash: HEAD, committedFiles: <git diff-tree --root --no-commit-id --name-only -r HEAD>}}`.
     That reuses its exactly-one-manifest and rename rules.
  3. Read `originalHead` from the committed manifest. Verify it is a commit
     and an ancestor of HEAD (`git merge-base --is-ancestor`).
  4. `amendmentRound = (git rev-list --count --first-parent originalHead..HEAD) - 1`.

  Any git error, a missing manifest, a missing or non-ancestor
  `originalHead`, or a count below 1 makes the wave ineligible (D1 rule 6).
- `MAX_CHECKPOINT_AMENDMENTS` stays **2**, with one definition. The wave
  outcome imports it from `dispatch-wave.py` (importlib), so the bound cannot
  drift. Rationale: existing tests and README/EXPECTED_RESULTS pin two
  rounds. A blocked-wave amendment asks Opus to resolve every blocker of the
  wave at once, not one gap per restart. The intake allowed a modest raise
  but did not require one. Raising the bound later changes one constant and
  its docs (see `design-docs/user-qa/opus-terra-blocked-wave-amendment.md`).
- Scope: "per checkpoint lineage" means per run, from the manifest's
  `originalHead` (the run's intake HEAD) to the current checkpoint. If a
  resumed run reuses a manifest whose `originalHead` predates the run, the
  wave outcome counts earlier checkpoints too. That is stricter than
  dispatch's per-session inbox count, so the run still stays bounded. This
  divergence is accepted.

Worked bound: C0 is the initial checkpoint (round 0). A dispatch amendment
creates C1 (round 1). A blocked wave at C1 is amendment-eligible
(1 < 2) and creates C2. A second blocked wave at C2 has round 2, which is
not below the bound, so it goes to `implementation-blocked-output`. A
dispatch amendment at C2 likewise returns `amendment_blocked`.

### D3. Output contract

stdout becomes
`{"when": {"implementation_blocked": B, "partial_success": P, "amendment_required": A}, "payload": {...verdict, "amendment_required": A, ["checkpointAmendment": {...}]}}`.
`amendment_required` is always emitted. `checkpointAmendment` is emitted
only when `A` is true:

```
{
  "reason": "blocked-wave-scope-or-contract",
  "blockedPlanIds": [...],                 // verdict order
  "blockers": [                            // every substantive blocker, verbatim
    {"planId", "paths"?, "path"?, "dependency"?, "evidence"?, "resumeCriterion"?, "resumeCriteria"?, "message"?}
  ],                                       // copy only these keys, only when present
  "manifestPath": "<D2>",
  "previousCheckpointCommit": "<HEAD>",
  "amendmentRound": <int>,
  "maxAmendmentRounds": MAX_CHECKPOINT_AMENDMENTS,
  "summaryPath": "<wave-summary.json>",
  "rawJoinPath": "<fanout-join.json>"
}
```

The verdict's existing six fields keep their current values and caps.
`nodes/node-implementation-wave-outcome.json` `output.jsonSchema` (closed,
`additionalProperties: false`) gains `amendment_required: boolean`
(required) and `checkpointAmendment: object` (optional). `SCHEMA_KEYS`
gains `amendment_required`. A separate optional-key constant lists
`checkpointAmendment`.

### D4. Routing (workflow.json, `implementation-wave-outcome.transitions`)

The transitions, in this order, are mutually exclusive by label:

1. `step4-impl-plan-create`: `implementation_blocked && !(partial_success) && amendment_required` (new)
2. `implementation-blocked-output`: `implementation_blocked && !(partial_success || amendment_required)`
3. `reconcile-implementations`: `!(implementation_blocked) || partial_success` (unchanged)

The script sets `amendment_required` only for a fully blocked wave. The labels
also encode that condition, so a partial-success wave can never take route 1.
The step description is updated to "blocked-only waves amend within budget
or terminate". Nothing else in workflow.json changes. Step 4 →
Step 5 → `plan-checkpoint` → `plan-contract-validate` → `plan-git-commit` →
`plan-push-gate`/`plan-git-push` → `dispatch-plans` then redispatches. That
path already exists.

### D5. Wave summary evidence

`wave-summary.json` gains one top-level object:
`amendmentDecision: {eligible, amendmentRequired, amendmentRound|null, maxAmendmentRounds, ineligibleReasons: [string]}`.
It holds at most 10 reasons, each at most 160 chars. It gives an operator the
deterministic reason a blocked wave was not auto-amended. The payload
handed to `implementation-blocked-output` is unchanged for ineligible and
exhausted waves, apart from `amendment_required: false`. The prompt
`prompts/implementation-blocked-output.md` needs no change.

### D6. Prompt changes (no redesign)

- `prompts/step4-impl-plan-create.md`, bounded amendment bullet: accept the
  amendment from `dispatch-plans` **or `implementation-wave-outcome`**. For
  `reason: blocked-wave-scope-or-contract`, decide each listed blocker
  conservatively within the accepted design:
  - authorize the exact extra repository paths in the owning pending plan's
    `writePaths` (concrete paths, no globs or directories broader than the
    blocker named);
  - specify a missing additive port/field/authority/readback rule as an
    additive contract in the plan that owns it;
  - assign an unowned fixture/composition file to exactly one plan, and keep
    plans at the same dependency level free of write clashes (otherwise
    order them with `dependsOn` or keep the file in one plan);
  - record the decisions in a dated `## Amendment <YYYY-MM-DD> (blocked-wave-scope-or-contract, round N)`
    section in each affected plan.

  Never redesign. A gap that needs a design change is not decided here: Step 4
  states it as a Step 5 blocker so that `needs_design_revision` handles it.
  Keep plan IDs stable. Record accepted plans (`successfulPlanIds`, or
  previously accepted) as `acceptedDependencies`. Carry `checkpointAmendment`
  verbatim. Update the "after two amendments" sentence: the bound is shared
  across dispatch and blocked-wave amendments.
- `prompts/plan-checkpoint.md`: the existing amendment paragraph applies to
  both reasons. Add one sentence: for `blocked-wave-scope-or-contract`, the
  working tree holds blocked plans' uncommitted implementation changes,
  which stay unstaged and out of `committedFiles`. The HEAD check against
  `previousCheckpointCommit` is unchanged.
- `prompts/step5-impl-plan-review.md`: the scope sentence covers the new
  reason. It also checks per-blocker decisions, that no redesign took place,
  and that there are no same-level write clashes. This is one sentence.

### D7. Tests, scenario, docs, release

- `tests/test_wave_outcome.py`: update the three assertions the feature
  necessarily changes. They stay exact equalities, not weakened ones: the
  `when` dict for a blocked-only wave adds `amendment_required: False`
  (non-git temp root ⇒ ineligible); the payload-key set uses the extended
  `SCHEMA_KEYS`; and the exact 3-transition list from D4.
- New `tests/test_blocked_wave_amendment.py`. It uses temp Git repos with
  an intake commit, a checkpoint commit containing a manifest with
  `originalHead`, and optional extra checkpoint commits. It covers:
  - eligible wave → `amendment_required`, with an exact `checkpointAmendment`
    (verbatim blockers, round, max, commit, manifest);
  - each ineligible class → blocked: gate types other than
    implementation-dependency, environment flag, each denylist family,
    string-only blocker, gate-marker-only plan, tracking-rejected,
    evidence-incomplete, failed, and a non-git/unresolvable checkpoint;
  - plural-field exclusion regressions: for each of the four families
    (environment/runtime, external service, review rejection, test
    integrity), a blocker with `paths`, a scope `dependency` and the marker
    **only** in `resumeCriteria` → `amendment_required: false`. One case is
    the review's exact reproduction:
    `{paths:['tests/test_contract.py'], dependency:'missing additive field', resumeCriteria:['Resolve test-integrity failure: restore skipped test before continuing.']}`.
    The same applies when the marker is only in the plan-level
    `resumeCriteria`, and a non-string `resumeCriteria` entry is also
    ineligible;
  - positive scope-only control: the same blocker with
    `resumeCriteria: ['Authorize tests/test_contract.py in writePaths via checkpoint amendment.']`
    → `amendment_required: true`;
  - exhausted budget (two extra checkpoint commits) → blocked;
  - shared counter: one dispatch-amendment checkpoint followed by a blocked
    wave gives round 1 and is eligible, then one more checkpoint exhausts
    the budget. Also asserts the wave outcome's
    `MAX_CHECKPOINT_AMENDMENTS` is dispatch-wave's object;
  - partial-success with eligible-looking blockers → `amendment_required: false`;
  - transition order/labels in workflow.json, and that the labels are
    mutually exclusive over all 8 boolean combinations;
  - prompts mention `blocked-wave-scope-or-contract` (step4,
    plan-checkpoint).
- New `mock-scenario-blocked-wave-amendment.json`, derived from
  `mock-scenario-local.json` (local-only, `gitPush:false`), runs initial
  dispatch_ready → blocked wave → Step 4 amendment → Step 5 → checkpoint →
  redispatch → successful wave → reconcile → integration review → normal
  local finalization.

  **Sequencing contract (verified).** A mock entry keyed by node id may be
  an **array** of responses. Responses are consumed by a per-node cursor in
  visit order, and the last entry repeats once the array is exhausted. This
  is the ScenarioNodeAdapter behavior, mirrored by the repo runner at
  `.agents/skills/riela-package-release/scripts/check-package-compat.ts:241-255`
  ("Match ScenarioNodeAdapter's per-step visit and per-node response
  cursor"; `entry[Math.min(sequenceIndex - 1, entry.length - 1)]`). No
  production routing changes for the mock.

  Array entries:
  - `implementation-progress-check`:
    `[{when:{implementation_blocked:true}, payload: blocked implementation-dependency with paths}, {when:{implementation_blocked:false}, payload: ready-for-test-integrity}]`
  - `implementation-wave-outcome`:
    `[{when:{implementation_blocked:true, partial_success:false, amendment_required:true}, payload:{…, amendment_required:true, checkpointAmendment:{reason:"blocked-wave-scope-or-contract", …}}}, {when:{implementation_blocked:false, partial_success:false, amendment_required:false}, payload: success}]`
  - `plan-git-commit`: two responses with distinct `commitHash` values, so
    the trace shows two checkpoints.

  `dispatch-plans` keeps a single `dispatch_ready` response, which serves
  both the initial dispatch and the redispatch. Step 4/Step 5/
  `plan-checkpoint`/`plan-contract-validate`/`plan-push-gate` keep single
  accepting responses, used twice. The second Step 4 response needs no
  separate entry.

  Verification runs as a separate documented command in the style of
  mock-scenario-local.json:
  `riela workflow run opus-terra-design-and-implement-review-loop --workflow-definition-dir packages/opus-terra-design-and-implement-review-loop/workflows --mock-scenario packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/mock-scenario-blocked-wave-amendment.json --variables '{"workflowInput":{"gitPush":false}}' --session-store tmp/scenario-bwa/sessions --artifact-root tmp/scenario-bwa/artifacts --output json > tmp/scenario-bwa/run.json`.

  Required assertions:
  - exit 0 and `status: completed`;
  - `session.executions[].stepId` contains, in order, `dispatch-plans`
    (1st), `implementation-wave-outcome` (1st), `step4-impl-plan-create`,
    `step5-impl-plan-review`, `plan-checkpoint`, `plan-git-commit` (2nd),
    `dispatch-plans` (2nd), `implementation-wave-outcome` (2nd),
    `reconcile-implementations`, `integration-review`, `workflow-output`;
  - `implementation-blocked-output` is absent;
  - the complete JSON log path and exit status are recorded.

  EXPECTED_RESULTS.md lists the exact route and command. The default
  `mock-scenario.json` and the `mise run workflow:check-scenarios` route map
  (`.agents/.../expected-routes.json`, outside package scope) are unchanged.

  **Escalation rule.** If the installed riela rejects array entries, or
  produces a different route at runtime, the implementer must not substitute
  a blocked-terminal scenario or unit tests. The implementer reports a
  blocker naming the capability gap and requests an acceptance amendment.
- README and EXPECTED_RESULTS.md: document the route, the eligibility rules
  in summary, the shared bound of 2 total amendments per run, and how to run
  the new scenario.
- Release: version 0.1.16, digests refreshed, registry index regenerated,
  `__pycache__` removed before validation. Other packages stay
  byte-identical.

## Non-goals

- No change to `dispatch-plans.py`, dispatch-wave's counting or messages,
  partial-success/reconcile routing, the progress gate, or Step 6.
- No model-based classification. Tracking-contract waves are not
  auto-amended.
- No new workflow step or node.

## Verification

`python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -v`;
`riela workflow validate opus-terra-design-and-implement-review-loop --workflow-definition-dir packages/opus-terra-design-and-implement-review-loop/workflows`;
`mise run workflow:check-scenarios`, plus a `riela workflow run ... --mock-scenario mock-scenario-blocked-wave-amendment.json` run with an isolated `--session-store`/`--artifact-root`;
`bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-terra-design-and-implement-review-loop`;
`mise run package:generate-index`; delete `packages/**/__pycache__`;
`riela package validate packages/opus-terra-design-and-implement-review-loop --output json` (valid true);
`mise run package:check-digests`; `mise run package:check-index`.

## Verification gaps

- The design step could not read the monja wave summaries for sessions
  630-651, because they are outside this sandbox and access was denied.
  The eligibility vocabulary comes from this package's own contracts
  (progress-check `blocked_result`, the Step 6 blocker contract). Step 4
  should sample those files read-only if the plan sandbox allows it, and
  confirm that their blockers satisfy D1 rule 4 and miss the D1 rule 5
  markers.
- Mock array sequencing is confirmed from repository evidence:
  `check-package-compat.ts:241-255`, plus array entries already used by
  `packages/codex-adversarial-implementation-review-loop/.../mock-scenario.json:34`
  (`adversarial-review`), `packages/codex-deepdesign/.../mock-scenario.json:32,224,358`
  and `packages/codex-design-and-implement-review-loop/.../mock-scenario-fanout.json:50`.
  The new scenario itself has not been executed yet. Running it is an
  implementation-step verification, and the D7 escalation rule applies if
  it fails.
