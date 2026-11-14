# bwa-scenario-docs

Status: completed (2026-11-03; accepted in session-673 and released in 0.1.16). Wave 2, after `bwa-wave-outcome`. Issue `local:tacogips/riela-packages#opus-terra-blocked-wave-amendment`.
Design: `design-docs/specs/design-opus-terra-blocked-wave-amendment.md` D7 (mock scenario, README, EXPECTED_RESULTS), user-QA Q1/Q2.

```json
{
  "planId": "bwa-scenario-docs",
  "planPath": "impl-plans/active/bwa-scenario-docs.md",
  "dependsOn": ["bwa-wave-outcome"],
  "writePaths": [
    "impl-plans/active/bwa-scenario-docs.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/mock-scenario-blocked-wave-amendment.json",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/mock-scenario.json",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/mock-scenario-local.json",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/mock-scenario-fanout.json",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/EXPECTED_RESULTS.md",
    "packages/opus-terra-design-and-implement-review-loop/README.md"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "riela workflow validate opus-terra-design-and-implement-review-loop --workflow-definition-dir packages/opus-terra-design-and-implement-review-loop/workflows",
    "mkdir -p tmp/scenario-bwa && riela workflow run opus-terra-design-and-implement-review-loop --workflow-definition-dir packages/opus-terra-design-and-implement-review-loop/workflows --mock-scenario packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/mock-scenario-blocked-wave-amendment.json --variables '{\"workflowInput\":{\"gitPush\":false}}' --session-store tmp/scenario-bwa/sessions --artifact-root tmp/scenario-bwa/artifacts --output json > tmp/scenario-bwa/run.json; echo exit=$?",
    "jq -r '.status, ([.session.executions[].stepId]|join(\" \"))' tmp/scenario-bwa/run.json",
    "mkdir -p tmp/scenario-local && riela workflow run opus-terra-design-and-implement-review-loop --workflow-definition-dir packages/opus-terra-design-and-implement-review-loop/workflows --mock-scenario packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/mock-scenario-local.json --variables '{\"workflowInput\":{\"gitPush\":false}}' --session-store tmp/scenario-local/sessions --artifact-root tmp/scenario-local/artifacts --output json > tmp/scenario-local/run.json; echo exit=$?",
    "mkdir -p tmp/scenario-fanout && riela workflow run opus-terra-design-and-implement-review-loop --workflow-definition-dir packages/opus-terra-design-and-implement-review-loop/workflows --mock-scenario packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/mock-scenario-fanout.json --session-store tmp/scenario-fanout/sessions --artifact-root tmp/scenario-fanout/artifacts --output json > tmp/scenario-fanout/run.json; echo exit=$?",
    "mise run workflow:check-scenarios",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "Existing mocks (mock-scenario.json, -local, -fanout) give implementation-wave-outcome amendment_required:false in both when and payload. Their routes and step counts are unchanged.",
    "The new mock-scenario-blocked-wave-amendment.json run exits 0 with status completed. The executions stepId sequence contains, in order: dispatch-plans, implementation-wave-outcome, step4-impl-plan-create, step5-impl-plan-review, plan-checkpoint, plan-git-commit, dispatch-plans, implementation-wave-outcome, reconcile-implementations, integration-review, workflow-output. implementation-blocked-output is absent.",
    "EXPECTED_RESULTS.md documents the new route, the exact command and the observed execution count. README.md documents eligibility in summary, the shared bound (2 total checkpoint amendments per run across dispatch and blocked-wave sources) and the unchanged partial-success route.",
    "mise run workflow:check-scenarios exits 0. Complete logs are kept under tmp/scenario-*/run.json."
  ]
}
```

## Intent and context

This plan adds the required deterministic scenario: blocked wave → amendment → redispatch → success (design D7). It also keeps the existing mocks valid under the new required `amendment_required` schema field.

Abbreviation: `W` = `packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop`.

Prerequisites from `bwa-wave-outcome`:
- the node schema requires `amendment_required`;
- the routes in `W/workflow.json` follow D4.

Sequencing contract: a per-node response array is consumed in visit order, and its last entry repeats. See `.agents/skills/riela-package-release/scripts/check-package-compat.ts:241-255`. Example fixture: `packages/codex-deepdesign/workflows/codex-deepdesign/mock-scenario.json:32`.

## Non-goals

- Do not edit `.agents/**`, `expected-routes.json`, root `README.md`, scripts, workflow.json, nodes, prompts or tests.
- Do not change the default `mock-scenario.json` route.
- Do not replace the success scenario with a blocked-terminal scenario or with unit tests.

## File-level changes

1. Existing mocks. In each `implementation-wave-outcome` entry, add `"amendment_required": false` to `when` and to `payload`. Change nothing else.
2. New `W/mock-scenario-blocked-wave-amendment.json`. Copy `W/mock-scenario-local.json`, then change these entries:
   - `implementation-progress-check`: no existing mock defines this entry, so do not add one. Leave it unmocked exactly as in `mock-scenario-local.json`. Fanout branch steps do not appear in the top-level `session.executions` route, so the asserted route is driven only by the `implementation-wave-outcome` and `plan-git-commit` arrays. A missing progress-check entry is not a capability gap.
   - `implementation-wave-outcome`: a 2-element array.
     - [0] `when {implementation_blocked:true, partial_success:false, amendment_required:true}`. The payload holds the six fields plus `amendment_required:true` and a D3-shaped `checkpointAmendment` with reason `blocked-wave-scope-or-contract`, `amendmentRound:0` and `maxAmendmentRounds:2`.
     - [1] is the existing success response plus `amendment_required:false`.
   - `plan-git-commit`: a 2-element array with two distinct 40-hex `commitHash` values. Otherwise each element is identical to the existing entry.
   - Keep the `model` field values in the same style as the existing entries.
   - Leave `step4-impl-plan-create` and `step5-impl-plan-review` as they are in `mock-scenario-local.json`. They are already 2-element arrays; for example, step5 is `[needs_revision:true, accepted]`. The amendment visit is their 3rd visit, so it reuses the last (accepting) entry under last-repeat semantics. Do not append entries.
3. EXPECTED_RESULTS.md. Add a `mock-scenario-blocked-wave-amendment.json` bullet with:
   - the exact command;
   - status completed, exitCode 0, and the observed execution count;
   - the ordered key steps;
   - a note that implementation-blocked-output never runs.

   Update the dispatch-amendment sentence so it says the two-round bound is shared with blocked-wave amendments. Add a sentence that a fully blocked wave with only scope/contract blockers amends within that budget, while other blocked-only waves still terminate.
4. README.md, around lines 39-40. Describe the blocked-wave amendment route, the eligibility summary (implementation-dependency scope/contract gaps only; environment/runtime, external-service, review-rejection and test-integrity blockers, other gate types and budget exhaustion all still end blocked), and the shared bound of 2.

## Pitfalls

- Mock payloads must satisfy the closed node schemas. `checkpointAmendment` is allowed only on wave-outcome. Do not add unknown keys to other nodes.
- The `when` object must include `amendment_required` explicitly. Do not rely on a missing key evaluating to false.
- Keep the single implementation item from `mock-scenario-local.json`. Do not add fanout items.
- If riela rejects array entries, or the route differs from the expected sequence, do not substitute anything. Stop, record a blocker naming the capability gap together with the complete log path and exit status, and request an acceptance amendment (design D7 escalation rule).
- If `riela workflow run` fails, keep each run's complete JSON log. Never report a partial log as passing.

## Test cases

- Blocked-wave scenario run → exit 0, completed, the ordered steps listed above, and no implementation-blocked-output.
- Local and fanout scenario runs → exit 0, completed. The local run keeps the same execution count as before (24, per EXPECTED_RESULTS).
- `mise run workflow:check-scenarios` → exit 0.

## Done criteria

All verification commands exit 0, with `exit=0` echoed and the jq status `completed`. Add a dated `## Progress` section to this file that records the log paths and exit statuses.

## Progress 2026-11-03

- Added `amendment_required: false` to both outputs in the three existing fixtures and a blocked-wave amendment/redispatch fixture. Updated README and EXPECTED_RESULTS for eligibility, the shared budget, route and observed count.
- Workflow validation exited 0 (`tmp/blocked-wave-amendment/bwa-scenario-docs/attempt-1/validate.log`). The new, local, fanout and default scenarios exited 0 and completed with 33, 25, 28 and 28 executions respectively; complete JSON is under `tmp/scenario-{bwa,local,fanout,default}/run.json`. Fixture and route assertions exited 0 (`tmp/blocked-wave-amendment/bwa-scenario-docs/attempt-1/assertions.log`).
- `mise run workflow:check-scenarios` exited 1 before running scenarios because its default evidence parent `tmp/registry-contract-migration/verification/compat-verification` does not exist (`tmp/blocked-wave-amendment/bwa-scenario-docs/attempt-1/check-scenarios.log`). The task writes outside the authorized plan evidence root; a checkpoint amendment or authorized lifecycle for that output is required before retrying the exact gate.
- Formal review, downstream release metadata and final integration remain pending.

## Progress 2026-11-03 (retry)

- The previously missing compatibility evidence directory is available. `mise run workflow:check-scenarios` exited 0 with 60 workflows and zero failures (`tmp/blocked-wave-amendment/bwa-scenario-docs/attempt-2/check-scenarios-final.log`).
- Workflow validation and the blocked-wave, local, fanout and default mock runs exited 0. Complete scenario outputs are `tmp/scenario-{bwa,local,fanout,default}/run.json`; the blocked-wave route is recorded in `tmp/blocked-wave-amendment/bwa-scenario-docs/attempt-2/route.log`.
- Formal reviews, release metadata, final integration and Git finalization remain downstream.
