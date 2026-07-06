# codex-refactoring-divide-and-conquer

Divide the codebase into package or related processing-group slices, review slices concurrently, merge findings into a refactoring plan, implement one bounded task at a time, self-review, independently post-review, and loop until the plan is complete or only accepted residual risks remain. Duplicate-scavenge is an additive mode of this same workflow; detailed phase behavior lives in the step prompts.

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
