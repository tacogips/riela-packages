# codex-impl-plan-completion-review-loop

Run the Codex implementation-plan completion loop, then run the recent-change quality review-and-improve loop against the resulting work.

- Package id: `codex-impl-plan-completion-review-loop`
- Backends: `codex-agent`
- Workflows: `codex-impl-plan-completion-review-loop`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-impl-plan-completion-review-loop --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-impl-plan-completion-loop --local-path /path/to/riela-packages
riela package install codex-recent-change-quality-loop --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect codex-impl-plan-completion-review-loop --output json
riela workflow validate codex-impl-plan-completion-review-loop
riela workflow run codex-impl-plan-completion-review-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
