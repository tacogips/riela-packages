# cursor-cli-deepdesign

Create design-doc specifications, review deep, broad, and adversarial lenses concurrently with bounded read-only fanout, reduce findings, and revise until accepted.

- Package id: `cursor-cli-deepdesign`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-deepdesign`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-deepdesign --source /path/to/riela-packages/packages/cursor-cli-deepdesign
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-deepdesign --source /path/to/riela-packages/packages/codex-deepdesign
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
