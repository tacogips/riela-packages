# gate-routing-structured-runner

Status: completed. Wave 2. Issue tacogips/riela#125. Implementation accepted by test-integrity, adversarial and integration review in opus-luna-design-and-implement-review-loop-session-1 (integration-review-attempt-1-exec-93). Archived from `impl-plans/active/gate-routing-structured-runner.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "gate-routing-structured-runner",
  "planPath": "impl-plans/active/gate-routing-structured-runner.md",
  "dependsOn": ["gate-routing-negative-control"],
  "writePaths": [
    "impl-plans/active/gate-routing-structured-runner.md",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/scripts/implementation-progress-check.py",
    "packages/opus-luna-design-and-implement-review-loop/tests/test_progress_structured_runner.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-luna-design-and-implement-review-loop/tests/test_progress_structured_runner.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-luna-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'",
    "find packages/opus-luna-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "behavioral_kind() returns 'test' for a record whose kind is 'behavioral-test' (after strip and lower) unless its command matches NON_TEST_COMMAND_PATTERNS. The existing allowlist and swift-discovery exclusion are unchanged.",
    "A record that is behavioral only through kind succeeds only when record_exit_status() == 0, testsRun is an int (not bool) > 0, failureCount is an int (not bool) == 0, and the existing verification_succeeded/positive_test_count also hold. Otherwise it is failed behavioral evidence and blocks.",
    "Kind-declared build, lint, format, diff and similar commands (design D1.3 list) are not behavioral.",
    "The implementation-materially-unverified resume criterion names the allowlisted runner forms and the structured {kind:'behavioral-test', exitStatus:0, testsRun>0, failureCount:0} form, and states that build, lint, format and diff commands never count.",
    "test_progress_structured_runner.py covers design Verification 1 and passes. All opus-luna and codex package tests pass and no __pycache__ remains."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-luna-gate-routing-0110.md` D1 (#125). `W` and `T` as in `impl-plans/active/gate-routing-negative-control.md`.

In session 222 (plan FST-22), Step 6 reported `{"command":"node tmp/fst/FST-22/wasm-smoke-rerun.mjs","exitStatus":0,"testsRun":2,"testsPassed":2,"failureCount":0}`. The gate rejected it because `behavioral_kind()` only matches command text against a regex allowlist. The implementer then retried the same form, because the resume text never said what is accepted.

This plan runs after `gate-routing-negative-control` and uses its `record_exit_status(record) -> int | None`. Read the current file fresh: that plan has already changed `verification_succeeded()`, `blocked_result()` and `classify()`.

## Non-goals

- Do not add `verificationDeferredTo`.
- Do not change `plan_requires_behavioral_tests()`. It passes `{"command": cmd}` without `kind`, so committed contracts keep today's classification.
- Do not apply the denylist to allowlist-matched records (for example `xcodebuild ... test`, `mise run ts-test`). Their behavior must stay identical.
- Do not touch sibling-blocker logic (the next plan), prompts, `workflow.json`, or other files.

## File-level changes

1. `W/scripts/implementation-progress-check.py`
   - Add a module constant `NON_TEST_COMMAND_PATTERNS: tuple[str, ...]`, matched with `re.search(pattern, command.lower())`. Exact coverage:
     - `\bcargo\s+(?:build|check|clippy|fmt|doc)\b`, `\bgo\s+(?:build|vet|fmt)\b`, `\bswift\s+build\b`
     - `\b(?:npm|pnpm|yarn|bun)\s+run\s+(?:build|lint|format|fmt|typecheck|check)\b`
     - `\bmake\s+(?:build|lint|fmt|format|check)\b`
     - `\b(?:tsc|eslint|prettier|rustfmt|gofmt|swiftlint|swiftformat|ruff|black|mypy|shellcheck)\b`
     - `\bgit\s+(?:diff|status|log|show)\b`, `\bdiff\b`, `\bwasm-pack\s+build\b`, `\btree-sitter\s+generate\b`
     - `\bpython(?:3(?:\.\d+)?)?\s+-m\s+(?:json\.tool|py_compile|compileall)\b`
   - Pinned helpers:
     - `declared_behavioral(record: dict) -> bool`: `kind` is a str whose `.strip().lower() == "behavioral-test"`.
     - `allowlisted_test_command(command: str) -> bool`: the existing `test_patterns` match, moved into this helper. Keep the pattern tuple byte-for-byte.
   - `behavioral_kind(record)`:
     1. Keep the swift discovery early `return None`.
     2. If `allowlisted_test_command(command)` -> `"test"`.
     3. Elif `declared_behavioral(record)` and no `NON_TEST_COMMAND_PATTERNS` match -> `"test"`.
     4. Else `None`.
   - `successful_behavioral_verification(record)`: keep the current conjunction. When `declared_behavioral(record) and not allowlisted_test_command(command)`, also require `record_exit_status(record) == 0`, `type(record.get("testsRun")) is int and record["testsRun"] > 0`, and `type(record.get("failureCount")) is int and record["failureCount"] == 0`.
   - `blocked_result()`: replace the resume text for `implementation-materially-unverified`. It must keep the existing sentence start `Run and report verification that exercises the changed implementation before review.` and append:
     - the accepted runner forms: swift test, cargo test, cargo nextest run, go test, pytest, python -m unittest, ctest, bun test, vitest run, npm/pnpm/yarn test, tree-sitter test, deno test, node --test, and task/mise run/make/npm|pnpm|yarn|bun run `<name containing test>`;
     - the structured form `{"kind": "behavioral-test", "exitStatus": 0, "testsRun": >0, "failureCount": 0}` for any other runner;
     - `Build, lint, format and diff commands never count.`
2. `T/test_progress_structured_runner.py`: a new module. Load the script and build envelopes as in `T/test_progress_gate.py`.

## Key points and pitfalls

- `bool` is a subclass of `int`. `testsRun: True` must fail, so use `type(x) is int`.
- `positive_test_count()` already returns False for a zero count. For kind records the strict int checks are added on top; do not remove the existing checks.
- A kind-declared record that fails must make `has_failed_behavioral_evidence` return True, so the branch blocks. Do not silently ignore it.
- `cargo fmt --check` with kind -> not behavioral. It then does not count as failed behavioral evidence either. This is intended: it never counts.
- Compound commands such as `cargo build && node smoke.mjs` with kind are rejected because the denylist hits. This fail-closed choice is accepted in the design.
- Keep codex `test_implementation_progress_check.py::test_bun_custom_runner_does_not_hide_missing_or_failed_tests` and `test_discovery_alone_is_not_behavioral_evidence` green.

## Test cases

- Session-222 record above plus `"kind":"behavioral-test"`, with planned `["cargo test"]` -> `behavioral_kind == "test"`, success True, and classify `status == "ready-for-test-integrity"`.
- The same record without `kind` -> `behavioral_kind is None`, and classify blocks with "positive test count".
- Kind record with `testsRun` 0, testsRun missing, `failureCount` 1, `exitStatus` 1, `testsRun: "2"` or `testsRun: True` -> classify blocks as implementation-materially-unverified.
- Kind + each of `cargo build`, `cargo clippy --all-targets -- -D warnings`, `cargo fmt --check`, `npm run lint`, `git diff --stat`, `tsc --noEmit` -> `behavioral_kind is None`.
- Kind + `node --test x.mjs` (allowlisted), with `outcome "passed"` and testsRun 3 -> still behavioral. Allowlist semantics apply.
- The blocked "no positive count" result's `resumeCriteria[-1]` contains `behavioral-test`, `node --test` and `never count`.

## Done criteria

- [x] All assigned D1 behavior is implemented and the existing allowlist tuple is unchanged; strict kind-only status/count checks and the non-test command exclusion are covered by regression tests.
- [x] Resume criteria name the accepted runner forms, structured behavioral record, and excluded build/lint/format/diff commands.
- [x] Focused structured-runner, opus-luna package, and codex package suites pass; no package `__pycache__` remains and `git diff --check` passes.
- Evidence logs are under `tmp/opus-luna-gate-routing/gate-routing-structured-runner/`.

## Progress log

- 2026-10-24: Implemented D1 in `implementation-progress-check.py`: preserved the allowlist tuple and Swift discovery exclusion, added normalized `behavioral-test` declarations with the D1.3 non-test denylist, required exact integer structured success fields for kind-only records, and expanded the materially-unverified resume criterion. Added `test_progress_structured_runner.py` for session 222, unmarked custom runners, missing/invalid counts including absent `failureCount`/exit status, non-test commands, allowlist behavior and resume text. Also addressed the review feedback about malformed retained commands: `behavioral_kind()` safely handles null/non-string `command`, including through inherited prior-verification evaluation, while kind-only success fails closed.
  - Current verification: focused suite 7 tests, exit 0 (`verify-focused-final2.log`); opus-luna suite 93 tests, exit 0 (`verify-opus-tests-final2.log`); codex suite 91 tests, exit 0 (`verify-codex-tests-final.log`); allowlist comparison exit 0 (`verify-allowlist.log`); no `__pycache__` found (exit 0, `verify-pycache-final.log`); `git diff --check` exit 0 (`verify-diff-check-final2.log`). Structured evidence is in `verification.json`.
  - Superseded attempts retained: initial focused run exposed two fixture expectation errors, corrected in the final suite; first codex invocation yielded before a complete log, then the rerun completed with 91 passing tests.
  - Formal test-integrity/adversarial review and downstream documentation/release work remain with their assigned workflow steps.
