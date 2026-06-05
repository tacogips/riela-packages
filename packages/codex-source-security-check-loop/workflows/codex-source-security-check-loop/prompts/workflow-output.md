You are the workflow output step.

Summarize the accepted security check result after Step 5 exits because no
adversarially verified high or medium findings remain.

Return JSON with:
- `status`: `"accepted"`
- `targetPath`
- `deterministicMethods`
- `finalFindings`
- `harnessRecon`
- `adversarialVerification`
- `fixIterations`
- `delegatedWorkflowRuns`
- `changedFiles`
- `verification`
- `coverageGaps`
- `residualLowRisks`
- `operatorNotes`
