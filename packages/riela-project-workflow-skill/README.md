# riela-project-workflow-skill

Skill package that teaches agents to turn work into a project-scope Riela workflow and then execute that workflow.

- Package id: `riela-project-workflow-skill`
- Skills: Claude Code, Codex, Cursor

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install riela-project-workflow-skill --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

## Usage

Installing this package projects its skills into the agent skill
directories for the chosen scope. See the skill files under
`skills/` for the exact guidance that gets installed.

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
