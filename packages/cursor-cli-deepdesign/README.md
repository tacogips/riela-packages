# cursor-cli-deepdesign

Create and iteratively review design-doc specifications with one Cursor CLI author, one deep edge-case reviewer, and one broad integration reviewer until no high or middle findings remain.

- Package id: `cursor-cli-deepdesign`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-deepdesign`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-deepdesign --local-path /path/to/riela-packages
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
riela workflow inspect cursor-cli-deepdesign --output json
riela workflow validate cursor-cli-deepdesign
riela workflow run cursor-cli-deepdesign --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
