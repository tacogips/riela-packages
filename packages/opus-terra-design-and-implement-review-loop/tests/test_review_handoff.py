"""Keep Opus review revisions owned by Terra and preserve detailed dispatch briefs."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / 'workflows/opus-terra-design-and-implement-review-loop'
SPEC = importlib.util.spec_from_file_location('terra_dispatch', WORKFLOW / 'scripts/dispatch-plans.py')
dispatch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dispatch)


class ReviewHandoffTests(unittest.TestCase):
    def test_review_rejections_return_to_terra_without_serial_repair(self):
        workflow = json.loads((WORKFLOW / 'workflow.json').read_text())
        steps = {step['id']: step for step in workflow['steps']}
        for gate in ('step6-test-integrity-check', 'step7-adversarial-review'):
            self.assertIn({'toStepId': 'step6-implement', 'label': 'needs_revision'}, steps[gate]['transitions'])
            node = json.loads((WORKFLOW / f'nodes/node-{gate}.json').read_text())
            self.assertEqual(node['agentSandbox'], 'read-only')
            self.assertIn('repairInstructions', node['output']['jsonSchema']['properties']['findings']['items']['properties'])
        self.assertEqual(steps['integration-review']['transitions'][0], {'toStepId': 'dispatch-plans', 'label': 'needs_revision'})
        self.assertNotIn('reconcile-implementations', [edge['toStepId'] for edge in steps['integration-review']['transitions']])
        implementer = json.loads((WORKFLOW / 'nodes/node-step6-implement.json').read_text())
        self.assertEqual(implementer['model'], 'gpt-6.1-terra')

    def test_selective_dispatch_preserves_full_nested_repair_instructions(self):
        scratch = PACKAGE.parents[1] / 'tmp'
        scratch.mkdir(exist_ok=True)
        brief = {'findingId': 'missing-check', 'rootCause': 'Missing required guard',
                 'orderedChanges': ['Add guard before writing'],
                 'verification': ['python -m unittest tests.test_guard'],
                 'completionCriteria': ['Invalid input performs no write']}
        finding = {'severity': 'mid', 'file': 'src/owner.py', 'message': 'Unsafe write', 'repairInstructions': brief}
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            root = Path(directory)
            manifest_path = 'impl-plans/active/dispatch.json'
            manifest = root / manifest_path
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({
                'taskId': 'review-retry', 'workflowMode': 'issue-resolution',
                'implementationBranch': 'feat/retry', 'baseBranch': 'main', 'remote': 'origin',
                'evidenceRoot': 'tmp/review-retry',
                'reviewContext': {'issueReference': 'issue-1', 'userProblem': 'Unsafe write',
                    'requiredOutcomes': ['Reject invalid input'], 'nonGoals': [], 'constraints': [],
                    'designDecisionsAndRationale': [], 'intentionalTradeoffs': [],
                    'supportedEdgeCases': [], 'outOfScopeEdgeCases': [], 'sourcePaths': ['src/owner.py']},
                'plans': [{'planId': 'owner', 'planPath': 'impl-plans/active/owner.md',
                    'dependsOn': [], 'writePaths': ['src/owner.py'], 'sharedPaths': [],
                    'acceptanceCriteria': ['Invalid input performs no write'], 'verification': ['python -m unittest']}]
            }))
            messages = [{'fromStepId': 'integration-review', 'createdOrder': 1, 'payload': {
                'needs_revision': True, 'redispatch_required': True, 'repair_in_place': False,
                'findings': [finding], 'repairRequests': [brief], 'feedback': ['Extra top-level feedback']}}]
            with mock.patch.object(dispatch.Path, 'cwd', return_value=root), \
                 mock.patch.object(dispatch, 'checkpoint_source', return_value=(manifest_path, 'a' * 40)), \
                 mock.patch.object(dispatch, 'verify_checkpoint'):
                result = dispatch.project({'input': {'_rielaInput': {'messages': messages}}})
            item = result['payload']['implementationItems'][0]
            self.assertEqual(item['planId'], 'owner')
            self.assertEqual(item['reviewFeedback']['findings'], [finding])


if __name__ == '__main__':
    unittest.main()
