# claude-code-deepdesign

Create design-doc specifications, review deep, broad, and adversarial lenses concurrently with bounded read-only fanout, reduce findings, and revise until accepted.

- Package id: `claude-code-deepdesign`
- Backends: `claude-code-agent`
- Workflows: `claude-code-deepdesign`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install claude-code-deepdesign --source /path/to/riela-packages/packages/claude-code-deepdesign
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
riela workflow inspect claude-code-deepdesign --output json
riela workflow validate claude-code-deepdesign
riela workflow run claude-code-deepdesign --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
