# riela-package-manager-skill

Skill package that teaches agents how to search, install, inspect, validate, and use riela packages, including RielaApp enable/disable and required environment metadata.

- Package id: `riela-package-manager-skill`
- Skills: Claude Code, Codex

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install riela-package-manager-skill --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

## Usage

Installing this package projects its skills into the agent skill
directories for the chosen scope. See the skill files under
`skills/` for the exact guidance that gets installed.

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
