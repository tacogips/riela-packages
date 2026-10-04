# codex-design-and-implement-review-loop

Codex design/implementation workflow with native shared-branch fanout and overwrite reconciliation.

All agent roles, including design documentation, implementation-plan authoring, implementation, and combined-tree integration review, use GPT-6 Sol at medium effort. No workflow node uses Astra or high, xhigh, or extra-high effort. The design author checks existing relevant design docs first, uses a sound draft as the implementation baseline, and creates a new design only when none applies. The adversarial gate emits feedback only for material spec violations, correctness/data-loss/security risks, likely regressions, or missing material verification; style nits, naming-only comments, speculative refactors, and overengineering are forbidden.

Plan dispatch is not an agent judgment. A deterministic command projects the exact committed manifest and the latest runtime-owned `acceptedPlanIds` from the direct inbox into native fanout items. Riela's dependency scheduler decides the ready wave; an empty, unknown, or fully completed acceptance set fails explicitly instead of silently producing an empty dispatch.

- Package id: `codex-design-and-implement-review-loop`
- Backends: `codex-agent`
- Workflows: `codex-design-and-implement-review-loop`
- Skills: Codex (`codex-design-and-implement-review-loop`)

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-design-and-implement-review-loop --source /path/to/riela-packages/packages/codex-design-and-implement-review-loop
```

Add `--scope user` to install for the current user instead of the
current project.

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect codex-design-and-implement-review-loop --output json
riela workflow validate codex-design-and-implement-review-loop
riela workflow run codex-design-and-implement-review-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.

## Shared-branch implementation

Design and all implementation plans are authored by a single author node per phase. Accepted designs/plans are committed before implementation. Native Riela fanout runs dependency-ready implementation/review branches in the same working directory and Git branch (default concurrency 4; --max-concurrency can lower it). No worktrees are created.

The runtime calls each parallel execution a **fanout branch**, its input an **item**, and the aggregation a **join**. This is separate from a Git branch. Built-in fanout.dependencies selects ready branches from stable IDs and accepted dependencies. Built-in fanout.changeTracking captures immutable file content, hashes and modes at node boundaries, and reports drift candidates at join. No workflow-local evidence script is needed.

### Write ownership, source snapshots and generated artifacts

Each manifest plan separates three responsibilities:

- **Write ownership**: `writePaths` and `sharedPaths` say where the plan may edit or produce output. Conflict detection and integration-review ownership use them unchanged.
- **Source snapshot paths**: the dispatcher projects `trackedPaths = writePaths + sharedPaths - artifactRoots`. Native change tracking snapshots their full content at every node boundary within the core limits: 512 declared paths, 512 expanded entries (directories and missing declared paths count), 8,000,000 bytes per file and 64,000,000 bytes in total, with symlinks and special files rejected.
- **Generated artifact roots**: the optional `artifactRoots` array names tool installs, download/build caches and large binaries. Each entry must exactly equal one of the plan's `writePaths`, may not appear in `sharedPaths`, may not lie inside a remaining source path or another artifact root, and at most 64 are allowed. The runtime records them as bounded digest and count manifests, never content. An authored audit manifest such as `native-tools/toolchain.json`, which records tool versions, install commands, exit codes and digests, stays in `writePaths` as a source snapshot even though it sits inside the `native-tools` artifact root. At least one source path must remain.

Manifests without `artifactRoots` keep the previous source-only behaviour.

Validation happens before expensive work. After the plan checkpoint writes the manifest, the deterministic `plan-contract-validate` gate runs the same rules and preflight that dispatch uses. It reports every selected root with its current entry and byte counts, the limits, and whether the root is expected to grow. A rejection returns to the plan author with high findings, and the plan review and checkpoint gates then run again. No path is silently dropped and a rejection is never converted into acceptance. Maintainers can run the same check directly; it prints a JSON report and exits 1 on any violation:

```bash
python3 <workflow-dir>/scripts/dispatch-plans.py --validate-manifest impl-plans/active/<task-id>-dispatch.json
```

A runtime tracking rejection, such as a `policy_blocked: fanout snapshot ...` branch failure or a join whose `changeEvidence.complete` is false, is classified as an implementation blocker. It carries the structured branch, node, phase, root, path, observed and limit diagnostic and the resume criterion to amend the checkpoint. Successful sibling branches are preserved for integration review.

The dispatch coordinator is a bounded manifest-projection step. It may read only the direct inbox, checkpoint commit, exact committed manifest, and accepted plan IDs; repository exploration, example discovery, skill rereads, tests, and dependency-wave reasoning are forbidden there. Native fanout owns dependency validation and ready-wave selection.

After all branches stop, Sol serial reconciliation repairs missing/overwritten behavior and a read-only Sol integration review checks the combined tree against every plan and the design. The reviewer returns the immutable wave-acceptance record in its output, and the runtime persists that communication for later dependency dispatch rather than asking the reviewer to write evidence files. Each implementation branch uses only one adversarial material-issue review gate after test-integrity; there is no duplicate ordinary implementation-review pass. A combined-tree defect routes back through reconciliation, while failed branches or missing worker-owned evidence route through plan dispatch for a fresh native worker attempt. Failed branches stay pending; already accepted branch IDs are skipped on subsequent dispatch. Preserve original evidence and existing user changes. Node-boundary snapshots cannot detect every transient overwrite inside an agent call, so per-edit intention records and behavior tests remain required.

If Sol cannot start a plan because required external dependency evidence is absent, it returns an explicit dependency-blocked outcome without editing. A blocked-only wave terminates before reconciliation with blocked plan IDs, evidence-backed blockers, and resume criteria. If the same wave also contains evidence-complete successful candidates, it preserves their branch hashes through reconciliation and Sol integration review; only that review can add them to `acceptedPlanIds`, so a later retry skips accepted work and dispatches only blocked plans. This prevents no-change work from entering a success-shaped review/reconcile cycle without repeating verified predecessors.

Completeness is plan-scoped. The accepted manifest DAG and plan text decide ownership, so a predecessor is not blocked because wiring or another task is explicitly assigned to a pending downstream dependent plan. Review accepts the verified predecessor, carries the downstream plan as pending, and unlocks it through `acceptedPlanIds`; ambiguous ownership and real predecessor defects still fail closed.

Integration review is fail-closed for convergence: only an explicit `repair_in_place: true` routes to serial reconciliation. Missing or ambiguous routing evidence, failed workers, and missing native provenance route to a fresh bounded redispatch, preventing repeated reconcile/review loops over unchanged evidence.

Implementation plans are deliberately detailed enough for even a lower-capability implementation model to execute without guessing: they must include intent/context, non-goals, exact file-level changes, invariants, acceptance criteria, and verification commands with required evidence. The Sol implementation and test-integrity nodes maximize safely independent delegated investigation and verification, while retaining one owner and prohibiting overlapping writes.

For Swift changes, selected-file strict SwiftLint uses only a nonempty NUL-delimited changed-file manifest. It retains the target repository's rules and never starts argument-less SwiftLint, which would apply `.swiftlint.yml` `included` paths to unrelated baseline files.

Git operations are serialized: the accepted plan checkpoint is committed and non-force pushed before implementation, then the final implementation commit is non-force pushed before base-branch integration. This keeps each built-in push limited to one unpublished commit. workflowInput.baseBranch defaults to the current branch; an explicit different base is merged only after combined verification. No force push or automatic discard of unrelated edits. A blocked checkpoint or final push prevents completion.

The planning checkpoint manifest always references every accepted design and plan, while its git `committedFiles` allowlist contains only the newly written manifest and accepted design/plan files that actually differ from HEAD. Already committed accepted files remain valid manifest inputs but are never added to the exact staged set. An empty or indeterminate checkpoint terminates explicitly as blocked instead of requesting an empty commit.

Requires a Riela build with fanout.dependencies, fanout.changeTracking and shared-branch finalization evidence support. The explicit shared-workspace ownership mode makes older runners reject the new bundle instead of silently ignoring its dependency/tracking fields. Use the paired Riela source changes before installing this update.

`changeTracking.artifactRootsFrom` requires a Riela core with the issue #130 artifact-evidence support. An older core ignores the field, so artifact roots are then neither snapshotted nor recorded as manifests while source snapshot paths keep working.

Runtime tracking rejections are checked mechanically after the native fanout join. Source snapshot or artifact-policy failures return to the plan author with the native diagnostics, then repeat independent plan review, contract preflight, checkpoint commit/push and dispatch. Incomplete wave evidence never promotes successful siblings to accepted plans. Checkpoint amendments preserve existing implementation changes and use the newest successfully pushed checkpoint. Dependency and no-progress blockers retain their existing terminal/partial-success behavior.
