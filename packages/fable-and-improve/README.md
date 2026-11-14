# fable-and-improve

Claude Code Fable orchestrator workflow that researches the request, maintains markdown goal and plan state, delegates implementation and review to codex-design-and-implement-review-loop, and repeats until Fable verifies completion.

- Package id: `fable-and-improve`
- Backends: `claude-code-agent`, `codex-agent`
- Workflows: `fable-and-improve`
- Skills: Claude Code

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install fable-and-improve --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-design-and-implement-review-loop --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect fable-and-improve --output json
riela workflow validate fable-and-improve
riela workflow run fable-and-improve --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
