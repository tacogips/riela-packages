# cursor-cli-simple-work-package

Lightweight Cursor CLI workflow for small code or documentation changes when no dedicated workflow applies. It implements with Cursor CLI Sonnet 4.5 high effort, reviews the diff, and loops back only for high or middle findings.

- Package id: `cursor-cli-simple-work-package`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-simple-work-package`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-simple-work-package --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-simple-work-package --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect cursor-cli-simple-work-package --output json
riela workflow validate cursor-cli-simple-work-package
riela workflow run cursor-cli-simple-work-package --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
