# cursor-cli-hydra-codex-design-and-implement-review-loop

Explicit hydra workflow variant that uses Codex GPT-5.6 SOL for design, review, and all non-implementation agent steps, while using Cursor Composer 2.5 for implementation.

- Package id: `cursor-cli-hydra-codex-design-and-implement-review-loop`
- Backends: `codex-agent`, `cursor-cli-agent`
- Workflows: `cursor-cli-hydra-codex-design-and-implement-review-loop`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-hydra-codex-design-and-implement-review-loop --local-path /path/to/riela-packages
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
riela workflow inspect cursor-cli-hydra-codex-design-and-implement-review-loop --output json
riela workflow validate cursor-cli-hydra-codex-design-and-implement-review-loop
riela workflow run cursor-cli-hydra-codex-design-and-implement-review-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
