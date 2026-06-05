# Rielflow Package Release

Use this instruction in a `rielflow-packages` registry checkout when preparing
package updates for commit, push, or release. This is maintainer-facing; for
installing or updating a package as an end user, use `rielflow-package`.

## Repository Assumptions

- Run commands from the repository root.
- Package roots live at `packages/<package-id>`.
- Each package has `rielflow-package.json`.
- The local rielflow source checkout is expected at `../rielflow` unless
  `RIELFLOW_ROOT` is set.
- `bun` and `task` should be available; `flake.nix` includes `go-task`.

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
bun .rielflow/workflows/rielflow-package-release-skill/scripts/update-package-digests.ts <package-id>
```

For broad changes or after moving shared packaged skills, refresh every
manifest:

```bash
bun .rielflow/workflows/rielflow-package-release-skill/scripts/update-package-digests.ts --all
```

Use `--dry-run` first when you only need to see stale manifests.

3. Validate package metadata and workflows:

```bash
task check
```

This runs digest checks for every package and validates all packaged workflows
with cross-workflow callees visible.

4. If package names, descriptions, tags, backends, or package inventory changed,
   update `README.md` package listings and verify the table still matches
   `packages/*/rielflow-package.json`.

5. Review install-facing behavior for changed packages:

```bash
bun run "${RIELFLOW_ROOT:-../rielflow}/packages/rielflow/src/bin.ts" package search "<package-id>" --registry default --refresh --output json
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

`kind: "node-addon"` packages are skipped by this script until rielflow exposes
a generic non-workflow package digest API. Validate node-addon structure through
`task package:check-digests`.

Examples:

```bash
bun .rielflow/workflows/rielflow-package-release-skill/scripts/update-package-digests.ts codex-design-and-implement-review-loop
bun .rielflow/workflows/rielflow-package-release-skill/scripts/update-package-digests.ts --all --dry-run
RIELFLOW_ROOT=/path/to/rielflow bun .rielflow/workflows/rielflow-package-release-skill/scripts/update-package-digests.ts --all
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
