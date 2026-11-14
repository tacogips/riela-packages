"""Keep PR handoff fail-closed before any base-branch mutation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[1] / "workflows/codex-design-and-implement-review-loop"


class PullRequestHandoffContractTests(unittest.TestCase):
    def test_finalization_schema_accepts_pr_without_claiming_base_push(self) -> None:
        node = json.loads((WORKFLOW / "nodes/node-base-branch-integrate.json").read_text())
        properties = node["output"]["jsonSchema"]["properties"]

        self.assertIn("pr-open", properties["mergeStatus"]["enum"])
        self.assertIn("not-requested", properties["basePushStatus"]["enum"])
        self.assertTrue({"pullRequestURL", "pullRequestNumber", "pullRequestDraft", "pullRequestBaseBranch"} <= set(properties))
        self.assertIn("merged", properties["mergeStatus"]["enum"])

    def test_existing_pr_blocks_merge_and_requires_exact_publication_evidence(self) -> None:
        handoff = (WORKFLOW / "prompts/base-branch-integrate.md").read_text()
        output = (WORKFLOW / "prompts/workflow-output.md").read_text()

        for required in (
            "query open pull requests",
            "head commit equal",
            "PR base to equal that recorded base",
            "repository's verified default branch",
            "do not checkout, merge, commit, or push the base",
            "unavailable PR lookup",
            'mergeStatus:"pr-open"',
            'basePushStatus:"not-requested"',
        ):
            self.assertIn(required, handoff)
        self.assertIn("base branch has not been merged", output)
        self.assertIn("pullRequestURL", output)


if __name__ == "__main__":
    unittest.main()
