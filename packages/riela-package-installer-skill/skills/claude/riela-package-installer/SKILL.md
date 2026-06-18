---
name: riela-package-installer
description: Use when bootstrapping the riela-package package-management skill from the tacogips/riela-packages registry into project or user scope.
user-invocable: true
---

# Riela Package Installer

Use this skill when the user wants to install the `riela-package` skill from
the `tacogips/riela-packages` registry.

This is a bootstrap skill. Its target package is:

```text
riela-package-manager-skill
```

Registry:

```text
https://github.com/tacogips/riela-packages
```

## Install

Default to project scope:

```bash
riela package install riela-package-manager-skill \
  --registry https://github.com/tacogips/riela-packages \
  --pre-install-check \
  --output json
```

Use user scope only when the user asks for a user-wide skill:

```bash
riela package install riela-package-manager-skill \
  --registry https://github.com/tacogips/riela-packages \
  --user-scope \
  --pre-install-check \
  --output json
```

## Existing Installs

If installation reports a duplicate, inspect before replacing:

```bash
riela package list --scope auto --output json
riela package status riela-package-manager-skill --output json
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

Expected installed skills include `riela-package` for Claude and Codex when
the package manager projects both vendors.
