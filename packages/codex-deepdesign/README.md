# codex-deepdesign

Create and iteratively review design-doc specifications with one Codex author, one deep edge-case reviewer, and one broad integration reviewer until no high or middle findings remain.

- Package id: `codex-deepdesign`
- Backends: `codex-agent`
- Workflows: `codex-deepdesign`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-deepdesign --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect codex-deepdesign --output json
riela workflow validate codex-deepdesign
riela workflow run codex-deepdesign --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
