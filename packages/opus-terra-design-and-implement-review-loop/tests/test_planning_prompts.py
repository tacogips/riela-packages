from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "workflows/opus-terra-design-and-implement-review-loop/prompts"


class PlanningPromptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.step4 = (PROMPTS / "step4-impl-plan-create.md").read_text()
        cls.step5 = (PROMPTS / "step5-impl-plan-review.md").read_text()
        cls.checkpoint = (PROMPTS / "plan-checkpoint.md").read_text()

    def test_step4_contract_and_amendment_rules(self):
        for anchor in (
            "plan-contract-validate",
            "contract_valid: false",
            "amendment_required",
            "checkpointAmendment",
            "acceptedDependencies",
            "impl-plans/active",
            "impl-plans/completed",
            "workspace-wide",
        ):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, self.step4)
        self.assertIn("never raise snapshot limits", self.step4)
        self.assertIn("After two amendments", self.step4)
        self.assertIn("own `writePaths`", self.step4)

    def test_step5_reports_scope_violations_and_limits_amendment_review(self):
        for anchor in (
            "impl-plans/active",
            "impl-plans/completed",
            "512-entry",
            "workspace-wide",
            "checkpointAmendment",
            "acceptedDependencies",
        ):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, self.step5)
        self.assertIn("Report a `mid` finding", self.step5)
        self.assertIn("review only the amendment's scope", self.step5)
        self.assertIn("Carry `checkpointAmendment` forward unchanged", self.step5)

    def test_checkpoint_amendment_preserves_checkpoint_boundary(self):
        for anchor in (
            "checkpointAmendment.previousCheckpointCommit",
            "acceptedDependencies",
            "plan-contract-validate",
            "leave all implementation changes unstaged",
        ):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, self.checkpoint)
        self.assertIn("update the existing dispatch manifest in place", self.checkpoint)
        self.assertIn("Commit only changed manifest, plan, and design files", self.checkpoint)


if __name__ == "__main__":
    unittest.main()
