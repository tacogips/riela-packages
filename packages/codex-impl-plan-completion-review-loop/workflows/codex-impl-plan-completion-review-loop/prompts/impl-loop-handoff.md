You are the implementation-loop handoff step.

Prepare a delegated workflow-call input for `codex-impl-plan-completion-loop`. Do not complete implementation work locally in this wrapper workflow.

Rules:
- Read the wrapper manager output and the original `runtimeVariables.workflowInput`.
- Preserve `workflowInput.planPath` when supplied so the child workflow can constrain itself to one active implementation plan.
- Preserve `workflowInput.maxIterations` and `workflowInput.constraints` when supplied.
- Make clear that the child workflow owns completing active implementation plans, updating plan progress, verification, and any commit behavior already defined by its delegated design-and-implement workflow.
- Keep review settings such as `hours` and `targetPaths` in wrapper context for the later review handoff; do not pass them as implementation requirements unless they are also part of user constraints.

Return adapter JSON shaped like:

```json
{
  "payload": {
    "workflowInput": {
      "planPath": "impl-plans/active/example.md",
      "maxIterations": 5,
      "constraints": []
    },
    "wrapperContext": {
      "nextWorkflowId": "codex-recent-change-quality-loop",
      "reviewInput": {
        "hours": 24,
        "targetPaths": []
      }
    },
    "handoffSummary": "Delegating implementation-plan completion before review."
  }
}
```
