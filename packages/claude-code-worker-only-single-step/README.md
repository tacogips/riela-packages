# claude-code-worker-only-single-step

Minimal manager-less reference workflow that starts directly at one worker step through explicit entryStepId authoring.

- Package id: `claude-code-worker-only-single-step`
- Backends: `claude-code-agent`
- Workflows: `claude-code-worker-only-single-step`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install claude-code-worker-only-single-step --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect claude-code-worker-only-single-step --output json
riela workflow validate claude-code-worker-only-single-step
riela workflow run claude-code-worker-only-single-step --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
