# claude-code-goal

Generic Claude Code Opus 4.8 workflow that actively investigates available Riela workflows at each step, defines and reviews a goal, creates and reviews an in-session plan without writing plan files, performs the work, may delegate to a more specific workflow when appropriate, and reviews goal completion before looping back to work or planning.

- Package id: `claude-code-goal`
- Backends: `claude-code-agent`
- Workflows: `claude-code-goal`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install claude-code-goal --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-goal --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect claude-code-goal --output json
riela workflow validate claude-code-goal
riela workflow run claude-code-goal --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
