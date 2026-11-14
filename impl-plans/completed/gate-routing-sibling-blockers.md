# gate-routing-sibling-blockers

Status: completed. Wave 3. Issue tacogips/riela#126. Implementation accepted by test-integrity, adversarial and integration review in opus-terra-design-and-implement-review-loop-session-1 (integration-review-attempt-1-exec-93). Archived from `impl-plans/active/gate-routing-sibling-blockers.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "gate-routing-sibling-blockers",
  "planPath": "impl-plans/active/gate-routing-sibling-blockers.md",
  "dependsOn": ["gate-routing-structured-runner"],
  "writePaths": [
    "impl-plans/active/gate-routing-sibling-blockers.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/implementation-progress-check.py",
    "packages/opus-terra-design-and-implement-review-loop/tests/test_progress_sibling_blockers.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_progress_sibling_blockers.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'",
    "find packages/opus-terra-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "When every Step 6 blocker is sibling-owned per design D3.2, classify() does not return implementation-dependency and evaluates the remaining gates unchanged. Blockers are classified against the manifest read with `git show <checkpointCommit>:<manifestPath>` from variables.implementation.",
    "Every fail-closed case in design D3.3 still returns implementation-dependency: no implementation item, git show failure, non-JSON manifest, string blocker, blocker without path(s), own-path blocker, unowned path, owner in acceptedPlanIds, implementation_blocked true with no blockers, and a mix of sibling and non-sibling blockers.",
    "On the ready outcome with deferred blockers, the payload has blockers [] plus siblingOwnedBlockers and siblingOwnedBlockersPath. The file <evidenceRoot>/<planId>/sibling-owned-blockers.json is written atomically. A write failure, or an unsafe evidenceRoot or planId, blocks as implementation-dependency.",
    "A sibling-only blocker on a branch without positive-count behavioral evidence still blocks as implementation-materially-unverified.",
    "test_progress_sibling_blockers.py covers design Verification 3 and passes. All opus-terra and codex package tests pass and no __pycache__ remains."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-terra-gate-routing-0110.md` D3 (#126). `W`/`T` as in `impl-plans/active/gate-routing-negative-control.md`.

In session 222 (FST-22), every gate the plan owns passed. A workspace-wide `cargo fmt --check` exited 1 only because of `src/cli/tests/fmt.rs`, a file owned by the concurrently running FST-20. Step 6 reported `blockers: [{owner:"FST-20", path:"src/cli/tests/fmt.rs"}]` and the gate ended the branch as `implementation-dependency`.

This plan is the third link of the same-file chain. Read the file fresh: the negative-control and structured-runner plans have already edited it.

The integration-review prompt rule that re-runs deferred gates is owned by `gate-routing-runtime-prompts`. Pin the file path exactly as `<evidenceRoot>/<planId>/sibling-owned-blockers.json` so that rule matches.

## Non-goals

- Do not exempt failed behavioral tests or compile failures caused by sibling files (the Rust shared-crate case). The remaining gates still decide.
- Do not import `dispatch-plans.py`. Copy only the one-line ownership semantics: equal to, or under, a `writePaths` entry.
- Do not trust the blocker's `owner` text.
- Do not edit prompts, `workflow.json`, `implementation-wave-outcome.py`, or other files.

## File-level changes

1. `W/scripts/implementation-progress-check.py`
   - Add `import os`, `import subprocess` and `import tempfile` as needed. Standard library only.
   - Pinned helpers:
     - `safe_repo_path(value) -> str | None`
       - Accept a non-empty str and strip a leading `./`.
       - Use the `PurePosixPath` parts. Reject an absolute path, `..`, `.git`, an empty path, and any backslash.
       - Return the posix string.
     - `path_owned(path: str, owned: list[str]) -> bool`: `path == o or path.startswith(o.rstrip("/") + "/")`.
     - `checkpoint_manifest(item: dict) -> dict | None`
       - Require `checkpointCommit` matching `^[0-9a-f]{40}$|^[0-9a-f]{64}$`, and a `manifestPath` that passes `safe_repo_path`.
       - Run `subprocess.run(["git", "show", f"{commit}:{path}"], cwd=Path.cwd(), capture_output=True, text=True, check=False)`.
       - Return None on a nonzero exit, a JSON error, or a non-dict result.
     - `sibling_owned_blockers(envelope: dict, blockers: list) -> list[dict] | None`
       - Return a classified list only when *every* blocker qualifies, and None otherwise.
       - Get `item = envelope.get("variables", {}).get("implementation")`. Own `planId` and `writePaths` come from `item`.
       - The accepted set is `item.get("acceptedPlanIds", [])`.
       - Sibling candidates are manifest `plans[]` dict entries whose `planId` is not the own ID and not accepted. Use their `writePaths` string lists.
       - Each entry is `{"paths": [...], "ownerPlanIds": sorted([...])}`. Copy `command`, `exitStatus` and `message` when present.
   - In `classify()`, replace the first blocker branch:
     - `raw = normalized_list(current.get("blockers"))`.
     - If `implementation_blocked is True` or `raw` is non-empty:
       - compute `deferred = sibling_owned_blockers(envelope, raw) if raw else None`;
       - if `deferred` is None, return the existing `implementation-dependency` block, with the message unchanged.
     - Otherwise continue with `deferred` (or `[]` when there are no blockers).
     - The later `blocked_result(current, ...)` calls keep `current["blockers"]` as they are today, so blocked outcomes preserve the original blockers.
   - On the final ready payload only, when `deferred` is non-empty:
     - Validate `evidenceRoot` (from `item`) with `safe_repo_path`. Its first part must be `tmp`, and `(Path.cwd()/evidenceRoot).resolve()` must lie under `(Path.cwd()/"tmp").resolve()`.
     - Validate `planId` against `^[A-Za-z0-9._-]+$`.
     - Write `{"schemaVersion":1,"planId","checkpointCommit","manifestPath","siblingOwnedBlockers":deferred}` with `tempfile.NamedTemporaryFile(dir=target_dir, delete=False)` followed by `os.replace`.
     - On any failure, `return blocked_result(current, "implementation-dependency", "Step 6 sibling-owned blockers could not be recorded for integration review.", fingerprint)`.
     - Add the `siblingOwnedBlockers` and `siblingOwnedBlockersPath` keys to the ready payload only when `deferred` is non-empty.
   - The continuation path (`implementation_continue`) writes no file.
2. `T/test_progress_sibling_blockers.py`: a new module.
   - In `setUp`, create `tempfile.TemporaryDirectory()`, run `git init -q`, and commit `impl-plans/active/x-dispatch.json` with `git -c user.email=t@example.invalid -c user.name=t commit`. The manifest has plans FST-22 (`writePaths ["src/wasm"]`), FST-20 (`["src/cli/tests/fmt.rs"]`) and DONE-1 (`["src/done"]`).
   - `os.chdir` into the directory, with `addCleanup` to restore the previous cwd.
   - Build envelopes with `variables.implementation = {planId:"FST-22", writePaths:["src/wasm"], acceptedPlanIds:["DONE-1"], manifestPath, checkpointCommit:<HEAD sha>, evidenceRoot:"tmp/task", verification:["cargo test"]}` and a Step 6 payload with passing `cargo test` evidence (testsRun 5, failureCount 0, exitStatus 0).

## Key points and pitfalls

- Restore cwd in every test. A leaked chdir breaks the other test modules in the same `discover` run.
- `git show` must not use `shell=True`, and must not read the working-tree manifest.
- A blocker naming two paths qualifies only if *both* are sibling-owned.
- Keep codex `test_external_blocker_stops_immediately` green. It has `blockers: [{"type":"missing-dependency"}]` with no path and no implementation item, which must still return implementation-dependency.
- Do not change the ready `when` object.

## Test cases

- Blocker `{"owner":"FST-20","path":"src/cli/tests/fmt.rs","command":"cargo fmt --check","exitStatus":1}` with passing own tests -> ready. `siblingOwnedBlockers[0].ownerPlanIds == ["FST-20"]`, `payload.blockers == []`, and the file exists with the same list.
- Path `src/wasm/lib.rs` (own) -> implementation-dependency.
- `src/unowned.rs` -> implementation-dependency.
- `src/done/a.rs` (owner accepted) -> implementation-dependency.
- Blocker `"waiting on FST-20"` (string), or `{}` with no path -> implementation-dependency.
- Two blockers, one sibling and one unowned -> implementation-dependency.
- `checkpointCommit` of 40 zeros (git show fails) -> implementation-dependency.
- Sibling-only blocker, with verification only `cargo fmt --check` exit 1 -> implementation-materially-unverified.
- `evidenceRoot: "../x"` with a valid sibling blocker -> implementation-dependency ("could not be recorded").
- `implementation_blocked: true` with `blockers: []` -> implementation-dependency.

## Done criteria

- [x] All verification commands exit 0. Evidence is under `tmp/opus-terra-gate-routing/gate-routing-sibling-blockers/`.
- [x] Classifier defers only fully sibling-owned blockers from the committed manifest, preserves all fail-closed cases, keeps remaining gates active, and atomically records deferred blockers for integration review.
- [x] Focused regression, full opus-terra, full codex, no-`__pycache__`, and diff checks pass. Formal reviews, integration validation, and release checks remain downstream workflow steps.

## Progress log

- 2026-10-24: Implemented D3 in `implementation-progress-check.py`; added `test_progress_sibling_blockers.py` with seven tests for sibling deferral/evidence, malformed and mixed blockers, missing implementation item, checkpoint manifest failures including invalid UTF-8, unsafe evidence destinations, and retained behavioral-test requirements. Final focused suite passed 7 tests (`final6-focused.log`); opus-terra passed 108 tests (`final6-opus-suite.log`); codex passed 91 tests (`final6-codex-suite.log`). `final6-pycache.log` had no output and `final6-diff-check.log` was clean. The earlier `final5-focused.log` and `final5-opus-suite.log` failures exposed the decode-boundary issue and are superseded by final6. Ready for downstream test-integrity and adversarial review; integration and release checks remain pending.
