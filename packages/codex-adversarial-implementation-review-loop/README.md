# codex-adversarial-implementation-review-loop

Run a scoped Codex implementation request, adversarially review the implemented result, delegate blocking fixes, and repeat until no high or medium findings remain.

- Package id: `codex-adversarial-implementation-review-loop`
- Backends: `codex-agent`
- Workflows: `codex-adversarial-implementation-review-loop`

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-adversarial-implementation-review-loop --local-path /path/to/riela-packages
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
riela workflow inspect codex-adversarial-implementation-review-loop --output json
riela workflow validate codex-adversarial-implementation-review-loop
riela workflow run codex-adversarial-implementation-review-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
