# gate-routing-release

Status: active. Wave 4 (last). Package release 0.1.10 for tacogips/riela #125, #126, #128, #129, #132, #134.

```json
{
  "planId": "gate-routing-release",
  "planPath": "impl-plans/active/gate-routing-release.md",
  "dependsOn": ["gate-routing-sibling-blockers", "gate-routing-graph", "gate-routing-planning-prompts", "gate-routing-runtime-prompts"],
  "writePaths": [
    "impl-plans/active/gate-routing-release.md",
    "packages/opus-luna-design-and-implement-review-loop/riela-package.json",
    "registry-index.json"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "find packages/opus-luna-design-and-implement-review-loop -name __pycache__",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-luna-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'",
    "riela workflow validate opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows",
    "bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-luna-design-and-implement-review-loop",
    "mise run package:check-digests",
    "mise run package:check-index",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "riela-package.json version is 0.1.10, and its checksum and integrity are refreshed by update-package-digests.ts after every other package edit. registry-index.json carries the matching version and digests.",
    "mise run package:check-digests exits 0. mise run package:check-index exits 0; if it reports a stale index, run mise run package:generate-index once, then rerun it.",
    "Final opus-luna and codex unit test runs exit 0 with failureCount 0, and riela workflow validate is valid. No __pycache__ exists in the package before or after the digest refresh."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-luna-gate-routing-0110.md` D7 (release). Every other plan has been accepted by integration review before this wave starts.

A stray `__pycache__`, or any edit after the digest refresh, breaks the package checksum, so this plan runs last and changes nothing else.

## Non-goals

- Do not edit any package file other than `riela-package.json`. Do not edit other packages' entries in `registry-index.json`.
- Do not archive plans or edit `impl-plans/README.md`. That happens in Step 8 and `plan-archive`.
- No push, merge or tag (`gitPush=false`).

## File-level changes

1. `packages/opus-luna-design-and-implement-review-loop/riela-package.json`: change `"version": "0.1.9"` to `"0.1.10"`. Leave every other field to the digest script.
2. Run `find packages/opus-luna-design-and-implement-review-loop -name __pycache__`. It must print nothing; if it prints anything, delete only those directories.
3. Run `bun .agents/skills/riela-package-release/scripts/update-package-digests.ts opus-luna-design-and-implement-review-loop`. It refreshes `checksum`/`integrity` and the registry entry.
4. Confirm that `registry-index.json` shows `0.1.10` with the new digests for this package only (`git diff registry-index.json`).
5. Run `mise run package:check-digests` and `mise run package:check-index`.

## Key points and pitfalls

- Run every Python command with `PYTHONDONTWRITEBYTECODE=1`, before and after the refresh.
- If any verification fails, do not hand-edit digests. Report a blocker with the exact command and log path.
- Imitate `impl-plans/completed/wave-release.md`, the 0.1.9 release.

## Test cases

- `python3 -c "import json;print(json.load(open('packages/opus-luna-design-and-implement-review-loop/riela-package.json'))['version'])"` -> `0.1.10`.
- `mise run package:check-digests` -> exit 0.

## Done criteria

- All verification commands exit 0. Evidence logs, with integer exitStatus and, for the unit test runs, testsRun and failureCount, are under `tmp/opus-luna-gate-routing/gate-routing-release/`.

## Progress log

- (implementer appends dated entries)
