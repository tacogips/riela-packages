# cursor-cli-source-security-check-loop

Run deterministic security checks, partition the attack surface, review focus areas concurrently, reduce and adversarially verify findings, then delegate blocking fixes.

- Package id: `cursor-cli-source-security-check-loop`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-source-security-check-loop`
- Skills: Cursor

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-source-security-check-loop --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-source-security-check-loop --local-path /path/to/riela-packages
riela package install cursor-cli-design-and-implement-review-loop --local-path /path/to/riela-packages
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect cursor-cli-source-security-check-loop --output json
riela workflow validate cursor-cli-source-security-check-loop
riela workflow run cursor-cli-source-security-check-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
