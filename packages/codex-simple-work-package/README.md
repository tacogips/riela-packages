# codex-simple-work-package

Lightweight Codex workflow for small code or documentation changes when no dedicated workflow applies. It implements with Codex GPT-5.6 SOL high effort, reviews the diff, and loops back only for high or middle findings.

- Package id: `codex-simple-work-package`
- Backends: `codex-agent`
- Workflows: `codex-simple-work-package`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-simple-work-package --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect codex-simple-work-package --output json
riela workflow validate codex-simple-work-package
riela workflow run codex-simple-work-package --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
