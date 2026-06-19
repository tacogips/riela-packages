---
name: riela-package
description: Use when searching, installing, listing, updating, or removing riela workflow packages through the riela package manager. Covers local source installs, project-scope installs, user-scope installs, installed package verification, and package-installed skills.
metadata:
  short-description: Search and install riela packages
---

# Riela Package

Use this skill when the user wants to find or install a riela package. Riela packages are Git-backed workflow bundles and may also install agent skills.

For raw public GitHub workflow directory URLs, use `riela-workflow-checkout` instead.

## Command

When `riela` is installed, prefer local package sources:

```bash
find <riela-packages-checkout>/packages -mindepth 1 -maxdepth 1 -type d -name "*<query>*"
riela package install <package-id> --source <riela-packages-checkout>/packages/<package-id>
```

Inside the riela source checkout, prefer:

```bash
find ../riela-packages/packages -mindepth 1 -maxdepth 1 -type d -name "*<query>*"
riela package install <package-id> --source ../riela-packages/packages/<package-id>
```

Default local package checkout:

```text
~/gits/tacogips/riela-packages
```

## Standard Workflow

1. Search local package directories before installing unless the package id is already explicit:

```bash
find ~/gits/tacogips/riela-packages/packages -mindepth 1 -maxdepth 1 -type d -name "*<keyword>*"
```

If the package id is known, derive the source path directly:

```bash
package_id="<package-id>"
package_source="$HOME/gits/tacogips/riela-packages/packages/$package_id"
```

2. Pick the package id from the matching directory name. If search results are empty, report that no matching package was found and include the query used.

3. Choose install scope:
   - Project scope is the default for project-local workflow and skill use.
   - User scope is for user-wide reusable packages and skills; use `--scope user`.
   - Use `--project-root <path>` or `--user-root <path>` only when the destination root must be explicit.

4. Install the package:

```bash
riela package install <package-id> --source <package-dir> --output json
```

User scope:

```bash
riela package install <package-id> --source <package-dir> --scope user --output json
```

5. Verify the install:

```bash
riela package list --scope project --output json
riela package list --scope user --output json
riela package status <workflow-name-or-package-id> --output json
```

For installed workflow packages, also run:

```bash
riela workflow validate <workflow-name>
riela workflow usage <workflow-name>
```

For skill packages, inspect the install JSON `skills` array and report projected
paths such as `AGENTS.md`, `.codex/skills/<name>/SKILL.md`,
`.claude/skills/<name>/SKILL.md`, `.cursor/rules/<name>.mdc`,
`~/.codex/skills/<name>/SKILL.md`, `~/.claude/skills/<name>/SKILL.md`, or
`~/.cursor/skills/<name>/SKILL.md`. User-scope `skills/agents/AGENTS.md`
entries are managed-only and do not create root `AGENTS.md`.

## Duplicates And Updates

- Duplicate package installs fail unless `--overwrite` is used. Use `--overwrite` only when the user explicitly wants replacement.
- Use `package list --output json` to find `installId` when multiple records may match.
- Remove by install id when identity is ambiguous:

```bash
riela package remove --install-id <install-id>
```

- Update an installed package:

```bash
riela package update <workflow-name-or-package-id> --yes --output json
```

## Registry Commands

List registries:

```bash
riela package registry list --output json
```

Register another registry:

```bash
riela package registry add <id> --registry-url <url> --local-path <path> --branch <branch>
```

## Reporting

Report the selected package id, source path, scope, workflow name, destination, checksum/content digest, and installed skills. If an install was skipped or failed, include the exact package command and the failure message.
