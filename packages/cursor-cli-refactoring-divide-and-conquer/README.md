# cursor-cli-refactoring-divide-and-conquer

Review codebase slices concurrently, build a dependency-aware refactoring DAG, implement disjoint ready tasks in shared-workspace waves, and reconcile each wave.

- Package id: `cursor-cli-refactoring-divide-and-conquer`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-refactoring-divide-and-conquer`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-refactoring-divide-and-conquer --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-refactoring-divide-and-conquer --local-path /path/to/riela-packages
riela package install cursor-cli-refactoring-slice-review --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect cursor-cli-refactoring-divide-and-conquer --output json
riela workflow validate cursor-cli-refactoring-divide-and-conquer
riela workflow run cursor-cli-refactoring-divide-and-conquer --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.

This variant inherits the compact 6-step graph from codex-refactoring-divide-and-conquer. Author self-checks run within authoring steps; independent review gates and revision routes remain separate.
