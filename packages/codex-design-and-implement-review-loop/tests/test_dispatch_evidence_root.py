"""Regression checks for committed dispatch-manifest evidence roots."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "workflows/codex-design-and-implement-review-loop/scripts/dispatch-plans.py"
)
SPEC = importlib.util.spec_from_file_location("dispatch_plans", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
dispatch_plans = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dispatch_plans)


class ManifestEvidenceRootTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]

    def test_explicit_root_is_preserved(self) -> None:
        manifest = {"taskId": "p1-6c", "evidenceRoot": "tmp/custom-evidence"}
        self.assertEqual(
            dispatch_plans.manifest_evidence_root(manifest, self.root),
            "tmp/custom-evidence",
        )

    def test_older_checkpoint_uses_canonical_task_root(self) -> None:
        self.assertEqual(
            dispatch_plans.manifest_evidence_root({"taskId": "work-runtime-p1-6c-2c7cf9334b26"}, self.root),
            "tmp/work-runtime-p1-6c-2c7cf9334b26",
        )

    def test_empty_explicit_root_is_not_silently_replaced(self) -> None:
        with self.assertRaisesRegex(ValueError, "evidenceRoot must be a non-empty string"):
            dispatch_plans.manifest_evidence_root(
                {"taskId": "p1-6c", "evidenceRoot": ""}, self.root
            )

    def test_unsafe_fallback_task_id_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "taskId must be a safe path component"):
            dispatch_plans.manifest_evidence_root({"taskId": "../other"}, self.root)


if __name__ == "__main__":
    unittest.main()
