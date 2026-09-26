---
name: riela-auto-improve
description: Use when migrating or troubleshooting workflows that still mention the removed Riela auto-improve supervision flags.
metadata:
  short-description: Migrate retired auto-improve usage
---

# Riela Auto Improve Migration

Riela 0.2.0 removed the engine-owned auto-improve mode. Do not pass
`--auto-improve`, `--nested-supervisor`, `--max-supervised-attempts`, or
`--workflow-mutation-mode` to current CLI commands. There is no direct
automatic-recovery replacement.

For a long-running workflow, use:

```bash
riela workflow run <workflow-name> --output jsonl
riela session progress <session-id>
riela session status <session-id> --output json
```

Keep the session id from the JSONL stream. Diagnose any failure using recorded
step evidence; then explicitly use `session resume` or `session rerun` if
safe. Do not claim that `--supervisor-mode` restores auto-improve: it only
changes how Codex agents may use subagents.

Read `references/auto-improve.md` for a concise migration map.
