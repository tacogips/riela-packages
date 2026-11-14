# codex-deep-creation

Run deep design, adversarial implementation-plan completion, and source security checks as one Codex creation workflow.

- Package id: `codex-deep-creation`
- Backends: `codex-agent`
- Workflows: `codex-deep-creation`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-deep-creation --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-deepdesign --local-path /path/to/riela-packages
riela package install codex-impl-plan-completion-loop --local-path /path/to/riela-packages
riela package install codex-source-security-check-loop --local-path /path/to/riela-packages
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
