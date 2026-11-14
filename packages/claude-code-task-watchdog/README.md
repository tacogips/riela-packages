# claude-code-task-watchdog

Long-running Claude Code task watcher backed by ./tasks/list.jsonl, with cron/event polling, dependency workflow dispatch, ad hoc Claude Code execution, post-task skill mining, skill review, and commit.

- Package id: `claude-code-task-watchdog`
- Backends: `claude-code-agent`
- Workflows: `claude-code-task-watchdog`
- Skills: Claude Code

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install claude-code-task-watchdog --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-task-watchdog --local-path /path/to/riela-packages
riela package install claude-code-design-and-implement-review-loop --local-path /path/to/riela-packages
riela package install claude-code-deepdesign --local-path /path/to/riela-packages
riela package install claude-code-recent-change-quality-loop --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect claude-code-task-watchdog --output json
riela workflow validate claude-code-task-watchdog
riela workflow run claude-code-task-watchdog --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
