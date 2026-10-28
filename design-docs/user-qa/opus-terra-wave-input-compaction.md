# Opus Luna wave input compaction: scope decision

Status: **decided: Option A** (operator, 2026-10-22). Continue D1-D6 in this package now; the upstream riela change (scope `fanoutJoin` to the join step, no run-level persistence, no branch inheritance) is tracked in the riela repository as a follow-up to `feat/agent-prompt-overflow-guard`. Record the minimum riela version as pending until that release exists; do not implement Option B. Design:
`design-docs/specs/design-opus-terra-wave-input-compaction.md` (D7).

## Question

Riela 0.2.34 (`3f921eb4`) stores the raw fanout join as a run-level request
variable (`DeterministicWorkflowRunner.swift:426`). It renders that variable
into every later agent system prompt (`DeterministicWorkflowRunner+Prompting.swift:60-101, 154-165`)
and copies it into every later fanout branch (`DeterministicWorkflowRunner+Fanout.swift:242`).
The in-package join compaction (D1-D6) stops the overflow at
`implementation-wave-outcome`, but the ~8 MB join still reaches
`reconcile-implementations` and every later Opus or Luna step. Which bounding
path should this issue take?

## Options

| Option | Scope | Covers | Contract impact |
| --- | --- | --- | --- |
| A. Upstream riela change (recommended): scope `fanoutJoin` to the join step, with no run-level persistence and no branch inheritance | riela repository plus a release; package records the minimum riela version | all post-join and next-wave or redispatch steps | none |
| B. In-package `fanoutJoin` stub shadowing in predecessor payloads | this package only (schemas of wave-outcome, reconcile, integration-review, step7b, step8, step9; `git-push-gate.py`) | blocked-output, reconcile, integration-review, step7b/8/9, local-only workflow-output | changes the closed six-field `implementation-wave-outcome` contract (acceptance signal 3). Leaves `base-branch-integrate`, push-mode `workflow-output` and every next-wave or redispatch branch exposed. |
| C. D1-D6 only | this package | join step only | none; the requested outcome is not met |

## Recommendation

Choose A, and continue implementing D1-D6 in this package now, since they are
required under every option.

## Blocked until decided

- Acceptance signal 1 at the rendered-prompt level ("Opus-bound input below a
  fixed bound"). The projection-level test is unaffected.
- Requested outcome: "the run proceeds to reconciliation/integration as
  before".
- Prompt-level verification: a runner test (A, owner: riela maintainer) and a
  first live multi-branch wave check (owner: operator).
