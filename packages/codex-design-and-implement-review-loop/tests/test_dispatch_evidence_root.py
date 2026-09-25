"""Regression checks for committed dispatch-manifest evidence roots."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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

    def test_dispatch_selects_unique_new_manifest_when_checkpoint_also_updates_old_manifest(self) -> None:
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
            active = root / "impl-plans/active"
            active.mkdir(parents=True)
            old_manifest = active / "prior-dispatch.json"
            old_manifest.write_text(json.dumps({"plans": [{"planId": "prior"}]}))
            run("add", ".")
            run("commit", "-qm", "prior checkpoint")

            old_manifest.write_text(json.dumps({"plans": [{"planId": "prior"}], "status": "historical"}))
            new_manifest = active / "resume-dispatch.json"
            new_manifest.write_text(json.dumps({"plans": [{"planId": "resume"}]}))
            run("add", ".")
            run("commit", "-qm", "resume checkpoint")
            commit = run("rev-parse", "HEAD")
            push = {"fromStepId": "plan-git-push", "payload": {
                "git": {"operation": "push", "status": "pushed", "commitHash": commit}
            }}
            self.assertEqual(
                dispatch_plans.checkpoint_source([push], root),
                ("impl-plans/active/resume-dispatch.json", commit),
            )

            (active / "another-dispatch.json").write_text(json.dumps({"plans": []}))
            (active / "third-dispatch.json").write_text(json.dumps({"plans": []}))
            run("add", ".")
            run("commit", "-qm", "ambiguous checkpoint")
            push["payload"]["git"]["commitHash"] = run("rev-parse", "HEAD")
            with self.assertRaisesRegex(ValueError, "exactly one dispatch manifest"):
                dispatch_plans.checkpoint_source([push], root)

    def test_integration_revision_is_projected_to_owned_plan(self) -> None:
        result = self._project_revision("Tests/owned.swift")
        items = result["payload"]["implementationItems"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["reviewFeedback"]["findings"][0]["file"], "Tests/owned.swift")

    def test_integration_revision_outside_ownership_requires_amendment(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounded checkpoint amendment required.*Tests/catalog.swift"):
            self._project_revision("Tests/catalog.swift")

    def test_integration_evidence_log_does_not_require_write_ownership(self) -> None:
        evidence = "tmp/review-retry/reconcile/aggregate-tests.log"
        result = self._project_revision(evidence)
        item = result["payload"]["implementationItems"][0]
        self.assertEqual(item["reviewFeedback"]["findings"][0]["file"], evidence)

    def _project_revision(self, finding_path: str) -> dict:
        scratch_root = self.root.parents[1] / "tmp"
        scratch_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root) as directory:
            root = Path(directory)
            manifest_path = "impl-plans/active/dispatch.json"
            manifest_file = root / manifest_path
            manifest_file.parent.mkdir(parents=True)
            manifest_file.write_text(json.dumps({
                "taskId": "review-retry",
                "workflowMode": "issue-resolution",
                "implementationBranch": "feat/retry",
                "baseBranch": "main",
                "remote": "origin",
                "evidenceRoot": "tmp/review-retry",
                "reviewContext": {
                    "issueReference": "issue-1",
                    "userProblem": "Repair the example catalog",
                    "requiredOutcomes": ["Catalog validates replacement examples"],
                    "nonGoals": [],
                    "constraints": [],
                    "designDecisionsAndRationale": [],
                    "intentionalTradeoffs": [],
                    "supportedEdgeCases": [],
                    "outOfScopeEdgeCases": [],
                    "sourcePaths": ["Tests/owned.swift"],
                },
                "plans": [{
                    "planId": "example-tests",
                    "planPath": "impl-plans/active/plan.md",
                    "dependsOn": [],
                    "writePaths": ["Tests/owned.swift"],
                    "sharedPaths": [],
                    "acceptanceCriteria": ["Catalog test passes"],
                    "verification": ["swift test --filter CatalogTests"],
                }],
            }))
            messages = [
                {"fromStepId": "plan-git-push", "createdOrder": 1, "payload": {}},
                {"fromStepId": "integration-review", "createdOrder": 2, "payload": {
                    "needs_revision": True,
                    "redispatch_required": True,
                    "repair_in_place": False,
                    "findings": [{"severity": "mid", "file": finding_path, "message": "Missing catalog coverage"}],
                    "recoveryDiagnostic": "Repair the reviewed catalog test",
                }},
            ]
            envelope = {"input": {"_rielaInput": {"messages": messages}}}
            with mock.patch.object(dispatch_plans.Path, "cwd", return_value=root), \
                 mock.patch.object(dispatch_plans, "checkpoint_source", return_value=(manifest_path, "a" * 40)), \
                 mock.patch.object(dispatch_plans, "verify_checkpoint"):
                return dispatch_plans.project(envelope)


if __name__ == "__main__":
    unittest.main()
