# gate-routing-contract-gate

Status: completed. Wave 1. Issue tacogips/riela#128 (pre-commit half). Implementation accepted by test-integrity, adversarial and integration review in opus-terra-design-and-implement-review-loop-session-1 (integration-review-attempt-1-exec-93). Archived from `impl-plans/active/gate-routing-contract-gate.md`; the dispatch record keeps the historical active path.

```json
{
  "planId": "gate-routing-contract-gate",
  "planPath": "impl-plans/active/gate-routing-contract-gate.md",
  "dependsOn": [],
  "writePaths": [
    "impl-plans/active/gate-routing-contract-gate.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/validate-plan-contract.py",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/nodes/node-plan-contract-validate.json",
    "packages/opus-terra-design-and-implement-review-loop/tests/test_plan_contract_gate.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "cmp packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/scripts/validate-plan-contract.py packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/validate-plan-contract.py",
    "cmp packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/nodes/node-plan-contract-validate.json packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/nodes/node-plan-contract-validate.json",
    "test -x packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/validate-plan-contract.py",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_plan_contract_gate.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s packages/opus-terra-design-and-implement-review-loop/tests -p 'test_*.py' -v",
    "find packages/opus-terra-design-and-implement-review-loop -name __pycache__",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "W/scripts/validate-plan-contract.py and W/nodes/node-plan-contract-validate.json are byte-identical copies of the Codex base files (cmp exit 0), and the script is executable (mode 755).",
    "test_plan_contract_gate.py covers: byte identity of both files; a pending plan whose sharedPaths directory expands past 512 entries -> when {contract_valid:false}, payload.needs_revision true, and findings naming the plan ID and directory with targetStep step4-impl-plan-create; a valid manifest -> when {contract_valid:true}, with commitMessage/committedFiles passed through unchanged.",
    "dispatch-plans.py is not modified. All opus-terra package tests pass and no __pycache__ remains."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Design: `design-docs/specs/design-opus-terra-gate-routing-0110.md` D4 (#128). `W`/`T` as in `impl-plans/active/gate-routing-negative-control.md`.

Session 226 failed at dispatch of its last wave with `fanout snapshot exceeds 512 entries`, after five hours of accepted waves. The Codex base already validates the written manifest before the checkpoint commit with `plan-contract-validate`. This plan ports that gate unchanged. `gate-routing-graph` wires it into `workflow.json`, and `gate-routing-planning-prompts` ports the Step 4 rule. The dispatch-time over-cap case (#128 at dispatch) belongs to `gate-routing-dispatch-amendment`.

## Non-goals

- Do not edit the copied files. Byte identity is a criterion.
- Do not edit `workflow.json`, prompts, mocks or `dispatch-plans.py`.
- Do not test the dispatch-time wrapper here.

## File-level changes

1. Copy `packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/scripts/validate-plan-contract.py` to `W/scripts/validate-plan-contract.py` byte for byte, and set mode 755.
2. Copy `packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/nodes/node-plan-contract-validate.json` to `W/nodes/node-plan-contract-validate.json` byte for byte.
3. `T/test_plan_contract_gate.py`: a new module.
   - Load `W/scripts/validate-plan-contract.py` with `importlib`. It loads its sibling `dispatch-plans.py` itself.
   - Use a temp dir, and `os.chdir` with cleanup, because the gate uses `Path.cwd()`.
   - Each envelope has one `plan-checkpoint` message: `{"manifestPath":"impl-plans/active/t-dispatch.json","commitMessage":"m","committedFiles":["impl-plans/active/t-dispatch.json"],"checkpoint_blocked":false,"status":"ready","blockers":[]}`.
   - The manifest has one plan `CMP-40`, with `writePaths ["src/closeout.md"]` and `sharedPaths ["src"]`. `src/` contains 600 files.
   - Imitate the fixtures in `packages/codex-design-and-implement-review-loop/tests/test_artifact_roots.py`, which test the Codex copy of this gate.

## Key points and pitfalls

- Copy the bytes; do not retype. `cmp` must pass.
- The gate reads the *working-tree* manifest. No git repo is needed for these tests.
- Restore cwd in `addCleanup`.

## Test cases

- Byte identity: both files equal their Codex sources.
- 600-file `src` -> `when == {"contract_valid": False}`, `payload.needs_revision is True`, and a finding message contains `CMP-40` and `'src'` with `limit 512`.
- `sharedPaths []` -> `when == {"contract_valid": True}`, and `payload.commitMessage == "m"` with the same `committedFiles`.

## Done criteria

- Complete: the copied files are byte-identical, executable mode is 755, regression cases pass, `dispatch-plans.py` is unchanged, package discovery passes, and no package `__pycache__` remains. Stable-tree test evidence is in `tmp/opus-terra-gate-routing/gate-routing-contract-gate/final-focused-tests-rerun-02.log` and `final-package-tests-rerun-02.log`; command-level evidence is in the adjacent `final-*.log` files.

## Progress log

- (implementer appends dated entries)
- 2026-10-24 Step 6: added the Codex-identical executable contract validator and node plus the focused regression module. Focused gate tests passed 3/3 (`tmp/opus-terra-gate-routing/gate-routing-contract-gate/focused-tests.log`). Script/node identity, executable mode 755, unchanged dispatch-plans identity, no package `__pycache__`, and `git diff --check` passed (individual logs in the same evidence directory). Full package suite ran 52 tests: 51 passed, one failed in `test_planning_prompts.py::PlanningPromptContractTests::test_checkpoint_amendment_preserves_checkpoint_boundary`; concurrent prompt text says “amend the existing dispatch manifest in place” but its test expects “update the existing dispatch manifest in place” (`package-tests.log`). Both files are outside this plan's writePaths and were left untouched; full suite requires stable-tree rerun.
- 2026-10-24 Step 6 rerun: package test discovery changed to 81 tests and failed with 3 failures/2 errors (`tmp/opus-terra-gate-routing/gate-routing-contract-gate/package-tests-rerun-01.log`): dispatch-amendment missing Codex reference path and round assertion, archive fourth-message assertion, and two negative-control assertions. These files are outside this plan's writePaths and were left untouched. Package-wide verification remains incomplete pending a stable combined tree; the assigned focused tests and copy/mode checks pass.
- 2026-10-24 Step 6 stable-tree rerun: focused contract tests passed 3/3 (`tmp/opus-terra-gate-routing/gate-routing-contract-gate/final-focused-tests-rerun-02.log`); package discovery passed 86/86 (`final-package-tests-rerun-02.log`). Validator script and node byte-identity checks, executable mode, and unchanged `dispatch-plans.py` passed (`final-cmp-script-rerun-02.log`, `final-cmp-node-rerun-02.log`, `final-exec-mode-rerun-02.log`, `final-dispatch-unchanged-rerun-02.log`); final package `__pycache__` inventory was empty (`final-no-pycache-rerun-04.log`) and `git diff --check` passed (`final-diff-check-rerun-02.log`). Earlier failures remain in the prior log entries; this stable combined tree run resolves package verification.
