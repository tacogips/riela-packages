"""Regression coverage for the pre-commit plan contract gate (#128)."""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
OPUS_WORKFLOW = REPO / "packages/opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop"
CODEX_WORKFLOW = REPO / "packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop"
GATE_SCRIPT = OPUS_WORKFLOW / "scripts/validate-plan-contract.py"


def load_gate():
    spec = importlib.util.spec_from_file_location("opus_plan_contract_gate", GATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load gate from {GATE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PlanContractGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory()
        self.root = Path(self._directory.name).resolve()
        self._old_cwd = Path.cwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, self._old_cwd)
        self.addCleanup(self._directory.cleanup)
        self.gate = load_gate()

    def run_gate(self, plan: dict) -> dict:
        manifest_path = "impl-plans/active/t-dispatch.json"
        manifest_file = self.root / manifest_path
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_file.write_text(json.dumps({"plans": [plan]}))
        envelope = {
            "input": {
                "_rielaInput": {
                    "messages": [{
                        "fromStepId": "plan-checkpoint",
                        "createdOrder": 1,
                        "payload": {
                            "manifestPath": manifest_path,
                            "commitMessage": "m",
                            "committedFiles": [manifest_path],
                            "checkpoint_blocked": False,
                            "status": "ready",
                            "blockers": [],
                        },
                    }]
                }
            }
        }
        return self.gate.validate(envelope)

    def test_copied_gate_files_are_byte_identical_to_codex(self) -> None:
        self.assertEqual(
            GATE_SCRIPT.read_bytes(),
            (CODEX_WORKFLOW / "scripts/validate-plan-contract.py").read_bytes(),
        )
        self.assertEqual(
            (OPUS_WORKFLOW / "nodes/node-plan-contract-validate.json").read_bytes(),
            (CODEX_WORKFLOW / "nodes/node-plan-contract-validate.json").read_bytes(),
        )

    def test_shared_directory_expanding_past_limit_requires_plan_revision(self) -> None:
        source = self.root / "src"
        source.mkdir()
        for index in range(600):
            (source / f"f{index:04d}").write_text("")

        result = self.run_gate({
            "planId": "CMP-40",
            "writePaths": ["src/closeout.md"],
            "sharedPaths": ["src"],
        })

        self.assertEqual(result["when"], {"contract_valid": False})
        self.assertTrue(result["payload"]["needs_revision"])
        self.assertTrue(result["payload"]["findings"])
        finding = result["payload"]["findings"][0]
        self.assertEqual(finding["targetStep"], "step4-impl-plan-create")
        self.assertIn("CMP-40", finding["message"])
        self.assertIn("src", finding["message"])
        self.assertIn("limit 512", finding["message"])

    def test_valid_manifest_passes_checkpoint_payload_through(self) -> None:
        result = self.run_gate({
            "planId": "CMP-40",
            "writePaths": ["src/closeout.md"],
            "sharedPaths": [],
        })

        self.assertEqual(result["when"], {"contract_valid": True})
        self.assertEqual(result["payload"]["commitMessage"], "m")
        self.assertEqual(result["payload"]["committedFiles"], ["impl-plans/active/t-dispatch.json"])
