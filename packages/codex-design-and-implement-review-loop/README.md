# codex-design-and-implement-review-loop

Codex design/implementation workflow with native shared-branch fanout and overwrite reconciliation.

Design documentation, implementation-plan authoring, and combined-tree integration review use GPT-6 Astra at medium effort. Implementation, revisions, overwrite repair, intake, design/plan/test-integrity gates, the single adversarial implementation gate, documentation, commit, and manager coordination use GPT-6 Sol at medium effort. No workflow node uses high, xhigh, or extra-high effort. The adversarial gate emits feedback only for material spec violations, correctness/data-loss/security risks, likely regressions, or missing material verification; style nits, naming-only comments, speculative refactors, and overengineering are forbidden.

Plan dispatch is not an agent judgment. A deterministic command projects the exact committed manifest and the latest runtime-owned `acceptedPlanIds` from the direct inbox into native fanout items. Riela's dependency scheduler decides the ready wave; an empty, unknown, or fully completed acceptance set fails explicitly instead of silently producing an empty dispatch.

- Package id: `codex-design-and-implement-review-loop`
- Backends: `codex-agent`
- Workflows: `codex-design-and-implement-review-loop`
- Skills: Codex (`codex-design-and-implement-review-loop`)

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-design-and-implement-review-loop --local-path /path/to/riela-packages
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

The dispatch coordinator is a bounded manifest-projection step. It may read only the direct inbox, checkpoint commit, exact committed manifest, and accepted plan IDs; repository exploration, example discovery, skill rereads, tests, and dependency-wave reasoning are forbidden there. Native fanout owns dependency validation and ready-wave selection.

After all branches stop, Sol serial reconciliation repairs missing/overwritten behavior and Astra integration review checks the combined tree against every plan and the design. Astra remains read-only: it returns the immutable wave-acceptance record in its output, and the runtime persists that communication for later dependency dispatch rather than asking the reviewer to write evidence files. Each implementation branch uses only one adversarial material-issue review gate after test-integrity; there is no duplicate ordinary implementation-review pass. A combined-tree defect routes back through reconciliation, while failed branches or missing worker-owned evidence route through plan dispatch for a fresh native worker attempt. Failed branches stay pending; already accepted branch IDs are skipped on subsequent dispatch. Preserve original evidence and existing user changes. Node-boundary snapshots cannot detect every transient overwrite inside an agent call, so per-edit intention records and behavior tests remain required.

If Sol cannot start a plan because required external dependency evidence is absent, it returns an explicit dependency-blocked outcome without editing. A blocked-only wave terminates before reconciliation with blocked plan IDs, evidence-backed blockers, and resume criteria. If the same wave also contains evidence-complete successful candidates, it preserves their branch hashes through reconciliation and Astra integration review; only that review can add them to `acceptedPlanIds`, so a later retry skips accepted work and dispatches only blocked plans. This prevents no-change work from entering a success-shaped review/reconcile cycle without repeating verified predecessors.

Completeness is plan-scoped. The accepted manifest DAG and plan text decide ownership, so a predecessor is not blocked because wiring or another task is explicitly assigned to a pending downstream dependent plan. Review accepts the verified predecessor, carries the downstream plan as pending, and unlocks it through `acceptedPlanIds`; ambiguous ownership and real predecessor defects still fail closed.

Integration review is fail-closed for convergence: only an explicit `repair_in_place: true` routes to serial reconciliation. Missing or ambiguous routing evidence, failed workers, and missing native provenance route to a fresh bounded redispatch, preventing repeated reconcile/review loops over unchanged evidence.

Implementation plans are deliberately detailed enough for even a lower-capability implementation model to execute without guessing: they must include intent/context, non-goals, exact file-level changes, invariants, acceptance criteria, and verification commands with required evidence. The Sol implementation and test-integrity nodes maximize safely independent delegated investigation and verification, while retaining one owner and prohibiting overlapping writes.

For Swift changes, selected-file strict SwiftLint uses only a nonempty NUL-delimited changed-file manifest. It retains the target repository's rules and never starts argument-less SwiftLint, which would apply `.swiftlint.yml` `included` paths to unrelated baseline files.

Git operations are serialized: planning checkpoint, final implementation commit/push, and base-branch integration. workflowInput.baseBranch defaults to the current branch; an explicit different base is merged only after combined verification. No force push or automatic discard of unrelated edits. A blocked merge/push prevents completion.

The planning checkpoint manifest always references every accepted design and plan, while its git `committedFiles` allowlist contains only the newly written manifest and accepted design/plan files that actually differ from HEAD. Already committed accepted files remain valid manifest inputs but are never added to the exact staged set. An empty or indeterminate checkpoint terminates explicitly as blocked instead of requesting an empty commit.

Requires a Riela build with fanout.dependencies, fanout.changeTracking and shared-branch finalization evidence support. The explicit shared-workspace ownership mode makes older runners reject the new bundle instead of silently ignoring its dependency/tracking fields. Use the paired Riela source changes before installing this update.
