# claude-code-website-builder

Event-ready Claude Code workflow that designs, assets, implements, runs Bun inside Docker, reviews, iterates, and snapshots SolidJS websites.

- Package id: `claude-code-website-builder`
- Backends: `claude-code-agent`
- Workflows: `claude-code-website-builder`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install claude-code-website-builder --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-website-builder --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect claude-code-website-builder --output json
riela workflow validate claude-code-website-builder
riela workflow run claude-code-website-builder --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
