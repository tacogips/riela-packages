# D4: Fable workflow agent output contracts

Status: proposed for independent adversarial design review. Workflow mode: `issue-resolution`.
Issue: `tacogips/riela-packages`, “Migrate fable-and-improve bundles to the agent-node output contract”; supplied title/body, no issue number or URL. No codex-agent reference repository or Cursor CLI behavior mapping is applicable.

## Scope and evidence

The accepted Step 1 intake and effective workflowInput govern this migration. The runner-resolved workflow provenance is authoritative. This work changes package declarations, not Riela runtime behavior.

Source roots present at intake HEAD `36ddde7880f1e6bcbd9667ec802f4f4920e8b450`:

- `packages/fable-and-improve-opus/workflows/fable-and-improve-opus`
- `packages/fable-and-improve-codex/workflows/fable-and-improve-codex`

Each has 16 agent nodes. Opus has 5 explicit sandbox declarations and Codex has 3; the missing counts are 11 and 13. Both already have 8 schemas, including implementation review, dispatch and integration review. Historical upstream counts must not replace these current observations.

The requested `packages/fable-and-improve/workflows/fable-and-improve` source is absent, including from `git ls-tree -d HEAD packages/fable-and-improve`. Do not create a substitute or modify another package. Track the third-package acceptance gap in `design-docs/user-qa/fable-output-contract-d4.md`; implementation of the two present bundles can proceed, but claiming all three migrated requires resolution.

Read-only upstream references: `../../riela/design-docs/specs/design-agent-node-output-contract.md` §2/§6 and `../../riela/impl-plans/active/agent-node-output-contract.md`, “Excluded (riela-packages — separate follow-up work package, D4)”. The requested completed-plan path was not found locally; the available active document records the D4 exclusion. Its historical runtime implementation status does not override the supplied statement that core is already implemented. No Riela source changes are authorized.

## Sandbox behavior

Every sandbox-consuming agent must explicitly declare a supported sandbox value. Preserve existing declarations. For missing declarations use `workspace-write` for design/checkpoint, implementation, reconciliation, completion cleanup, branch evidence and integration nodes that write artifacts; use `read-only` for review, knowledge judgment and final reporting nodes whose prompts forbid or do not require writes. `kb-self-review`, `kb-merge-judge` and `kb-archive-brief` emit payloads; their add-ons own knowledge persistence. `dispatch-plans` reads the committed manifest and emits fanout payloads; declare `read-only` for its missing sandbox. No blanket full-access grant and no changes to models, backend, session reuse, graph, fanout, Git add-ons or routing labels.

## Required producer contracts

Schemas validate the business payload, not the adapter envelope. Keep `when` routing in its existing envelope location; do not require invented payload copies of routing flags. Preserve all existing payload fields and permissive additional-property behavior where prompts return rich evidence.

Determine required producers from conditional transitions and add-on config/input payload references, including bare fields and `inbox.latest.output.payload.*`. Follow incoming edges through forwarding add-ons to the agent producer, with a visited set for loops. Context-only references do not justify schemas. Prompt prose references alone do not justify blanket additions. Existing dispatch and reconciliation schemas remain intact; fanout item shapes must remain compatible.

| Producer | Contract boundary |
| --- | --- |
| `fable-analysis` | Existing schema requires `knowledgeQuery` used by `kb-recall-prior`. |
| `kb-self-review` | Preserve actual `knowledgeQuery`, `candidateContent`, `candidateTags` consumed by `kb-recall-related`; use existing payload types. |
| `kb-merge-judge` | Existing create/merge/skip decision and routing; require merge fields on merge only, leaving skip/create valid. Respect actual add-on inputs as well as config. |
| `kb-archive-brief` | Existing `archive_note`; require archive note ID/body only when archive is selected. |
| `opus-review` / `codex-review` | Existing review payload schema; label `needs_revision` remains in `when` as prompted. Add explicit validation-attempt budget. |
| `fable-goal-review` | Add an object schema for each bundle's actual completion evidence fields; Opus and Codex prompts differ. `needs_replan` / `needs_todo` remain in `when`, mutually exclusive by existing prompt. Do not invent common payload field names. |
| `integration-review` | Preserve existing schema and label fields; add explicit validation-attempt budget. |
| `plan-checkpoint` | Require `commitMessage` string with `minLength: 1`, `committedFiles` array of path strings, `manifestPath` and `evidenceRoot` strings, matching current prompt. |
| `step9-commit-message` | Branch-aware completion and commit schema as below; keep `git` relay field visible to downstream template validation. |

Use explicit `output.maxValidationAttempts: 2` on every required producer (one retry). Retain compatible existing schemas and budgets. No schema is required merely because an agent exists. In particular, leave contract-less unconditional terminal/reporting nodes alone unless the actual consumer walk establishes a dependency.

Step 9 publishes `needs_revision` in the payload and matching `when.needs_revision`. Declare shared completion fields from its prompt, with `decision` and boolean `needs_revision`. Use supported `anyOf`/`oneOf` plus `const` to distinguish revision from acceptance. Revision accepts `decision: needs-revision`, `needs_revision: true` without commit fields. Acceptance requires `decision: accepted`, `needs_revision: false`, `accepted: true`, `findings: []`, nonempty `commitMessage` and a `committedFiles` array of repository-relative strings. Planning-only remains valid and skips archiving. Never require commit fields on revision or make them optional on acceptance.

The git-push template consumes `git.commitHash` after git-commit. The backward walk can therefore require a top-level `git` property in Step 9's schema. Declare its compatible object shape if required by validation, but do not require the agent to manufacture a commit hash: the git-commit add-on supplies it after publication. Preserve this distinction between declared relay-visible shape and fields required at producer publication.

## Verification and delivery

Implementation must save complete command output, final exit, scenario name, assertion/test counts and session outcomes under worktree `tmp/output-contract-d4/`. Commands run in the foreground and are polled to exit. A mock CLI exit alone is insufficient: assert completed status, intended branch traces and payloads. Mock verification exercises contracts and routing, not real model sandbox enforcement or real Git/knowledge side effects.

For each present changed package `P`, from `packages/P/workflows/P`, using absolute worktree-local evidence paths:

```sh
riela workflow validate P --workflow-definition-dir .. --output json
riela workflow run P --workflow-definition-dir .. --mock-scenario ./mock-scenario.json --session-store "$EVIDENCE/sessions" --artifact-root "$EVIDENCE/artifacts" --output json
```

Replace P and EVIDENCE explicitly in recorded commands. Validation here concerns target bundles, never rediscovery of the running orchestration workflow. Use installed Riela. Isolate scenario stores and artifacts. Preserve happy-path fixtures, then cover Step 9 revision without commit fields, acceptance with a valid message, rejected missing/empty commit messages, and knowledge create/merge/archive/skip paths touched by schema changes. Verify unchanged transitions, models and fanout definitions against the baseline. Do not assert mock retry coverage unless the installed mock mechanism actually passes the malformed output through validation.

Refresh only changed manifests:

```sh
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve-opus fable-and-improve-codex
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts fable-and-improve-opus fable-and-improve-codex --dry-run
mise run check
git diff --check
```

The repository uses `mise.toml`, not Taskfile. `mise run check` includes Swift source-based checks; it complements, never replaces, installed-Riela target validation. Keep its scratch/build evidence under this worktree's tmp, using supported overrides or equivalent explicitly recorded commands if needed to respect the no-other-worktree-write constraint. Report unrelated baseline failures without expanding scope. Check generated registry-index consistency; change derived metadata only if required by changed manifests. No release archives, App Store, Homebrew or x64 release is requested.

Update prompts and EXPECTED_RESULTS only where necessary to state these existing payload contracts and reproducible verification accurately. Refresh digests after final payload edits. Independent adversarial review must have no unresolved material findings; commit only reviewed paths and push non-force to `feat/output-contract-d4`, then prepare a PR. Do not touch the dirty main checkout, other worktrees or unrelated packages.

## Author self-check

The design maps the sandbox requirement, producer selection, D4 checkpoint/commit contract, deterministic verification, digest checks and reviewed delivery directly to intake. It introduces no runtime layer or adapter. Branch-specific schemas preserve legitimate revision outputs. Current source discrepancies are explicit in user-QA, not treated as orchestration provenance defects. Independent review and implementation verification remain later gates; this document does not claim they passed.
