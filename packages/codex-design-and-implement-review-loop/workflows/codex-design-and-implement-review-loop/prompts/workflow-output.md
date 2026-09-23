Publish the final accepted workflow result.

Use only the executed-step payloads provided in this input message. Do not run
commands. Do not read files. Do not inspect repository state, logs, skills,
sessions, or prior history. Produce the final JSON immediately from the
provided payloads.

If Step 5 accepted a planning-only run, Step 9 emitted the commit message, Step 10 committed it, and Step 11 pushed it, return JSON with:
- `status`: `accepted`
- `workflowMode`: `design-plan-only`
- `designDocPaths`
- `implPlanPaths`
- `codexAgentReferences`
- `designReviewSummary`
- `implPlanReviewSummary`
- `commitMessage`
- `commitHash`
- `committedFiles`
- `pushedRemote`
- `pushedBranch`
- `baseBranch`
- `mergeStatus`
- `basePushStatus`
- `nextStep`
- `residualRisks`

If the workflow continued through Step 8, Step 9 emitted the commit message, Step 10 committed it, and Step 11 pushed it, return JSON with:
- `status`: `accepted`
- `workflowMode`: `issue-resolution`
- `issueReference`
- `issueTitle`
- `designDocPaths`
- `implPlanPaths`
- `changedFiles`
- `designReviewSummary`
- `implPlanReviewSummary`
- `implementationSummary`
- `testIntegritySummary`
- `implementationReviewSummary`
- `adversarialReviewSummary` when the adversarial implementation review gate ran
- `documentationFiles`
- `documentationSummary`
- `archivedImplPlanPaths`
- `implPlanCompletionSummary`
- `commitMessage`
- `commitHash`
- `committedFiles`
- `pushedRemote`
- `pushedBranch`
- `baseBranch`
- `mergeStatus`
- `basePushStatus`
- `verification`
- `residualRisks`

Copy `commitMessage`, `commitHash`, and `committedFiles` exactly from the accepted
Step 10 `git` payload. Copy `pushedRemote` and `pushedBranch` exactly from the
accepted Step 11 `git` payload. For both modes, copy `baseBranch`, `mergeStatus`,
and `basePushStatus` exactly from the accepted `base-branch-integrate` payload;
include them even when the implementation branch is already the base branch.

For issue-resolution include checkpointCommit, all integrated plan IDs, wave/branch session evidence, overwrite detections and repairs, and combined verification. Do not claim completion if a branch failed or required behavior/evidence is missing. Planning-only has no implementation waves. Read final git integration evidence, not only the earlier implementation-branch push.
