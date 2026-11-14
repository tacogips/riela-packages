# gate-routing-release

Status: completed. Wave 4 (last). Package release 0.1.10 for tacogips/riela #125, #126, #128, #129, #132, #134. Implementation accepted by test-integrity (exec-88), adversarial (exec-89) and integration review (integration-review-attempt-1-exec-93) in opus-terra-design-and-implement-review-loop-session-1. Archived from `impl-plans/active/gate-routing-release.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "gate-routing-release",
  "planPath": "impl-plans/active/gate-routing-release.md",
  "dependsOn": ["gate-routing-sibling-blockers", "gate-routing-graph", "gate-routing-planning-prompts", "gate-routing-runtime-prompts"],
  "writePaths": [
    "impl-plans/active/gate-routing-release.md",
    "packages/opus-terra-design-and-implement-review-loop/riela-package.json",
    "registry-index.json"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "find packages/opus-terra-design-and-implement-review-loop -name __pycache__",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'",
    "riela workflow validate opus-terra-design-and-implement-review-loop --workflow-definition-dir packages/opus-terra-design-and-implement-review-loop/workflows",
    "bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-terra-design-and-implement-review-loop",
    "mise run package:check-digests",
    "mise run package:check-index",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "riela-package.json version is 0.1.10, and its checksum and integrity are refreshed by update-package-digests.ts after every other package edit. registry-index.json carries the matching version and digests.",
    "mise run package:check-digests exits 0. mise run package:check-index exits 0; if it reports a stale index, run mise run package:generate-index once, then rerun it.",
    "Final opus-terra and codex unit test runs exit 0 with failureCount 0, and riela workflow validate is valid. No __pycache__ exists in the package before or after the digest refresh."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-terra-gate-routing-0110.md` D7 (release). Every other plan has been accepted by integration review before this wave starts.

A stray `__pycache__`, or any edit after the digest refresh, breaks the package checksum, so this plan runs last and changes nothing else.

## Non-goals

- Do not edit any package file other than `riela-package.json`. Do not edit other packages' entries in `registry-index.json`.
- Do not archive plans or edit `impl-plans/README.md`. That happens in Step 8 and `plan-archive`.
- No push, merge or tag (`gitPush=false`).

## File-level changes

1. `packages/opus-terra-design-and-implement-review-loop/riela-package.json`: change `"version": "0.1.9"` to `"0.1.10"`. Leave every other field to the digest script.
2. Run `find packages/opus-terra-design-and-implement-review-loop -name __pycache__`. It must print nothing; if it prints anything, delete only those directories.
3. Run `bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-terra-design-and-implement-review-loop`. It refreshes `checksum`/`integrity` and the registry entry.
4. Confirm that `registry-index.json` shows `0.1.10` with the new digests for this package only (`git diff registry-index.json`).
5. Run `mise run package:check-digests` and `mise run package:check-index`.

## Key points and pitfalls

- Run every Python command with `PYTHONDONTWRITEBYTECODE=1`, before and after the refresh.
- If any verification fails, do not hand-edit digests. Report a blocker with the exact command and log path.
- Imitate `impl-plans/completed/wave-release.md`, the 0.1.9 release.

## Test cases

- `python3 -c "import json;print(json.load(open('packages/opus-terra-design-and-implement-review-loop/riela-package.json'))['version'])"` -> `0.1.10`.
- `mise run package:check-digests` -> exit 0.

## Done criteria

- Final-source release verification passes. Evidence logs, with integer exitStatus and, for the unit test runs, testsRun and failureCount, are under `tmp/opus-terra-gate-routing/gate-routing-release/`.
- The package is at version 0.1.10 with refreshed checksum/integrity, the matching registry entry, and no package `__pycache__`.
- Formal test-integrity, adversarial and integration reviews remain downstream workflow steps.

## Progress log

- 2026-10-24: Confirmed all four dependencies are accepted in the runtime fanout item. On the combined tree, opus-terra tests passed (108/0), codex tests passed (91/0), workflow validation was valid, all four mocks exited 0 with transition counts 27/27/24/15 (node execution counts 28/28/25/16), workflow:check-compact passed 30 regressions, and no package `__pycache__` was found. Logs: `tmp/opus-terra-gate-routing/gate-routing-release/attempt-1/`.
- 2026-10-24: Bumped `riela-package.json` to 0.1.10, refreshed checksum/integrity with `update-package-digests.ts`, and regenerated `registry-index.json` once after `package:check-index` found it stale. Final `package:check-digests`, `package:check-index`, registry-entry comparison, version check, `git diff --check`, and package `__pycache__` check pass. The first index check was exit 1 and was resolved by regeneration; its log remains `attempt-1/check-index.log`.
- 2026-10-24: Carry the expected-routes dependency `{dependency: ".agents/skills/riela-package-release/fixtures/expected-routes.json", reason: "route gains plan-contract-validate and plan-archive", owner: "operator"}` as an operator risk. The fixture is outside this plan's writePaths and user-qa option A expects the route assertion to remain stale until operator follow-up. No push, merge or tag performed; formal review and integration remain downstream.
- 2026-10-24: Post-digest final-source rerun passed: opus-terra 108 tests/0 failures, codex 91/0, workflow validate `valid:true`, no `__pycache__`, and `git diff --check` clean. Logs: `tmp/opus-terra-gate-routing/gate-routing-release/attempt-1/{opus-final,codex-final,validate-final,pycache-postfinal,diffcheck-postfinal}.log`.
