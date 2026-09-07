You are the workflow output step.

Summarize the accepted design result after the parallel deep, broad, and adversarial review branches were reduced with no high or middle findings.

Return JSON with:
- `status`: `accepted`
- `feature`
- `designDocPaths`
- `designSummary`
- `deepReviewSummary`
- `broadReviewSummary`
- `adversarialReviewSummary`
- `acceptedFindings`
- `provisionalDecisions`
- `residualLowRisks`
- `verificationPlan`
- `recommendedNextSteps`
- `fanoutSummary`: review IDs, concurrency used, and whether every branch completed
