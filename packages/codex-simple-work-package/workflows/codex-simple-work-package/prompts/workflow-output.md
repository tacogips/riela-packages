Publish the final accepted simple-work result.

Use only the implementation and review payloads provided in this input
message. Do not run commands. Do not read files. Do not inspect repository
state, logs, skills, sessions, or prior history. Produce the final JSON
immediately from the provided payloads.

Return JSON with:
- `status`: `accepted`
- `changedFiles`
- `implementationSummary`
- `reviewSummary`
- `verification`
- `residualRisks`
- `nextStep`
