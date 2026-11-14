You are the independent review step for project-scope skill changes created by
codex-task-watchdog.

Read the latest `skill-opportunity-mining` output, then inspect every created or
updated file under `.agents/skills`.

Review criteria:
- The skill is justified by reusable knowledge from the completed task log.
- The frontmatter has valid `name` and `description` fields.
- The description is specific enough to trigger only for the right future work.
- The body is concise, procedural, and repo-specific.
- The skill avoids private data, credentials, machine-local absolute paths, and
  copied task logs.
- The skill does not duplicate an existing `.agents/skills/*/SKILL.md`.
- Any `agents/openai.yaml`, references, scripts, or assets are necessary and
  consistent with the skill body.

If you find high or medium severity issues in the skill files, fix them in this
step and re-review the affected files. If a created skill is not justified,
delete that skill directory only when it contains no unrelated pre-existing
files; otherwise remove only the unjustified new files.

Do not stage, commit, push, or revert unrelated worktree changes.

Return JSON with:
- `taskId`
- `verdict`: `accepted`, `fixed-and-accepted`, or `rejected`
- `findings`
- `fixedFiles`
- `acceptedSkillFiles`
- `rejectedSkillFiles`
- `residualRisks`
