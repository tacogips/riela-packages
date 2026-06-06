---
name: rielflow-package-release
description: Use when maintaining a rielflow-packages registry for package updates, release preparation, publishing registry changes, refreshing rielflow-package.json checksum and integrity digests, validating packaged workflows, updating README package listings, or doing pre-push release checks for packages under packages/*.
---

# Rielflow Package Release

Use this skill in a `rielflow-packages` registry checkout when preparing
package updates for commit, push, or release. This is maintainer-facing; for
installing or updating a package as an end user, use `rielflow-package`.

## Standard Workflow

Package roots live under filesystem-safe `packages/<package-id>` directories.
The registry-visible package id in `rielflow-package.json.name` may be
unscoped or npm-style scoped, for example
`@tacogips/youtube-mp4-download-addon`; prefer scoped ids for third-party or
personal registries. Node add-on package entries use a separate add-on
namespace in `addons[].name`, for example
`tacogips/youtube-mp4-download`. The `rielflow/` add-on namespace is reserved
for built-ins.

1. Inspect the intended release scope:

```bash
git status --short
git diff --stat
git diff -- packages/<package-id>
```

2. Refresh package digests after changing a workflow, packaged skill, prompt,
   script, or package payload:

```bash
bun .rielflow/workflows/rielflow-package-release-skill/scripts/update-package-digests.ts <package-id>
```

For broad changes:

```bash
bun .rielflow/workflows/rielflow-package-release-skill/scripts/update-package-digests.ts --all
```

3. Validate package metadata and workflows:

```bash
task check
```

4. Update `README.md` package listings when package inventory, descriptions,
   tags, backends, or skill vendors change.

5. Before commit or push, review intended content for credentials, private
   URLs, and machine-local absolute paths.

## Notes

- The local rielflow source checkout is expected at `../rielflow` unless
  `RIELFLOW_ROOT` is set.
- `kind: "node-addon"` packages are skipped by the digest script; validate them
  through `task package:check-digests`.
- For project-scope installs, this package also projects broad maintainer
  guidance to `AGENTS.md`; the named Codex skill remains available under
  `.codex/skills/rielflow-package-release`.
