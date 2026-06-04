# Implementation Plan: Greeting Node Add-on JSON Output Safety

Issue reference: `tacogips/rielflow-packages`, title `Self-review greeting executable node-addon package JSON output safety`. No GitHub issue URL or issue number was provided; this plan traces to runtimeVariables and the accepted design in `design-docs/specs/notes.md`.

Workflow mode: `issue-resolution`.

Codex-agent references: none supplied. No Cursor or external codex-agent behavior is part of this change.

## Source of Truth

- Accepted design: `design-docs/specs/notes.md`
- Target package: `packages/greeting-node-addon`
- Known must-fix finding: `packages/greeting-node-addon/addons/examples/greeting-shell/1/greeting.bash` builds JSON with `printf` interpolation and can emit invalid JSON for quotes, backslashes, tabs, or newlines.

## Tasks

1. Fix executable JSON emission.
   - File scope: `packages/greeting-node-addon/addons/examples/greeting-shell/1/greeting.bash`
   - Replace direct JSON `printf` interpolation with a real JSON encoder.
   - Preferred implementation: use `jq -n` with `--arg` for `greeting`, `greetingIndex`, `timezone`, and `timestamp`.
   - Fail before writing `output.json` when the encoder is unavailable or `date` fails.
   - Preserve the existing payload shape exactly: `greeting`, `greetingIndex`, `timezone`, `timestamp`.
   - Preserve existing timestamp behavior through `TZ="$timezone" date '+%Y-%m-%dT%H:%M:%S%z'`.

2. Reflect runtime dependency metadata if the implementation uses a new encoder.
   - File scope: `packages/greeting-node-addon/addons/examples/greeting-shell/1/addon.json`, `packages/greeting-node-addon/rielflow-package.json`
   - If `jq` is used, add `jq` to both `execution.runtimeHints` arrays while keeping `bash`.
   - Keep `execution`, `capabilities`, add-on name, version, and sourcePath aligned between `addon.json` and `rielflow-package.json`.

3. Refresh package metadata after payload changes.
   - File scope: `packages/greeting-node-addon/rielflow-package.json`
   - Refresh `addons[0].contentDigest` for allowed add-on files `addon.json` and `greeting.bash` using the node-addon digest algorithm from `../rielflow/packages/rielflow/src/workflow/packages/node-addon-install.ts`.
   - Refresh package `checksum` with `computeWorkflowNodeAddonPackageChecksum`.
   - Refresh `integrity.digest` with `computeWorkflowNodeAddonPackageIntegrityDigest`.
   - Keep `checksumAlgorithm: "md5"` and `integrity.digestAlgorithm: "sha256"`.

4. Self-review README scope.
   - File scope: `packages/greeting-node-addon/README.md`
   - Update only if the implementation adds an install-facing requirement that is not clear from current docs, such as a new `jq` runtime requirement or executable grant guidance.
   - Do not rewrite unrelated README sections.

5. Verify and prepare commit.
   - Run focused script smoke tests that include quotes, backslashes, tabs, and newlines.
   - Run an explicit node-addon metadata check that validates add-on contentDigest and package checksum/integrity; `task package:check-digests` currently checks node-addon structure but skips node-addon digest comparison.
   - Run install-facing search/install checks and a local Rielflow CLI smoke through an add-on-backed temporary workflow with a direct executable add-on grant.
   - Review `git diff` for package-local scope plus this plan/design only.
   - Commit changes under `commitPolicy=commit-no-push`; do not push unless a later workflow gate explicitly overrides the policy.

## Dependencies

- Step 3 accepted `design-docs/specs/notes.md`; implementation can proceed.
- `jq` must be available if selected as the JSON encoder; otherwise choose another real JSON encoder already available in the local runtime and update runtime hints accordingly.
- `bun`, `task`, and `../rielflow` are expected for digest and package verification.

## Parallelization

- Task 1 and Task 4 can be worked in parallel only after the JSON encoder choice is fixed, because write scopes are disjoint.
- Tasks 2 and 3 are dependent on Task 1 and cannot be safely parallelized with it.
- Task 5 depends on Tasks 1 through 4.

## Verification Commands

```bash
git status --short
```

```bash
tmp="$(mktemp -d)" && RIEL_MAILBOX_DIR="$tmp" GREETING_TIMEZONE=$'UTC "zone" \\ path\nnext' GREETING_INDEX=$'idx "quote" \\ slash\tTabbed\nline' bash packages/greeting-node-addon/addons/examples/greeting-shell/1/greeting.bash $'Ada "Lovelace" \\ path\tTabbed\nnext' && jq -e '.greeting == "Hello Ada \"Lovelace\" \\\\ path\tTabbed\nnext" and .greetingIndex == "idx \"quote\" \\\\ slash\tTabbed\nline" and .timezone == "UTC \"zone\" \\\\ path\nnext" and (.timestamp | type == "string")' "$tmp/outbox/output.json"
```

```bash
task package:check-digests
```

```bash
node_addon_check='
import { validateWorkflowPackageAddons } from "../rielflow/packages/rielflow/src/workflow/packages/node-addon-install.ts";
import { computeWorkflowNodeAddonPackageChecksum, computeWorkflowNodeAddonPackageIntegrityDigest } from "../rielflow/packages/rielflow/src/workflow/packages/checksum.ts";

const packageRoot = `${process.cwd()}/packages/greeting-node-addon`;
const manifest = await Bun.file(`${packageRoot}/rielflow-package.json`).json();
const artifacts = await validateWorkflowPackageAddons({ packageRoot, addons: manifest.addons });
if (!artifacts.ok) throw new Error(artifacts.error.message);
const contentDigest = artifacts.value[0]?.contentDigest;
const checksum = await computeWorkflowNodeAddonPackageChecksum({ packageRoot });
if (!checksum.ok) throw new Error(checksum.error.message);
const integrity = await computeWorkflowNodeAddonPackageIntegrityDigest({ packageRoot });
if (!integrity.ok) throw new Error(integrity.error.message);
if (manifest.addons[0]?.contentDigest !== contentDigest) throw new Error(`contentDigest mismatch: ${manifest.addons[0]?.contentDigest} !== ${contentDigest}`);
if (manifest.checksum !== checksum.value.checksum) throw new Error(`checksum mismatch: ${manifest.checksum} !== ${checksum.value.checksum}`);
if (manifest.integrity?.digest !== integrity.value.digest) throw new Error(`integrity digest mismatch: ${manifest.integrity?.digest} !== ${integrity.value.digest}`);
console.log(JSON.stringify({ contentDigest, checksum: checksum.value.checksum, integrityDigest: integrity.value.digest }, null, 2));
'
bun -e "$node_addon_check"
```

```bash
bun run "${RIELFLOW_ROOT:-../rielflow}/packages/rielflow/src/bin.ts" package search greeting-node-addon --registry default --refresh --kind node-addon --output json
```

```bash
bun run "${RIELFLOW_ROOT:-../rielflow}/packages/rielflow/src/bin.ts" package install greeting-node-addon --registry default --refresh --overwrite --yes --output json
```

```bash
tmp="$(mktemp -d)" && mkdir -p "$tmp/greeting-addon-smoke" && jq -n '{
  workflowId: "greeting-addon-smoke",
  description: "Temporary executable add-on smoke.",
  defaults: { maxLoopIterations: 1, nodeTimeoutMs: 120000 },
  entryStepId: "greeting",
  nodes: [{
    id: "greeting",
    addon: {
      name: "examples/greeting-shell",
      version: "1",
      inputs: {
        name: "{{workflowInput.name}}",
        greetingIndex: "{{workflowInput.greetingIndex}}",
        timezone: "{{workflowInput.timezone}}"
      }
    }
  }],
  steps: [{ id: "greeting", nodeId: "greeting", role: "worker" }]
}' > "$tmp/greeting-addon-smoke/workflow.json" && digest="$(jq -r '.addons[0].contentDigest' packages/greeting-node-addon/rielflow-package.json)" && grant="$(jq -n --arg digest "$digest" '{packageId:"greeting-node-addon",kind:"node-addon",addons:[{name:"examples/greeting-shell",version:"1",contentDigest:$digest,capabilityGrant:{"process.spawn":{allowed:true,scope:"addon.entrypoint"}}}]}')" && vars="$(jq -n --arg name $'Ada "Lovelace" \\ path\tTabbed\nnext' --arg greetingIndex $'idx "quote" \\ slash\tTabbed\nline' --arg timezone "UTC" '{workflowInput:{name:$name,greetingIndex:$greetingIndex,timezone:$timezone}}')" && bun run "${RIELFLOW_ROOT:-../rielflow}/packages/rielflow/src/bin.ts" workflow run greeting-addon-smoke --workflow-definition-dir "$tmp" --direct-executable-addon-grant "$grant" --variables "$vars" --output json
```

```bash
git diff -- packages/greeting-node-addon design-docs/specs/notes.md impl-plans/active/greeting-node-addon-json-output-safety.md
```

## Completion Criteria

- [x] `greeting.bash` no longer interpolates unescaped JSON strings with `printf`.
- [x] The smoke command proves `output.json` parses and preserves problematic input strings.
- [x] The local Rielflow CLI temporary workflow smoke runs the installed `examples/greeting-shell@1` add-on with a direct executable grant.
- [x] Runtime hints and README are accurate for the added `jq` encoder dependency.
- [x] `packages/greeting-node-addon/rielflow-package.json` has current add-on contentDigest, checksum, and integrity digest.
- [x] Focused package verification succeeds; adjusted commands and transient failures are recorded below.
- [x] Final implementation commit is created locally and not pushed.

## Progress Log Expectations

- Record changed files and why each changed.
- Record old and new digest fields when metadata is refreshed.
- Record every verification command and result.
- Record commit SHA and explicitly state that no push occurred under `commit-no-push`.

## Progress Log

### 2026-06-04 Step 6 Implementation

Changed files:

- `packages/greeting-node-addon/addons/examples/greeting-shell/1/greeting.bash`: replaced direct JSON `printf` interpolation with `jq -n --arg` encoding, added a `jq` preflight, and writes through a temporary file before moving to `outbox/output.json`.
- `packages/greeting-node-addon/addons/examples/greeting-shell/1/addon.json`: added `jq` to `execution.runtimeHints`.
- `packages/greeting-node-addon/rielflow-package.json`: added `jq` to add-on runtime hints and refreshed metadata.
- `packages/greeting-node-addon/README.md`: documented `bash`, `date`, and `jq` runtime expectations.
- `impl-plans/active/greeting-node-addon-json-output-safety.md`: recorded Step 6 progress and completion status.

Digest updates:

- `addons[0].contentDigest`: `sha256:3cbc41cb730af8a3e46951ea9453990b14e5a1bb57ab8ba48e502417335a00f1` -> `sha256:109e94f6d305901a578d50d10b9d78aa627a63afe95b0bf2fc920b042330254f`
- `checksum`: `51ca68728fbf61496e522c5028db2a2f` -> `8745e476cfef4bf341638e2f12b2ed86`
- `integrity.digest`: `c081edcd9272ffbc46d99644c03f5fef46805b60555c9ced7d0d92ad52cab928` -> `1f448f0a022c3608384bcc5fd783f97c83334481e83379a0ead34398407c6592`

Verification results:

- `git status --short`: reviewed before edits; scope was untracked design/plan files only.
- Original smoke command from this plan: output parsed but returned `false` because the inline jq literal expected two backslash characters while the shell input supplied one.
- Adjusted smoke command using `jq --arg` for expected strings: passed.
- `task package:check-digests`: passed; `greeting-node-addon node-addon=ok`.
- Explicit Bun node-addon metadata check: passed with contentDigest `sha256:109e94f6d305901a578d50d10b9d78aa627a63afe95b0bf2fc920b042330254f`, checksum `8745e476cfef4bf341638e2f12b2ed86`, integrity digest `1f448f0a022c3608384bcc5fd783f97c83334481e83379a0ead34398407c6592`.
- `package search greeting-node-addon --registry default --refresh --kind node-addon --output json`: passed and returned updated `jq` runtime hints and refreshed digest metadata.
- Initial `package install greeting-node-addon --registry default --refresh --overwrite --yes --output json`: failed with `package 'greeting-node-addon' not found` because install uses cached search with `refresh:false` internally while the cache refresh was still racing.
- Rerun after refreshed search cache, `package install greeting-node-addon --registry default --overwrite --yes --output json`: passed and installed `examples/greeting-shell@1` to project scope.
- Temporary workflow smoke with `--workflow-definition-dir`: failed because direct workflow roots skip project add-on scope and direct add-on roots reject executable add-ons without library-only `allowUnpackagedExecutableAddons`.
- Adjusted temporary workflow smoke with `--workflow-json-file`, `--project-root "$PWD"`, installed add-on, and direct executable add-on grant: passed with session `riel-greeting-addon-smoke-1780571559-5a02221e`.
- Session export assertion against `nodeExecutions[].outputJson | fromjson | .payload`: passed, verifying quoted, backslashed, tabbed, and multiline inputs were preserved.
- `git diff -- packages/greeting-node-addon`: reviewed; only package-local changes present.
- Pre-commit safety check over the staged target: passed; no whitespace errors, credential patterns, credential-bearing URLs, or machine-local absolute paths found.
- Commit: created locally by Step 6; final commit SHA is reported in Step 6 JSON output because a commit cannot contain its own final hash. No push performed under `commit-no-push`.

## Risks

- A hand-rolled shell escaping fix may still corrupt JSON; avoid it.
- `task package:check-digests` validates node-addon structure in this repository; contentDigest, checksum, and integrity digest comparison must be performed by the explicit Bun metadata check.
- Invalid timezone strings may still make `date` fail; keep that existing behavior and fail before publishing malformed output.
