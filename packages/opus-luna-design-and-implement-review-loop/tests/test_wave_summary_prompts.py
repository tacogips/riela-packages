"""Static contract checks for bounded wave-summary prompt inputs."""

from pathlib import Path
import unittest


PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / "workflows/opus-luna-design-and-implement-review-loop"
PROMPTS = WORKFLOW / "prompts"


class WaveSummaryPromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reconcile = (PROMPTS / "reconcile-implementations.md").read_text(encoding="utf-8")
        cls.integration = (PROMPTS / "integration-review.md").read_text(encoding="utf-8")
        cls.blocked_output = (PROMPTS / "implementation-blocked-output.md").read_text(encoding="utf-8")

    def test_downstream_prompts_ignore_raw_runtime_join(self):
        forbidden = ("runtimeVariables.fanoutJoin", "fanoutJoin.branches", "fanoutJoin.dispatchedBranchIds")
        for prompt in (self.reconcile, self.integration):
            for literal in forbidden:
                self.assertNotIn(literal, prompt)
        for literal in forbidden[:2]:
            self.assertNotIn(literal, self.blocked_output)

    def test_reconcile_binds_inbox_verdict_to_highest_wave_summary(self):
        for literal in (
            "implementation-wave-outcome",
            "tmp/opus-luna-waves/<_rielaInput.workflowExecutionId>/wave-NNN/wave-summary.json",
            "highest",
            "workflowExecutionId",
            "verdict",
            "deep-equal",
            "blocking evidence gap",
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.reconcile)

    def test_reconcile_uses_summary_projection_and_returns_both_paths(self):
        for literal in (
            "plans[]",
            "dispatchedBranchIds",
            "pendingBranchIds",
            "checkpointProvenance",
            "reviewDecisions",
            "changedFiles",
            "evidencePaths",
            "changeEvidence",
            "bySelection",
            "byKind",
            'selection: \"source\"',
            'selection: \"artifact\"',
            "complete",
            "captureFailures",
            "reduceFailures",
            "waveSummaryPath",
            "rawJoinPath",
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.reconcile)

    def test_both_prompts_only_allow_pointer_targeted_raw_extraction(self):
        for prompt in (self.reconcile, self.integration):
            self.assertIn("rawPointer", prompt)
            self.assertIn("targeted query", prompt)
            self.assertIn("Never read `fanout-join.json` whole", prompt)
            self.assertIn("never read, quote, or summarize it", prompt)
        self.assertIn("rawJoinPath", self.integration)

    def test_integration_binds_reconcile_path_to_its_own_wave_locator(self):
        for literal in (
            "reconcile-supplied `waveSummaryPath`",
            "equal the highest",
            "tmp/opus-luna-waves/<_rielaInput.workflowExecutionId>/wave-NNN/wave-summary.json",
            "your own `_rielaInput.workflowExecutionId`",
            "summary's `workflowExecutionId`",
            "summary's `dispatchedBranchIds` and `plans[]`",
            "`changeEvidence` in the summary",
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.integration)

    def test_reconcile_preserves_checkpoint_and_drift_semantics(self):
        for literal in (
            "Independently verify the commit object",
            "Require the branches to agree",
            'selection: "artifact"',
            "never restore or merge them as source overwrites",
            "If `changeEvidence.complete` is `false`",
            "partial_success:true",
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.reconcile)

    def test_integration_preserves_luna_revision_handoff_and_loop_gate(self):
        for literal in (
            "payload.loopGate",
            "repairInstructions",
            "redispatch_required:true",
            "repair_in_place:false",
            "Luna ownership of integration-review revisions",
            "Detailed revision handoff",
            "Selective integration dispatch preserves findings",
            "partial_success:true",
        ):
            with self.subTest(literal=literal):
                self.assertIn(literal, self.integration)


if __name__ == "__main__":
    unittest.main()
