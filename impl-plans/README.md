# Implementation plans

## Issue #14 compatibility migration

The implementation for [issue #14](https://github.com/tacogips/riela-packages/issues/14) is verified on `fix/registry-contract-migration` and awaits review/merge of [Draft PR #15](https://github.com/tacogips/riela-packages/pull/15). The accepted plan files remain at their original `active/` paths so the committed dispatch and runtime evidence retain valid references; they are not outstanding implementation tasks:

- [compat-agent-contracts](active/compat-agent-contracts.md): Codex workflow authority and payload contracts.
- [compat-agent-contracts-supporting](active/compat-agent-contracts-supporting.md): supporting workflow contracts.
- [compat-assets](active/compat-assets.md): add-ons, packaged skills and examples.
- [compat-inheritance](active/compat-inheritance.md): Claude/Cursor effective wrappers.
- [compat-reconcile](active/compat-reconcile.md): combined verification and metadata refresh.

The completed prerequisite [compat-verification](active/compat-verification.md) and [dispatch](active/riela-021-dispatch.json) are retained for provenance. The [inventory](active/riela-021-inventory.json) covers 65 packages and 59 workflows. On 2026-09-27, the corrected source Riela CLI from [core PR #119](https://github.com/tacogips/riela/pull/119) passed `mise run check`: 65 package manifests, 59 workflow validate/inspect pairs, 47 direct/inherited mock scenarios, asset checks, 18 package-local contract scripts, 23 compatibility-harness tests, 25 compact regressions, and 42 dispatch tests. Separate evidence under ignored `tmp/registry-contract-migration/` records 75/75 core example validations. The no-merge handoff and structured recovery changes from [package PR #18](https://github.com/tacogips/riela-packages/pull/18) and [package PR #20](https://github.com/tacogips/riela-packages/pull/20) are incorporated here. No live model/provider execution or release was performed; the Riela workflow was stopped at the user's request and remaining verification was manual.

The two D4 dispatch JSON files in `active/` are retained as historical checkpoint records; they are not current implementation plans.

## Completed

- [d4-opus-contracts](completed/d4-opus-contracts.md) — Opus bundle output contracts; implementation and review accepted.
- [d4-codex-contracts](completed/d4-codex-contracts.md) — Codex bundle output contracts; implementation and review accepted.
- [d4-reconcile-verify](completed/d4-reconcile-verify.md) — combined validation and package metadata; implementation and review accepted.

The D4 exact-file commit, non-force push and PR handoff are subsequent workflow publication steps. Historical active paths in dispatch records and progress logs identify the paths used during implementation.

### Opus-luna wave input compaction (package 0.1.9)

[Design](../design-docs/specs/design-opus-luna-wave-input-compaction.md) · [Q1 decision](../design-docs/user-qa/opus-luna-wave-input-compaction.md). Accepted by integration review in session-480:

- [wave-outcome-script](completed/wave-outcome-script.md) — deterministic `implementation-wave-outcome` command; stores `fanout-join.json` and a bounded `wave-summary.json` under `tmp/opus-luna-waves/<workflowExecutionId>/wave-NNN/`.
- [wave-summary-prompts](completed/wave-summary-prompts.md) — reconciliation and integration-review prompts read the wave summary instead of the raw join.
- [wave-fixtures-docs](completed/wave-fixtures-docs.md) — mock scenarios, EXPECTED_RESULTS.md, package README and SKILL.md.
- [wave-release](completed/wave-release.md) — version 0.1.9, refreshed digests and registry index.

The prompt-level bound and "run proceeds to reconciliation/integration" remain BLOCKED pending the upstream riela change (Q1 Option A); riela 0.2.34 still renders the persistent `fanoutJoin` request variable into later agent prompts. The [dispatch record](active/wave-compaction-dispatch.json) stays in `active/` as a historical checkpoint and keeps the original `active/` plan paths.
