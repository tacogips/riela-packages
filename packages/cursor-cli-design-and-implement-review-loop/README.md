# cursor-cli-design-and-implement-review-loop

Shared Cursor CLI workflow for issue resolution or planning-only design and implementation-plan handoff. The workflow owns both the sequential path and the bounded feature-local fanout path, then joins accepted plans before implementation or planning-only completion.

- Package id: `cursor-cli-design-and-implement-review-loop`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-design-and-implement-review-loop`
- Skills: Cursor

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-design-and-implement-review-loop --local-path /path/to/riela-packages
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
riela workflow inspect cursor-cli-design-and-implement-review-loop --output json
riela workflow validate cursor-cli-design-and-implement-review-loop
riela workflow run cursor-cli-design-and-implement-review-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
