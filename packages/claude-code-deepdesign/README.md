# claude-code-deepdesign

Create and iteratively review design-doc specifications with one Claude Code author, one deep edge-case reviewer, and one broad integration reviewer until no high or middle findings remain.

- Package id: `claude-code-deepdesign`
- Backends: `claude-code-agent`
- Workflows: `claude-code-deepdesign`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install claude-code-deepdesign --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-deepdesign --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect claude-code-deepdesign --output json
riela workflow validate claude-code-deepdesign
riela workflow run claude-code-deepdesign --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
