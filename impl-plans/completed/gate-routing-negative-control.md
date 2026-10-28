# gate-routing-negative-control

Status: completed. Wave 1. Issue tacogips/riela#134. Implementation accepted by test-integrity, adversarial and integration review in opus-terra-design-and-implement-review-loop-session-1 (integration-review-attempt-1-exec-93). Archived from `impl-plans/active/gate-routing-negative-control.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "gate-routing-negative-control",
  "planPath": "impl-plans/active/gate-routing-negative-control.md",
  "dependsOn": [],
  "writePaths": [
    "impl-plans/active/gate-routing-negative-control.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/implementation-progress-check.py",
    "packages/opus-terra-design-and-implement-review-loop/tests/test_progress_negative_control.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_progress_negative_control.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'",
    "find packages/opus-terra-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "implementation-progress-check.py defines record_exit_status(record) and exit_status_invalid(record). verification_succeeded() uses them: a leading 'exit=N' / 'exit N' / 'exit: N' / 'exit code N' / 'exit status N' in outcome is the exit status when no structured exitStatus/exitCode exists, and a structured value that conflicts with the parsed one, or a non-numeric structured value, makes the record unsuccessful.",
    "A verification record with negativeControl true, an integer nonzero exit status, a matching expectedExitStatus when present, and a command that is not a committed implementation.verification command is excluded from failed and successful behavioral evidence and from the static-plan success check.",
    "A record flagged negativeControl true that fails any of those rules blocks with blockerType implementation-materially-unverified and the exact message from design D2.3.",
    "Ready payloads carry negativeControlEvidence only when at least one valid negative control exists. Blocked materially-unverified blockers carry failingCommands (at most 5 strings) when any offending command is known.",
    "test_progress_negative_control.py covers every case in design Verification 2 and passes. All opus-terra and codex package tests pass with exit status 0 and failureCount 0, and no __pycache__ remains."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-terra-gate-routing-0110.md` D2 (#134). Below, `W` = `packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop` and `T` = `packages/opus-terra-design-and-implement-review-loop/tests`.

Sessions 265, 269 and 282 were blocked because intentional mutation runs (`negativeControl: true`, exit 100) in `verification[]` counted as failed behavioral tests. Session 283 was blocked because green records gave their exit status only in `outcome` text (`"exit 0 in 1010.466 seconds; 3 skipped"`), and `verification_succeeded()` fell through to `return False`.

This plan is the first link of the same-file chain: negative-control (this) -> structured-runner (#125) -> sibling-blockers (#126). The structured-runner plan calls `record_exit_status()`, so keep the pinned name and signature below.

## Non-goals

- Do not change `behavioral_kind()`, `positive_test_count()`, the runner allowlist, `plan_requires_behavioral_tests()` or `concrete_verification()`. Those belong to the next plan or must stay unchanged.
- Do not add "latest record per command" deduplication. Do not read `priorVerification[]`.
- Do not touch `W/scripts/dispatch-plans.py`, prompts, `workflow.json`, nodes, mocks, docs, other packages, or `tmp/opus-terra-bundle`.
- Do not change the ready-outcome `when` object. `T/test_progress_gate.py` asserts it equals exactly `{'implementation_blocked': False}`.

## File-level changes

1. `W/scripts/implementation-progress-check.py`
   - Pinned helpers (module level, standard library only):
     - `record_exit_status(record: dict) -> int | None`
       - **Structured value first.** Use `exitStatus`, then `exitCode`, when the value is an `int` that is not a `bool`, or a string matching `^-?\d+$`.
       - **Parsed fallback.** Otherwise apply `re.match(r"^\s*exit(?:\s+(?:status|code))?\s*[=:]?\s*(-?\d+)\b", outcome, re.IGNORECASE)` to a string `outcome`.
       - **Absent.** Return `None` when neither source gives a value.
     - `exit_status_invalid(record: dict) -> bool` returns True when any of these holds:
       - `exitStatus` or `exitCode` is present (not None and not `""`) but is not an int/decimal string, or is a bool;
       - `exitStatus` and `exitCode` are both present with different integer values;
       - a structured integer exists, the outcome-parsed integer also exists, and the two differ.
   - `verification_succeeded()`. Keep the existing order: environment-blocked, failure-count recursion, failed/skipped text. Then replace the `exitStatus`/`exitCode` loop:
     1. If `exit_status_invalid` -> False.
     2. Else, if `record_exit_status` is not None -> return `status == 0`.
     3. Else, keep the existing pass-word fallback.

     The string `"0"` must still pass, and the string `"passed"` in `exitStatus` must still fail, as today.
   - Pinned helpers: `normalize_command(text: str) -> str` (`" ".join(text.split())`) and `negative_control_status(record: dict, planned: list[str] | None) -> str | None`. The latter returns:
     - `None` when `record.get("negativeControl") is not True`;
     - `"valid"` when exit status is a nonzero int, `exit_status_invalid` is false, `expectedExitStatus` is absent or an int (not bool) equal to the exit status, and the normalized command is not in `{normalize_command(c) for c in planned}` (skip that last check when `planned` is None);
     - `"invalid"` otherwise.
   - `classify()`. Right after the `material_findings` block:
     - Compute `planned = planned_verification_commands(envelope)`.
     - Split `verification` into `negative_valid`, `negative_invalid` and `gated`. `gated` = records whose status is None.
     - If `negative_invalid` is non-empty, return `blocked_result(... "implementation-materially-unverified", "Step 6 reported a negative-control record that did not fail as declared or names a committed verification command.", ...)` with `failingCommands` = their commands.
     - From then on, use `gated` instead of `verification` in: the `reviewable_records` / `baseline_candidates` / `unreviewable_verification` computation, `has_failed_behavioral_evidence`, `has_behavioral_evidence`, the static-plan `any(verification_succeeded(...))` check, and the `verificationGaps` `inherited_behavioral_evidence` call.
     - Keep `verification`, the full list, for the earlier no-progress and "material changes without verification" checks, for the fingerprint, and for `has_new_item`.
   - `blocked_result()` gets an optional keyword `failing_commands: list[str] | None = None`. When it is non-empty, the new blocker dict gets `"failingCommands": failing_commands[:5]`. Pass it from:
     - the failed-behavioral path: commands of records in the unreviewable set where `behavioral_kind(r)` is set and `not successful_behavioral_verification(r)`;
     - the no-positive-evidence path: commands of `gated` records, capped at 5;
     - the invalid-negative-control path.

     Keep the existing message strings byte-identical. Tests match `'positive test count'`.
   - Ready payload: add `"negativeControlEvidence": negative_valid` only when it is non-empty.
   - Imitate the existing style: `normalized_list`, `canonical_items`, and the `blocked_result` dict-building pattern in this file.
2. `T/test_progress_negative_control.py`: a new `unittest` module.
   - Load the script like `T/test_progress_check.py` does, with `importlib.util.spec_from_file_location`.
   - Build envelopes like `T/test_progress_gate.py` (`envelope(payload, planned_commands)`): a step6 message under `input._rielaInput.messages`, and `variables.implementation.verification`.

## Key points and pitfalls

- `exitCode` handling in `baseline_review_candidate()` / `matched_baseline_record()` stays unchanged. Those functions require an int `exitCode` themselves.
- A negative control never satisfies the positive-evidence gate. A plan whose only behavioral record is a valid negative control must still block, with "no successful behavioral test evidence with a positive test count".
- A negative control whose command equals a committed verification command (after whitespace normalization) is invalid. Final-source gates are never exempt.
- Do not trust `negativeControl: "true"` (a string). It must be the JSON boolean True.
- The outcome regex is anchored at the start. `"tests passed; exit 0"` is not parsed, and it then falls back to the pass words.
- Keep codex `packages/codex-design-and-implement-review-loop/tests/test_implementation_progress_check.py` green. It runs these cases against this file: external blocker stops immediately, failed required gate despite other passing tests, baseline review candidate, bun custom runner.

## Test cases (`input -> expected`)

- Session-282 shape: passing `cargo nextest run` (testsRun 2816, failureCount 0, exitStatus 0), passing `vitest run` (703/703), and two records `{"command":"cargo mutants --file x","negativeControl":true,"exitStatus":100,"expectedExitStatus":100,"testsRun":1,"failureCount":1}`, with planned `["cargo nextest run"]` -> `status == "ready-for-test-integrity"` and `negativeControlEvidence` has 2 entries.
- Session-283 record `{"command":"cargo nextest run","failureCount":0,"outcome":"exit 0 in 1010.466 seconds; 3 skipped; ...","testsPassed":2816,"testsRun":2816}` (no exitStatus) -> `verification_succeeded` True, and classify is ready.
- `outcome: "exit=1 after 3s"` with counts -> `verification_succeeded` False.
- `exitStatus: 0` and `outcome: "exit 1"` -> False (conflict).
- Negative control with exitStatus 0 -> blocked materially-unverified, with the D2.3 message and `failingCommands` containing its command.
- Negative control with no exit status -> blocked.
- Negative control with `expectedExitStatus: 2` and exitStatus 100 -> blocked.
- Negative control whose command is `"cargo  nextest run"` (two spaces) while planned is `["cargo nextest run"]` -> blocked.
- Unflagged failing record (`exitStatus 1`, failureCount 3) alongside a passing one -> blocked with "failed, blocked, skipped, or zero-count", and `failingCommands` names it.
- The only behavioral record is a valid negative control -> blocked with "positive test count".
- `record_exit_status`: `{"exitCode":"0"}` -> 0, `{"exitStatus":True}` -> invalid, `{"outcome":"Exit code 2"}` -> 2.

## Done criteria

- All verification commands exit 0. Record each command, exit status, testsRun and failureCount (integers), and the log path under `tmp/opus-terra-gate-routing/gate-routing-negative-control/`.
- `find ... -name __pycache__` prints nothing.

## Progress log

- 2026-10-24: Implemented D2 in `implementation-progress-check.py`: structured and leading-outcome exit parsing, conflict/non-numeric rejection, strict negative-control validation, exclusion from behavioral/static success gates, optional `negativeControlEvidence`, and bounded `failingCommands`. Added `test_progress_negative_control.py` for parser forms, conflicts, valid/invalid controls (including missing command/status), planned-command collisions, positive-evidence behavior, and unchanged failed-test blocking. Script SHA-256 before edits: `a0eaea5c63613f936897ffb206e16c7b4dd2e9dcbebc26a4f5b2fbda817ae8c6`; final before this plan-log edit: `ce3d8cd30ced1d0b7f4900a8e5cbac7aec6b7f774fae6990a5ccf7c276ca9846`.
- Initial focused run exposed two test issues (9 tests, 1 failure, 1 error, exit 1); complete log: `tmp/opus-terra-gate-routing/gate-routing-negative-control/test-negative-control.log`. The failure led to retaining flagged records without exit fields for validation; the expectation was corrected so valid controls do not appear as failing commands. Final source-matched checks: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_progress_negative_control.py -v` (9 tests, 0 failures, exit 0; `tmp/opus-terra-gate-routing/gate-routing-negative-control/test-negative-control-final.log`); `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -p 'test_*.py' -v` (86 tests, 0 failures, exit 0; `tmp/opus-terra-gate-routing/gate-routing-negative-control/opus-tests-final.log`); `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'` (91 tests, 0 failures, exit 0; `tmp/opus-terra-gate-routing/gate-routing-negative-control/codex-tests-final.log`); `find packages/opus-terra-design-and-implement-review-loop -name __pycache__` (exit 0, no paths; `tmp/opus-terra-gate-routing/gate-routing-negative-control/no-pycache.log`); `git diff --check` (exit 0; `tmp/opus-terra-gate-routing/gate-routing-negative-control/diff-check.log`).
- Completion criteria met for this plan: regression and both package test suites pass on the final implementation, no package `__pycache__` remains, and diff check is clean. Test-integrity/adversarial review and later workflow integration/release work remain downstream.
- Final verification rerun after ready-payload normalization (empty/stale `negativeControlEvidence` is removed unless current validated controls exist): script SHA-256 `2b069e6b8f24076d5e14ef609aef235912fa2d86da15caa91a9d09fa9c45d0b4`. Regression suite: 9 run, 0 failures, exit 0 (`tmp/opus-terra-gate-routing/gate-routing-negative-control/test-negative-control-final2.log`); Opus suite: 86 run, 0 failures, exit 0 (`tmp/opus-terra-gate-routing/gate-routing-negative-control/opus-tests-final2.log`); Codex suite: 91 run, 0 failures, exit 0 (`tmp/opus-terra-gate-routing/gate-routing-negative-control/codex-tests-final2.log`); no `__pycache__` paths, exit 0 (`tmp/opus-terra-gate-routing/gate-routing-negative-control/no-pycache-final.log`); `git diff --check`, exit 0 (`tmp/opus-terra-gate-routing/gate-routing-negative-control/diff-check-final2.log`).
