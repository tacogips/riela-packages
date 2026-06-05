---
name: rielflow-package-installer
description: Use when bootstrapping the rielflow-package package-management skill from the tacogips/rielflow-packages registry into project or user scope.
user-invocable: true
---

# Rielflow Package Installer

Use this skill when the user wants to install the `rielflow-package` skill from
the `tacogips/rielflow-packages` registry.

This is a bootstrap skill. Its target package is:

```text
rielflow-package-manager-skill
```

Registry:

```text
https://github.com/tacogips/rielflow-packages
```

## Install

Default to project scope:

```bash
rielflow package install rielflow-package-manager-skill \
  --registry https://github.com/tacogips/rielflow-packages \
  --pre-install-check \
  --output json
```

Use user scope only when the user asks for a user-wide skill:

```bash
rielflow package install rielflow-package-manager-skill \
  --registry https://github.com/tacogips/rielflow-packages \
  --user-scope \
  --pre-install-check \
  --output json
```

## Existing Installs

If installation reports a duplicate, inspect before replacing:

```bash
rielflow package list --scope auto --output json
rielflow package status rielflow-package-manager-skill --output json
```

Use `--overwrite` only when the user explicitly asks to replace the installed
package.

## Verify

Report:

- install scope
- package id
- registry URL
- pre-install check result
- projected skill paths from the install JSON

Expected installed skills include `rielflow-package` for Codex and Claude when
the package manager projects both vendors.
