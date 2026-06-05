You are Step 6: delegated security-fix handoff.

Prepare a delegated issue-resolution request for `codex-design-and-implement-review-loop` from the latest Step 3 triage, Step 4 adversarial verification, and Step 5 exit-gate outputs. Do not fix findings locally in this workflow.

Rules:
- Build a concise delegated request consumable through `runtimeVariables.workflowCall.input`.
- Set delegated workflow mode to issue resolution.
- Include only Step 4 verified high and medium findings that need code or config changes.
- Preserve Step 4 dismissed, duplicate, and residual-low decisions as review context, not as requested fixes.
- Preserve target paths, dirty worktree constraints, and user constraints from the manager input.
- Include deterministic verification commands that should be rerun after the delegated fix.
- Ask the delegated workflow not to stage, commit, or push unless the user explicitly requested it.

Return JSON with:
- `workflowInput`
- `reviewContext`
- `handoffSummary`

The `workflowInput` should include:
- `mode`: `"issue-resolution"`
- `requestedBehavior`
- `targetDirectory`
- `constraints`
- `acceptanceCriteria`
- `verificationHint`
