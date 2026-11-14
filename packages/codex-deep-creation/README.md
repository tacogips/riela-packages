# codex-deep-creation

Run deep design, adversarial implementation-plan completion, and source security checks as one Codex creation workflow.

- Package id: `codex-deep-creation`
- Backends: `codex-agent`
- Workflows: `codex-deep-creation`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-deep-creation --source /path/to/riela-packages/packages/codex-deep-creation
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-deepdesign --source /path/to/riela-packages/packages/codex-deepdesign
riela package install codex-impl-plan-completion-loop --source /path/to/riela-packages/packages/codex-impl-plan-completion-loop
riela package install codex-source-security-check-loop --source /path/to/riela-packages/packages/codex-source-security-check-loop
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect codex-deep-creation --output json
riela workflow validate codex-deep-creation
riela workflow run codex-deep-creation --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
