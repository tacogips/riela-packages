# gate-routing-dispatch-amendment

Status: completed. Wave 1. Issues tacogips/riela#132 and #128 (dispatch-time half). Implementation accepted by test-integrity, adversarial and integration review in opus-luna-design-and-implement-review-loop-session-1 (integration-review-attempt-1-exec-93). Archived from `impl-plans/active/gate-routing-dispatch-amendment.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "gate-routing-dispatch-amendment",
  "planPath": "impl-plans/active/gate-routing-dispatch-amendment.md",
  "dependsOn": [],
  "writePaths": [
    "impl-plans/active/gate-routing-dispatch-amendment.md",
    "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/scripts/dispatch-wave.py",
    "packages/opus-luna-design-and-implement-review-loop/tests/test_dispatch_amendment.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "test -x packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/scripts/dispatch-wave.py",
    "cmp packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/scripts/dispatch-plans.py packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/scripts/dispatch-plans.py",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-luna-design-and-implement-review-loop/tests/test_dispatch_amendment.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-luna-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/codex-design-and-implement-review-loop/tests -p 'test_*.py'",
    "find packages/opus-luna-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "New executable W/scripts/dispatch-wave.py wraps the unchanged dispatch-plans.py project(). A normal projection returns project()'s payload plus dispatch_ready true, amendment_required false and amendment_blocked false, with the same three booleans as the when object.",
    "A ValueError whose text starts with dispatch.AMENDMENT returns exit 0 with when.amendment_required true (amendmentRound < 2) or when.amendment_blocked true (amendmentRound >= 2). The payload keys equal AMENDMENT_PAYLOAD_KEYS, including top-level acceptedPlanIds, manifestPath and checkpointCommit, plus checkpointAmendment with reason, error, unmatchedPaths, ownerCandidates, findings, manifestPath, previousCheckpointCommit, amendmentRound and maxAmendmentRounds.",
    "Every other ValueError, JSON error or OSError prints {error} to stderr and exits 1.",
    "dispatch-plans.py stays byte-identical to the Codex base (cmp exit 0).",
    "test_dispatch_amendment.py covers design Verification 5 and the dispatch-time over-cap case from Verification 4, and passes. Opus-luna and codex package tests pass and no __pycache__ remains."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-luna-gate-routing-0110.md` D5. `W`/`T` as in `impl-plans/active/gate-routing-negative-control.md`.

Session 271: integration review routed findings on `editor/src/code/pointer.ts`, `editor/test/e2e/behavior.mjs`, `editor/test/e2e/ios-sim.mjs` and `editor/test/e2e/measure.mjs`. Those paths lie outside every pending plan's `writePaths`, so `dispatch-plans.py` raised `bounded checkpoint amendment required before redispatch: ...` at lines 740-745. The node exited 1 and the session failed as `provider_error`. Preflight snapshot violations (#128) raise the same `AMENDMENT` prefix (lines 199-239 and 379-404, raised at 695).

`dispatch-plans.py` must not change. `packages/codex-design-and-implement-review-loop/tests/test_artifact_roots.py::test_dispatch_scripts_stay_identical` requires byte identity, and `test_dispatch_evidence_root.py:317` expects `project()` to raise. Routing therefore lives in this wrapper. `gate-routing-graph` points `node-dispatch-plans.json` at it, adds the routes and extends the schema with exactly `AMENDMENT_PAYLOAD_KEYS`.

## Non-goals

- Do not edit `dispatch-plans.py`, `workflow.json`, node files, prompts or mocks.
- Do not widen `writePaths` automatically. Do not treat non-amendment errors as routes.

## File-level changes

1. `W/scripts/dispatch-wave.py`: a new file, mode 755, standard library only.
   - Imitate `W/scripts/validate-plan-contract.py` (as copied from `packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/scripts/validate-plan-contract.py`): `load_dispatch_module()` uses `importlib` to load `Path(__file__).resolve().with_name("dispatch-plans.py")`, and `main()` reads one stdin line.
   - Pinned module constants:
     - `MAX_CHECKPOINT_AMENDMENTS = 2`
     - `CHECKPOINT_STEPS = ("plan-git-push", "plan-git-commit", "plan-push-gate")`
     - `UNMATCHED_MARKER = "outside manifest writePaths: "`
     - `FINDINGS_CAP = 20`
     - `ROUTE_KEYS = ("dispatch_ready", "amendment_required", "amendment_blocked")`
     - `AMENDMENT_PAYLOAD_KEYS = ("dispatch_ready", "amendment_required", "amendment_blocked", "acceptedPlanIds", "manifestPath", "checkpointCommit", "checkpointAmendment", "pendingPlanIds", "blockedPlanIds", "successfulPlanIds", "issueReference", "blockers", "resumeCriteria", "nextStep")`
   - Pinned `route(envelope: dict) -> dict`:
     - Call `dispatch.project(envelope)`. On success, return `{"when": flags, "payload": {**projected["payload"], **flags}}`.
     - On `ValueError` whose text starts with `dispatch.AMENDMENT`, build the amendment result. Any other error propagates.
   - Amendment result:
     - **Checkpoint.** `root = Path.cwd().resolve()`, `messages = dispatch.messages_from(envelope)`, `(manifest_path, commit) = dispatch.checkpoint_source(messages, root)` (a raise here propagates and gives exit 1). Read the manifest JSON from `root / manifest_path`.
     - **Plan ID sets.**
       - `accepted` = the strings in `dispatch.latest_value(messages, "acceptedPlanIds")`, or `[]`.
       - `pending` = manifest plan IDs not in `accepted`, in manifest order.
       - `blockedPlanIds = pending`, `successfulPlanIds` = the accepted IDs.
     - **Reason and paths.**
       - `reason = "integration-paths-outside-writePaths" if UNMATCHED_MARKER in text else "tracking-contract"`.
       - `unmatchedPaths` = `sorted(p.strip() for p in text.split(UNMATCHED_MARKER, 1)[1].split(", "))` when the marker is present, else `[]`.
       - `ownerCandidates` = `[{"path": p, "plans": [{"planId": id, "accepted": id in accepted}...]}]` for manifest plans whose `writePaths` own `p` (`dispatch.path_is_owned`).
     - **Findings.** From `dispatch.latest_integration_feedback(messages)` (None -> `[]`), take findings whose `file` or `filePath` is in `unmatchedPaths`, capped at `FINDINGS_CAP`.
     - **Amendment round.** `amendmentRound` = `max(0, len(distinct str payload.git.commitHash over messages whose fromStepId is in CHECKPOINT_STEPS) - 1)`.
     - **Route.** `required = amendmentRound < MAX_CHECKPOINT_AMENDMENTS`. flags = `{dispatch_ready: False, amendment_required: required, amendment_blocked: not required}`.
     - **Issue reference.** `issueReference` = `dispatch.issue_reference(...)` on the manifest `reviewContext.issueReference`, or on `{"communicationId": reviewContext.intakeCommunicationId}`. On a `ValueError`, fall back to `str(manifest.get("taskId") or manifest_path)`.
     - **Blockers.** `[{"type": "checkpoint-amendment-required" | "checkpoint-amendment-exhausted", "dependency": manifest_path, "planIds": pending, "paths": unmatchedPaths, "message": text}]`.
     - **Resume criteria and next step.**
       - When required: resumeCriteria `["Amend the dispatch manifest so every listed path is owned by a pending plan's writePaths, or narrow/reclassify tracked paths, then repeat Step 5 review and the plan checkpoint before redispatch."]`, nextStep `"step4-impl-plan-create: bounded checkpoint amendment"`.
       - When blocked: resumeCriteria `["Operator: amend <manifest_path> so the listed paths are owned or narrowed, commit a new plan checkpoint, and start a resume run."]`, and a nextStep that lists the paths, or the error text when there are none.
     - **Payload.** Exactly `AMENDMENT_PAYLOAD_KEYS`, with `manifestPath = manifest_path` and `checkpointCommit = commit`, both top-level and inside `checkpointAmendment` (`previousCheckpointCommit = commit`).
   - `main()` prints compact JSON (`separators=(",",":")`, `ensure_ascii=False`) and returns 0. On `ValueError`, `OSError` or `json.JSONDecodeError` it prints `{"error": str}` to stderr and returns 1.
2. `T/test_dispatch_amendment.py`: a new module.
   - Fixture: build a temp git repo like `T/test_git_push_gate.py::test_dispatch_accepts_the_local_only_checkpoint` and `packages/codex-design-and-implement-review-loop/tests/test_dispatch_evidence_root.py`.
     - The committed manifest has `reviewContext`, `evidenceRoot`, `implementationBranch`, `baseBranch` and `remote`, and plans P1 (`writePaths ["src/a"]`) and P2 (`["src/b"]`).
     - The inbox has a `plan-push-gate` message carrying `git.commitHash` = HEAD and `committedFiles` = [manifest].
   - Restore cwd in cleanup.

## Key points and pitfalls

- Detect amendments only by the `dispatch.AMENDMENT` prefix. Never by catching every `ValueError`: unknown accepted IDs and bad push receipts must still exit 1.
- `blockedPlanIds` must be non-empty. `project()` raises a non-amendment error before any amendment when every plan is accepted, so `pending` is never empty on this route.
- Payload keys must be exactly `AMENDMENT_PAYLOAD_KEYS`. The graph plan's schema is `additionalProperties: false`.
- Count distinct commit hashes, not messages. A push run delivers one message per checkpoint.
- Do not mutate git or the manifest.

## Test cases

- Session-271 shape: an `integration-review` message with `needs_revision: true`, `acceptedPlanIds ["P1"]` and high findings `{file:"editor/src/code/pointer.ts"}`, `{file:"editor/test/e2e/behavior.mjs"}` -> exit 0 and `when == {dispatch_ready:False, amendment_required:True, amendment_blocked:False}`. `unmatchedPaths` lists both, `findings` has 2 entries, `checkpointAmendment.amendmentRound == 0`, `manifestPath` and `checkpointCommit` are top-level, and the payload keys equal `AMENDMENT_PAYLOAD_KEYS`.
- The same, plus checkpoint messages carrying 3 distinct commit hashes -> `amendment_blocked`, `blockedPlanIds == ["P2"]`, and non-empty `blockers`, `resumeCriteria` and `nextStep`.
- #128 at dispatch: P2 `sharedPaths ["src/big"]` with 600 files created after the commit -> `amendment_required`, reason `tracking-contract`, and the error contains `limit 512`.
- `acceptedPlanIds ["nope"]` -> `route` raises, and `main()` returns 1.
- A clean manifest with no feedback -> payload equals `project()` payload plus the three flags, with `dispatch_ready` True.
- `dispatch-plans.py` bytes equal the Codex copy.

## Done criteria

- `dispatch-wave.py` is executable and routes normal projection plus bounded amendment results with exact payload keys; only `dispatch.AMENDMENT` errors are routed.
- Regression tests cover the session-271 shape, amendment exhaustion, dispatch-time 512-entry over-cap, non-amendment errors and byte identity.
- Focused tests, opus-luna package tests, codex package tests, no-`__pycache__` check, and `git diff --check` pass on the source snapshot used for final verification.
- Complete command logs and exit statuses are under `tmp/opus-luna-gate-routing/gate-routing-dispatch-amendment/`.

## Progress log

- 2026-10-24: Added executable `dispatch-wave.py` and six regression tests. Focused suite passed (6 tests); executable check, dispatch byte comparison and codex package suite passed. The first full opus-luna package run was on the moving shared tree and reported 2 failures plus 1 error in the concurrent `test_progress_negative_control.py`; the subsequent source-stable rerun passed all 86 tests with exit 0 (`opus-tests-rerun.log`). The earlier failure remains recorded as moving-tree evidence. Final verification after the OSError assertion passed focused tests (6), opus-luna tests (86) and codex tests (91), with executable, byte-identity, no-`__pycache__` and diff checks passing; complete logs use the `verified-` prefix in the plan-local evidence directory.
