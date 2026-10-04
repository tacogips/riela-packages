"""Native tracking rejections must re-enter reviewed checkpoint authoring."""
import importlib.util
import json
import unittest
import tempfile
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "workflows/codex-design-and-implement-review-loop"
spec = importlib.util.spec_from_file_location("tracking_gate", ROOT / "scripts/check-runtime-tracking-contract.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
dispatch_spec = importlib.util.spec_from_file_location("checkpoint_dispatch", ROOT / "scripts/dispatch-plans.py")
dispatch = importlib.util.module_from_spec(dispatch_spec)
dispatch_spec.loader.exec_module(dispatch)


def envelope(join):
    return {"input": {"_rielaInput": {"messages": [{"payload": {"fanoutJoin": join}}]}}}


class RuntimeTrackingRepairTests(unittest.TestCase):
    def test_growth_failure_routes_to_author_without_accepting_sibling(self):
        join = {"branches": [
            {"branchId": "tools", "status": "failed", "failureReason": "policy_blocked: fanout snapshot exceeds 512 entries"},
            {"branchId": "source", "status": "completed", "output": {"changedFiles": ["src/a.swift"]}},
        ], "completedBranchIds": ["previous"], "changeEvidence": {"complete": True, "captureFailures": [
            {"branchId": "tools", "node": "implement", "phase": "capture", "selection": "source",
             "root": "tmp/tools", "path": "tmp/tools/cache", "observed": 513, "limit": 512,
             "contents": "must not be copied"}
        ]}}
        result = gate.classify(envelope(join))
        self.assertTrue(result["when"]["tracking_contract_rejected"])
        self.assertEqual(result["payload"]["acceptedPlanIds"], ["previous"])
        self.assertEqual(result["payload"]["affectedPlanIds"], ["tools"])
        self.assertNotIn("contents", result["payload"]["findings"][-1]["diagnostic"])
        self.assertEqual(result["payload"]["fanoutJoin"], join)

    def test_reduction_failure_routes_even_when_all_branches_completed(self):
        join = {"branches": [{"branchId": "tools", "status": "completed"}],
                "changeEvidence": {"complete": False, "reduceFailures": [{"branchId": "tools", "phase": "reduce", "limit": 512}]}}
        self.assertTrue(gate.classify(envelope(join))["when"]["tracking_contract_rejected"])

    def test_missing_diagnostic_does_not_waive_incomplete_evidence(self):
        result = gate.classify(envelope({"changeEvidence": {"complete": False}}))
        self.assertTrue(result["when"]["tracking_contract_rejected"])
        self.assertTrue(result["payload"]["findings"])

    def test_dependency_blockers_and_provider_errors_keep_existing_outcome_route(self):
        for branch in [{"status": "completed", "output": {"implementation_blocked": True}},
                       {"status": "failed", "failureReason": "provider_error: transient failure"}]:
            result = gate.classify(envelope({"branches": [branch], "changeEvidence": {"complete": True}}))
            self.assertFalse(result["when"]["tracking_contract_rejected"])

    def test_all_native_policy_families_trigger_repair(self):
        for prefix in gate.POLICY_PREFIXES:
            self.assertTrue(gate.classify(envelope({"branches": [{"failureReason": prefix + " rejected"}]}))["when"]["tracking_contract_rejected"])

    def test_standalone_progress_blocker_is_preserved(self):
        payload = {"implementation_blocked": True, "status": "blocked", "blockedPlanIds": ["dependency"]}
        result = gate.classify({"input": {"_rielaInput": {"messages": [
            {"fromStepId": "implementation-progress-check", "payload": payload}]}}})
        self.assertFalse(result["when"]["tracking_contract_rejected"])
        for key, value in payload.items():
            self.assertEqual(result["payload"][key], value)

    def test_missing_join_fails_closed(self):
        with self.assertRaises(ValueError):
            gate.classify({})

    def test_parent_join_reaches_author_review_checkpoint_and_redispatch(self):
        workflow = json.loads((ROOT / "workflow.json").read_text())
        steps = {step["id"]: step for step in workflow["steps"]}
        self.assertEqual(steps["dispatch-plans"]["transitions"][0]["fanout"]["joinStepId"], "runtime-tracking-contract-check")
        self.assertEqual(steps["branch-evidence"]["transitions"][0]["toStepId"], "runtime-tracking-contract-check")
        self.assertEqual(steps["implementation-progress-check"]["transitions"][1]["toStepId"], "runtime-tracking-contract-check")
        self.assertEqual(steps["runtime-tracking-contract-check"]["transitions"], [
            {"toStepId": "step4-impl-plan-create", "label": "tracking_contract_rejected"},
            {"toStepId": "implementation-wave-outcome", "label": "!(tracking_contract_rejected)"}])
        for source, target in [("step4-impl-plan-create", "step5-impl-plan-review"),
                               ("plan-checkpoint", "plan-contract-validate"),
                               ("plan-git-commit", "plan-git-push"),
                               ("plan-git-push", "dispatch-plans")]:
            self.assertIn(target, [transition["toStepId"] for transition in steps[source]["transitions"]])


class CheckpointAmendmentTests(unittest.TestCase):
    def test_latest_pushed_amendment_is_the_dispatch_authority(self):
        scratch = ROOT.parents[3] / "tmp"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            root = Path(directory)
            for name in ["old.json", "amended.json"]:
                (root / name).write_text(json.dumps({"plans": []}))
            def push(commit):
                return {"fromStepId": "plan-git-push", "payload": {"git": {
                    "operation": "push", "status": "pushed", "commitHash": commit}}}
            calls = []
            def git(_root, *args):
                calls.append(args)
                return SimpleNamespace(returncode=0, stdout="amended.json\n" if args[-1] == "b" * 40 else "old.json\n")
            with mock.patch.object(dispatch, "git", side_effect=git):
                self.assertEqual(dispatch.checkpoint_source([push("a" * 40), push("b" * 40)], root), ("amended.json", "b" * 40))
                self.assertEqual(len(calls), 1)
                latest_failed = push("c" * 40)
                latest_failed["payload"]["git"]["status"] = "failed"
                with self.assertRaisesRegex(ValueError, "successful push"):
                    dispatch.checkpoint_source([push("a" * 40), latest_failed], root)
                self.assertEqual(len(calls), 1)
