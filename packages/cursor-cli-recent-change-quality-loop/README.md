# cursor-cli-recent-change-quality-loop

Inventory recent changes, review independent slices concurrently with bounded read-only fanout, reduce findings, and delegate blocking fixes until accepted.

- Package id: `cursor-cli-recent-change-quality-loop`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-recent-change-quality-loop`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-recent-change-quality-loop --source /path/to/riela-packages/packages/cursor-cli-recent-change-quality-loop
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-recent-change-quality-loop --source /path/to/riela-packages/packages/codex-recent-change-quality-loop
riela package install cursor-cli-design-and-implement-review-loop --source /path/to/riela-packages/packages/cursor-cli-design-and-implement-review-loop
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
