"""Every dispatched unit owns its own plan document."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE / "workflows/opus-terra-design-and-implement-review-loop/scripts/dispatch-plans.py"


def load_script():
    spec = importlib.util.spec_from_file_location("terra_dispatch_plans_ownership", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


dispatch = load_script()


class PlanPathOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def test_missing_plan_path_is_added_to_write_paths(self):
        plan = {"planPath": "impl-plans/active/unit.md", "writePaths": ["src/a.ts"]}
        contract = dispatch.plan_tracking_contract(plan, "unit", self.root)
        self.assertEqual(contract["writePaths"], ["src/a.ts", "impl-plans/active/unit.md"])
        self.assertIn("impl-plans/active/unit.md", contract["trackedPaths"])

    def test_plan_path_already_owned_is_not_duplicated(self):
        plan = {"planPath": "impl-plans/active/unit.md", "writePaths": ["impl-plans/active/unit.md", "src/a.ts"]}
        contract = dispatch.plan_tracking_contract(plan, "unit", self.root)
        self.assertEqual(contract["writePaths"], ["impl-plans/active/unit.md", "src/a.ts"])

    def test_plan_path_inside_owned_directory_is_not_duplicated(self):
        plan = {"planPath": "impl-plans/active/unit.md", "writePaths": ["impl-plans/active", "src/a.ts"]}
        contract = dispatch.plan_tracking_contract(plan, "unit", self.root)
        self.assertEqual(contract["writePaths"], ["impl-plans/active", "src/a.ts"])


if __name__ == "__main__":
    unittest.main()
