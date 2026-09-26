# Riela 0.2.1 package compatibility

Status: proposed for Step 3 adversarial review; author self-check complete. Workflow mode: `issue-resolution`.
Issue: https://github.com/tacogips/riela-packages/issues/14.

## Scope and evidence

Step 1 intake and effective workflowInput authorize migration of every `packages/*` package, including workflow bundles, inherited Claude/Cursor wrappers, add-ons, packaged skills and examples. The reported focus is 39 invalid legacy agent workflows. This count describes intake evidence, not a fixed inventory or a fresh validation result. The YouTube direct-catalog unresolved executable is a separate dependency-resolution case, not evidence that its installed package is broken.

Use branch `fix/registry-contract-migration`, initially clean at `b3bbf8c15760a56423b0d58120fc11f72280381a`. Preserve other worktrees; do not modify sibling repositories. Runtime-resolved workflow provenance is authoritative; no contradiction exists in the supplied input. This design changes repository package payloads and their verification, not the running workflow or Riela core. Do not rediscover the running workflow through registries. No release or merge is authorized as part of this handoff; downstream completion commits and pushes the reviewed changes to this branch.

Author inspection confirmed `riela --version` prints `0.2.1`, branch/HEAD match intake, and `git status --short` was empty before this document. Retained `tmp/issue-114-validation/codex-simple-work-package.json` reports missing `agentSandbox` on implementation/review/output agents and missing `output.jsonSchema` on its conditional reviewer. Retained `tmp/issue-114-validation/youtube-mp4-to-text.json` reports `unresolvedAddonExecutable` for `download-video`. These are prior diagnostics, not renewed verification receipts. Their directory label does not change the accepted issue reference to #114.

There is no supplied codex-agent reference repository mapping (`codexAgentReferences: []`); no reference checkout or adapter implementation is needed. Existing `design-docs/specs/design-fable-output-contract-d4.md` concerns a separate migration and is not amended or treated as current acceptance evidence.

## Contract and authority boundaries

Inventory manifests, concrete workflows, inherited wrappers, add-on descriptors, skills and examples from tracked repository payloads. Record each package's disposition: compatible unchanged, changed and verified, or failing with exact evidence. Resolve shared bases before wrappers and cross-workflow callees before callers. Do not flatten inheritance or duplicate migrated base nodes into wrappers.

For every agent requiring a sandbox declaration, select authority from the prompt's actual operations. Review-only and reporting agents that emit JSON use `read-only`; agents writing design, plans, code or evidence use `workspace-write`. If a role requires broader authority, justify that individual declaration against its existing operations and verify the installed backend accepts the value; do not grant blanket `danger-full-access`. Preserve valid existing authority unless it conflicts with actual role requirements. A reviewer that currently writes files must either retain an accurately classified writer role or have that persistence assigned to its existing writer consumer; do not silently forbid required behavior. Add-on/command permissions remain their own contracts, not agent permissions. Preserve models, backend selection, routing, session reuse and prompts except for compatibility corrections required by these contracts.

Derive each required `output.jsonSchema` from its prompt, existing mock output, conditional transitions and downstream template/add-on inputs. Validate the business payload, preserving the adapter envelope's `when` routing flags. Follow forwarding add-ons and cross-workflow handoffs to the original producer; distinguish fields produced by the agent from fields appended later by add-ons. Declare relay-visible fields when needed without requiring agents to invent later Git results. Require concrete field types, meaningful required fields, nested consumed shapes and existing decision values. Preserve valid revision, failure, skip and planning-only outputs through branch-aware schemas; commit fields are required only on paths that actually commit. Do not impose closed additional-property rules unless already required by the contract. Retain existing validation budgets; add an explicit supported retry budget where the installed contract requires one. No vacuous object schemas or blanket schemas for unconditional terminal agents.

For example, `packages/codex-simple-work-package/workflows/codex-simple-work-package/prompts/review.md` defines `payload.needs_revision` (boolean), `findings` (objects containing severity/file/line/message), `feedback` (strings), and `accepted` (boolean). Its schema must describe those fields, accept the prompt's `high`, `middle`, `low` severities, and preserve `when.needs_revision` outside the payload schema. Behavioral checks verify revision for high/middle findings and acceptance otherwise; schema presence alone is insufficient.

Cursor and Claude differences stay in existing `extends` patches and replacement maps. For example, `packages/cursor-cli-design-and-implement-review-loop/workflows/cursor-cli-design-and-implement-review-loop/workflow.json` maps `codex-agent` to `cursor-cli-agent`, reference field names to Cursor equivalents, and the implementation model to `composer-2.5`. Preserve those mappings; verify effective inherited schemas, sandbox declarations, replaced property names and backend-specific overrides after base migration. These package wrappers are the existing adaptation boundary; no new adapter modules are justified without reference input or runtime code changes.

## Dependencies and package coverage

The YouTube workflow manifest declares three external add-on dependencies and content locks: download, audio extraction and transcription. Verify it through an isolated installation of repository payloads with those dependencies resolved. Keep its capability grants, executable resolution and input/output flow intact. A raw workflow-only catalog cannot prove installed-package failure. Conversely, do not waive an actual resolved-installation failure as the known catalog false positive. Deterministic scenarios should exercise the data handoffs without requiring live YouTube/GCP credentials or paid calls.

Include add-on source/descriptor compatibility, capability and environment mappings, manifest dependency locks, skill frontmatter and referenced files, and examples' documented invocations in the inventory. Edit only concrete incompatibilities. Reuse existing package tests and deterministic fixtures; do not rewrite working add-ons, skills or examples solely to make every package change. Update relevant `EXPECTED_RESULTS.md` and documentation when corrected contracts change their expected evidence.

## Verification design

The implementation plan must identify exact changed producers, their consumers, authority rationale and affected fixtures per base family. Record installed CLI version, source identity, expanded command, final exit code, complete log path and case/assertion counts under repository-root `tmp/registry-contract-migration/verification/`. Keep sessions, artifacts, isolated install roots, catalog copies and build scratch beneath `tmp/`. Run in the foreground and poll any yielded session through exit. An incomplete log, zero tests or a mock process exit without asserted session outcomes is not a pass.

`mise.toml` currently validates manifests via `swift run --package-path "${RIELA_ROOT:-../riela}"`, and copies only workflow directories for validation. Adapt the existing check entry points minimally to use installed Riela 0.2.1, repository-local scratch, and dependency-aware package resolution. Do not introduce a second general validation framework. Keep complete manifest coverage, detect catalog name collisions, include all cross-workflow callees, and validate every effective inherited wrapper rather than skipping it. Installation/validation here concerns target repository packages in an isolated test context, never readiness of the running orchestration workflow. Establish actual supported installation flags from CLI help during implementation; do not infer installed behavior from mutable user registries.

Required command families (record concrete workflow names and paths when executed):

```sh
riela --version
mise run package:validate
mise run workflow:validate
riela workflow validate <target-workflow> --workflow-definition-dir <isolated-target-root> --output json
riela workflow inspect <target-workflow> --workflow-definition-dir <isolated-target-root> --output json
riela workflow run <target-workflow> --workflow-definition-dir <isolated-target-root> --mock-scenario <fixture> --session-store <tmp-session-root> --artifact-root <tmp-artifact-root> --output json
mise run workflow:check-compact
mise run workflow:check-codex-dispatch
bun packages/fable-and-improve-opus/tests/check-output-contract.ts --evidence-root <tmp-opus-evidence>
bun packages/fable-and-improve-codex/tests/check-output-contract.ts --evidence-root <tmp-codex-evidence>
mise run check
git diff --check
```

Run existing relevant scenarios for every changed base and effective wrapper. Focus regression additions on accept/revise routing, malformed/missing consumed fields, conditional commit fields, cross-workflow handoffs, inheritance preservation and external add-on resolution. Assert observed payloads, selected and bypassed steps, terminal status and no unintended side effects. Mocks do not prove real backend sandbox enforcement; static authority checks plus installed contract validation cover declarations. If mocks bypass output validation, demonstrate negative schema rejection through the installed validator's supported entry point and state the remaining coverage limit rather than claiming runtime rejection.

Capture a source-matched baseline before implementation changes. A remaining `mise run check` failure may be accepted only with the same failure reproduced at the intake commit in a disposable copy under `tmp/`, an exact command/log/exit comparison, and a separate tracked issue reference. New failures and unexplained differences block completion. An unavailable executable or network resource is a verification gap, not a passing or proven pre-existing check. Preserve all failures in the final report.

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

No unresolved user decision or supplied provenance/input contradiction was identified. Issue #14 title/body were unavailable during intake because GitHub was unreachable; the supplied brief remains authoritative. Retrieving that issue later is traceability follow-up, not permission to expand scope. No Step 3/5 feedback was supplied for this execution.

The author checked issue/scope mapping, concrete producer/consumer contracts, per-role authority, inherited backend behavior, dependency-aware YouTube validation, whole-package coverage, bounded metadata updates and reviewed branch delivery. No high/mid design finding remains. Implementation and independent review are downstream gates, not claims made by this design. Residual delivery risks are broad inherited-contract propagation, dependency-resolution verification and baseline failure attribution; each has an explicit verification gate above.
