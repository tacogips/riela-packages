"""Keep static-only plans reviewable and the integration-review envelope explicit."""
import importlib.util
import json
from pathlib import Path
import re
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / 'workflows/opus-luna-design-and-implement-review-loop'
SPEC = importlib.util.spec_from_file_location('luna_progress', WORKFLOW / 'scripts/implementation-progress-check.py')
progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(progress)

STATIC_PLAN_VERIFICATION = [
    'bash -n scripts/build-app.sh',
    'scripts/build-app.sh --bogus (expect exit 2)',
    'plutil -lint packaging/app/Info.plist',
]


def envelope(payload, planned=None):
    variables = {}
    if planned is not None:
        variables['implementation'] = {'planId': 'PLAN-02', 'verification': planned}
    return {
        'variables': variables,
        'input': {'_rielaInput': {'messages': [
            {'fromStepId': 'step6-implement', 'createdOrder': 1, 'payload': payload},
        ]}},
    }


def static_payload(verification=None):
    return {
        'implementation_blocked': False,
        'implementationIncomplete': False,
        'blockers': [],
        'changedFiles': ['scripts/build-app.sh', 'packaging/app/Info.plist'],
        'implPlanUpdates': ['PLAN-02 progress log updated'],
        'verification': verification if verification is not None else [
            {'command': 'bash -n scripts/build-app.sh', 'exitCode': 0, 'outcome': 'Passed'},
            {'command': 'scripts/build-app.sh --bogus', 'exitCode': 2, 'outcome': 'Passed expected invalid-argument behavior'},
            {'command': 'plutil -lint packaging/app/Info.plist', 'exitCode': 0, 'outcome': 'Passed: OK'},
        ],
        'risks': [],
        'authorSelfCheck': {'findings': [], 'verificationGaps': [], 'residualRisks': []},
    }


class ProgressGateTests(unittest.TestCase):
    def test_static_only_plan_reaches_test_integrity(self):
        result = progress.classify(envelope(static_payload(), STATIC_PLAN_VERIFICATION))
        self.assertEqual(result['when'], {'implementation_blocked': False})
        self.assertEqual(result['payload']['status'], 'ready-for-test-integrity')
        self.assertEqual(result['payload']['verificationPolicy'], 'plan-declared-static')

    def test_static_only_plan_without_any_successful_check_stays_blocked(self):
        failed = [{'command': 'plutil -lint packaging/app/Info.plist', 'exitCode': 1, 'outcome': 'failed'}]
        result = progress.classify(envelope(static_payload(failed), STATIC_PLAN_VERIFICATION))
        self.assertEqual(result['when'], {'implementation_blocked': True})
        self.assertEqual(result['payload']['blockerType'], 'implementation-materially-unverified')

    def test_plan_with_declared_test_runner_still_requires_behavioral_evidence(self):
        planned = STATIC_PLAN_VERIFICATION + ['swift test --filter AppCoreTests']
        result = progress.classify(envelope(static_payload(), planned))
        self.assertEqual(result['when'], {'implementation_blocked': True})
        self.assertIn('positive test count', result['payload']['blockers'][-1]['message'])

    def test_missing_committed_verification_contract_fails_closed(self):
        for planned in (None, []):
            with self.subTest(planned=planned):
                result = progress.classify(envelope(static_payload(), planned))
                self.assertEqual(result['when'], {'implementation_blocked': True})
                self.assertIn('positive test count', result['payload']['blockers'][-1]['message'])

    def test_behavioral_plan_with_positive_count_is_unchanged(self):
        payload = static_payload([
            {'command': 'swift test --filter AppCoreTests', 'exitCode': 0, 'testsRun': 27, 'testsPassed': 27, 'failureCount': 0},
        ])
        result = progress.classify(envelope(payload, ['swift test --filter AppCoreTests']))
        self.assertEqual(result['when'], {'implementation_blocked': False})
        self.assertEqual(result['payload']['verificationPolicy'], 'behavioral-tests')


class IntegrationReviewEnvelopeTests(unittest.TestCase):
    def test_prompt_shows_when_payload_envelope_with_review_fields_in_payload(self):
        prompt = (WORKFLOW / 'prompts/integration-review.md').read_text()
        self.assertIn('## Output envelope', prompt)
        blocks = re.findall(r'```json\n(.*?)\n```', prompt, flags=re.DOTALL)
        envelopes = [json.loads(block) for block in blocks]
        envelope_example = next(item for item in envelopes if set(item) == {'when', 'payload'})
        node = json.loads((WORKFLOW / 'nodes/node-integration-review.json').read_text())
        required = node['output']['jsonSchema']['required']
        self.assertTrue(set(required) <= set(envelope_example['payload']))
        self.assertEqual(
            set(envelope_example['when']),
            {'needs_revision', 'redispatch_required', 'repair_in_place', 'plans_remaining'},
        )


if __name__ == '__main__':
    unittest.main()
