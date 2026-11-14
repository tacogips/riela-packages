# Workflow fanout and concurrency review

## Scope

This review covers all 58 authored workflows in the registry after Riela 0.1.37 added bounded dependency-wave fanout, durable branch reservations, shared-workspace write ownership, change tracking, resume-safe joins, and descendant-process cancellation.

The governing rule is to parallelize independent expensive work, while keeping dispatch, reduction, shared-state mutation, external side effects, and dependency chains serial. Read-only review fanout uses `writeOwnership.mode: read-only`. Concurrent implementation requires complete branch inputs, disjoint tracked paths, dependency edges, `shared-workspace` ownership, and a serial combined-tree reconciliation step.

## Directly improved base workflows

| Workflow | Change |
| --- | --- |
| `codex-deepdesign` | Replaced three serial reviews with deep, broad, and adversarial read-only branches at concurrency 3, followed by one reducer. |
| `codex-recent-change-quality-loop` | Added change-slice planning and read-only review fanout at concurrency 6, with the exit gate acting as coverage reducer. |
| `codex-source-security-check-loop` | Partitions the attack surface into 3–8 complete review items, runs them at concurrency 8, then serially triages and adversarially verifies merged findings. |
| `codex-adversarial-implementation-review-loop` | Dispatches correctness, integration, and adversarial review lenses concurrently at concurrency 3, then reduces before fix routing. |
| `codex-website-builder` | Reviews UX/design, assets/media, and implementation/runtime concurrently at concurrency 3, then reduces to exactly one iteration route. |
| `codex-refactoring-divide-and-conquer` | Retains concurrent slice review and adds dependency-aware shared-workspace implementation waves at concurrency 4, tracked-path evidence, accepted-task resume state, and serial combined-tree reconciliation. |

## Improved through inheritance

These 12 workflows inherit the corresponding base graph and therefore receive the same fanout behavior. Their authored descriptions were updated so inspection and registry discovery expose the actual behavior.

- `claude-code-deepdesign`, `cursor-cli-deepdesign`
- `claude-code-recent-change-quality-loop`, `cursor-cli-recent-change-quality-loop`
- `claude-code-source-security-check-loop`, `cursor-cli-source-security-check-loop`
- `claude-code-adversarial-implementation-review-loop`, `cursor-cli-adversarial-implementation-review-loop`
- `claude-code-website-builder`, `cursor-cli-website-builder`
- `claude-code-refactoring-divide-and-conquer`, `cursor-cli-refactoring-divide-and-conquer`

## Already using the new model effectively

- `codex-design-and-implement-review-loop` and its five derived variants (`claude-code-design-and-implement-review-loop`, `cursor-cli-design-and-implement-review-loop`, `cursor-cli-fable-design-and-implement-review-loop`, `cursor-cli-hydra-claude-design-and-implement-review-loop`, `cursor-cli-hydra-codex-design-and-implement-review-loop`) already use dependency-aware shared-workspace implementation fanout and serial reconciliation.
- `fable-and-improve-codex` and `fable-and-improve-opus` already use the same bounded implementation/review pattern.

## Correctly retained as serial or leaf workflows

| Workflows | Reason |
| --- | --- |
| `codex-refactoring-slice-review`, `claude-code-refactoring-slice-review`, `cursor-cli-refactoring-slice-review` | These are read-only fanout leaf workers; adding nested fanout would duplicate ownership and overhead. |
| `codex-simple-work-package`, `claude-code-simple-work-package`, `cursor-cli-simple-work-package` | Small-work fast path with one tightly scoped implementation and review; fanout startup/reduction cost would dominate. |
| `codex-goal`, `claude-code-goal`, `cursor-cli-goal` | Goal, plan, work, and acceptance are causally dependent. Specialized delegated workflows may fan out internally. |
| `codex-impl-plan-completion-loop`, `claude-code-impl-plan-completion-loop`, `cursor-cli-impl-plan-completion-loop` | The outer plan-state reassessment stays serial; the called implementation workflow performs safe task fanout. |
| `codex-impl-plan-completion-review-loop`, `claude-code-impl-plan-completion-review-loop`, `cursor-cli-impl-plan-completion-review-loop` | Completion must precede recent-change review, so cross-workflow composition is intentionally sequential. |
| `codex-task-watchdog`, `claude-code-task-watchdog`, `cursor-cli-task-watchdog` | Queue claiming, status mutation, skill mining, and commit are shared external state and deliberately one task at a time. Dispatched child workflows may fan out. |
| `codex-deep-creation` | Design, implementation, and security verification form a strict dependency chain; each called workflow now supplies its own safe concurrency. |
| `claude-code-worker-only-single-step`, `cursor-cli-developer-workflows` | Reference/marker workflows with no independent expensive branches. |
| `greeting-container`, `greeting-shell` | Single deterministic execution nodes. |
| `riela-package-installer-skill`, `riela-package-manager-skill`, `riela-package-release-skill`, `riela-project-workflow-skill`, `riela-temporary-workflow-skill`, `riela-workflow-creator-skill`, `riela-workflow-skill-creator-skill` | Skill-package marker workflows; fanout would add no useful work. |
| `youtube-mp4-to-text`, `youtube-shorts-to-text-container` | Download, extraction, and transcription are data-dependent pipeline stages. Parallelizing them would race missing artifacts. |

## Per-workflow audit (58 of 58)

`Inherited` means the authored file intentionally contains only an `extends`
overlay; the effective fanout shown here comes from its resolved base workflow.

| # | Workflow | Effective fanout | Decision | Evidence-based reason |
| ---: | --- | --- | --- | --- |
| 1 | `claude-code-adversarial-implementation-review-loop` | 3 read-only lenses | Improved, inherited | Resolves the updated Codex base and only patches backend/model references. |
| 2 | `claude-code-deepdesign` | 3 read-only lenses | Improved, inherited | Deep, broad, and adversarial design reviews are independent and reduced serially. |
| 3 | `claude-code-design-and-implement-review-loop` | 4 shared-workspace workers | Already optimal, inherited | Base already has dependency-aware implementation fanout and serial reconciliation. |
| 4 | `claude-code-goal` | None | Keep serial, inherited | Goal, plan, work, and acceptance are causally ordered; delegated specialists may fan out. |
| 5 | `claude-code-impl-plan-completion-loop` | Child fanout | Keep serial outer loop | Shared plan status is reassessed serially; the called implementation loop owns concurrency. |
| 6 | `claude-code-impl-plan-completion-review-loop` | Child fanout | Keep serial composition | Completion must finish before recent-change review begins. |
| 7 | `claude-code-recent-change-quality-loop` | 6 read-only slices | Improved, inherited | Independent changed-file slices fan out before one coverage reducer. |
| 8 | `claude-code-refactoring-divide-and-conquer` | 8 read-only + 4 shared-workspace | Improved, inherited | Inherits concurrent discovery and dependency-wave implementation. |
| 9 | `claude-code-refactoring-slice-review` | None | Keep as leaf | This is already a single read-only worker invoked by parent fanout. |
| 10 | `claude-code-simple-work-package` | None | Keep serial, inherited | Small-task implementation/review loop would pay more fanout overhead than useful work. |
| 11 | `claude-code-source-security-check-loop` | 8 read-only focus areas | Improved, inherited | Independent attack-surface reviews precede serial triage and verification. |
| 12 | `claude-code-task-watchdog` | Child fanout | Keep serial supervisor | Queue claiming, task status, skill mining, and commit mutate shared state. |
| 13 | `claude-code-website-builder` | 3 read-only lenses | Improved, inherited | UX, assets, and runtime review can proceed independently after the server is ready. |
| 14 | `claude-code-worker-only-single-step` | None | Keep single step | Minimal manager-less reference workflow has no divisible work. |
| 15 | `codex-adversarial-implementation-review-loop` | 3 read-only lenses | Improved directly | Added correctness, integration, and adversarial branches plus a fail-closed reducer. |
| 16 | `codex-deep-creation` | Child fanout | Keep serial composition | Design → implementation → security is a strict dependency chain; each child now fans out internally. |
| 17 | `codex-deepdesign` | 3 read-only lenses | Improved directly | Replaced serial deep/broad/adversarial review with bounded fanout and one reducer. |
| 18 | `codex-design-and-implement-review-loop` | 4 shared-workspace workers | Already optimal | Uses dependency ids, completed ids, tracked paths, shared ownership, and reconciliation. |
| 19 | `codex-goal` | None | Keep serial | Each stage consumes the decision/evidence produced by the preceding stage. |
| 20 | `codex-impl-plan-completion-loop` | Child fanout | Keep serial outer loop | Delegates implementation to the fanout-capable adversarial implementation workflow. |
| 21 | `codex-impl-plan-completion-review-loop` | Child fanout | Keep serial composition | Calls completion then quality review; reversing or overlapping them reviews unstable state. |
| 22 | `codex-recent-change-quality-loop` | 6 read-only slices | Improved directly | Inventory emits complete review slices; the exit gate reduces all branch evidence. |
| 23 | `codex-refactoring-divide-and-conquer` | 8 read-only + 4 shared-workspace | Improved directly | Adds disjoint tracked-path implementation waves, dependency scheduling, and combined-tree reconciliation. |
| 24 | `codex-refactoring-slice-review` | None | Keep as leaf | One bounded slice is the unit already dispatched by the parent concurrency layer. |
| 25 | `codex-simple-work-package` | None | Keep serial | Three-step fast path intentionally optimizes latency for one small write scope. |
| 26 | `codex-source-security-check-loop` | 8 read-only focus areas | Improved directly | Deterministic recon partitions 3–8 complete focus items before serial security triage. |
| 27 | `codex-task-watchdog` | Child fanout | Keep serial supervisor | Claims one queue item and performs shared external/status/git effects; children own safe concurrency. |
| 28 | `codex-website-builder` | 3 read-only lenses | Improved directly | Post-build UX, asset, and runtime review now fan out and reduce to one iteration route. |
| 29 | `cursor-cli-adversarial-implementation-review-loop` | 3 read-only lenses | Improved, inherited | Resolves the updated base with Cursor backend patches. |
| 30 | `cursor-cli-deepdesign` | 3 read-only lenses | Improved, inherited | Resolves the updated parallel design-review base. |
| 31 | `cursor-cli-design-and-implement-review-loop` | 4 shared-workspace workers | Already optimal, inherited | Inherits dependency-aware implementation fanout. |
| 32 | `cursor-cli-developer-workflows` | None | Keep single step | Package-set marker/dispatcher reference contains no expensive independent work. |
| 33 | `cursor-cli-fable-design-and-implement-review-loop` | 4 shared-workspace workers | Already optimal, inherited | Uses the established design-and-implement dependency-wave graph. |
| 34 | `cursor-cli-goal` | None | Keep serial, inherited | Goal lifecycle ordering is intentional. |
| 35 | `cursor-cli-hydra-claude-design-and-implement-review-loop` | 4 shared-workspace workers | Already optimal, inherited | Backend/model overlay retains the proven implementation fanout graph. |
| 36 | `cursor-cli-hydra-codex-design-and-implement-review-loop` | 4 shared-workspace workers | Already optimal, inherited | Backend/model overlay retains the proven implementation fanout graph. |
| 37 | `cursor-cli-impl-plan-completion-loop` | Child fanout | Keep serial outer loop | Plan-state reassessment must remain ordered while the called workflow fans out. |
| 38 | `cursor-cli-impl-plan-completion-review-loop` | Child fanout | Keep serial composition | Completion precedes quality review by contract. |
| 39 | `cursor-cli-recent-change-quality-loop` | 6 read-only slices | Improved, inherited | Resolves the updated sliced-review base. |
| 40 | `cursor-cli-refactoring-divide-and-conquer` | 8 read-only + 4 shared-workspace | Improved, inherited | Resolves the updated two-level refactoring fanout graph. |
| 41 | `cursor-cli-refactoring-slice-review` | None | Keep as leaf | Parent fanout supplies exactly one slice per invocation. |
| 42 | `cursor-cli-simple-work-package` | None | Keep serial, inherited | One small task does not justify dispatch/reduction overhead. |
| 43 | `cursor-cli-source-security-check-loop` | 8 read-only focus areas | Improved, inherited | Resolves the updated security focus-area fanout graph. |
| 44 | `cursor-cli-task-watchdog` | Child fanout | Keep serial supervisor | Queue and repository side effects require one owner. |
| 45 | `cursor-cli-website-builder` | 3 read-only lenses | Improved, inherited | Resolves the updated website review graph. |
| 46 | `fable-and-improve-codex` | 4 shared-workspace workers | Already optimal | Already authors complete implementation items, tracks writes, and reconciles serially. |
| 47 | `fable-and-improve-opus` | 4 shared-workspace workers | Already optimal | Same mature dependency-wave implementation pattern with an Opus backend. |
| 48 | `greeting-container` | None | Keep single step | One deterministic container command has no independent subtask. |
| 49 | `greeting-shell` | None | Keep single step | One deterministic shell command has no independent subtask. |
| 50 | `riela-package-installer-skill` | None | Keep marker | Skill-package reference workflow performs no divisible execution. |
| 51 | `riela-package-manager-skill` | None | Keep marker | Skill-package reference workflow performs no divisible execution. |
| 52 | `riela-package-release-skill` | None | Keep marker | Skill-package reference workflow performs no divisible execution. |
| 53 | `riela-project-workflow-skill` | None | Keep marker | Skill-package reference workflow performs no divisible execution. |
| 54 | `riela-temporary-workflow-skill` | None | Keep marker | Skill-package reference workflow performs no divisible execution. |
| 55 | `riela-workflow-creator-skill` | None | Keep marker | Skill-package reference workflow performs no divisible execution. |
| 56 | `riela-workflow-skill-creator-skill` | None | Keep marker | Skill-package reference workflow performs no divisible execution. |
| 57 | `youtube-mp4-to-text` | None | Keep serial pipeline | Downloaded media is required before audio extraction, which is required before transcription. |
| 58 | `youtube-shorts-to-text-container` | None | Keep single container | Its download/extract/transcribe lifecycle is intentionally encapsulated in one container execution. |

## Safety and efficiency invariants

- Dispatchers emit small descriptions for selection but complete branch payloads for execution.
- Branch dispatch ids are stable within an attempt and unique across repair attempts; semantic task ids remain stable, dependencies are explicit, and completed dispatch ids are carried across waves.
- Read-only reviews never mutate the worktree.
- Concurrent writers have disjoint `trackedPaths`; overlap is represented as a dependency or a single task.
- `collect-partial` preserves evidence, but reducers fail closed on missing, failed, duplicated, or malformed branch results.
- Serial reducers reread the combined state and own the only downstream routing decision.
- Concurrency is bounded (3 for fixed review lenses, 4 for shared-workspace implementation, 6–8 for read-only partitioned analysis).
