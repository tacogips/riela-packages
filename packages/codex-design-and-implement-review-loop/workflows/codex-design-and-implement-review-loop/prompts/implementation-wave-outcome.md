Classify the native implementation wave before serial reconciliation.

Use only runtimeVariables.fanoutJoin or the joined inbox payload and the executed branch payloads supplied in this input. Do not run commands, inspect repository state, edit files, or invent missing dependency evidence.

Set `implementation_blocked` to true when any `fanoutJoin.branches[]` terminal output has `implementation_blocked: true` or `status: "blocked"`. A branch that routes directly from Step 6 to this join retains the Step 6 payload as its terminal output. Preserve that branch's plan ID, blockers, and concrete resume criteria. These are dependency/readiness outcomes, not successful implementations: do not send them through test-integrity review, adversarial review, reconciliation, integration review, documentation, or git finalization. Preserve successfulPlanIds only as diagnostic work-in-progress; do not claim those plans are accepted.

Set `implementation_blocked` to false only when no branch reported an implementation blocker. Ordinary failed or cancelled branches remain eligible for the existing reconciliation and selective-redispatch path and do not by themselves set this discriminator.

Return JSON `{implementation_blocked,blockedPlanIds,successfulPlanIds,blockers,resumeCriteria}`. When blocked, include at least one blocked plan, blocker, and resume criterion. When unblocked, return empty blockedPlanIds, blockers, and resumeCriteria.
