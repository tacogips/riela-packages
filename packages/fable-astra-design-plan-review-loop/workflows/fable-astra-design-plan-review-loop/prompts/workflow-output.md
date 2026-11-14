Report the latest Astra review without changing any files or planning decisions.
Verify it explicitly accepted the current revision and that both artifact files
still match artifactDigests. If evidence is missing or files changed, report
status=blocked and accepted=false; never manufacture successful acceptance.
Otherwise report status=accepted and accepted=true, workflowInput, revision,
designDocPaths, implPlanPaths, artifactDigests, reviewEvidence, discussionHistory,
findingDispositions, residualLowRisks, assumptions and planned verification.
State that design and implementation planning are complete and implementation
has not run. Return {"when":{"always":true},"payload":{...}}.
