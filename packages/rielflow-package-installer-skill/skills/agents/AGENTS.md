# Rielflow Package Installer

Use this instruction when the user wants to bootstrap the `rielflow-package`
skill from the `tacogips/rielflow-packages` registry.

The target package is:

```text
rielflow-package-manager-skill
```

The registry is:

```text
https://github.com/tacogips/rielflow-packages
```

## Install

Prefer project scope unless the user asks for user-wide installation:

```bash
rielflow package install rielflow-package-manager-skill \
  --registry https://github.com/tacogips/rielflow-packages \
  --pre-install-check \
  --output json
```

User scope:

```bash
rielflow package install rielflow-package-manager-skill \
  --registry https://github.com/tacogips/rielflow-packages \
  --user-scope \
  --pre-install-check \
  --output json
```

## Verify

After installation, report the projected skill paths from the install JSON.
Expected skills include:

- `.codex/skills/rielflow-package` for Codex-capable installs
- `.claude/skills/rielflow-package` for Claude-capable installs

Also run:

```bash
rielflow package status rielflow-package-manager-skill --output json
```

Do not use `--overwrite` unless the user explicitly asks to replace an existing
installation.
