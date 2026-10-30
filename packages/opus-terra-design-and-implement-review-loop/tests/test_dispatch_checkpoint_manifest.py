"""Tests for locating the dispatch manifest in a plan checkpoint commit."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE / "workflows/opus-terra-design-and-implement-review-loop/scripts/dispatch-plans.py"


def load_script():
    spec = importlib.util.spec_from_file_location("terra_dispatch_plans", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


dispatch = load_script()


class CheckpointManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.old_cwd = Path.cwd()
        os.chdir(self.root)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.write("impl-plans/active/old-dispatch.json", {"taskId": "old", "plans": [{"id": "old-01"}]})
        self.git("add", "-A")
        self.git("commit", "-qm", "old dispatch")

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def git(self, *arguments):
        return subprocess.run(["git", *arguments], cwd=self.root, check=True, capture_output=True, text=True)

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def commit_message(self, committed):
        commit = self.git("rev-parse", "HEAD").stdout.strip()
        payload = {"git": {"operation": "commit", "commitHash": commit, "committedFiles": committed}}
        return commit, [{"fromStepId": "plan-git-commit", "payload": payload}]

    def test_archived_manifest_does_not_count_as_a_new_manifest(self):
        (self.root / "impl-plans/completed").mkdir(parents=True)
        self.git("mv", "impl-plans/active/old-dispatch.json", "impl-plans/completed/old-dispatch.json")
        self.write("impl-plans/active/new-dispatch.json", {"taskId": "new", "plans": [{"id": "new-01"}]})
        self.git("add", "-A")
        self.git("commit", "-qm", "archive old dispatch and add new dispatch")
        committed = ["impl-plans/completed/old-dispatch.json", "impl-plans/active/new-dispatch.json"]
        commit, messages = self.commit_message(committed)

        self.assertEqual(dispatch.checkpoint_source(messages, self.root), ("impl-plans/active/new-dispatch.json", commit))

    def test_two_new_manifests_remain_ambiguous(self):
        self.write("impl-plans/active/a-dispatch.json", {"plans": []})
        self.write("impl-plans/active/b-dispatch.json", {"plans": []})
        self.git("add", "-A")
        self.git("commit", "-qm", "two dispatches")
        _, messages = self.commit_message(["impl-plans/active/a-dispatch.json", "impl-plans/active/b-dispatch.json"])

        with self.assertRaisesRegex(ValueError, "exactly one dispatch manifest"):
            dispatch.checkpoint_source(messages, self.root)


if __name__ == "__main__":
    unittest.main()
