"""Regression coverage for D3 sibling-owned implementation blockers."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / "workflows/opus-terra-design-and-implement-review-loop"
SPEC = importlib.util.spec_from_file_location(
    "terra_progress_sibling_blockers",
    WORKFLOW / "scripts/implementation-progress-check.py",
)
progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(progress)


class SiblingBlockerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.previous_cwd = Path.cwd()
        self.addCleanup(os.chdir, self.previous_cwd)
        self.root = Path(self.temp_dir.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        self.manifest_path = Path("impl-plans/active/x-dispatch.json")
        self.manifest = {
            "plans": [
                {"planId": "FST-22", "writePaths": ["src/wasm"]},
                {"planId": "FST-20", "writePaths": ["src/cli/tests/fmt.rs"]},
                {"planId": "DONE-1", "writePaths": ["src/done"]},
            ]
        }
        self.commit_manifest(json.dumps(self.manifest))
        os.chdir(self.root)

    def commit_manifest(self, contents):
        manifest_file = self.root / self.manifest_path
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(contents, bytes):
            manifest_file.write_bytes(contents)
        else:
            manifest_file.write_text(contents, encoding="utf-8")
        subprocess.run(["git", "add", str(self.manifest_path)], cwd=self.root, check=True)
        subprocess.run([
            "git", "-c", "user.email=t@example.invalid", "-c", "user.name=t",
            "commit", "-q", "-m", "manifest",
        ], cwd=self.root, check=True)
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()

    def envelope(self, blockers, *, verification=None, implementation_blocked=False, item_overrides=None):
        item = {
            "planId": "FST-22",
            "writePaths": ["src/wasm"],
            "acceptedPlanIds": ["DONE-1"],
            "manifestPath": self.manifest_path.as_posix(),
            "checkpointCommit": self.checkpoint,
            "evidenceRoot": "tmp/task",
            "verification": ["cargo test"],
        }
        item.update(item_overrides or {})
        record = {
            "command": "cargo test",
            "exitStatus": 0,
            "testsRun": 5,
            "failureCount": 0,
        }
        value = {
            "implementation_blocked": implementation_blocked,
            "implementationIncomplete": False,
            "blockers": blockers,
            "changedFiles": ["src/wasm/lib.rs"],
            "implPlanUpdates": ["progress updated"],
            "verification": [record] if verification is None else verification,
            "risks": [],
            "authorSelfCheck": {"findings": [], "verificationGaps": [], "residualRisks": []},
        }
        return {
            "variables": {"implementation": item},
            "input": {"_rielaInput": {"messages": [
                {"fromStepId": "step6-implement", "createdOrder": 1, "payload": value},
            ]}},
        }

    def setUp_manifest_commit(self):
        self.checkpoint = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()

    def test_sibling_owned_blocker_is_deferred_and_recorded(self):
        self.setUp_manifest_commit()
        blocker = {
            "owner": "untrusted-owner-text",
            "path": "src/cli/tests/fmt.rs",
            "command": "cargo fmt --check",
            "exitStatus": 1,
            "message": "sibling formatting failure",
        }
        result = progress.classify(self.envelope([blocker]))
        self.assertEqual(result["when"], {"implementation_blocked": False})
        payload = result["payload"]
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(payload["siblingOwnedBlockers"][0]["ownerPlanIds"], ["FST-20"])
        self.assertEqual(payload["siblingOwnedBlockers"][0]["paths"], ["src/cli/tests/fmt.rs"])
        self.assertEqual(payload["siblingOwnedBlockers"][0]["command"], blocker["command"])
        evidence = self.root / payload["siblingOwnedBlockersPath"]
        self.assertTrue(evidence.is_file())
        self.assertEqual(json.loads(evidence.read_text())["siblingOwnedBlockers"], payload["siblingOwnedBlockers"])

    def test_all_unclassifiable_blockers_fail_closed(self):
        self.setUp_manifest_commit()
        cases = [
            [{"path": "src/wasm/lib.rs"}],
            [{"path": "src/unowned.rs"}],
            [{"path": "src/done/a.rs"}],
            ["waiting on FST-20"],
            [{}],
            [{"paths": ["src/cli/tests/fmt.rs", "src/unowned.rs"]}],
            [{"paths": ["../unsafe"]}],
            [{"path": ".git/config"}],
            [{"path": "/absolute/path"}],
        ]
        for blockers in cases:
            with self.subTest(blockers=blockers):
                result = progress.classify(self.envelope(blockers))
                self.assertEqual(result["when"], {"implementation_blocked": True})
                self.assertEqual(result["payload"]["blockerType"], "implementation-dependency")

    def test_git_show_failure_and_non_json_manifest_fail_closed(self):
        self.setUp_manifest_commit()
        bad_commit = "0" * 40
        result = progress.classify(self.envelope(
            [{"path": "src/cli/tests/fmt.rs"}], item_overrides={"checkpointCommit": bad_commit},
        ))
        self.assertEqual(result["payload"]["blockerType"], "implementation-dependency")
        bad_sha = self.commit_manifest("not-json")
        result = progress.classify(self.envelope(
            [{"path": "src/cli/tests/fmt.rs"}], item_overrides={"checkpointCommit": bad_sha},
        ))
        self.assertEqual(result["payload"]["blockerType"], "implementation-dependency")
        invalid_utf8_sha = self.commit_manifest(b"\xff")
        result = progress.classify(self.envelope(
            [{"path": "src/cli/tests/fmt.rs"}], item_overrides={"checkpointCommit": invalid_utf8_sha},
        ))
        self.assertEqual(result["payload"]["blockerType"], "implementation-dependency")

    def test_implementation_blocked_without_blockers_fails_closed(self):
        self.setUp_manifest_commit()
        result = progress.classify(self.envelope([], implementation_blocked=True))
        self.assertEqual(result["payload"]["blockerType"], "implementation-dependency")

    def test_missing_implementation_item_fails_closed(self):
        self.setUp_manifest_commit()
        value = self.envelope([{"path": "src/cli/tests/fmt.rs"}])
        value["variables"].pop("implementation")
        result = progress.classify(value)
        self.assertEqual(result["when"], {"implementation_blocked": True})
        self.assertEqual(result["payload"]["blockerType"], "implementation-dependency")

    def test_sibling_blocker_does_not_replace_positive_test_evidence(self):
        self.setUp_manifest_commit()
        failed_gate = [{"command": "cargo fmt --check", "exitStatus": 1}]
        result = progress.classify(self.envelope(
            [{"path": "src/cli/tests/fmt.rs"}], verification=failed_gate,
        ))
        self.assertEqual(result["payload"]["blockerType"], "implementation-materially-unverified")

    def test_unsafe_evidence_paths_and_write_failures_block(self):
        self.setUp_manifest_commit()
        blocker = [{"path": "src/cli/tests/fmt.rs"}]
        for override in (
            {"evidenceRoot": "../x"},
            {"planId": "../escape"},
        ):
            with self.subTest(override=override):
                result = progress.classify(self.envelope(blocker, item_overrides=override))
                self.assertEqual(result["payload"]["blockerType"], "implementation-dependency")
                self.assertIn("could not be recorded", result["payload"]["blockers"][-1]["message"])
        bad_root = self.root / "tmp"
        bad_root.write_text("not a directory")
        result = progress.classify(self.envelope(blocker))
        self.assertEqual(result["payload"]["blockerType"], "implementation-dependency")


if __name__ == "__main__":
    unittest.main()
