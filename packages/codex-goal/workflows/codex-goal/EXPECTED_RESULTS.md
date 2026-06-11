# Expected Results

The mock scenario should run the generic goal loop once:

- `goal` converts the operator request into a testable goal.
- `goal-quality-review` accepts the goal before planning, or routes back to
  `goal` when the goal needs improvement.
- `plan` creates an in-session plan without writing plan files.
- `plan-quality-review` accepts the plan before work, or routes back to `plan`
  when the plan needs improvement.
- `work` performs the requested work and records verification evidence.
- `goal-review` accepts the result when the goal is achieved.
- `workflow-output` publishes the accepted goal, plan summary, work evidence,
  verification, and residual risks.

Each goal, review, planning, and work step should actively investigate whether
an available Rielflow workflow should be used. Outputs should record workflow
discovery evidence, the delegation decision, and any invoked workflow results.

If `goal-quality-review` returns `when.needs_goal_revision: true`, the workflow
must route back to `goal` before planning.

If `plan-quality-review` returns `when.needs_plan_revision: true`, the workflow
must route back to `plan` before work.

If `goal-review` returns `when.needs_replan: true`, the workflow must route back
to `plan`. If it returns `when.needs_work: true`, the workflow must route back
to `work`. It should reach `workflow-output` only when both flags are false.

Goal, planning, work, and review outputs should preserve recommended or invoked
Rielflow workflow delegation when a specialized workflow is a better fit.
