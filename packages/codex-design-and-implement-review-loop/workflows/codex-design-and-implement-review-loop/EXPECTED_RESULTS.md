# Expected results

Use the paired Riela source build and workflow validate/inspect with --workflow-definition-dir pointing to the package workflows directory. Run each bundled mock scenario with an isolated --session-store and --artifact-root; no live models or Git mutations are executed.

- mock-scenario.json: completed, exitCode 0. Astra authors the design and plan; Terra implements and reconciles; Sol runs the intake, design/plan/test-integrity gates and one adversarial material-issue review; Astra accepts the combined design/implementation before final Git operations. There is no duplicate ordinary Step 7 review. plan-git-commit precedes native implementation fanout, and each branch stops before reconcile-implementations.
- mock-scenario-fanout.json: two items become two fanout branches, joined in input order. Both implementation/review subpaths run; the parent performs reconciliation and finalization once. No feature-local planning fanout.
- mock-scenario-planning-only.json: completed, exitCode 0. No dispatch-plans, implementation or reconciliation; plans remain active, final documentation commit/push and base integration run.

Native join returns branchId/status/sessionId/output, dispatchedBranchIds, pendingBranchIds, completedBranchIds and changeEvidence. Drift is a candidate requiring semantic review. Combined-tree repair findings return to reconciliation; failed branches and missing worker-owned evidence return to dispatch-plans for selective native redispatch. Failed branches remain pending and block final completion. Ignore timestamps, generated IDs and artifact paths.

Every agent node has low or medium effort. Astra design, plan, and integration-review nodes are medium effort; no node may declare high, xhigh, or extra-high effort. `dispatch-plans` performs only a bounded projection from the direct inbox and exact committed manifest; it does not explore the repository or recompute native dependency scheduling.

An explicit Step 6 dependency/readiness blocker with no implementation changes bypasses test-integrity and adversarial review. The wave outcome publishes an actionable blocked result before reconciliation, with blocked plan IDs, blockers and resume criteria; it never enters the review/reconcile loop as a successful implementation.

Maintainer regressions: RIELA_BIN=<paired-build>/riela bun .agents/skills/riela-package-release/scripts/check-compact-workflows.ts. Includes dependency-blocked implementation termination, completion and integrity revision, integration repair, selective redispatch, planning-only and Fable implementation review loops. Engine tests cover concurrency/failure policies, dependency waves and native change evidence.

The compact regression also verifies that an integration result missing its `when.repair_in_place` discriminator conservatively redispatches, and that repeated identical in-place integration findings terminate through the integration gate's configured convergence bounds instead of cycling until `maxStepsExceeded`.
