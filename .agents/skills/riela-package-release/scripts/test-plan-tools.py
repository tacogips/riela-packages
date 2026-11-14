import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / "packages/codex-impl-plan-completion-loop/workflows/codex-impl-plan-completion-loop/scripts"
sys.path.insert(0, str(SCRIPTS))
from plan_tools import metadata


class PlanToolsTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="plan-tools-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "impl-plans/active").mkdir(parents=True)

    def write_plan(self, name, status="Ready", task="Not Started"):
        path = self.root / f"impl-plans/active/{name}.md"
        path.write_text(f"# Plan\n**Status**: {status}\n**Design Reference**: design.md\n\n### REF-001: Implement\n**Status**: {task}\n- [ ] Verify behavior\n")
        return path

    def run_script(self, name, env=None):
        result = subprocess.run([sys.executable, str(SCRIPTS / name)], cwd=self.root,
                                env={**os.environ, "PLAN_PATH": "", "TARGET_TASKS_JSON": "", **(env or {})},
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["payload"]

    def test_auto_batches_and_explicit_request_stays_scoped(self):
        self.write_plan("a")
        self.write_plan("b")
        result = self.run_script("assess-plan.py")
        self.assertEqual(result["implementationPlanPaths"], ["impl-plans/active/a.md", "impl-plans/active/b.md"])
        self.assertFalse(result["plan_complete"])
        explicit = self.run_script("assess-plan.py", {"PLAN_PATH": "impl-plans/active/b.md"})
        self.assertEqual(explicit["implementationPlanPaths"], ["impl-plans/active/b.md"])

    def test_incomplete_ref_task_blocks_archival_and_existing_destination_is_preserved(self):
        path = self.write_plan("a", "Completed", "Not Started")
        self.assertFalse(metadata(path)["complete"])
        self.assertEqual(self.run_script("archive-completed-plans.py")["archivedPlans"], [])
        self.write_plan("a", "Completed", "Completed")
        destination = self.root / "impl-plans/completed/a.md"
        destination.parent.mkdir(exist_ok=True)
        destination.write_text("previous archived evidence")
        self.assertEqual(self.run_script("archive-completed-plans.py")["archivedPlans"], [])
        self.assertEqual(destination.read_text(), "previous archived evidence")
        self.assertTrue(path.exists())

    def test_archive_moves_completed_file(self):
        path = self.write_plan("a", "Completed", "Completed")
        result = self.run_script("archive-completed-plans.py")
        self.assertEqual(len(result["archivedPlans"]), 1)
        self.assertFalse(path.exists())
        self.assertTrue((self.root / "impl-plans/completed/a.md").exists())


if __name__ == "__main__":
    unittest.main()
