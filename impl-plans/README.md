# Implementation plans

## Active

Riela 0.2.1 compatibility migration for [issue #14](https://github.com/tacogips/riela-packages/issues/14); design accepted, plans pending Step 5 review:

- [compat-verification](active/compat-verification.md): baseline and isolated installed-CLI checks.
- [compat-agent-contracts](active/compat-agent-contracts.md): concrete workflow authority and payload contracts.
- [compat-assets](active/compat-assets.md): add-ons, packaged skills and examples.
- [compat-inheritance](active/compat-inheritance.md): effective Claude/Cursor wrappers after base migration.
- [compat-reconcile](active/compat-reconcile.md): serial repair, metadata and combined verification.

Dispatch: [riela-021-dispatch.json](active/riela-021-dispatch.json). Static source inventory: [riela-021-inventory.json](active/riela-021-inventory.json). Checkpoint the accepted design, all five plans, both JSON files and this index together after plan acceptance and before native fanout. Workers do not mutate Git or archive plans.

The two D4 dispatch JSON files in `active/` are retained as historical checkpoint records; they are not current implementation plans.

## Completed

- [d4-opus-contracts](completed/d4-opus-contracts.md) — Opus bundle output contracts; implementation and review accepted.
- [d4-codex-contracts](completed/d4-codex-contracts.md) — Codex bundle output contracts; implementation and review accepted.
- [d4-reconcile-verify](completed/d4-reconcile-verify.md) — combined validation and package metadata; implementation and review accepted.

The D4 exact-file commit, non-force push and PR handoff are subsequent workflow publication steps. Historical active paths in dispatch records and progress logs identify the paths used during implementation.
