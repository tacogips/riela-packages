# cursor-cli-goal

Generic Cursor CLI workflow that actively investigates available Riela workflows at each step, defines and reviews a goal, creates and reviews an in-session plan without writing plan files, performs the work with Composer 2.5, uses GPT-5.6 SOL for the other steps, may delegate to a more specific workflow when appropriate, and reviews goal completion before looping back to work or planning.

- Package id: `cursor-cli-goal`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-goal`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-goal --local-path /path/to/riela-packages
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
riela workflow inspect cursor-cli-goal --output json
riela workflow validate cursor-cli-goal
riela workflow run cursor-cli-goal --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
