import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_ROOT = ROOT / "workflows" / "opus-luna-design-and-implement-review-loop"


def load_json(path):
    return json.loads(path.read_text())


class WorkflowRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = load_json(WORKFLOW_ROOT / "workflow.json")
        cls.nodes = {item["id"]: item for item in cls.workflow["nodes"]}
        cls.steps = {item["id"]: item for item in cls.workflow["steps"]}

    def test_contract_gate_edges(self):
        self.assertEqual(
            self.steps["plan-checkpoint"]["transitions"],
            [{"toStepId": "plan-contract-validate", "label": "!(checkpoint_blocked)"}],
        )
        self.assertEqual(
            self.steps["plan-contract-validate"]["transitions"],
            [
                {"toStepId": "plan-git-commit", "label": "contract_valid"},
                {"toStepId": "step4-impl-plan-create", "label": "!(contract_valid)"},
            ],
        )

    def test_dispatch_fanout_and_amendment_edges(self):
        transitions = self.steps["dispatch-plans"]["transitions"]
        self.assertEqual(transitions[0]["label"], "dispatch_ready")
        self.assertEqual(
            transitions[0]["fanout"]["changeTracking"],
            {"pathsFrom": "/trackedPaths", "artifactRootsFrom": "/artifactRoots"},
        )
        self.assertEqual(transitions[0]["fanout"]["joinStepId"], "implementation-wave-outcome")
        self.assertNotIn("concurrency", transitions[0]["fanout"])
        self.assertEqual(
            transitions[1:],
            [
                {"toStepId": "step4-impl-plan-create", "label": "amendment_required"},
                {"toStepId": "implementation-blocked-output", "label": "amendment_blocked"},
            ],
        )

    def test_archive_edges(self):
        self.assertEqual(self.steps["step8-docs-refresh"]["transitions"], [{"toStepId": "plan-archive"}])
        self.assertEqual(
            self.steps["plan-archive"]["transitions"],
            [
                {"toStepId": "step9-commit-message", "label": "!(completion_blocked)"},
                {"toStepId": "implementation-blocked-output", "label": "completion_blocked"},
            ],
        )

    def test_referenced_node_files_exist(self):
        for node_id in ("plan-contract-validate", "plan-archive"):
            node_file = self.nodes[node_id]["nodeFile"]
            self.assertTrue((WORKFLOW_ROOT / node_file).is_file(), node_file)

    def test_command_scripts_and_dispatch_schema_match_wrapper(self):
        dispatch = load_json(WORKFLOW_ROOT / "nodes/node-dispatch-plans.json")
        archive = load_json(WORKFLOW_ROOT / "nodes/node-plan-archive.json")
        contract = load_json(WORKFLOW_ROOT / "nodes/node-plan-contract-validate.json")
        self.assertEqual(dispatch["command"]["scriptPath"], "scripts/dispatch-wave.py")
        self.assertEqual(archive["command"]["scriptPath"], "scripts/plan-archive.py")
        self.assertEqual(contract["command"]["scriptPath"], "scripts/validate-plan-contract.py")
        spec = importlib.util.spec_from_file_location(
            "dispatch_wave_for_routing_test", WORKFLOW_ROOT / "scripts/dispatch-wave.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        schema = dispatch["output"]["jsonSchema"]
        props = schema["properties"]
        self.assertTrue(set(module.AMENDMENT_PAYLOAD_KEYS) <= set(props))
        self.assertEqual(
            schema["required"],
            ["acceptedPlanIds", "manifestPath", "checkpointCommit", "dispatch_ready", "amendment_required", "amendment_blocked"],
        )
        self.assertNotIn("implementationItems", schema["required"])
        self.assertEqual(props["implementationItems"]["minItems"], 1)
        self.assertIn("artifactRoots", props["implementationItems"]["items"]["required"])
        self.assertFalse(schema["additionalProperties"])

    def test_step8_archive_request_and_issue_reference_schema(self):
        node = load_json(WORKFLOW_ROOT / "nodes/node-step8-docs-refresh.json")
        schema = node["output"]["jsonSchema"]
        self.assertIn("issueReference", schema["required"])
        self.assertEqual(schema["properties"]["issueReference"], {"type": "string", "minLength": 1})
        self.assertEqual(
            schema["properties"]["archiveRequests"]["items"]["required"],
            ["source", "destination"],
        )
        self.assertNotIn("archiveRequests", schema["required"])

    def test_blocked_output_accepts_amendment_without_plan_ids(self):
        schema = load_json(WORKFLOW_ROOT / "nodes/node-implementation-blocked-output.json")["output"]["jsonSchema"]
        self.assertNotIn("minItems", schema["properties"]["blockedPlanIds"])
        self.assertEqual(schema["properties"]["blockedStepId"], {"type": "string"})

    def test_three_full_scenarios_cover_new_routes_and_planning_only_stays_unchanged(self):
        for name in ("mock-scenario.json", "mock-scenario-fanout.json", "mock-scenario-local.json"):
            scenario = load_json(WORKFLOW_ROOT / name)
            dispatch = scenario["dispatch-plans"]
            self.assertEqual(dispatch["model"], "scripts/dispatch-wave.py")
            self.assertEqual(dispatch["when"], {"dispatch_ready": True, "amendment_required": False, "amendment_blocked": False})
            self.assertTrue(dispatch["payload"]["dispatch_ready"])
            self.assertFalse(dispatch["payload"]["amendment_required"])
            self.assertFalse(dispatch["payload"]["amendment_blocked"])
            self.assertEqual(scenario["plan-contract-validate"]["model"], "scripts/validate-plan-contract.py")
            self.assertEqual(scenario["plan-contract-validate"]["payload"]["commitMessage"], scenario["plan-checkpoint"]["payload"]["commitMessage"])
            self.assertEqual(scenario["plan-archive"]["model"], "scripts/plan-archive.py")
            archive_payload = scenario["plan-archive"]["payload"]
            step8 = scenario["step8-docs-refresh"]["payload"]
            self.assertTrue(step8["issueReference"].strip())
            self.assertEqual(archive_payload["issueReference"], step8["issueReference"])
            self.assertIn("archiveRequests", step8)
            self.assertEqual(archive_payload["archivedImplPlanPaths"], scenario["step9-commit-message"]["payload"]["archivedImplPlanPaths"])
            self.assertTrue(set(archive_payload["archivedImplPlanPaths"]) <= set(scenario["step9-commit-message"]["payload"]["committedFiles"]))
        planning = load_json(WORKFLOW_ROOT / "mock-scenario-planning-only.json")
        self.assertNotIn("plan-archive", planning)


if __name__ == "__main__":
    unittest.main()
