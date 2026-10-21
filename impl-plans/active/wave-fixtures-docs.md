# wave-fixtures-docs

Status: proposed for Step 5 review.

```json
{
  "planId": "wave-fixtures-docs",
  "planPath": "impl-plans/active/wave-fixtures-docs.md",
  "dependsOn": [],
  "writePaths": [
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-fanout.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-local.json",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/EXPECTED_RESULTS.md",
    "packages/opus-luna-design-and-implement-review-loop/README.md",
    "packages/opus-luna-design-and-implement-review-loop/skills/claude/opus-luna-design-and-implement-review-loop/SKILL.md"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "progressFile": "tmp/wave-compaction/wave-fixtures-docs/progress.json",
  "verification": [
    "python3 -m json.tool packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario.json",
    "python3 -m json.tool packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-fanout.json",
    "python3 -m json.tool packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-local.json",
    "riela workflow run opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows --working-dir . --mock-scenario packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario.json --session-store tmp/wave-compaction/wave-fixtures-docs/attempt-N/sessions/default --artifact-root tmp/wave-compaction/wave-fixtures-docs/attempt-N/artifacts/default --output json",
    "riela workflow run opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows --working-dir . --mock-scenario packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-fanout.json --session-store tmp/wave-compaction/wave-fixtures-docs/attempt-N/sessions/fanout --artifact-root tmp/wave-compaction/wave-fixtures-docs/attempt-N/artifacts/fanout --output json",
    "riela workflow run opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows --working-dir . --mock-scenario packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-local.json --variables '{\"workflowInput\":{\"gitPush\":false}}' --session-store tmp/wave-compaction/wave-fixtures-docs/attempt-N/sessions/local --artifact-root tmp/wave-compaction/wave-fixtures-docs/attempt-N/artifacts/local --output json",
    "riela workflow run opus-luna-design-and-implement-review-loop --workflow-definition-dir packages/opus-luna-design-and-implement-review-loop/workflows --working-dir . --mock-scenario packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/mock-scenario-planning-only.json --session-store tmp/wave-compaction/wave-fixtures-docs/attempt-N/sessions/planning-only --artifact-root tmp/wave-compaction/wave-fixtures-docs/attempt-N/artifacts/planning-only --output json",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-luna-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "In mock-scenario.json, mock-scenario-fanout.json and mock-scenario-local.json the implementation-wave-outcome response has model 'scripts/implementation-wave-outcome.py' and when {implementation_blocked:false, partial_success:false}. Payloads and all other entries are unchanged. mock-scenario-planning-only.json is unchanged.",
    "All four mock scenarios complete (status completed, exit 0). mock-scenario.json's route equals the 26-step expected-routes entry, and mock-scenario-local.json still has 23 executions.",
    "EXPECTED_RESULTS.md line 28 states implementation-wave-outcome is a deterministic command and line 42 excludes it and the reconcile/integration-review prompts from the shared-with-Codex statement. A new paragraph documents the wave summary path, bounds, verdict binding and the open Q1 persistent-request-variable limitation.",
    "Package README.md has a node-table row for implementation-wave-outcome (command, scripts/implementation-wave-outcome.py) and a 'Compact wave summary' section naming tmp/opus-luna-waves/<workflowExecutionId>/wave-NNN/{fanout-join.json,wave-summary.json}, the 64 KiB bound and the Q1 limitation. SKILL.md's 'GPT-6 Luna fanout' section has a matching short paragraph."
  ]
}
```

## Intent and context

Issue `workflowInput:opus-luna-wave-input-compaction`, mode `issue-resolution`. Accepted design: `design-docs/specs/design-opus-luna-wave-input-compaction.md` (D6, Verification commands). This plan updates the mock fixtures and the user-facing documentation for the deterministic wave-outcome command and the compact wave summary. Mock scenarios answer every node by node id and execute no scripts, so the fixture edits are labels and routing flags only. `W` = `packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop`.

## Non-goals

- Do not change any mock payload or route.
- Do not add or remove mock entries.
- Do not edit `mock-scenario-planning-only.json`, `workflow.json`, nodes, prompts, scripts, tests, `riela-package.json`, `registry-index.json`, the root `README.md`, `.agents/` (including `expected-routes.json`), or other packages.
- Do not claim in the docs that later steps' prompts are bounded. The docs must state the Q1 limitation.

## File-level changes

1. In the three mock scenario files, the `"implementation-wave-outcome"` object (`mock-scenario.json` around line 806, `mock-scenario-fanout.json` around line 867, `mock-scenario-local.json` around line 774):
   - Change `"model": "claude-opus-5-5"` to `"model": "scripts/implementation-wave-outcome.py"`. Imitate the `plan-push-gate` entry, which uses `"model": "scripts/git-push-gate.py"`.
   - Add `"partial_success": false` to its `when`.
   - Keep 2-space indentation and the existing key order. Edit by targeted text replacement, not by reserializing the whole file, so unrelated formatting does not churn.
2. `W/EXPECTED_RESULTS.md`
   - Line 28: keep the sentence's meaning for the agent nodes, and add that `implementation-wave-outcome` is a deterministic command (`scripts/implementation-wave-outcome.py`), not an agent.
   - Line 42: add that `implementation-wave-outcome` (now a command) and the `reconcile-implementations` and `integration-review` prompts diverge from the Codex base.
   - Append one paragraph:
     - The join command writes `fanout-join.json` and `wave-summary.json` under `tmp/opus-luna-waves/<workflowExecutionId>/wave-NNN/`.
     - Summary ≤ 49152 bytes and verdict ≤ 16384 bytes.
     - Reconciliation and integration review locate the highest wave and require `verdict` equality.
     - Mock scenarios do not execute the command.
     - Riela 0.2.34 still renders the persistent `fanoutJoin` request variable into later agent prompts. This is pending decision Q1 (`design-docs/user-qa/opus-luna-wave-input-compaction.md`).
3. `packages/opus-luna-design-and-implement-review-loop/README.md`
   - Add a table row ``| Wave aggregation (fanout join) | `implementation-wave-outcome` | `command` / `scripts/implementation-wave-outcome.py` |`` after the Implementation row.
   - Add a short `## Compact wave summary` section with the same facts as the EXPECTED_RESULTS paragraph.
4. `packages/opus-luna-design-and-implement-review-loop/skills/claude/opus-luna-design-and-implement-review-loop/SKILL.md`: in `## GPT-6 Luna fanout`, append 2-4 sentences giving the wave-summary location and telling the operator to inspect it (not the raw join) when reporting a wave, plus the Q1 limitation.

## Key pitfalls

- The `when` keys must include `implementation_blocked:false` and `partial_success:false`. The transition `!(implementation_blocked) || partial_success` must still route to reconcile.
- `tests/test_git_push_gate.py` asserts that `mock-scenario-local.json` has no `plan-git-push`, `step11-git-push` or `base-branch-integrate` keys. Keep it that way.
- The workflow run's `--workflow-definition-dir` is the package `workflows` directory (the parent of the bundle), and the workflow id is positional. This matches `.agents/skills/riela-package-release/scripts/check-package-compat.ts`.
- If the `riela` CLI is unavailable or fails for environmental reasons, record a blocked check with the exact command, exit code and log. Do not mark it passed.

## Test and assertion cases (`situation -> expected`)

- `mock-scenario.json` run -> `status: completed`. The `session.executions[].stepId` route equals the opus-luna entry in `.agents/skills/riela-package-release/fixtures/expected-routes.json` (26 steps). The `implementation-wave-outcome` acceptedOutput payload contains the six fields.
- `mock-scenario-fanout.json` run -> completed, and two branches join in input order.
- `mock-scenario-local.json` run with `gitPush:false` -> completed with 23 executions, and `workflow-output` reports `mergeStatus: local-only`.
- `mock-scenario-planning-only.json` run -> completed, and no `implementation-wave-outcome` execution.
- Package unittest discover -> exit 0.

## Execution, drift and progress contract

- Write only the six `writePaths`. Before each edit, freshly read the file. Record its SHA-256 and an intent note under `tmp/wave-compaction/wave-fixtures-docs/attempt-N/intent/`, re-check the hash before writing, reconcile on drift, and record post-hashes.
- Replace `attempt-N` in the commands with the actual unused attempt number, and record the exact argv.
- Save each run's complete JSON output and stderr, its exit code, and the extracted route under the attempt directory.
- Maintain `progress.json` and `handoff.json`. Run everything in the foreground from the repository root.
- No git mutations.

## Completion criteria

All acceptance criteria are evidenced by saved run outputs and diffs. A blocked CLI check is reported as blocked, not passed. No open high or mid finding remains.

## Operator amendment (2026-10-22, rerun after session-476)

Attempt 1 was blocked by workflow bookkeeping, not by this plan's code: the
installed progress gate did not recognize `python3 -m unittest` as a
behavioral test runner. That gate is fixed in cfa5880 and the rerun uses the
fixed gate. The attempt-1 implementation is still in the working tree; reuse
it, re-run this plan's verification, and report each test command with an
integer `exitCode`, `testsRun` and `failureCount`. The package suite currently
passes (31 tests, including `tests/test_progress_check.py`).
