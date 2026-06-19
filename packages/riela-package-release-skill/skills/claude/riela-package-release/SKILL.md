---
name: riela-package-release
description: Use when maintaining a riela-packages registry for package updates, release preparation, publishing registry changes, refreshing riela-package.json checksum and integrity digests, validating packaged workflows, updating README package listings, or doing pre-push release checks for packages under packages/*.
---

# Riela Package Release

Use this skill in a `riela-packages` registry checkout when preparing
package updates for commit, push, or release. This is maintainer-facing; for
installing or updating a package as an end user, use `riela-package`.

## Repository Assumptions

- Run commands from the repository root.
- Package roots live at `packages/<package-id>`.
- Each package has `riela-package.json`.
- Directory names under `packages/` should be filesystem-safe. The package id
  in `riela-package.json.name` may be unscoped or npm-style scoped, for
  example `@tacogips/youtube-mp4-download-addon`; prefer scoped ids for
  third-party or personal registries.
- Node add-on package entries use a separate add-on namespace in
  `addons[].name`, for example `tacogips/youtube-mp4-download`. The
  `riela/` add-on namespace is reserved for built-ins.
- The local riela source checkout is expected at `../riela` unless
  `RIELA_ROOT` is set.
- `bun`, `task`, and the local Swift Riela checkout should be available.

## Standard Workflow

1. Inspect the intended release scope:

```bash
git status --short
git diff --stat
git diff -- packages/<package-id>
```

2. If a workflow, packaged skill, prompt, script, or package payload changed,
   refresh package digests:

```bash
bun .riela/workflows/riela-package-release-skill/scripts/update-package-digests.ts <package-id>
```

For broad changes or after moving shared packaged skills, refresh every
manifest:

```bash
bun .riela/workflows/riela-package-release-skill/scripts/update-package-digests.ts --all
```

Use `--dry-run` first when you only need to see stale manifests.

3. Validate package metadata and workflows:

```bash
task check
```

This runs digest checks for every package, validates every package manifest
with the Swift Riela decoder, and validates concrete packaged workflows with
cross-workflow callees visible. Workflows that only extend another workflow are
covered by package validation and skipped during direct workflow validation.

4. If package names, descriptions, tags, backends, or package inventory changed,
   update `README.md` package listings and verify the table still matches
   `packages/*/riela-package.json`.

5. Review install-facing behavior for changed packages:

```bash
swift run --package-path "${RIELA_ROOT:-../riela}" riela package search "<package-id>" --registry default --output json
```

For workflow packages, also verify the workflow can be inspected or validated
from the package payload when relevant.

6. Before commit or push, run a commit-target safety review. Check only staged
   or intended content for real credentials, private URLs, and machine-local
   absolute paths.

## Digest Script

`scripts/update-package-digests.ts` recomputes workflow package digests:

- `checksum` using `computeWorkflowPackageChecksum`
- `integrity.digest` using `computeWorkflowPackageIntegrityDigest`
- `checksumAlgorithm: "md5"`
- `integrity.digestAlgorithm: "sha256"`

`kind: "node-addon"` packages are included by this script. Their package-level
checksum and integrity digest cover the package payload, while add-on
`contentDigest` values remain explicit add-on artifact locks.

Examples:

```bash
bun .riela/workflows/riela-package-release-skill/scripts/update-package-digests.ts codex-design-and-implement-review-loop
bun .riela/workflows/riela-package-release-skill/scripts/update-package-digests.ts --all --dry-run
RIELA_ROOT=/path/to/riela bun .riela/workflows/riela-package-release-skill/scripts/update-package-digests.ts --all
```

If `--dry-run` finds stale manifests, it exits non-zero and reports the fields
that would change.

## Release Readiness

Treat a package update as release-ready only when:

- package manifests are refreshed and `task package:check-digests` passes
- packaged workflows validate through `task workflow:validate`
- generated or packaged skills still have valid `SKILL.md` frontmatter and
  matching `agents/openai.yaml`
- `README.md` reflects any package inventory or metadata changes
- `git diff --cached` has been safety-reviewed before commit
- the final branch is pushed to the registry branch that consumers use,
  normally `main`

## Reporting

Report the changed package ids, refreshed digest fields, validation commands and
results, commit id, and pushed branch. If validation cannot run, state the
missing dependency or failing command exactly.
