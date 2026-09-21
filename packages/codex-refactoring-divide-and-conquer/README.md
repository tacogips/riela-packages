# codex-refactoring-divide-and-conquer

Divide the codebase into slices, review concurrently, build a dependency-aware refactoring task DAG, implement ready disjoint tasks in shared-workspace waves, reconcile and review each wave, and repeat until complete.

- Package id: `codex-refactoring-divide-and-conquer`
- Backends: `codex-agent`
- Workflows: `codex-refactoring-divide-and-conquer`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-refactoring-divide-and-conquer --local-path /path/to/riela-packages
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
riela workflow inspect codex-refactoring-divide-and-conquer --output json
riela workflow validate codex-refactoring-divide-and-conquer
riela workflow run codex-refactoring-divide-and-conquer --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.

The compact graph has 6 steps. Implementation uses GPT-5.6 SOL low effort and includes a bounded author self-check. The independent post-refactor review uses SOL medium effort and routes only material security, functionality, data-integrity, regression, scope, or severe code-quality findings back to implementation; speculative optimization and overengineering are excluded.
