"""Keep model selection and existing-design handoff explicit in the package."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[1] / "workflows/codex-design-and-implement-review-loop"


class AuthoringModelPolicyTests(unittest.TestCase):
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
