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
When `mergeStatus` is `branch-only`, state that only the implementation branch was pushed and the base branch was not merged or pushed by this workflow. Do not imply a PR exists. When `mergeStatus` is `pr-open`, also copy `pullRequestURL`, `pullRequestNumber`,
`pullRequestDraft`, and `pullRequestBaseBranch` exactly. State that the base branch has not been merged or
pushed by this workflow; do not turn PR handoff into a base-integration claim.

Local-only runs (`workflowInput.gitPush: false`): the accepted `final-push-gate`
payload carries the Step 10 `git` commit with `gitPush: false`, and Step 11 and
`base-branch-integrate` did not run. Copy `commitMessage`, `commitHash` and
`committedFiles` from that payload, set `pushedRemote` and `pushedBranch` to
`null`, `baseBranch` to the intake git context's base branch, `mergeStatus` to
`local-only` and `basePushStatus` to `not-pushed`. State that the plan checkpoint
and final commits exist only in the local repository and that nothing was pushed,
merged or integrated by this workflow. Treat the skipped steps as intentional, not
as failed git operations.

For issue-resolution include checkpointCommit, all integrated plan IDs, wave/branch session evidence, overwrite detections and repairs, and combined verification. Do not claim completion if a branch failed or required behavior/evidence is missing. Planning-only has no implementation waves. Read final PR-handoff or git-integration evidence, not only the earlier implementation-branch push.
