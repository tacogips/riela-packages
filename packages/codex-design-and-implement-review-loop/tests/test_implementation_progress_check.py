"""Regression checks for bounded branch-local implementation continuation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "workflows/codex-design-and-implement-review-loop/scripts/implementation-progress-check.py"
)
SPEC = importlib.util.spec_from_file_location("implementation_progress_check", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(progress)


def attempt(number: int, *, incomplete: bool = True) -> dict:
    return {
        "planId": "p1-dispatch",
        "implementation_blocked": False,
        "implementationIncomplete": incomplete,
        "blockers": [],
        "changedFiles": ["Sources/RielaCLI/TaskDispatch.swift"],
        "implPlanUpdates": [{"path": "impl-plans/progress/p1-dispatch.md", "attempt": number}],
        "verification": [{
            "command": "swift test --filter CancellationTests",
            "exitCode": 0,
            "testsRun": number,
            "failureCount": 0,
        }],
        "authorSelfCheck": {"verificationGaps": ["Live cancellation still pending"] if incomplete else []},
    }


def envelope(*outputs: dict) -> dict:
    return {
        "input": {
            "_rielaInput": {
                "messages": [
                    {"fromStepId": "step6-implement", "payload": output, "createdOrder": index}
                    for index, output in enumerate(outputs)
                ]
            }
        }
    }


class ImplementationContinuationTests(unittest.TestCase):
    def baseline_case(self, *, identical: bool = True, failures: int = 11, extra_failure: bool = False):
        scratch_root = Path(__file__).resolve().parents[3] / "tmp"
        scratch_root.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=scratch_root)
        root = Path(temporary.name)
        evidence = root / "tmp"
        evidence.mkdir()
        (evidence / "aggregate.log").write_text("11 failing assertions; retained failed aggregate\n")
        (evidence / "baseline.log").write_text("11 matching checkpoint assertions\n")
        (evidence / "comparison.json").write_text(json.dumps({
            "identical": identical,
            "aggregateAssertionCount": failures,
            "baselineAssertionCount": 11,
            "aggregateOnly": ["new regression"] if extra_failure else [],
            "baselineOnly": [],
            "aggregateLog": "tmp/aggregate.log",
            "baselineLog": "tmp/baseline.log",
        }))
        completed = attempt(1, incomplete=False)
        completed["verification"].append({
            "command": "swift test --filter 'RielaGraphQLTests|RielaAppSupportTests'",
            "exitCode": 1,
            "testsRun": 1469,
            "failureCount": 11,
            "comparison": "tmp/comparison.json",
            "log": "tmp/aggregate.log",
        })
        return temporary, root, completed

    def test_workflow_routes_continuation_before_reviews(self) -> None:
        workflow_path = SCRIPT.parents[1] / "workflow.json"
        workflow = json.loads(workflow_path.read_text())
        step = next(step for step in workflow["steps"] if step["id"] == "implementation-progress-check")
        self.assertEqual(
            [(transition["label"], transition["toStepId"]) for transition in step["transitions"]],
            [
                ("implementation_continue", "step6-implement"),
                ("implementation_blocked", "implementation-wave-outcome"),
                ("!(implementation_blocked || implementation_continue)", "step6-test-integrity-check"),
            ],
        )

    def test_first_and_second_productive_partial_continue(self) -> None:
        first = progress.classify(envelope(attempt(1)))
        self.assertEqual(first["when"], {"implementation_continue": True})
        self.assertEqual(first["payload"]["continuationAttempt"], 1)

        second = progress.classify(envelope(attempt(1), attempt(2)))
        self.assertEqual(second["when"], {"implementation_continue": True})
        self.assertEqual(second["payload"]["continuationAttempt"], 2)

    def test_third_incomplete_attempt_stops(self) -> None:
        result = progress.classify(envelope(attempt(1), attempt(2), attempt(3)))
        self.assertEqual(result["when"], {"implementation_blocked": True})
        self.assertEqual(result["payload"]["blockerType"], "implementation-incomplete")

    def test_completed_review_round_resets_partial_attempt_bound(self) -> None:
        result = progress.classify(
            envelope(attempt(1), attempt(2, incomplete=False), attempt(3))
        )
        self.assertEqual(result["when"], {"implementation_continue": True})
        self.assertEqual(result["payload"]["continuationAttempt"], 1)

    def test_repeated_evidence_stops_before_continuation(self) -> None:
        result = progress.classify(envelope(attempt(1), attempt(1)))
        self.assertEqual(result["payload"]["blockerType"], "implementation-no-progress")

    def test_external_blocker_stops_immediately(self) -> None:
        blocked = attempt(1)
        blocked["implementation_blocked"] = True
        blocked["blockers"] = [{"type": "missing-dependency"}]
        result = progress.classify(envelope(blocked))
        self.assertEqual(result["payload"]["blockerType"], "implementation-dependency")

    def test_failed_or_missing_behavioral_test_stops(self) -> None:
        failed = attempt(1)
        failed["verification"][0]["exitCode"] = 1
        result = progress.classify(envelope(failed))
        self.assertEqual(result["payload"]["blockerType"], "implementation-materially-unverified")

    def test_failed_required_gate_stops_despite_other_passing_tests(self) -> None:
        failed = attempt(1)
        failed["verification"].append({
            "command": "swift test --filter RequiredBeforeRemovalSuite",
            "exitCode": 1,
            "testsRun": 60,
            "testsFailed": 2,
            "failureCount": 4,
        })
        result = progress.classify(envelope(failed))
        self.assertEqual(result["payload"]["blockerType"], "implementation-materially-unverified")
        self.assertEqual(result["when"], {"implementation_blocked": True})

    def test_matching_baseline_failure_reaches_independent_review_not_pass(self) -> None:
        temporary, root, completed = self.baseline_case()
        with temporary, patch.object(progress.Path, "cwd", return_value=root):
            result = progress.classify(envelope(completed))
        self.assertEqual(result["when"], {"implementation_blocked": False})
        self.assertEqual(result["payload"]["status"], "ready-for-test-integrity")
        self.assertEqual(result["payload"]["baselineReviewPending"][0]["decision"], "pending-independent-review")
        self.assertEqual(result["payload"]["verification"][-1]["exitCode"], 1)

    def test_structured_comparison_and_matching_baseline_record_reach_review(self) -> None:
        temporary, root, completed = self.baseline_case()
        completed["verification"][-1]["comparison"] = {
            "path": "tmp/comparison.json",
            "identical": True,
            "aggregateAssertionCount": 11,
            "baselineAssertionCount": 11,
            "aggregateOnly": [],
            "baselineOnly": [],
        }
        completed["verification"].append({
            "command": "swift test --package-path tmp/checkpoint --filter BroadTests",
            "exitCode": 1,
            "testsRun": 1475,
            "failureCount": 11,
            "log": "tmp/baseline.log",
        })
        with temporary, patch.object(progress.Path, "cwd", return_value=root):
            result = progress.classify(envelope(completed))
        self.assertEqual(result["payload"]["status"], "ready-for-test-integrity")
        self.assertEqual(len(result["payload"]["baselineReviewPending"]), 1)
        self.assertEqual(result["payload"]["baselineReviewPending"][0]["baselineLog"], "tmp/baseline.log")
        self.assertEqual(result["payload"]["verification"][-1]["exitCode"], 1)

    def test_structured_baseline_does_not_hide_unlinked_or_mismatched_failure(self) -> None:
        for mismatch in (
            "comparison", "aggregate-log", "baseline-file-missing",
            "baseline-count", "baseline-log", "extra-failure",
        ):
            with self.subTest(mismatch=mismatch):
                temporary, root, completed = self.baseline_case()
                completed["verification"][-1]["comparison"] = {
                    "path": "tmp/comparison.json", "identical": True,
                    "aggregateAssertionCount": 11, "baselineAssertionCount": 11,
                    "aggregateOnly": [], "baselineOnly": [],
                }
                baseline = {
                    "command": "swift test --package-path tmp/checkpoint --filter BroadTests",
                    "exitCode": 1, "testsRun": 1475, "failureCount": 11,
                    "log": "tmp/baseline.log",
                }
                completed["verification"].append(baseline)
                if mismatch == "comparison":
                    completed["verification"][1]["comparison"]["baselineAssertionCount"] = 10
                elif mismatch == "aggregate-log":
                    comparison = json.loads((root / "tmp/comparison.json").read_text())
                    comparison["aggregateLog"] = "tmp/another-aggregate.log"
                    (root / "tmp/comparison.json").write_text(json.dumps(comparison))
                elif mismatch == "baseline-file-missing":
                    (root / "tmp/baseline.log").unlink()
                elif mismatch == "baseline-count":
                    baseline["failureCount"] = 10
                elif mismatch == "baseline-log":
                    baseline["log"] = "tmp/unlinked.log"
                else:
                    completed["verification"].append({
                        "command": "swift test --filter NewRegression", "exitCode": 1,
                        "testsRun": 3, "failureCount": 1,
                    })
                with temporary, patch.object(progress.Path, "cwd", return_value=root):
                    result = progress.classify(envelope(completed))
                self.assertEqual(result["payload"]["blockerType"], "implementation-materially-unverified")

    def test_baseline_candidate_never_masks_new_or_unproven_failure(self) -> None:
        for overrides in ({"identical": False}, {"failures": 12}, {"extra_failure": True}):
            with self.subTest(overrides=overrides):
                temporary, root, completed = self.baseline_case(**overrides)
                with temporary, patch.object(progress.Path, "cwd", return_value=root):
                    result = progress.classify(envelope(completed))
                self.assertEqual(result["payload"]["blockerType"], "implementation-materially-unverified")

    def test_baseline_candidate_requires_log_comparison_and_passing_focused_test(self) -> None:
        temporary, root, completed = self.baseline_case()
        with temporary, patch.object(progress.Path, "cwd", return_value=root):
            (root / "tmp/comparison.json").unlink()
            result = progress.classify(envelope(completed))
            self.assertEqual(result["payload"]["blockerType"], "implementation-materially-unverified")

            (root / "tmp/comparison.json").write_text(json.dumps({
                "identical": True, "aggregateAssertionCount": 11, "baselineAssertionCount": 11,
                "aggregateOnly": [], "baselineOnly": [],
            }))
            completed["verification"][0]["exitCode"] = 1
            result = progress.classify(envelope(completed))
            self.assertEqual(result["payload"]["blockerType"], "implementation-materially-unverified")

    def test_incomplete_implementation_cannot_defer_failed_gate_to_review(self) -> None:
        temporary, root, completed = self.baseline_case()
        completed["implementationIncomplete"] = True
        with temporary, patch.object(progress.Path, "cwd", return_value=root):
            result = progress.classify(envelope(completed))
        self.assertEqual(result["payload"]["blockerType"], "implementation-materially-unverified")

    def test_every_independent_gate_retains_baseline_review_responsibility(self) -> None:
        for name in (
            "step6-test-integrity-check.md", "step7-adversarial-review.md",
            "branch-evidence.md", "reconcile-implementations.md", "integration-review.md",
        ):
            with self.subTest(prompt=name):
                prompt = (SCRIPT.parents[1] / "prompts" / name).read_text()
                self.assertIn("baselineReviewPending", prompt)
                self.assertIn("nonzero", prompt)

    def test_swift_discovery_does_not_fail_passing_behavioral_run(self) -> None:
        completed = attempt(1, incomplete=False)
        completed["verification"].insert(0, {
            "command": "/Applications/Xcode.app/usr/bin/swift test --scratch-path tmp/build list",
            "exitCode": 0,
            "outcome": "Seven moved tests discovered once.",
        })
        result = progress.classify(envelope(completed))
        self.assertEqual(result["when"], {"implementation_blocked": False})
        self.assertEqual(result["payload"]["status"], "ready-for-test-integrity")

    def test_discovery_alone_is_not_behavioral_evidence(self) -> None:
        completed = attempt(1, incomplete=False)
        completed["verification"] = [{
            "command": "swift test --list-tests",
            "exitCode": 0,
            "outcome": "Tests discovered.",
        }]
        result = progress.classify(envelope(completed))
        self.assertEqual(result["payload"]["blockerType"], "implementation-materially-unverified")

    def test_incomplete_attempt_with_high_finding_stops_before_continuation(self) -> None:
        finding = attempt(1)
        finding["authorSelfCheck"]["findings"] = [
            "High: canonical adapter failure kind is not persisted"
        ]
        result = progress.classify(envelope(finding))
        self.assertEqual(result["payload"]["blockerType"], "implementation-material-finding")
        self.assertEqual(result["when"], {"implementation_blocked": True})

    def test_incomplete_attempt_with_structured_material_risk_stops(self) -> None:
        finding = attempt(1)
        finding["risks"] = [{"severity": "high", "message": "missing approved write path"}]
        result = progress.classify(envelope(finding))
        self.assertEqual(result["payload"]["blockerType"], "implementation-material-finding")

    def test_incomplete_attempt_with_top_level_high_finding_stops(self) -> None:
        finding = attempt(1)
        finding["findings"] = ["High: terminal persistence loses adapter failureKind"]
        result = progress.classify(envelope(finding))
        self.assertEqual(result["payload"]["blockerType"], "implementation-material-finding")

    def test_completed_attempt_enters_review(self) -> None:
        result = progress.classify(envelope(attempt(1), attempt(2, incomplete=False)))
        self.assertEqual(result["when"], {"implementation_blocked": False})
        self.assertFalse(result["payload"]["implementation_continue"])

    def test_post_review_finalization_is_not_step_six_incomplete(self) -> None:
        prompt = (SCRIPT.parents[1] / "prompts/step6-implement.md").read_text()
        self.assertIn("Separate implementation-phase completeness from workflow-finalization completeness", prompt)
        self.assertIn("review-dependent shared documentation/index updates", prompt)
        self.assertIn("Their pending status alone must not set `implementationIncomplete`", prompt)

        completed = attempt(3, incomplete=False)
        completed["implementationSummary"] = (
            "D1-D4 verified; formal review and D5 documentation/publication are downstream."
        )
        completed["authorSelfCheck"]["verificationGaps"] = []
        completed["risks"] = ["Historical non-slice broad failures remain open for parent P1."]
        result = progress.classify(envelope(attempt(1), attempt(2), completed))
        self.assertEqual(result["when"], {"implementation_blocked": False})
        self.assertEqual(result["payload"]["status"], "ready-for-test-integrity")

    def test_bunx_vitest_is_behavioral_evidence(self) -> None:
        current = attempt(1)
        current["verification"][0]["command"] = (
            "mise exec -- bunx --no-install vitest run packages/adapter/test/usecases/knowledge-links.test.ts"
        )
        result = progress.classify(envelope(current))
        self.assertEqual(result["when"], {"implementation_continue": True})


if __name__ == "__main__":
    unittest.main()
