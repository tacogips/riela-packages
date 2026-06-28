---
name: riela-package
description: Use when searching, installing, listing, updating, removing, validating, packing, or importing riela workflow packages through the riela package manager and RielaApp package flows. Covers local source installs, .rielapkg archives, project-scope installs, user-scope installs, installed package verification, package-required environment metadata, and package-installed skills.
metadata:
  short-description: Search and install riela packages
---

# Riela Package

Use this skill when the user wants to find, install, inspect, validate, pack, or use a riela package. Riela packages are local package directories or `.rielapkg` archives that can provide workflows, node add-ons, and agent skills.

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
riela package search <keyword> --output json
```

If the package id is known, derive the source path directly:

```bash
package_id="<package-id>"
package_source="$HOME/gits/tacogips/riela-packages/packages/$package_id"
```

2. Pick the package id from the matching directory name or `riela package search` result. Search matches package ids and manifest tags. If search results are empty, report that no matching package was found and include the query used.

3. Choose install scope:
   - Project scope is the default for project-local workflow and skill use.
   - User scope is for user-wide reusable packages and skills; use `--scope user`.
   - Use `--working-dir <path>` when project-scope installation should target a project other than the current working directory.

4. Install the package:

```bash
riela package install <package-id> --source <package-dir> --output json
```

User scope:

```bash
riela package install <package-id> --source <package-dir> --scope user --output json
```

For a package archive:

```bash
riela package install <package-id> --source <package-archive>.rielapkg --output json
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

If the package manifest has `environmentVariables`, report the required names
and whether they are configured when that is visible from the surface you are
using. In RielaApp, select the package-backed workflow to see `set`/`missing`
status and use `Set Env...` to write values to `~/.riela/rielaapp.env`.

For skill packages, inspect the install JSON `skills` array and report projected
paths such as `AGENTS.md`, `.codex/skills/<name>/SKILL.md`,
`.claude/skills/<name>/SKILL.md`, `.cursor/rules/<name>.mdc`,
`~/.codex/skills/<name>/SKILL.md`, `~/.claude/skills/<name>/SKILL.md`, or
`~/.cursor/skills/<name>/SKILL.md`. User-scope `skills/agents/AGENTS.md`
entries are managed-only and do not create root `AGENTS.md`.

## Duplicates, Updates, And Removal

- Duplicate package installs fail unless `--overwrite` is used. Use `--overwrite` only when the user explicitly wants replacement.
- Update an installed package after explicit approval:

```bash
riela package update <workflow-name-or-package-id> --yes --output json
```

- Remove an installed package by package id:

```bash
riela package remove <package-id> --output json
```

RielaApp profile availability is separate from package installation. Imported
workflow directories, package directories, and `.rielapkg` packages can be
disabled or enabled from the RielaApp Workflows window. Disable keeps the
profile import present but unavailable and stops auto-start; Enable makes the
selected disabled item available again.

## Package Metadata

When authoring or reviewing package manifests, use `environmentVariables` for
runtime values the package expects:

```json
"environmentVariables": [
  {"name": "RIELA_TELEGRAM_BOT_TOKEN", "description": "Telegram bot token", "secret": true},
  {"name": "RIELA_OPTIONAL_MODE", "required": false}
]
```

Names must be valid environment variable names. `required` defaults to `true`;
`secret` tells RielaApp to use a secure input field.

Package manifests must include top-level `tags`; workflow packages should also
include `workflow.tags` when the `workflow` metadata block is present. Use
short lowercase topic tags because `riela package search` matches tags as well
as package ids, and report package tags from JSON search/list/status output.

After editing package payload, refresh package digests before reporting the
package as ready.

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

Report the selected package id, tags, source path, scope, workflow name, destination, checksum/content digest, installed skills, and required environment variables. If an install, import, enable/disable, or validation step was skipped or failed, include the exact command or RielaApp action and the failure message.
