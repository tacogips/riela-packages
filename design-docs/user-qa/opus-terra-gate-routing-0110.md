# Opus Luna 0.1.10 gate/routing fixes: route fixture outside targetScope

Status: **open**. Default if no answer: do not edit the fixture, and report the
stale assertion as an out-of-scope dependency blocker.
Design: `design-docs/specs/design-opus-terra-gate-routing-0110.md` (D4, D6, D7).

## Question

D4 inserts `plan-contract-validate` between `plan-checkpoint` and
`plan-git-commit`. D6 inserts `plan-archive` between `step8-docs-refresh` and
`step9-commit-message`. Both are on the main route of
`mock-scenario.json`. The route assertion for this workflow lives in
`.agents/skills/riela-package-release/fixtures/expected-routes.json`
(entry `opus-terra-design-and-implement-review-loop`, around lines 347-383). That
file is outside the accepted targetScope, which is
`packages/opus-terra-design-and-implement-review-loop/**` and
`registry-index.json` only. Once the package changes, `mise run workflow:check-scenarios`
(part of `mise run check`) reports a route mismatch for this workflow until the
fixture is updated.

None of the accepted acceptance signals requires `workflow:check-scenarios`.
The mock scenarios themselves still run and pass.

## Options

| Option | Effect |
| --- | --- |
| A. Keep scope (default) | Do not edit the fixture. The implementation reports a blocker `{dependency: ".agents/skills/riela-package-release/fixtures/expected-routes.json", reason: "route gains plan-contract-validate and plan-archive", owner: "operator"}`. A follow-up edit inserts `plan-contract-validate` after `plan-checkpoint` and `plan-archive` after `step8-docs-refresh`. |
| B. Widen scope by one entry | Authorize editing only that fixture entry in this run, so `mise run check` stays green. |

## Recommendation

Choose B if `mise run check` must be green before the local commit. Otherwise,
choose A, the default that respects the stated constraint.
