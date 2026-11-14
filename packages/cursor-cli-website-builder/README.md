# cursor-cli-website-builder

Event-ready Cursor CLI workflow that designs, assets, implements, runs Bun inside Docker, reviews, iterates, and snapshots SolidJS websites.

- Package id: `cursor-cli-website-builder`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-website-builder`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-website-builder --local-path /path/to/riela-packages
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
riela workflow inspect cursor-cli-website-builder --output json
riela workflow validate cursor-cli-website-builder
riela workflow run cursor-cli-website-builder --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
