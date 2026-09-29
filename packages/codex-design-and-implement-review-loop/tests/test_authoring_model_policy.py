"""Keep model selection and existing-design handoff explicit in the package."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[1] / "workflows/codex-design-and-implement-review-loop"


class AuthoringModelPolicyTests(unittest.TestCase):
    def test_plan_author_schemas_require_concrete_path_arrays(self) -> None:
        repository = Path(__file__).resolve().parents[3]
        package_nodes = {
            "codex-design-and-implement-review-loop": "node-step4-impl-plan-create.json",
            "fable-and-improve-opus": "node-fable-design.json",
            "opus-luna-design-and-implement-review-loop": "node-step4-impl-plan-create.json",
        }
        for package_id, node_name in package_nodes.items():
            workflow = repository / "packages" / package_id / "workflows" / package_id
            node = json.loads((workflow / "nodes" / node_name).read_text())
            item = node["output"]["jsonSchema"]["properties"]["plans"]["items"]
            self.assertIn("sharedPaths", item["required"])
            pattern = item["properties"]["sharedPaths"]["items"]["pattern"]
            self.assertRegex("src/module.rs", pattern)
            for invalid in ("src/{a,b}.rs", "src/*.rs", "src/a.rs,src/b.rs", "free form prose"):
                with self.subTest(package=package_id, value=invalid):
                    self.assertNotRegex(invalid, pattern)
            review = (workflow / "prompts/step5-impl-plan-review.md").read_text()
            self.assertIn("Inspect each plan's declared `writePaths` and `sharedPaths`", review)
            checkpoint = (workflow / "prompts/plan-checkpoint.md").read_text()
            self.assertIn("Before writing the manifest, validate every `writePaths` and `sharedPaths` item", checkpoint)
            intake = workflow / "prompts" / ("fable-analysis.md" if package_id == "fable-and-improve-opus" else "step1-issue-intake.md")
            self.assertIn("base branch has N unpushed commits; push or rebase first", intake.read_text())
            write_roots = json.loads((workflow / "workflow.json").read_text())["loop"]["policies"]["mutation"]["allowedWriteRoots"]
            self.assertTrue({"src", "tests", "lib", "crates"}.issubset(write_roots))

    def test_every_agent_node_uses_gpt6_sol_at_bounded_effort(self) -> None:
        for path in sorted((WORKFLOW / "nodes").glob("node-*.json")):
            node = json.loads(path.read_text())
            if node.get("executionBackend") != "codex-agent":
                continue
            with self.subTest(node=path.name):
                self.assertEqual(node["model"], "gpt-6-sol")
                self.assertIn(node.get("effort"), ("low", "medium"))

    def test_scenarios_match_authored_agent_models(self) -> None:
        for path in sorted(WORKFLOW.glob("mock-scenario*.json")):
            scenario = json.loads(path.read_text())
            for response in scenario.values():
                for item in response if isinstance(response, list) else [response]:
                    if isinstance(item, dict) and item.get("model", "").startswith("gpt-"):
                        with self.subTest(scenario=path.name):
                            self.assertEqual(item["model"], "gpt-6-sol")

    def test_existing_design_is_the_first_implementation_baseline(self) -> None:
        design = (WORKFLOW / "prompts/step2-design-doc-update.md").read_text()
        plan = (WORKFLOW / "prompts/step4-impl-plan-create.md").read_text()
        self.assertIn("First locate design documentation relevant to the accepted intake", design)
        self.assertIn("If it is already sufficient, keep it unchanged", design)
        self.assertIn("Create a new design only when no relevant design exists", design)
        self.assertIn("use that accepted draft and its cited decisions as the implementation baseline", plan)


if __name__ == "__main__":
    unittest.main()
