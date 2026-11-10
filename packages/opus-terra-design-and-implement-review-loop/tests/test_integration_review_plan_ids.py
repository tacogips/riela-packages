"""Integration review plan-id lists reject prose so the step retries instead of failing dispatch."""

import json
from pathlib import Path
import re
import unittest

NODE = Path(__file__).resolve().parents[1] / "workflows/opus-terra-design-and-implement-review-loop/nodes/node-integration-review.json"


def plan_id_patterns():
    found = {}

    def walk(value):
        if isinstance(value, dict):
            for key in ("acceptedPlanIds", "pendingPlanIds"):
                entry = value.get(key)
                if isinstance(entry, dict) and isinstance(entry.get("items"), dict) and "pattern" in entry["items"]:
                    found[key] = entry["items"]["pattern"]
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(json.loads(NODE.read_text()))
    return found


class IntegrationReviewPlanIdTests(unittest.TestCase):
    def test_both_lists_carry_a_plan_id_pattern(self):
        self.assertEqual(sorted(plan_id_patterns()), ["acceptedPlanIds", "pendingPlanIds"])

    def test_pattern_accepts_plan_ids_and_rejects_prose(self):
        for key, pattern in plan_id_patterns().items():
            with self.subTest(key=key):
                for plan_id in ("b4-checkout-store", "b3-verify-faults", "TASK-001", "plan_2.a"):
                    self.assertRegex(plan_id, pattern)
                for prose in (
                    "acceptedDependencies recorded in impl-plans/active/x-dispatch.json at d2da7d5 (unchanged)",
                    "",
                    " b4-checkout-store",
                ):
                    self.assertIsNone(re.search(pattern, prose))


if __name__ == "__main__":
    unittest.main()
