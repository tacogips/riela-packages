---
name: rielflow-fix
description: Use when a rielflow workflow, CLI command, GraphQL control plane, event listener, package-installed workflow, user-scope workflow, project-scope workflow, or workflow-definition-dir run appears to fail because of an upstream rielflow or rielflow-package bug. Covers triage, issue creation, source checkout selection, fixes, validation, and commits.
---

# Rielflow Fix Workflow

Use this skill when work in this repository indicates that `rielflow` itself may be wrong, incomplete, or misaligned with its documented behavior.

## Source Boundary

First decide what is broken:

- If the defect is in a packaged workflow, node add-on, prompt, or package-installed skill, fix the package source repository, usually `tacogips/rielflow-packages`.
- If the defect is in CLI behavior, package installation, workflow resolution, GraphQL, events, runtime state, or shared engine code, fix `tacogips/rielflow`.
- If the defect is only the caller repository's Nix/Home Manager/task integration, fix that repository and do not file an upstream issue.

Do not require a `./rielflow` submodule. Use the best available runner for reproduction, in this order:

1. A repository-local rielflow source checkout when present, such as `./rielflow`, the current directory when it is the rielflow checkout, or an explicit user-provided source path.
2. The project-scope installed workflow under the current repository.
3. The user-scope installed workflow, with `--scope user` or `--user-root` when needed.
4. A direct workflow bundle with `--workflow-definition-dir <dir>` when the user points to unpacked workflow directories.
5. The installed `rielflow` binary for diagnosis or comparison when no local source checkout is available.

For source edits, work in the owning source checkout. If no source checkout is available, create the issue with reproduction evidence and report that implementation is blocked on a local checkout.

Preferred commands:

```bash
task rielflow -- <args>                         # parent repo wrapper when available
bun run packages/rielflow/src/bin.ts <args>     # from a rielflow monorepo checkout
bun run src/main.ts <args>                      # from a rielflow package checkout exposing src/main.ts
rielflow <args>                                 # installed binary for reproduction/comparison
```

## Triage

1. Reproduce the failure with the most relevant runner and scope. Preserve the exact command, including `--scope`, `--user-root`, `--project-root`, or `--workflow-definition-dir` flags.
2. Check whether the affected workflow came from package install, raw workflow checkout, project scope, user scope, or an explicit workflow directory:
   - `rielflow package status <package-or-workflow> --scope project --output json`
   - `rielflow package status <package-or-workflow> --scope user --output json`
   - `rielflow workflow usage <workflow> --scope project`
   - `rielflow workflow usage <workflow> --scope user`
   - `rielflow workflow validate <workflow> --workflow-definition-dir <dir>`
3. Determine whether the fault is in caller integration, `tacogips/rielflow`, or `tacogips/rielflow-packages`.
4. If the fault is integration-only, fix this repository and do not file an upstream issue.
5. If the fault is upstream, collect expected behavior, actual behavior, environment details, relevant package/workflow provenance, and logs.

## Upstream Issue

When the fault is in `rielflow`, create an issue in `tacogips/rielflow` before or alongside the fix:

```bash
gh issue create --repo tacogips/rielflow --title "<concise bug title>" --body-file <issue-body-file>
```

The issue body should include:

- Reproduction steps using the exact runner and scope that failed.
- Expected behavior and actual behavior.
- Environment details that affect execution, such as Bun, Nix, OS, package install scope, workflow root, and relevant command flags.
- Links or paths to affected workflow fixtures when they are safe to reference.

If `gh` is unavailable or authentication fails, write the issue body to a temporary markdown file, report the blocker, and continue only if the requested fix can still be validated locally.

## Source Fix

1. Work inside the owning source checkout: `tacogips/rielflow` for engine/CLI bugs, or `tacogips/rielflow-packages` for packaged workflow, prompt, add-on, or skill bugs.
2. Follow that checkout's `AGENTS.md` and implementation-plan requirements when present.
3. Keep fixes minimal and covered by targeted tests.
4. Run the smallest meaningful validation first, then broader checks when practical:
   - `bun test <targeted-test>`
   - `bun run typecheck`
   - `task ci`
   - `task check`
   - `rielflow workflow validate <workflow> --scope project|user`
   - `rielflow workflow validate <workflow> --workflow-definition-dir <dir>`
5. Commit the source fix with no automated-assistant attribution or co-authorship trailers.
6. If the caller repository tracks the fixed source by submodule, flake input, package lock, or vendored files, update and commit that pointer separately.

## Reporting

In the final response, include the issue URL or issue creation blocker, the source repository and commit hash when a fix was made, any caller repository pointer updated, and validation commands that passed or could not be run.
