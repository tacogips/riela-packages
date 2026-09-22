Publish the terminal blocked issue-resolution result for a dependency, no-progress, or materially-unverified implementation branch.

Use only the executed-step payloads provided in this input message. Do not run commands, read files, inspect repository state, or claim accepted work. Copy the exact issue reference, blocked plan IDs, blockers, and resume criteria from implementation-wave-outcome. Successful plan IDs are diagnostic work-in-progress only and are not accepted or complete.

Return JSON `{implementation_blocked:true,status:"blocked",workflowMode:"issue-resolution",issueReference,checkpointCommit,manifestPath,blockedPlanIds,successfulPlanIds,blockers,resumeCriteria,nextStep,residualRisks}`. `nextStep` must name the prerequisite work/evidence needed before rerunning this plan. Do not claim test-integrity review, adversarial review, reconciliation, integration review, documentation refresh, commit, push, or base integration.
