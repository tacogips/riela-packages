# Riela 0.2.1 package compatibility

Status: previously accepted design (Step 3 comm-000004, as recorded in the existing plans); checkpoint b212240 continuation updated for Step 3 review; independent approval pending. Workflow mode: `issue-resolution`.
Issue: https://github.com/tacogips/riela-packages/issues/14.

## Scope and evidence

Step 1 intake and effective workflowInput authorize continuation across all 65 packages, 59 packaged workflows and all examples for issue #14 and Draft PR #15 (https://github.com/tacogips/riela-packages/pull/15). Preserve accepted work and all five active plans. The current checkpoint is `b212240228ca02d9532d442bcf454b320e4affe3` on `fix/registry-contract-migration`; local author inspection confirms that HEAD and a clean tree before this edit. Older checkpoint and acceptance receipts remain historical evidence, not current validation results.

The intake reports passing source-CLI checks for 14 Codex mock workflows, four supporting mock workflows, two new fixtures and the asset audit. Recheck this first wave against final inputs. The other 12 supporting workflows have no fixtures: require validation and inspection of their effective graphs, never missing-scenario execution. The 50 reported workflow-validation command failures are actual failures, mainly involving 24 Claude/Cursor inherited wrappers and YouTube. They are command counts, not 50 distinct workflows; retain each failing command and assign its repair to an owner. Do not downgrade these accepted-scope failures to passing baseline diagnostics.

Package verification uses the source Riela #117 executable `/Users/taco/gits/tacogips/riela-worktrees/remaining-impl-plans/.build/debug/riela`. The runner separately uses `/Users/taco/gits/tacogips/riela-worktrees/fanout-directory-change-tracking/.build/debug/riela` for #118 directory tracking. Record actual executable identity for checks; never substitute the runner binary for package verification. Core https://github.com/tacogips/riela/issues/117 is the related fix reference, not an automatically outstanding blocker or waiver. Verify the supplied fixed executable against the installed YouTube dependency closure.

Runtime-resolved provenance and effective input are authoritative; no supplied contradiction exists. Do not rediscover the running workflow through registries. Preserve sibling repositories and prior work. All scratch stays under repository `tmp/registry-contract-migration/`; no live providers, release or merge to main. Later workflow gates commit and non-force push only `origin fix/registry-contract-migration` for Draft PR #15. Scratch labels do not change issue #14 to #114.

There is no supplied codex-agent reference repository mapping (`codexAgentReferences: []`); no reference checkout or adapter implementation is needed. Existing `design-docs/specs/design-fable-output-contract-d4.md` concerns a separate migration and is not amended or treated as current acceptance evidence.

## Contract and authority boundaries

Inventory manifests, concrete workflows, inherited wrappers, add-on descriptors, skills and examples from tracked repository payloads. Record each package's disposition: compatible unchanged, changed and verified, or failing with exact evidence. Resolve shared bases before wrappers and cross-workflow callees before callers. Do not flatten inheritance or duplicate migrated base nodes into wrappers.

For every agent requiring a sandbox declaration, select authority from the prompt's actual operations. Review-only and reporting agents that emit JSON use `read-only`; agents writing design, plans, code or evidence use `workspace-write`. If a role requires broader authority, justify that individual declaration against its existing operations and verify the installed backend accepts the value; do not grant blanket `danger-full-access`. Preserve valid existing authority unless it conflicts with actual role requirements. A reviewer that currently writes files must either retain an accurately classified writer role or have that persistence assigned to its existing writer consumer; do not silently forbid required behavior. Add-on/command permissions remain their own contracts, not agent permissions. Preserve models, backend selection, routing, session reuse and prompts except for compatibility corrections required by these contracts.

Derive each required `output.jsonSchema` from its prompt, existing mock output, conditional transitions and downstream template/add-on inputs. Validate the business payload, preserving the adapter envelope's `when` routing flags. Follow forwarding add-ons and cross-workflow handoffs to the original producer; distinguish fields produced by the agent from fields appended later by add-ons. Declare relay-visible fields when needed without requiring agents to invent later Git results. Require concrete field types, meaningful required fields, nested consumed shapes and existing decision values. Preserve valid revision, failure, skip and planning-only outputs through branch-aware schemas; commit fields are required only on paths that actually commit. Do not impose closed additional-property rules unless already required by the contract. Retain existing validation budgets; add an explicit supported retry budget where the installed contract requires one. No vacuous object schemas or blanket schemas for unconditional terminal agents.

For example, `packages/codex-simple-work-package/workflows/codex-simple-work-package/prompts/review.md` defines `payload.needs_revision` (boolean), `findings` (objects containing severity/file/line/message), `feedback` (strings), and `accepted` (boolean). Its schema must describe those fields, accept the prompt's `high`, `middle`, `low` severities, and preserve `when.needs_revision` outside the payload schema. Behavioral checks verify revision for high/middle findings and acceptance otherwise; schema presence alone is insufficient.

Cursor and Claude differences stay in existing `extends` patches and replacement maps. For example, `packages/cursor-cli-design-and-implement-review-loop/workflows/cursor-cli-design-and-implement-review-loop/workflow.json` maps `codex-agent` to `cursor-cli-agent`, reference field names to Cursor equivalents, and the implementation model to `composer-2.5`. Preserve those mappings; verify effective inherited schemas, sandbox declarations, replaced property names and backend-specific overrides after base migration. These package wrappers are the existing adaptation boundary; no new adapter modules are justified without reference input or runtime code changes.

## Dependencies and package coverage

The YouTube workflow manifest declares three external add-on dependencies and content locks: download, audio extraction and transcription. Verify it through an isolated installation of repository payloads with those dependencies resolved. Keep its capability grants, executable resolution and input/output flow intact. A raw workflow-only catalog cannot prove installed-package failure. The historical installed host-resolution defect is tracked as core #117; rerun with the supplied #117 executable to establish current behavior. Preserve its failing exit and complete log; do not suppress the failure, weaken validation, or repair core in this repository. Other failures require their own diagnosis and must not be attributed to #117 merely because they involve YouTube. Deterministic scenarios should exercise the data handoffs without requiring live YouTube/GCP credentials or paid calls.

Old YouTube local-command dependency locks are repository package data to migrate, not a reason to change core or discard installed validation. The asset author identifies exact obsolete fields and source-backed replacement values in `packages/youtube-mp4-to-text-workflow/riela-package.json` and its three add-on manifests; serial reconciliation owns manifest/lock writes using the supplied #117 executable. Match supported local-command metadata to each actual add-on descriptor, preserving canonical dependency identities, capabilities and content digests. Do not invent replacement fields before confirming the fixed CLI contract. If a fresh check fails, retain its exact command, final exit and complete log and repair the concrete package failure; a demonstrated tool defect remains a blocked check, never a presumed historical exception. Refresh dependent locks before package digests and index, and validate the installed dependency closure after the migration.

Include add-on source/descriptor compatibility, capability and environment mappings, manifest dependency locks, skill frontmatter and referenced files, and examples' documented invocations in the inventory. Edit only concrete incompatibilities. Reuse existing package tests and deterministic fixtures; do not rewrite working add-ons, skills or examples solely to make every package change. Update relevant `EXPECTED_RESULTS.md` and documentation when corrected contracts change their expected evidence.

## Verification design

The implementation plan must identify exact changed producers, their consumers, authority rationale and affected fixtures per base family. Record installed CLI version, source identity, expanded command, final exit code, complete log path and case/assertion counts under repository-root `tmp/registry-contract-migration/verification/`. Keep sessions, artifacts, isolated install roots, catalog copies and build scratch beneath `tmp/`. Run in the foreground and poll any yielded session through exit. An incomplete log, zero tests or a mock process exit without asserted session outcomes is not a pass.

The checkpoint already contains `.agents/skills/riela-package-release/scripts/check-package-compat.ts`, its Bun tests, and `mise.toml` validation entry points. Reuse this harness and repair only concrete gaps; do not rebuild it or introduce another framework. Preserve complete manifest coverage, catalog collision detection, cross-workflow callees and effective inherited wrapper checks. Target-package installation and validation use isolated repository-local test roots; they do not establish readiness of the running orchestration workflow. Do not modify installed user-scope packages. Keep every raw command failure visible until repaired and reverified.

Step 6 `verification` records current acceptance checks with exact outcomes, including failures; `baselineDiagnostics` preserves historical comparisons without granting exemptions; `externalBlockers` is reserved for newly demonstrated external failures with command, issue, exit and complete log evidence. All 50 reported command failures must be accounted for and corrected or explicitly left unresolved, which blocks compatibility completion. Never remove inventory entries or conceal aggregate nonzero outcomes. Preserve the accepted 17 harness regressions; rerun for final integration or affected inputs without reopening `compat-verification` implementation. Run the existing helper in manifests, workflows, scenarios and assets modes, digest/index checks, then `mise run check` on final source.

Every workflow needs validation and inspection; deterministic execution applies to workflows/examples with actual fixtures. The 12 supporting workflows without fixtures receive explicit `scenario: not-applicable` coverage with their validation/inspection receipts, not a failed or fabricated mock result. Step 4 identifies their exact IDs and payload paths from the existing supporting selection/inventory. Existing fixture-bearing cases retain route and payload assertions. Account for every example with an existing deterministic check or static command/asset verification when live providers would otherwise be required; state that coverage limit.

### Expected routes for every selected scenario

The route-oracle work is complete per intake. Preserve `.agents/skills/riela-package-release/fixtures/expected-routes.json`, `.agents/skills/riela-package-release/scripts/check-package-compat.ts` and its adjacent test file. The following rules describe retained behavior, not a new implementation wave. Serial reconciliation may correct a route entry only when changed package source demonstrates the need; do not derive routes from observed runs or restart `impl-plans/active/compat-verification.md`.

Identify a map entry by effective workflow ID and the selected fixture's repository-relative path, so wrappers and distinct scenarios cannot accidentally share an oracle. Each entry records a nonempty ordered array of step IDs and repository paths to the graph, fixture and available `EXPECTED_RESULTS.md` evidence used to derive it. Derive branches, bypasses and repeated steps from those sources before comparing any observed run; observed traces alone must never define the expected route. Missing expected-results documentation is not permission to guess: the graph and fixture must establish the route or the case fails with a concrete diagnostic.

Resolve the fixture (including its base inheritance) and expected route before asserting a selected case. Preserve existing explicit selection and fixture route support, with precedence selection route, fixture route, then map entry for the effective workflow/fixture pair. A supplied malformed route must fail rather than fall through. A route must be nonempty and contain only nonempty step IDs valid for the effective graph. With `--workflow-list` omitted, every default-selected case uses the same mandatory route resolution and comparison. Missing metadata fails closed with workflow/fixture identity; it never makes route checking optional.

For inherited fixtures, validate route meaning against the resolved wrapper graph and its patches/replacements. A base fixture's route may be reused only when its step sequence and branch meaning remain valid for that effective graph; otherwise require an explicit effective-workflow route. The map may record a wrapper-specific entry without copying base nodes or changing inheritance. Record route origin and expected versus observed ordered sequences in the scenario evidence. Require exact sequence equality, including repeated steps, along with completed terminal state and the existing fixture-backed payload assertions; CLI success or payload agreement alone is insufficient.

Keep all 17 accepted regressions intact, including default-selection cases proving that a wrong route fails despite completed status and matching payloads, that the matching route passes, and that absent or malformed metadata fails closed. Retain coverage of inherited fixture resolution with an effective-wrapper route and reject an incompatible base route. Evidence classification remains unchanged: these changed-harness checks belong in `verification`; historical package failures belong in `baselineDiagnostics`; a newly demonstrated external defect requires fresh evidence in `externalBlockers`; historical #117 attribution alone is insufficient.

Required command families (record concrete workflow names and paths when executed):

```sh
export RIELA_COMPAT_CLI=/Users/taco/gits/tacogips/riela-worktrees/remaining-impl-plans/.build/debug/riela
export RIELA_BIN="$RIELA_COMPAT_CLI"
"$RIELA_COMPAT_CLI" --version
shasum -a 256 "$RIELA_COMPAT_CLI"
bun test ./.agents/skills/riela-package-release/scripts/check-package-compat.test.ts
mise run package:validate
mise run workflow:validate
"$RIELA_COMPAT_CLI" workflow validate <target-workflow> --workflow-definition-dir <isolated-target-root> --output json
"$RIELA_COMPAT_CLI" workflow inspect <target-workflow> --workflow-definition-dir <isolated-target-root> --output json
"$RIELA_COMPAT_CLI" workflow run <target-workflow> --workflow-definition-dir <isolated-target-root> --mock-scenario <fixture> --session-store <tmp-session-root> --artifact-root <tmp-artifact-root> --output json
mise run workflow:check-compact
mise run workflow:check-codex-dispatch
bun packages/fable-and-improve-opus/tests/check-output-contract.ts --evidence-root <tmp-opus-evidence>
bun packages/fable-and-improve-codex/tests/check-output-contract.ts --evidence-root <tmp-codex-evidence>
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode manifests --evidence-root <fresh-attempt>/manifests
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode workflows --evidence-root <fresh-attempt>/workflows
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode scenarios --evidence-root <fresh-attempt>/scenarios
bun .agents/skills/riela-package-release/scripts/check-package-compat.ts --mode assets --evidence-root <fresh-attempt>/assets
mise run check
git diff --check
```

Run existing relevant scenarios for every changed base and effective wrapper. Focus regression additions on accept/revise routing, malformed/missing consumed fields, conditional commit fields, cross-workflow handoffs, inheritance preservation and external add-on resolution. Assert observed payloads, selected and bypassed steps, terminal status and no unintended side effects. Mocks do not prove real backend sandbox enforcement; static authority checks plus installed contract validation cover declarations. If mocks bypass output validation, demonstrate negative schema rejection through the installed validator's supported entry point and state the remaining coverage limit rather than claiming runtime rejection.

Bind literal `riela` subprocesses to the same #117 executable through a symlink directory beneath the fresh evidence attempt and prepend it to PATH; record `command -v riela`. The runner executable remains separate. Expand all placeholder workflow/fixture/root arguments into exact commands in receipts. The validate/inspect/run commands above target repository payload test catalogs only, never the current runner's scoped provenance. Execute all checks in the foreground and retain handles through terminal exit.

Reuse preserved receipts only after matching audited source, CLI hash/version, dependency inputs, effective arguments, final exit and complete logs; otherwise rerun the affected checks. Baseline reproduction, if needed, uses a disposable copy of `b212240228ca02d9532d442bcf454b320e4affe3` under `tmp/`. A historical failure does not waive an in-scope repair. Missing tools or incomplete logs are verification gaps, not passes. Final compatibility acceptance requires the full requested checks to pass; every unresolved failure remains explicit and blocks completion.

## Plan continuation and completion boundaries

This execution assigns all five plans together to one design author. Preserve their paths, IDs, accepted tasks, ownership and prior progress:

- `impl-plans/active/compat-agent-contracts.md`
- `impl-plans/active/compat-agent-contracts-supporting.md`
- `impl-plans/active/compat-assets.md`
- `impl-plans/active/compat-inheritance.md`
- `impl-plans/active/compat-reconcile.md`

Step 4 uses one plan author to update stale checkpoint/binary/#117-exception text to this continuation, retaining completed evidence and task IDs. The contract split already exists; do not recreate it. `impl-plans/active/compat-verification.md` remains completed prerequisite evidence, not a sixth dispatch. Preserve existing ownership/sizing receipts and refresh affected counts against current paths before dispatch: disjoint concurrent write roots, no lost ownership, each contract plan within its existing 400-entry planning bound and 512-entry runtime ceiling. Do not change the runner or limits.

Use dependency-ready native Riela waves on the current branch:

1. Recheck `compat-agent-contracts`, `compat-agent-contracts-supporting` and `compat-assets` within their existing disjoint roots. Preserve first-wave edits and fix only demonstrated defects. Review 14 Codex/four supporting mock workflows and two new fixtures; validate/inspect the 12 fixtureless supporting workflows and recheck the asset audit. Supporting source ownership includes YouTube workflow contracts; assets supplies descriptor/lock correction intent without writing reconciliation-owned manifests.
2. `compat-inheritance` waits for accepted outputs from both contract plans and assets. Fix and verify effective Claude/Cursor wrappers, including the reported 24-wrapper failure cohort, without copying base nodes. Cover the full wrapper inventory, not only that reported cohort.
3. `compat-reconcile` waits for all four other plans. Join evidence, repair shared contracts serially, migrate YouTube dependency locks, validate installed dependencies, refresh digests/index and run final whole-catalog and deterministic-example checks.

Preserve per-plan intent, hashes, progress and complete logs under separate fresh attempt directories. No concurrent writer may touch another plan's files; reconciliation's overlapping repair authority starts only after join. The dispatch manifest resolves every dependency and lists each plan exactly once. Riela checkpoint/publication gates commit and non-force push accepted design/plans before native fanout; a failed push stops dispatch. Workers do not perform Git mutations.

Passing package checks, deterministic assertions, metadata consistency and no unresolved high/mid findings are required before final delivery. Independent adversarial review and combined-tree review occur after implementation; formal downstream review is not a missing Step 6 implementation task. Review-changing edits invalidate affected receipts. Final commit/non-force push targets Draft PR #15 on the existing branch only. Historical #117 failures grant no exception to the current requested final verification. Do not describe compatibility migration as complete while any required check is failing or blocked.

## Metadata and rollout

After final payload changes, increment changed package versions consistently with existing package versioning. Include wrappers whose effective inherited behavior changes in release impact review; update their metadata/dependency pins where needed even when base migration avoids wrapper source duplication. If add-on sources change, refresh add-on content digests and every dependent lock first. Then refresh package checksum/integrity and regenerate `registry-index.json` serially. Index/digest checks must cover unchanged packages as well to detect accidental drift.

```sh
bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts <changed-addon-package>
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts <changed-package-ids>
mise run package:generate-index
mise run package:check-digests
mise run package:check-addon-digests
mise run package:check-index
```

The add-on update command is conditional on source changes. Update README listings only if inventory or displayed metadata changes. Do not publish images, archives, releases or merge branches for this migration. Independent design/plan and implementation adversarial review must explicitly accept the applicable source; resolve every high/mid finding before delivery. Verify after final metadata updates, review the exact intended diff for accidental private data/local paths, commit reviewed files, and push non-force to `origin fix/registry-contract-migration`. Record commit hash, push outcome, review decisions and residual failures. Material changes invalidate affected checks/reviews. Rollback is a normal reviewed revert of the migration commit(s); no consumer registry surgery is part of this design.

## Open questions and author self-check

No unresolved user decision or supplied provenance/input contradiction exists. Issue #14 title/body could not be fetched during intake; the supplied brief defines scope. No codex-agent reference mapping is supplied, so existing Cursor wrappers remain the adaptation boundary. The #117 executable's final-source results are an implementation verification obligation, not an unresolved design choice. Record concrete new failures if encountered.

The author self-check corrected three material stale design instructions before return: the old checkpoint, conflated #117/#118 binaries, and the historical #117 delivery waiver. It also clarified fixtureless supporting-workflow coverage and continuation of the existing five-plan split. No new Step 3/Step 5 feedback was supplied. Historical acceptance does not imply current independent approval.

This documentation-only step preserves every plan and package file. Author checks verify issue/intake mapping, all five plan paths/dependencies, contract/authority boundaries, existing Cursor adaptation, fixture coverage, verification commands, metadata ordering and publication constraints. Evidence is recorded in `tmp/registry-contract-migration/verification/step2-design-b212240/commands.json` with individual complete logs and final exits. No unresolved high/mid design finding remains. Package/scenario checks, plan updates, adversarial review and publication remain explicit downstream obligations; this author check does not claim those have passed.
