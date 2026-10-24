# gate-routing-graph

Status: completed. Wave 2. Issues tacogips/riela#128, #129 and #132 (graph wiring, schemas, fixtures, docs). Implementation accepted by test-integrity, adversarial and integration review in opus-luna-design-and-implement-review-loop-session-1 (integration-review-attempt-1-exec-93). Archived from `impl-plans/active/gate-routing-graph.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "gate-routing-graph",
  "planPath": "impl-plans/active/gate-routing-graph.md",
  "dependsOn": ["gate-routing-contract-gate", "gate-routing-dispatch-amendment", "gate-routing-plan-archive"],
  "writePaths": [
    "impl-plans/active/gate-routing-graph.md",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/workflow.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/nodes/node-dispatch-plans.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/nodes/node-step8-docs-refresh.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/nodes/node-implementation-blocked-output.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-fanout.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-local.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/EXPECTED_RESULTS.md",
    "packages/opus-luna-design-and-implement-review-loop/README.md",
    "packages/opus-luna-design-and-implement-review-loop/tests/test_workflow_routing.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-luna-design-and-implement-review-loop/tests/test_workflow_routing.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-luna-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'",
    "riela workflow validate opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows",
    "riela workflow run opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows --mock-scenario packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario.json --session-store tmp/opus-luna-gate-routing/gate-routing-graph/sessions-main --artifact-root tmp/opus-luna-gate-routing/gate-routing-graph/artifacts-main --output json",
    "riela workflow run opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows --mock-scenario packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-fanout.json --session-store tmp/opus-luna-gate-routing/gate-routing-graph/sessions-fanout --artifact-root tmp/opus-luna-gate-routing/gate-routing-graph/artifacts-fanout --output json",
    "riela workflow run opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows --mock-scenario packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-local.json --variables '{\"workflowInput\":{\"gitPush\":false}}' --session-store tmp/opus-luna-gate-routing/gate-routing-graph/sessions-local --artifact-root tmp/opus-luna-gate-routing/gate-routing-graph/artifacts-local --output json",
    "riela workflow run opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows --mock-scenario packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-planning-only.json --session-store tmp/opus-luna-gate-routing/gate-routing-graph/sessions-planning --artifact-root tmp/opus-luna-gate-routing/gate-routing-graph/artifacts-planning --output json",
    "mise run workflow:check-compact",
    "find packages/opus-luna-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "workflow.json adds nodes plan-contract-validate (nodes/node-plan-contract-validate.json) and plan-archive (nodes/node-plan-archive.json) and the edges from design D4.2, D5.5 and D6.2: plan-checkpoint !(checkpoint_blocked) -> plan-contract-validate; plan-contract-validate contract_valid -> plan-git-commit and !(contract_valid) -> step4-impl-plan-create; dispatch-plans transitions[0] is the unchanged fanout plus label dispatch_ready, transitions[1] amendment_required -> step4-impl-plan-create, transitions[2] amendment_blocked -> implementation-blocked-output; step8-docs-refresh -> plan-archive; plan-archive !(completion_blocked) -> step9-commit-message and completion_blocked -> implementation-blocked-output. Every other edge is unchanged.",
    "node-dispatch-plans.json uses scriptPath scripts/dispatch-wave.py. Its schema keeps properties.implementationItems (minItems 1, item schema unchanged including required artifactRoots), drops implementationItems from top-level required, adds the remaining keys of dispatch-wave AMENDMENT_PAYLOAD_KEYS as properties, keeps additionalProperties false, and requires acceptedPlanIds, manifestPath, checkpointCommit, dispatch_ready, amendment_required and amendment_blocked.",
    "node-step8-docs-refresh.json adds an optional archiveRequests array of {source, destination} string objects, plus a required property issueReference {type:string, minLength:1}, appended to required. node-implementation-blocked-output.json drops blockedPlanIds minItems and adds an optional blockedStepId string.",
    "mock-scenario.json, mock-scenario-fanout.json and mock-scenario-local.json add plan-contract-validate (model scripts/validate-plan-contract.py, when {contract_valid:true}, payload passing the checkpoint commitMessage/committedFiles plus contract_valid, report and findings) and plan-archive (model scripts/plan-archive.py, when {completion_blocked:false}, payload with archiveResults, archivedImplPlanPaths, docsRefreshRound 1 and completion_blocked false). Each dispatch-plans response uses model scripts/dispatch-wave.py and when/payload {dispatch_ready:true, amendment_required:false, amendment_blocked:false}. step8 payloads add archiveRequests and issueReference, using the scenario's existing issue reference value, e.g. \"tacogips/cursor-agent#123\" in mock-scenario.json. mock-scenario-planning-only.json is unchanged.",
    "riela workflow validate is valid. All four mock runs complete with exit 0. EXPECTED_RESULTS.md and README.md describe the new nodes, routes and bounds, with execution counts re-measured from these runs.",
    "test_workflow_routing.py asserts the edges, the node scriptPaths and the schema/payload-key consistency below. mise run workflow:check-compact passes. All opus-luna and codex tests pass and no __pycache__ remains."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-luna-gate-routing-0110.md`, D4.2, D5.5-D5.6, D5.8 (schema), D6.1-D6.2 and D7. `W`/`T` as in `impl-plans/active/gate-routing-negative-control.md`.

This plan wires the scripts and nodes delivered in wave 1:
- `gate-routing-contract-gate`: `W/scripts/validate-plan-contract.py`, `W/nodes/node-plan-contract-validate.json`;
- `gate-routing-dispatch-amendment`: `W/scripts/dispatch-wave.py` with `AMENDMENT_PAYLOAD_KEYS`;
- `gate-routing-plan-archive`: `W/scripts/plan-archive.py`, `W/nodes/node-plan-archive.json`.

It updates the fixtures and docs. `workflow.json` has a single owner here, because all three routing changes edit it.

## Non-goals

- Do not edit `.agents/skills/riela-package-release/fixtures/expected-routes.json`. It is outside scope. See `design-docs/user-qa/opus-luna-gate-routing-0110.md`, default option A.
- Do not edit scripts, prompts, `mock-scenario-planning-only.json`, `riela-package.json` or `registry-index.json`.
- Do not change `loop.convergence`, `defaults` or other steps' edges.
- Do not add a new mock scenario file.

## File-level changes

1. `W/workflow.json`
   - Add the two `nodes[]` entries. Imitate the existing `{ "id", "nodeFile" }` entries.
   - Add step `plan-contract-validate`. Copy its description and transitions from `packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/workflow.json` (step `plan-contract-validate`, around lines 607-622).
   - Add step `plan-archive`, role `worker`. Description: "Deterministically archive completed plans requested by Step 8 before the read-only completion check; stop with a blocked handoff after three rejected completion rounds."
   - Change the `step8-docs-refresh` transition target to `plan-archive`.
   - Insert `"label": "dispatch_ready"` into `dispatch-plans` `transitions[0]` without altering its `fanout` object. Append the two amendment transitions.
   - Update the `implementation-blocked-output` step description so it also covers dispatch amendment exhaustion and completion-loop blocks.
2. `W/nodes/node-dispatch-plans.json`
   - `command.scriptPath` -> `scripts/dispatch-wave.py`.
   - New `description` that mentions routed amendments.
   - Schema per acceptance criterion 2. Types:
     - booleans: `dispatch_ready`, `amendment_required`, `amendment_blocked`;
     - `checkpointAmendment`: `{type: object}`;
     - arrays of strings: `pendingPlanIds`, `blockedPlanIds`, `successfulPlanIds`, `resumeCriteria`;
     - `blockers`: `{type: array, items: {}}`;
     - strings: `issueReference`, `nextStep`.
3. `W/nodes/node-step8-docs-refresh.json`:
   - Add property `archiveRequests` as `{type: array, items: {type: object, properties: {source: {type: string}, destination: {type: string}}, required: [source, destination]}}`. Do not add it to `required`.
   - Add property `issueReference: {type: string, minLength: 1}` and append `issueReference` to `required` (Step 5 finding S5-F1).
     - Runtime validation then guarantees that `plan-archive` can forward a non-empty issue reference into the `completion_blocked` handoff.
     - This is required because `implementation-blocked-output` requires `issueReference` (minLength 1). Do not relax that requirement.
4. `W/nodes/node-implementation-blocked-output.json`: remove `"minItems": 1` from `blockedPlanIds` only, and add `blockedStepId: {type: string}`.
5. The three mock scenarios: the edits from acceptance criterion 4.
   - `mock-scenario.json`: insert the new keys near their predecessors, e.g. `plan-contract-validate` after `plan-checkpoint`.
   - `mock-scenario-fanout.json`: if `dispatch-plans` is an array of responses, update every element.
   - Use `archiveRequests: [{"source": "impl-plans/active/a.md", "destination": "impl-plans/completed/a.md"}]`, or match the scenario's plan path.
   - Add `issueReference` to every `step8-docs-refresh` payload, copying the scenario's existing issue reference (e.g. `step1-issue-intake.payload.issueReference`, `"tacogips/cursor-agent#123"` in `mock-scenario.json`). Also mirror it into the `plan-archive` mock payload. Check that step9's mock `archivedImplPlanPaths` and `committedFiles` stay consistent.
6. `W/EXPECTED_RESULTS.md`:
   - Line 5: route gains `plan-contract-validate` after `plan-checkpoint`, and `plan-archive` after `step8-docs-refresh`.
   - Line 7: replace "23 executions versus 26" with the counts measured from the mock run outputs.
   - Line 12: Step 8 requests archive moves, `plan-archive` performs them without git, Step 9 verifies `archiveResults`, and the loop ends blocked after three rejected rounds.
   - Line 18: the pre-commit `plan-contract-validate` gate routes rejections to Step 4.
   - Line 30: `dispatch-plans` runs `scripts/dispatch-wave.py` around the byte-identical projection.
   - New paragraph for amendment routing (`amendment_required` -> Step 4, max 2 amendments, then `amendment_blocked` -> blocked output).
   - Lines 34-40: one sentence each for sibling-owned blockers, negative controls, structured `kind: "behavioral-test"` and `exit=N` parsing.
   - Line 46: remove "This workflow has no pre-commit `plan-contract-validate` gate; the dispatch-time check is its only deterministic preflight." and keep "dispatch-plans is byte-identical to the Codex base".
7. `packages/opus-luna-design-and-implement-review-loop/README.md`:
   - In the role table, add a row "Deterministic gates | `plan-contract-validate`, `dispatch-plans`, `plan-archive` | `command`".
   - Under "Review revision routing", add three sentences: the pre-commit gate, the amendment route, and deterministic plan archiving with its bound.
8. `T/test_workflow_routing.py`: a new module.
   - Load the JSON files, plus `dispatch-wave.py` via `importlib` for `AMENDMENT_PAYLOAD_KEYS`.

## Key points and pitfalls

- `.agents/skills/riela-package-release/scripts/check-compact-workflows.ts:392-397` reads `dispatch-plans` `transitions[0].fanout.changeTracking` and `node-dispatch-plans.json` `output.jsonSchema.properties.implementationItems.items.required`. Keep both paths.
- Keep these existing tests green:
  - `T/test_git_push_gate.py:63-74`: plan-git-commit, plan-push-gate, step10 and final-push-gate edges; `mock-scenario-local.json` must not contain plan-git-push, step11-git-push or base-branch-integrate.
  - `T/test_review_handoff.py:21-26`: integration-review `transitions[0]` is `{dispatch-plans, needs_revision}`.
  - `T/test_wave_outcome.py:173-184`: implementation-wave-outcome node and edges unchanged.
- Mock dispatch payloads must satisfy the closed schema. Include the three booleans in the payload, not only in `when`.
- Measure execution counts from the actual run outputs. Do not guess.
- `mise run workflow:check-scenarios` is expected to report the opus-luna route as stale. Per user-qa option A and design D4/D6, this is an expected operator-owned out-of-scope dependency, not a gate for this plan: no accepted acceptance signal requires `workflow:check-scenarios`. Report the exact dependency object `{dependency: ".agents/skills/riela-package-release/fixtures/expected-routes.json", reason: "route gains plan-contract-validate and plan-archive", owner: "operator"}` in Step 6 `risks` and `authorSelfCheck.residualRisks`, not in `blockers`; keep it visible for the operator and release/final reporting.

## Test cases (`test_workflow_routing.py`)

- Edges equal exactly:
  - plan-checkpoint `[{plan-contract-validate, "!(checkpoint_blocked)"}]`;
  - plan-contract-validate `[{plan-git-commit, contract_valid}, {step4-impl-plan-create, "!(contract_valid)"}]`;
  - step8 `[{plan-archive}]`;
  - plan-archive `[{step9-commit-message, "!(completion_blocked)"}, {implementation-blocked-output, completion_blocked}]`.
- dispatch-plans:
  - `transitions[0]` has `label == "dispatch_ready"`, `fanout.changeTracking == {pathsFrom:"/trackedPaths", artifactRootsFrom:"/artifactRoots"}`, `fanout.joinStepId == "implementation-wave-outcome"`, and no `concurrency`;
  - `transitions[1:]` equal the two amendment edges.
- Node scriptPaths: dispatch-plans `scripts/dispatch-wave.py`, plan-archive `scripts/plan-archive.py`, plan-contract-validate `scripts/validate-plan-contract.py`. Every referenced `nodeFile` exists.
- `set(AMENDMENT_PAYLOAD_KEYS) <= set(dispatch schema properties)`, and the dispatch schema `required` equals the six keys.
- Each of the three mock scenarios has `plan-contract-validate` and `plan-archive` entries, and its `dispatch-plans` `when` has `dispatch_ready` True.
- `mock-scenario-planning-only.json` has no `plan-archive` key.
- The `node-step8-docs-refresh.json` schema lists `issueReference` in `required`, with `type: string` and `minLength: 1`. Every `step8-docs-refresh` mock payload in the three scenarios has a non-empty string `issueReference`.

## Done criteria

- All verification commands exit 0. For each command, keep the full log under `tmp/opus-luna-gate-routing/gate-routing-graph/`, with exit status, and the mock run status/route/execution count.

## Progress log

- 2026-10-24: Implemented the owned graph wiring for #128/#129/#132. Added `plan-contract-validate` and `plan-archive` workflow nodes and routes; changed dispatch to the amendment wrapper with its closed output schema; added Step 8 archive request/issue reference schema and blocked handoff schema support. Updated the three full-run mock scenarios while leaving planning-only unchanged, documented the new routes and measured counts, and added eight routing regressions. Full Opus suite passed 108 tests; Codex compatibility suite passed 91 tests; compact workflow check passed all 30 regressions. Workflow validation and all four mocks completed with exit 0: main 27 transitions, fanout 27, local-only 24, planning-only 15. Local and planning-only required absolute scenario paths because the CLI resolved the plan's relative form from the package root; their initial relative-path invocations exited 1 before workflow execution. Logs are under `tmp/opus-luna-gate-routing/gate-routing-graph/`. Formal independent review, integration review, and release/digest refresh remain downstream.
- 2026-10-24: IR8-F1 disposition: clarified that the stale `.agents/skills/riela-package-release/fixtures/expected-routes.json` route is an expected operator-owned dependency reported in Step 6 risks and `authorSelfCheck.residualRisks`, not a blocker, because no accepted acceptance signal requires `workflow:check-scenarios`. Kept the exact dependency object for operator reporting. Re-ran the assigned graph verification on the current combined tree; logs are under `tmp/opus-luna-gate-routing/gate-routing-graph/ir8-rerun/`.
