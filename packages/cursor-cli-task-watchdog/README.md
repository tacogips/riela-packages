# cursor-cli-task-watchdog

Long-running Cursor CLI task watcher backed by ./tasks/list.jsonl, with cron/event polling, dependency workflow dispatch, ad hoc Cursor CLI execution, post-task skill mining, skill review, and commit.

- Package id: `cursor-cli-task-watchdog`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-task-watchdog`
- Skills: Cursor

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-task-watchdog --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-task-watchdog --local-path /path/to/riela-packages
riela package install cursor-cli-design-and-implement-review-loop --local-path /path/to/riela-packages
riela package install cursor-cli-deepdesign --local-path /path/to/riela-packages
riela package install cursor-cli-recent-change-quality-loop --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect cursor-cli-task-watchdog --output json
riela workflow validate cursor-cli-task-watchdog
riela workflow run cursor-cli-task-watchdog --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
