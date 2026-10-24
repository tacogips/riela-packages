"""Static contract checks for runtime issue-resolution prompts."""
from pathlib import Path
import unittest


PACKAGE = Path(__file__).resolve().parents[1]
PROMPTS = PACKAGE / "workflows/opus-luna-design-and-implement-review-loop/prompts"


class RuntimePromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.step6 = (PROMPTS / "step6-implement.md").read_text(encoding="utf-8")
        cls.integration = (PROMPTS / "integration-review.md").read_text(encoding="utf-8")
        cls.step8 = (PROMPTS / "step8-docs-refresh.md").read_text(encoding="utf-8")
        cls.step9 = (PROMPTS / "step9-commit-message.md").read_text(encoding="utf-8")
        cls.blocked = (PROMPTS / "implementation-blocked-output.md").read_text(encoding="utf-8")

    def test_step6_verification_record_contract(self):
        for literal in (
            "exitStatus", "testsRun", "failureCount", "behavioral-test",
            "negativeControl", "expectedExitStatus", "committed verification commands",
            "Keep superseded attempts out of `verification[]`", "writePaths",
            "{paths, command, exitStatus, message}",
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.step6)
        for runner in (
            "swift test", "cargo test", "cargo nextest run", "go test", "pytest",
            "python -m unittest", "ctest", "bun test", "vitest run", "npm test",
            "pnpm test", "yarn test", "tree-sitter test", "deno test", "node --test",
        ):
            with self.subTest(runner=runner):
                self.assertIn(runner, self.step6)
        self.assertIn("Never use this kind for build, lint, format or diff commands", self.step6)
        self.assertIn("<evidenceRoot>/<planId>/", self.step6)
        self.assertNotIn("opus-luna-gate-routing", self.step6)

    def test_integration_rechecks_sibling_owned_blockers_and_preserves_envelope(self):
        for literal in (
            "sibling-owned-blockers.json", "siblingOwnedBlockers",
            "re-run every recorded command", "material finding owned by the plan",
            "rawJoinPath", "## Output envelope",
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.integration)

    def test_step8_returns_archive_requests_and_issue_reference(self):
        for literal in (
            "archiveRequests", "plan-archive", "archiveResults", "issueReference",
            "reviewContext.issueReference", "impl-plans/README.md",
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.step8)
        self.assertNotIn("Move only plans", self.step8)
        for line in self.step8.splitlines():
            if "git mv" in line.lower():
                self.assertIn("never", line.lower())

    def test_step9_uses_archive_results_without_moving(self):
        for literal in ("archiveResults", "already-archived", "conflict", "source", "destination"):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.step9)
        self.assertIn("Never attempt the move or index edit", self.step9)

    def test_blocked_output_copies_each_direct_predecessor_contract(self):
        for literal in (
            "implementation-wave-outcome", "dispatch-plans", "amendment_blocked",
            "plan-archive", "completion_blocked", "blockedStepId", "issueReference",
            "blockedPlanIds", "successfulPlanIds", "resumeCriteria", "nextStep",
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.blocked)
        self.assertNotIn("runtimeVariables.fanoutJoin", self.blocked)
        self.assertNotIn("fanoutJoin.branches", self.blocked)


if __name__ == "__main__":
    unittest.main()
