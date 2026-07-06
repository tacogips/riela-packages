# cursor-cli-recent-change-quality-loop

Review code changes introduced within a configurable recent time window, including uncommitted changes, and delegate any blocking findings into the design-and-implement workflow before re-reviewing until no high or mid findings remain.

- Package id: `cursor-cli-recent-change-quality-loop`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-recent-change-quality-loop`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-recent-change-quality-loop --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-recent-change-quality-loop --local-path /path/to/riela-packages
riela package install cursor-cli-design-and-implement-review-loop --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect cursor-cli-recent-change-quality-loop --output json
riela workflow validate cursor-cli-recent-change-quality-loop
riela workflow run cursor-cli-recent-change-quality-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
