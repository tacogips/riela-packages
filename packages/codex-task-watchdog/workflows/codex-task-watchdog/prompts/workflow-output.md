You are the codex-task-watchdog output step.

Read the latest upstream workflow outputs and publish a concise final status for this watchdog polling pass.

Cases:
- If `claim-next-task` skipped, report `status: "skipped"` and the skip reason.
- If a task was completed, report `status: "completed"`, task id, kind, where detailed execution artifacts can be inspected, any project-scope skills created or updated from the completed Codex log, the skill review verdict, and the commit hash when available.
- If the task kind was unsupported, report `status: "unsupported"` and name the supported kinds.

Return JSON with:
- `status`
- `taskId`
- `kind`
- `reason`
- `summary`
- `skillChanges`
- `skillReview`
- `commitHash`
- `nextAction`
