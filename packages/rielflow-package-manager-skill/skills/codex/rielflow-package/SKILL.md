---
name: rielflow-package
description: Use when searching, installing, listing, updating, or removing rielflow workflow packages through the rielflow package manager. Covers package search, registry refresh, project-scope installs, user-scope installs, installed package verification, and package-installed skills.
metadata:
  short-description: Search and install rielflow packages
---

# Rielflow Package

Use this skill when the user wants to find or install a rielflow registry package. Rielflow packages are Git-backed workflow bundles and may also install agent skills.

For raw public GitHub workflow directory URLs, use `rielflow-workflow-checkout` instead.

## Command

When `rielflow` is installed, prefer:

```bash
rielflow package search "<query>" --refresh
rielflow package install <package-id>
```

Inside the rielflow source checkout, prefer:

```bash
bun run packages/rielflow/src/bin.ts package search "<query>" --refresh
bun run packages/rielflow/src/bin.ts package install <package-id>
```

Default registry:

```text
https://github.com/tacogips/rielflow-packages
```

## Standard Workflow

1. Search before installing unless the package id is already explicit:

```bash
rielflow package search "<keyword>" --refresh --output json
```

Useful filters:

```bash
rielflow package search "<keyword>" --tag <tag> --backend <backend> --limit <n> --output json
rielflow package search "<keyword>" --registry <id-or-url> --refresh --output json
```

2. Pick the package id from `packages[].packageId` or `records[].packageName`. If search results are empty, run once with `--refresh` before reporting no match.

3. Choose install scope:
   - Project scope is the default for project-local workflow and skill use.
   - User scope is for user-wide reusable packages and skills; use `--user-scope`.
   - Use `--project-root <path>` or `--user-root <path>` only when the destination root must be explicit.

4. Install with pre-install checks when package contents may execute or install skills:

```bash
rielflow package install <package-id> --pre-install-check --output json
```

User scope:

```bash
rielflow package install <package-id> --user-scope --pre-install-check --output json
```

Strict pre-install checks:

```bash
rielflow package install <package-id> --pre-install-check --pre-install-check-mode reject --output json
```

5. Verify the install:

```bash
rielflow package list --scope project --output json
rielflow package list --scope user --output json
rielflow package status <workflow-name-or-package-id> --output json
```

For installed workflow packages, also run:

```bash
rielflow workflow validate <workflow-name>
rielflow workflow usage <workflow-name>
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
rielflow package remove --install-id <install-id>
```

- Update an installed package:

```bash
rielflow package update <workflow-name-or-package-id> --yes --output json
```

## Registry Commands

List registries:

```bash
rielflow package registry list --output json
```

Register another registry:

```bash
rielflow package registry add <id> --registry-url <url> --local-path <path> --branch <branch>
```

## Reporting

Report the selected package id, registry, scope, workflow name, destination, checksum/content digest, pre-install check status, and installed skills. If an install was skipped or failed, include the exact package command and the failure message.
