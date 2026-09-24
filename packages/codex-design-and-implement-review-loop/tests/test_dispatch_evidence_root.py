"""Regression checks for committed dispatch-manifest evidence roots."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
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

    def test_chat_request_uses_recorded_intake_id(self) -> None:
        context = {
            "issueReference": None,
            "intakeCommunicationId": "comm-001883",
            "userProblem": "Show readable links",
            "requiredOutcomes": ["Readable links are listed"],
            "nonGoals": [],
            "constraints": [],
            "designDecisionsAndRationale": [
                {"decision": "Use cursor pages", "rationale": "Bounds response size"}
            ],
            "intentionalTradeoffs": [],
            "supportedEdgeCases": [],
            "outOfScopeEdgeCases": [],
            "sourcePaths": ["workflows/codex-design-and-implement-review-loop/workflow.json"],
        }
        result = dispatch_plans.normalized_review_context(context, self.root)
        self.assertEqual(result["issueReference"], "comm-001883")
        self.assertEqual(
            result["designDecisionsAndRationale"],
            ["Use cursor pages Rationale: Bounds response size"],
        )

    def test_chat_request_without_recorded_intake_id_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "issueReference must identify"):
            dispatch_plans.normalized_review_context(
                {"issueReference": None, "intakeCommunicationId": None}, self.root
            )

    def test_dispatch_uses_successful_push_receipt_and_committed_manifest(self) -> None:
        scratch_root = self.root.parents[1] / "tmp"
        scratch_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root) as directory:
            root = Path(directory)
            def run(*arguments: str) -> str:
                return subprocess.run(
                    ["git", *arguments], cwd=root, check=True, text=True,
                    capture_output=True,
                ).stdout.strip()

            run("init", "-q")
            run("config", "user.name", "Riela Test")
            run("config", "user.email", "riela-test@example.invalid")
            manifest = root / "impl-plans/active/dispatch.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"plans": []}))
            run("add", "impl-plans/active/dispatch.json")
            run("commit", "-qm", "checkpoint")
            commit = run("rev-parse", "HEAD")
            push = {"fromStepId": "plan-git-push", "payload": {
                "git": {"operation": "push", "status": "already-pushed", "commitHash": commit}
            }}
            self.assertEqual(
                dispatch_plans.checkpoint_source([push], root),
                ("impl-plans/active/dispatch.json", commit),
            )
            push["payload"]["git"]["status"] = "failed"
            with self.assertRaisesRegex(ValueError, "successful push"):
                dispatch_plans.checkpoint_source([push], root)
            push["payload"]["git"].update(status="pushed", commitHash="--help")
            with self.assertRaisesRegex(ValueError, "commit hash is invalid"):
                dispatch_plans.checkpoint_source([push], root)


if __name__ == "__main__":
    unittest.main()
