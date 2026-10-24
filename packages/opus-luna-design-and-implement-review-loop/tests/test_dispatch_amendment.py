"""Tests for bounded dispatch amendment routing."""

import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / "workflows/opus-luna-design-and-implement-review-loop"
SCRIPT = WORKFLOW / "scripts/dispatch-wave.py"
CODEX_DISPATCH = PACKAGE.parent / "codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/scripts/dispatch-plans.py"
OPUS_DISPATCH = WORKFLOW / "scripts/dispatch-plans.py"


def load_script():
    spec = importlib.util.spec_from_file_location("luna_dispatch_wave", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


wave = load_script()


class DispatchAmendmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.old_cwd = Path.cwd()
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        self.manifest_path = "impl-plans/active/dispatch.json"
        self.manifest_file = self.root / self.manifest_path
        self.manifest_file.parent.mkdir(parents=True)
        self.manifest = self.make_manifest()
        self.write_manifest()
        subprocess.run(["git", "add", self.manifest_path], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "checkpoint"], cwd=self.root, check=True)
        self.commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root, check=True, capture_output=True, text=True).stdout.strip()
        os.chdir(self.root)
        self.messages = [self.checkpoint_message()]

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def make_manifest(self):
        return {
            "taskId": "dispatch-test",
            "workflowMode": "issue-resolution",
            "implementationBranch": "test/branch",
            "baseBranch": "main",
            "remote": "origin",
            "evidenceRoot": "tmp/dispatch-test",
            "reviewContext": {
                "issueReference": "tacogips/riela#132",
                "userProblem": "Test dispatch amendments",
                "requiredOutcomes": ["Route amendment errors"],
                "nonGoals": [], "constraints": [], "designDecisionsAndRationale": [],
                "intentionalTradeoffs": [], "supportedEdgeCases": [], "outOfScopeEdgeCases": [],
                "sourcePaths": ["src/a", "src/b"],
            },
            "plans": [
                {"planId": "P1", "planPath": "impl-plans/active/p1.md", "dependsOn": [],
                 "writePaths": ["src/a"], "sharedPaths": [], "acceptanceCriteria": ["P1 passes"],
                 "verification": ["python -m unittest"]},
                {"planId": "P2", "planPath": "impl-plans/active/p2.md", "dependsOn": [],
                 "writePaths": ["src/b"], "sharedPaths": [], "acceptanceCriteria": ["P2 passes"],
                 "verification": ["python -m unittest"]},
            ],
        }

    def write_manifest(self):
        self.manifest_file.write_text(json.dumps(self.manifest))

    def checkpoint_message(self, commit=None, step="plan-push-gate"):
        return {"fromStepId": step, "createdOrder": len(self.messages) + 1 if hasattr(self, "messages") else 1,
                "payload": {"git": {"operation": "commit", "commitHash": commit or self.commit,
                                      "committedFiles": [self.manifest_path]}}}

    def envelope(self, messages=None):
        return {"variables": {}, "input": {"_rielaInput": {"messages": messages if messages is not None else self.messages}}}

    def test_normal_projection_adds_route_flags_to_payload_and_when(self):
        result = wave.route(self.envelope())
        self.assertEqual(result["when"], {"dispatch_ready": True, "amendment_required": False, "amendment_blocked": False})
        self.assertTrue(all(result["payload"][key] == value for key, value in result["when"].items()))
        self.assertEqual(result["payload"]["implementationItems"][0]["planId"], "P1")

    def test_session_271_amendment_payload(self):
        paths = ["editor/src/code/pointer.ts", "editor/test/e2e/behavior.mjs"]
        messages = self.messages + [{"fromStepId": "integration-review", "createdOrder": 2, "payload": {
            "needs_revision": True, "acceptedPlanIds": ["P1"],
            "findings": [{"severity": "high", "file": path} for path in paths],
        }}]
        with mock.patch.object(wave.dispatch, "project", side_effect=ValueError(
            f"{wave.dispatch.AMENDMENT}: material integration-review paths outside manifest writePaths: {', '.join(paths)}")):
            result = wave.route(self.envelope(messages))
        self.assertEqual(result["when"], {"dispatch_ready": False, "amendment_required": True, "amendment_blocked": False})
        self.assertEqual(set(result["payload"]), set(wave.AMENDMENT_PAYLOAD_KEYS))
        self.assertEqual(result["payload"]["acceptedPlanIds"], ["P1"])
        self.assertEqual(result["payload"]["blockedPlanIds"], ["P2"])
        amendment = result["payload"]["checkpointAmendment"]
        self.assertEqual(amendment["reason"], "integration-paths-outside-writePaths")
        self.assertEqual(amendment["unmatchedPaths"], paths)
        self.assertEqual(len(amendment["findings"]), 2)
        self.assertEqual(result["payload"]["manifestPath"], self.manifest_path)
        self.assertEqual(result["payload"]["checkpointCommit"], self.commit)

    def test_amendment_exhaustion_after_three_distinct_checkpoints(self):
        messages = self.messages + [{"fromStepId": "integration-review", "createdOrder": 2, "payload": {
            "needs_revision": True, "acceptedPlanIds": ["P1"], "findings": []}}]
        for index in range(2):
            messages.append(self.checkpoint_message(commit=f"{index + 1:040x}", step="plan-git-commit"))
        with mock.patch.object(wave.dispatch, "project", side_effect=ValueError(
            f"{wave.dispatch.AMENDMENT}: material integration-review paths outside manifest writePaths: editor/file.py")):
            result = wave.route(self.envelope(messages))
        self.assertEqual(result["when"]["amendment_blocked"], True)
        self.assertEqual(result["payload"]["checkpointAmendment"]["amendmentRound"], 2)
        self.assertEqual(result["payload"]["blockedPlanIds"], ["P2"])
        self.assertTrue(result["payload"]["blockers"] and result["payload"]["resumeCriteria"] and result["payload"]["nextStep"])

    def test_dispatch_time_over_cap_is_routed_as_amendment(self):
        self.manifest["plans"][1]["sharedPaths"] = ["src/big"]
        self.write_manifest()
        subprocess.run(["git", "add", self.manifest_path], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "manifest with shared path"], cwd=self.root, check=True)
        # Restore the checkpoint commit as required by dispatch and add the oversized tree after it.
        self.commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root, check=True, capture_output=True, text=True).stdout.strip()
        self.messages = [self.checkpoint_message()]
        big = self.root / "src/big"
        big.mkdir(parents=True)
        for index in range(600):
            (big / f"file-{index:03}.txt").write_text("x")
        result = wave.route(self.envelope())
        self.assertTrue(result["when"]["amendment_required"])
        self.assertEqual(result["payload"]["checkpointAmendment"]["reason"], "tracking-contract")
        self.assertIn("limit 512", result["payload"]["checkpointAmendment"]["error"])

    def test_non_amendment_errors_propagate_and_cli_errors_exit_one(self):
        with mock.patch.object(wave.dispatch, "project", side_effect=ValueError("acceptedPlanIds contain unknown plans: nope")):
            with self.assertRaisesRegex(ValueError, "unknown plans"):
                wave.route(self.envelope())
        for raw in ("{bad json}\n", "{}\n"):
            completed = subprocess.run([sys.executable, str(SCRIPT)], input=raw, text=True, capture_output=True, cwd=self.root)
            self.assertEqual(completed.returncode, 1)
            self.assertTrue(completed.stderr.strip().startswith('{"error":'))
        error_output = io.StringIO()
        with mock.patch.object(wave.sys, "stdin", io.StringIO("{}\n")), \
             mock.patch.object(wave.sys, "stderr", error_output), \
             mock.patch.object(wave, "route", side_effect=OSError("cannot read manifest")):
            self.assertEqual(wave.main(), 1)
        self.assertEqual(json.loads(error_output.getvalue()), {"error": "cannot read manifest"})

    def test_dispatch_scripts_remain_byte_identical(self):
        self.assertEqual(CODEX_DISPATCH.read_bytes(), OPUS_DISPATCH.read_bytes())


if __name__ == "__main__":
    unittest.main()
