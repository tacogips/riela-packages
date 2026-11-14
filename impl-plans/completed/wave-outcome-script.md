# wave-outcome-script

Status: completed. Implementation accepted by test-integrity, adversarial and integration review in session-480 (integration-review-attempt-1-exec-7361, comm-008771). Archived from `impl-plans/active/wave-outcome-script.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "wave-outcome-script",
  "planPath": "impl-plans/completed/wave-outcome-script.md",
  "dependsOn": [],
  "writePaths": [
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/implementation-wave-outcome.py",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/nodes/node-implementation-wave-outcome.json",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/prompts/implementation-wave-outcome.md",
    "packages/opus-terra-design-and-implement-review-loop/tests/test_wave_outcome.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "progressFile": "tmp/wave-compaction/wave-outcome-script/progress.json",
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_wave_outcome.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'",
    "python3 -m json.tool packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/nodes/node-implementation-wave-outcome.json",
    "test -x packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/implementation-wave-outcome.py",
    "find packages/opus-terra-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "node-implementation-wave-outcome.json is nodeType command with command.scriptPath scripts/implementation-wave-outcome.py. Its output.jsonSchema is unchanged: the six fields, all required, additionalProperties false.",
    "prompts/implementation-wave-outcome.md is deleted.",
    "The script classifies a fanout join deterministically per design D2. It writes fanout-join.json and wave-summary.json into a new immutable tmp/opus-terra-waves/<workflowExecutionId>/wave-NNN/ per design D3, and prints {when:{implementation_blocked,partial_success},payload:<six fields>}.",
    "For a synthetic join of at least 8 MiB, wave-summary.json bytes plus payload bytes are at most 65536. Totals are exact and the per-plan status, blockers and resume criteria are preserved.",
    "Tracking-contract rejections and complete:false waves are blocked with the exact resume criterion 'amend checkpoint: declare artifactRoots / narrow writePaths'. Blocked-only waves report partial_success false.",
    "All ten design test cases pass under unittest with PYTHONDONTWRITEBYTECODE=1. No __pycache__ remains in the package."
  ]
}
```

## Intent and context

Issue `workflowInput:opus-terra-wave-input-compaction`, mode `issue-resolution`. Accepted design: `design-docs/specs/design-opus-terra-wave-input-compaction.md` (D1-D4, Verification cases 1-10). Session-471 overflowed the Opus context at the fanout join step `implementation-wave-outcome` because the prompt carried the raw ~8 MB `fanoutJoin`. This plan replaces that Opus step with a deterministic Python command. The command takes over the step's mechanical aggregation, stores the raw join on disk and emits a bounded summary. Below, `W` means `packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop`.

The prompt-level bound for later agent steps is NOT delivered by this plan. riela keeps `fanoutJoin` as a persistent request variable, and that is pending user decision Q1 in `design-docs/user-qa/opus-terra-wave-input-compaction.md`. Do not claim it.

## Non-goals

- Do not edit `W/workflow.json`. Step id, node id, `joinStepId`, edges and transitions stay byte-identical.
- Do not edit `W/scripts/dispatch-plans.py`, `W/scripts/implementation-progress-check.py` or `W/scripts/git-push-gate.py`. The Codex package tests load the first two byte-for-byte.
- Do not edit other prompts, mock scenarios, docs, `riela-package.json`, `registry-index.json`, other packages, `.agents/` or riela sources.
- Do not implement the D7 option B stub shadow. Do not add a `fanoutJoin` property to the output schema.
- Do not add command-line options, config files or generic frameworks.

## File-level changes

1. `W/nodes/node-implementation-wave-outcome.json`
   - Remove `executionBackend`, `agentSandbox`, `model`, `effort` and `promptTemplateFile`.
   - Add `"nodeType": "command"` and `"command": {"scriptPath": "scripts/implementation-wave-outcome.py"}`.
   - Keep `id`, `variables: {}`, `modelFreeze: false` and the whole `output` object (description, jsonSchema, maxValidationAttempts) semantically identical. Update `description` to say it deterministically aggregates the branch outcomes and writes the bounded wave summary.
   - Imitate `W/nodes/node-plan-push-gate.json` and `W/nodes/node-implementation-progress-check.json`.
2. `W/prompts/implementation-wave-outcome.md`: delete with `git rm`-equivalent file removal; no git staging is done by this worker. Its rules move into the script docstring and code.
3. `W/scripts/implementation-wave-outcome.py`: new file, mode 755 like the sibling scripts (`100755` in git), shebang `#!/usr/bin/env python3`, standard library only.
   - Imitate `W/scripts/dispatch-plans.py:main` for stdin and stdout handling.
   - Imitate `packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/scripts/check-runtime-tracking-contract.py:classify` for join lookup, `POLICY_PREFIXES` and `DIAGNOSTIC_KEYS`.

   Pinned interface (the tests depend on it):
   - `classify(envelope: dict, root: Path) -> dict` returns `{"when": {"implementation_blocked": bool, "partial_success": bool}, "payload": {six fields}}` and writes the wave files under `root`.
   - Module constants:
     - `SUMMARY_BYTE_LIMIT = 49152`, `VERDICT_BYTE_LIMIT = 16384`
     - `WAVE_ROOT = "tmp/opus-terra-waves"`
     - `TRACKING_RESUME_CRITERION = "amend checkpoint: declare artifactRoots / narrow writePaths"`
     - `POLICY_PREFIXES`, `DIAGNOSTIC_KEYS = ("branchId","node","phase","selection","root","path","observed","limit")`
     - `LEVELS`: a tuple of the four cap levels from the design D4 table.
   - `main() -> int` reads one stdin line, calls `classify(envelope, Path.cwd().resolve())` and prints compact JSON (`separators=(",",":")`, `ensure_ascii=False`). It returns 0. On `ValueError`, `OSError`, `TypeError`, `KeyError` or `json.JSONDecodeError` it prints `{"error": str}` to stderr and returns 1.

   Behavior, exactly per the design:
   - Join lookup. Use the latest direct-inbox message, ordered by `createdOrder`, in `envelope["input"]["_rielaInput"]["messages"]` whose `payload.fanoutJoin` is a dict.
     - Never read `envelope["input"]["fanoutJoin"]` or `envelope["variables"]["fanoutJoin"]`. Those can be a previous wave's persistent request variable.
     - With no join message, use the standalone fallback. Take the latest message from `implementation-progress-check` or `branch-evidence` with a dict payload and synthesize a one-branch join `{"branches":[{"branchId":planId,"status":"completed","output":payload}],"dispatchedBranchIds":[planId]}`. `planId` is `payload.planId`, falling back to `payload.blockedPlanIds[0]`. If no plan id can be found, raise `ValueError`.
     - With neither, raise `ValueError`.
   - Classification follows the D2 table. Precedence is `tracking-rejected` > `evidence-incomplete` > `blocked` > `successful` > `failed` / `cancelled` / `evidence-missing`. Plans listed in `pendingBranchIds` and absent from `branches` are `pending`.
     - Successful means: status in `{"completed","succeeded","success"}`, not blocked, `output.evidencePaths` is a non-empty list, and `output.changedFiles` is a list.
     - `changeEvidence.complete is False` with no attributable diagnostic `branchId` blocks every dispatched branch. A missing `changeEvidence` or `complete` is not treated as False.
   - Verdict:
     - `blockedPlanIds` and `successfulPlanIds` are in branch input order.
     - `partial_success = implementation_blocked and bool(successfulPlanIds)`.
     - An unblocked wave gets empty `blockedPlanIds`, `blockers` and `resumeCriteria`.
     - Each blocker is `{planId, blockerType, source, message}`, with `diagnostic` (DIAGNOSTIC_KEYS only) when present. `blockerType` is `tracking-contract`, `change-evidence-incomplete`, or the branch's `output.blockerType` (default `implementation-blocked`). `source` is `tracking-contract`, `change-evidence` or `progress-gate`.
     - `resumeCriteria` holds strings deduplicated in first-seen order. Tracking and evidence blocks use `TRACKING_RESUME_CRITERION`. Progress blocks use `output.resumeCriteria`, falling back to `"<planId>: resolve the <blockerType> blockers recorded in <summaryPath> and redispatch"`.
     - Verdict caps: at most 3 blockers per plan plus one `additional-blockers-omitted` marker carrying `omittedCount` and `summaryPath`, at most 3 resume criteria per plan, and 300-character strings. If that exceeds `VERDICT_BYTE_LIMIT`, retry with 1/1/120. If it still exceeds, raise `ValueError`.
   - Storage (D3):
     - `workflowExecutionId` comes from `input._rielaInput.workflowExecutionId`. It must match `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$` and contain no `..`; otherwise raise `ValueError`.
     - `root/tmp`, `root/tmp/opus-terra-waves` and the session directory: if one exists as a symlink or non-directory, raise `ValueError`; if missing, create it.
     - The ordinal is the max existing `wave-\d{3}` plus 1. Create it with `mkdir(exist_ok=False)` and retry on `FileExistsError`; beyond 999, raise `ValueError`.
     - Write `fanout-join.json` (compact UTF-8 JSON of the join, original key order) and then `wave-summary.json`, each through `<name>.tmp` plus `os.replace`.
     - Paths in the summary are repository-relative POSIX strings.
   - Summary (D4 schema, `schemaVersion: 1`, `generatedBy: "implementation-wave-outcome.py"`):
     - `rawJoinBytes` and `rawJoinSha256` are computed from the exact bytes written.
     - `verdict` deep-equals the printed payload.
     - Observation `kind` is `kind`, falling back to `type` and then `"unknown"`. `path` is `path`, falling back to `root`. `selection` defaults to `"other"`. Branch ids come from `branchId` or `branchIds`.
     - Drift-first ordering of `paths`: kind severity rank (deleted/removed/overwrit/content=0, added/new/membership=1, mode/kind=2, else 3), then selection rank (source=0, artifact=1, other=2), then `-observationCount`, then path.
     - Generic bounded projection for `reviewDecisions` and `checkpointProvenance`: depth, items and string caps per level. A cut string ends with `…[truncated N chars; see rawJoinPath#<RFC 6901 pointer>]`. Each plan carries `rawPointer: "/branches/<i>"`.
     - Try `LEVELS` in order and keep the first summary whose compact UTF-8 size is at most `SUMMARY_BYTE_LIMIT`. Record `truncation.level`. If none fits, raise `ValueError` naming the plan count. Never emit an oversized or silently cut summary.
     - No timestamps, randomness, or set iteration in output order.
4. `packages/opus-terra-design-and-implement-review-loop/tests/test_wave_outcome.py`: new `unittest` module.
   - Imitate `tests/test_git_push_gate.py:load`, which uses `importlib.util.spec_from_file_location` with a module name such as `luna_wave_outcome`.
   - Use `tempfile.TemporaryDirectory()` as `root`, and pass envelopes as `{"input": {"_rielaInput": {"workflowExecutionId": "session-test", "messages": [...]}}}`.

## Key pitfalls

- Do not derive `planId` from list index. Use `branchId`, then `output.planId`.
- Do not mark `failed` or `cancelled` branches as blocked. They must stay out of both id lists so reconciliation and selective redispatch handle them.
- Do not copy diagnostic `contents` or any non-DIAGNOSTIC_KEYS field into blockers or the summary.
- Do not put `waveSummaryPath` or any extra key in the payload. The schema is `additionalProperties:false`.
- Measure bytes as `len(json.dumps(obj, ensure_ascii=False, separators=(",",":")).encode("utf-8"))`, not `len(str)`.
- Totals must count every observation and diagnostic before capping.
- Do not overwrite or reuse an existing wave directory.
- Keep the file executable (`chmod 755`).

## Test cases (`input -> expected`)

1. A synthetic join with 4 branches: 3 completed with long continuation outputs and 300 KB+ review feedback strings, and 1 with `output.implementation_blocked:true` and `blockerType` / `blockers` / `resumeCriteria`. `changeEvidence` has ≥ 5,000 observations over ≥ 1,000 paths (both selections; kinds include content and membership drift), plus capture and reduce diagnostics carrying a `contents` field. The serialized join is ≥ 8 MiB.
   - summary bytes + payload bytes ≤ 65536.
   - `fanout-join.json` sha256 equals the sha256 of the same compact serialization of the input, and equals `rawJoinSha256`.
   - Verdict: blocked `[d]`, successful `[a,b,c]`, `partial_success:true`.
   - Every plan has `classification` and `status`.
   - `observationTotal`, `captureFailuresTotal`, `reduceFailuresTotal`, `complete` and `hasDrift` are exact.
   - `paths[0]` is a `source` content-drift path.
   - No `contents` key appears anywhere in the summary.
2. For each `POLICY_PREFIXES` entry, a failed branch with that `failureReason` plus a successful sibling gives `tracking-rejected`, `TRACKING_RESUME_CRITERION` present, and `partial_success:true`.
3. `complete:false` with a diagnostic `branchId:"b"` blocks only `b`. `complete:false` with no diagnostics blocks every dispatched branch.
4. Only blocked branches gives `implementation_blocked:true` and `partial_success:false`.
5. A `failed` branch with `provider_error: x` plus a `cancelled` branch gives `implementation_blocked:false` with neither in any id list.
6. All successful gives `partial_success:false` and empty `blockedPlanIds`, `blockers` and `resumeCriteria`.
7. Payload keys equal the six schema properties. The node file parses: `nodeType=="command"`, `command.scriptPath` matches, no `model` key, and `output.jsonSchema` equals the literal six-field schema embedded in the test (copied from git HEAD `81a4fcb`). The `workflow.json` transitions of `implementation-wave-outcome` equal `[{"toStepId":"implementation-blocked-output","label":"implementation_blocked && !(partial_success)"},{"toStepId":"reconcile-implementations","label":"!(implementation_blocked) || partial_success"}]`. `prompts/implementation-wave-outcome.md` does not exist.
8. Two calls create `wave-001` and `wave-002`, and `wave-001` bytes are unchanged. `workflowExecutionId` `"../x"` or a missing value raises `ValueError`. A symlinked `root/tmp` raises `ValueError`.
9. Determinism: the same input in two fresh roots gives identical summaries after removing `waveOrdinal`, `summaryPath` and `rawJoinPath`.
10. Patching `SUMMARY_BYTE_LIMIT` to a tiny value (`unittest.mock.patch.object`) makes `classify` raise `ValueError`. `main()` with invalid stdin returns 1 and writes a JSON error.
11. Standalone fallback: only an `implementation-progress-check` message with `implementation_blocked:true` and `planId:"p"` gives `blockedPlanIds ["p"]`. No join and no terminal message raises `ValueError`.

## Execution, drift and progress contract

- The accepted design and plans are committed by the later checkpoint step before native fanout. This worker shares the branch and working directory with the `wave-summary-prompts` and `wave-fixtures-docs` workers.
- Write only the four `writePaths`.
- Before each edit, freshly read the file. Record its SHA-256 and an immutable intent note under `tmp/wave-compaction/wave-outcome-script/attempt-N/intent/`. Re-check the hash immediately before writing; on drift, re-read and reconcile instead of overwriting. Record the post-edit hash.
- Maintain `tmp/wave-compaction/wave-outcome-script/progress.json` with task ids, status, changed paths with pre/post hashes, exact commands with cwd, final exit codes, complete log paths and test counts. Write `handoff.json` with requirement-to-test mapping.
- Run commands from the repository root in the foreground. Capture complete stdout and stderr to log files under the attempt directory.
- Never run `git add`, commit, push or branch commands. Never edit another plan's files or progress.

## Verification and required evidence

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_wave_outcome.py -v`: exit 0 and ≥ 11 tests run, 0 failures.
- The package-wide discover: exit 0, including the existing `test_git_push_gate.py` and `test_review_handoff.py`.
- The Codex package discover: exit 0. This proves the shared scripts are untouched.
- `python3 -m json.tool` on the node: exit 0.
- `test -x` on the script: exit 0.
- `find ... -name __pycache__`: no output. Delete any directory it finds and record the deletion.
- `git diff --check`: exit 0.

## Completion criteria

All acceptance criteria hold with recorded evidence, `progress.json` and `handoff.json` are complete, and no high or mid self-found issue is open. Independent test-integrity, adversarial and integration reviews are later gates.


## Step 6 implementation progress (2026-10-22)

Implemented this plan's four source paths: the join node is a command backed by `scripts/implementation-wave-outcome.py`, the old prompt is deleted, and `tests/test_wave_outcome.py` covers the deterministic classifier, bounded large-join summary, storage safety, fallback and node contract. The output JSON Schema compares equal to the committed schema.

Verification from the repository root passed: focused wave tests (12 tests), package tests (28 tests), Codex package tests (91 tests), node JSON parsing, executable-bit check, empty package `__pycache__` search, and `git diff --check`. Complete logs and exit evidence are in `tmp/wave-compaction/wave-outcome-script/attempt-1/logs/`; structured results are in `tmp/wave-compaction/wave-outcome-script/progress.json`.

Implementation-phase completion criteria are met. Independent test-integrity, adversarial and integration review remain downstream. The D7 Option A limitation (persistent `fanoutJoin` in later runtime prompts) remains an upstream Riela dependency already recorded in the accepted design; this plan does not own that change.

## Operator amendment (2026-10-22, rerun after session-476)

Attempt 1 was blocked by workflow bookkeeping, not by this plan's code: the
installed progress gate did not recognize `python3 -m unittest` as a
behavioral test runner. That gate is fixed in cfa5880 and the rerun uses the
fixed gate. The attempt-1 implementation is still in the working tree; reuse
it, re-run this plan's verification, and report each test command with an
integer `exitCode`, `testsRun` and `failureCount`. The package suite currently
passes (31 tests, including `tests/test_progress_check.py`).


## Operator amendment 2 (2026-10-22, rerun after session-477)

Design D4 is amended: kind severity is now deleted/removed/overwrite, then
content, then added/new/membership, then mode/kind, then other. A removed path
therefore outranks content drift regardless of observationCount, which is what
the adversarial regression `test_runtime_reason_observations_rank_removed_first`
asserts and what the current script does. The design/test conflict is resolved
in favor of the current implementation and test; keep both, make sure the
script's tie-break comments and any other ordering test match the amended D4,
then rerun the full package suite and report it.
