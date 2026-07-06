# cursor-cli-refactoring-slice-review

Read-only review workflow for one codebase slice produced by cursor-cli-refactoring-divide-and-conquer fanout, including duplicate-scavenge review when the parent workflow requests duplicate implementations or parallel custom implementations of the same concept.

- Package id: `cursor-cli-refactoring-slice-review`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-refactoring-slice-review`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-refactoring-slice-review --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-refactoring-slice-review --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect cursor-cli-refactoring-slice-review --output json
riela workflow validate cursor-cli-refactoring-slice-review
riela workflow run cursor-cli-refactoring-slice-review --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
