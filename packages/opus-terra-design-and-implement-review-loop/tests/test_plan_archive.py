"""Regression coverage for deterministic Step 8 plan archiving (design D6)."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / "workflows/opus-terra-design-and-implement-review-loop"
SCRIPT = WORKFLOW / "scripts/plan-archive.py"
SPEC = importlib.util.spec_from_file_location("terra_plan_archive", SCRIPT)
archive = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archive)


def message(payload, order=1, step="step8-docs-refresh"):
    return {"fromStepId": step, "createdOrder": order, "payload": payload}


def envelope(messages):
    return {"input": {"_rielaInput": {"messages": messages}}}


def request(source="impl-plans/active/a.md", destination="impl-plans/completed/a.md"):
    return {"source": source, "destination": destination}


class PlanArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "impl-plans/active").mkdir(parents=True)

    def route(self, requests, messages=None):
        if messages is None:
            messages = [message({"archiveRequests": requests, "documentationFiles": ["README.md"], "workflowMode": "issue-resolution", "issueReference": "tacogips/riela#129"})]
        return archive.route(envelope(messages), self.root)

    def test_moves_file_and_reports_archived_destination(self):
        source = self.root / "impl-plans/active/a.md"
        source.write_text("plan contents")
        result = self.route([request()])
        self.assertEqual(result["payload"]["archiveResults"][0]["status"], "moved")
        self.assertEqual((self.root / "impl-plans/completed/a.md").read_text(), "plan contents")
        self.assertFalse(source.exists())
        self.assertEqual(result["payload"]["archivedImplPlanPaths"], ["impl-plans/completed/a.md"])

    def test_duplicate_request_is_already_archived(self):
        (self.root / "impl-plans/active/a.md").write_text("plan")
        self.route([request()])
        result = self.route([request()])
        self.assertEqual(result["payload"]["archiveResults"][0]["status"], "already-archived")
        self.assertEqual(result["payload"]["archivedImplPlanPaths"], ["impl-plans/completed/a.md"])

    def test_conflict_preserves_both_files(self):
        source = self.root / "impl-plans/active/a.md"
        destination = self.root / "impl-plans/completed/a.md"
        destination.parent.mkdir()
        source.write_text("active")
        destination.write_text("completed")
        result = self.route([request()])
        self.assertEqual(result["payload"]["archiveResults"][0]["status"], "conflict")
        self.assertEqual(source.read_text(), "active")
        self.assertEqual(destination.read_text(), "completed")

    def test_missing_source_and_destination(self):
        result = self.route([request()])
        self.assertEqual(result["payload"]["archiveResults"][0]["status"], "missing")

    def test_rejects_unsafe_paths_and_bad_request_shapes(self):
        cases = [
            request("impl-plans/a.md", "impl-plans/completed/a.md"),
            request("impl-plans/active/a.md", "impl-plans/completed/b.md"),
            request("../x.md", "impl-plans/completed/x.md"),
            request("/tmp/a.md", "impl-plans/completed/a.md"),
            request("impl-plans//active/a.md", "impl-plans/completed/a.md"),
            request("impl-plans/active/.git/a.md", "impl-plans/completed/a.md"),
            {"source": "impl-plans/active/a.md"},
            "not an object",
        ]
        result = self.route(cases)
        self.assertEqual([item["status"] for item in result["payload"]["archiveResults"]], ["rejected"] * len(cases))
        result = self.route("not an array")
        self.assertEqual(result["payload"]["archiveResults"], [{
            "source": None, "destination": None, "status": "rejected", "message": "archiveRequests must be an array"
        }])

    def test_rejects_symlink_or_directory_source(self):
        target = self.root / "target.md"
        target.write_text("target")
        (self.root / "impl-plans/active/link.md").symlink_to(target)
        (self.root / "impl-plans/active/folder.md").mkdir()
        result = self.route([
            request("impl-plans/active/link.md", "impl-plans/completed/link.md"),
            request("impl-plans/active/folder.md", "impl-plans/completed/folder.md"),
        ])
        self.assertEqual([item["status"] for item in result["payload"]["archiveResults"]], ["rejected", "rejected"])
        self.assertTrue(target.exists())

    def test_rejects_symlinked_completed_directory_without_writing_outside_root(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / "impl-plans/completed").symlink_to(outside, target_is_directory=True)
        (self.root / "impl-plans/active/a.md").write_text("plan")
        result = self.route([request()])
        self.assertEqual(result["payload"]["archiveResults"][0]["status"], "rejected")
        self.assertFalse((outside / "a.md").exists())
        self.assertTrue((self.root / "impl-plans/active/a.md").exists())

    def test_forwards_step8_payload_and_uses_latest_created_order(self):
        earlier = message({"archiveRequests": [], "issueReference": "old", "workflowMode": "old"}, 1)
        latest = message({"archiveRequests": [], "issueReference": "tacogips/riela#129", "documentationFiles": ["README.md"], "workflowMode": "issue-resolution"}, 5)
        between = message({"archiveRequests": [], "ignored": True}, 2, step="other-step")
        result = self.route([], [latest, between, earlier])
        payload = result["payload"]
        self.assertEqual(payload["issueReference"], "tacogips/riela#129")
        self.assertEqual(payload["documentationFiles"], ["README.md"])
        self.assertEqual(payload["workflowMode"], "issue-resolution")
        self.assertNotIn("ignored", payload)
        self.assertEqual(payload["docsRefreshRound"], 2)
        self.assertEqual(result["when"], {"completion_blocked": False})

    def test_three_step8_messages_are_not_blocked(self):
        messages = [message({"archiveRequests": [], "issueReference": "tacogips/riela#129"}, order) for order in (1, 2, 3)]
        result = self.route([], messages)
        self.assertEqual(result["payload"]["docsRefreshRound"], 3)
        self.assertFalse(result["payload"]["completion_blocked"])
        self.assertEqual(result["when"], {"completion_blocked": False})

    def test_fourth_step8_message_applies_requests_then_blocks_with_forwarded_issue(self):
        messages = [message({
            "archiveRequests": [request("impl-plans/active/p.md", "impl-plans/completed/p.md")],
            "issueReference": "tacogips/riela#129",
            "documentationFiles": ["README.md"],
        }, order) for order in (1, 2, 3, 4)]
        result = self.route([], messages)
        payload = result["payload"]
        self.assertEqual(result["when"], {"completion_blocked": True})
        self.assertTrue(payload["completion_blocked"])
        self.assertTrue(payload["implementation_blocked"])
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["blockedStepId"], "step9-commit-message")
        self.assertEqual(payload["blockedPlanIds"], ["p"])
        self.assertEqual(payload["successfulPlanIds"], [])
        self.assertEqual(payload["archiveResults"][0]["status"], "missing")
        self.assertEqual(payload["issueReference"], "tacogips/riela#129")
        self.assertTrue(payload["blockers"])
        self.assertEqual(payload["blockers"][0]["type"], "completion-archive-loop")
        self.assertTrue(payload["resumeCriteria"])
        self.assertIn("impl-plans/active/p.md", payload["nextStep"])
        self.assertFalse((self.root / "impl-plans/completed/p.md").exists())

    def test_fourth_message_with_no_unresolved_plan_ids_still_blocks(self):
        messages = [message({"archiveRequests": [], "issueReference": "issue"}, order) for order in (1, 2, 3, 4)]
        result = self.route([], messages)
        self.assertEqual(result["payload"]["blockedPlanIds"], [])
        self.assertEqual(result["payload"]["nextStep"], "review the Step 9 completion findings")

    def test_no_step8_message_raises(self):
        with self.assertRaises(ValueError):
            archive.route(envelope([message({"archiveRequests": []}, step="other-step")]), self.root)

    def test_never_invokes_subprocess(self):
        (self.root / "impl-plans/active/a.md").write_text("plan")
        with mock.patch.object(subprocess, "run", side_effect=AssertionError("subprocess.run called")), \
                mock.patch.object(subprocess, "Popen", side_effect=AssertionError("subprocess.Popen called")):
            self.route([request()])

    def test_node_schema_requires_archive_outputs(self):
        node = json.loads((WORKFLOW / "nodes/node-plan-archive.json").read_text())
        self.assertEqual(node["nodeType"], "command")
        self.assertEqual(node["command"]["scriptPath"], "scripts/plan-archive.py")
        schema = node["output"]["jsonSchema"]
        self.assertEqual(set(schema["required"]), {"completion_blocked", "archiveResults", "docsRefreshRound"})
        self.assertTrue(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
