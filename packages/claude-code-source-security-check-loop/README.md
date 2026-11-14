# claude-code-source-security-check-loop

Run deterministic source-code security checks, derive harness-style focus areas, triage and adversarially verify findings with Claude Code, delegate blocking fixes, and rescan until verified high and medium findings are resolved.

- Package id: `claude-code-source-security-check-loop`
- Backends: `claude-code-agent`
- Workflows: `claude-code-source-security-check-loop`
- Skills: Claude Code

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install claude-code-source-security-check-loop --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-source-security-check-loop --local-path /path/to/riela-packages
riela package install claude-code-design-and-implement-review-loop --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect claude-code-source-security-check-loop --output json
riela workflow validate claude-code-source-security-check-loop
riela workflow run claude-code-source-security-check-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
