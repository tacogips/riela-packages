"""Incomplete attempts with self-reported findings continue instead of blocking."""
import importlib.util
from pathlib import Path
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / 'workflows/opus-terra-design-and-implement-review-loop'
SPEC = importlib.util.spec_from_file_location(
    'terra_progress_incomplete_findings',
    WORKFLOW / 'scripts/implementation-progress-check.py',
)
progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(progress)

HIGH = {'severity': 'high', 'message': 'The commit factory remains incomplete.'}


def smoke():
    return {
        'command': 'bunx --no-install vitest run x.test.ts',
        'kind': 'behavioral-test', 'exitStatus': 0, 'testsRun': 3,
        'testsPassed': 3, 'failureCount': 0,
    }


def payload(incomplete, changed, findings):
    return {
        'implementation_blocked': False,
        'implementationIncomplete': incomplete,
        'blockers': [],
        'changedFiles': changed,
        'implPlanUpdates': [f'progress {changed[-1] if changed else "none"}'],
        'verification': [smoke()],
        'risks': [],
        'authorSelfCheck': {'findings': findings, 'verificationGaps': [], 'residualRisks': []},
    }


def envelope(attempts):
    messages = [
        {'fromStepId': 'step6-implement', 'createdOrder': index + 1, 'payload': value}
        for index, value in enumerate(attempts)
    ]
    return {
        'variables': {'implementation': {'planId': 'INCOMPLETE-FINDINGS'}},
        'input': {'_rielaInput': {'messages': messages}},
    }


class IncompleteFindingsTests(unittest.TestCase):
    def test_incomplete_attempt_with_high_finding_continues(self):
        result = progress.classify(envelope([payload(True, ['a.ts'], [HIGH])]))
        self.assertEqual(result['when'], {'implementation_continue': True})

    def test_complete_attempt_with_high_finding_still_blocks(self):
        result = progress.classify(envelope([payload(False, ['a.ts'], [HIGH])]))
        self.assertTrue(result['when']['implementation_blocked'])
        types = [b.get('type') for b in result['payload']['blockers']]
        self.assertIn('implementation-material-finding', types)

    def test_incomplete_streak_limit_still_blocks_as_incomplete(self):
        attempts = [payload(True, [f'f{i}.ts'], [HIGH]) for i in range(5)]
        result = progress.classify(envelope(attempts))
        self.assertTrue(result['when']['implementation_blocked'])
        types = [b.get('type') for b in result['payload']['blockers']]
        self.assertIn('implementation-incomplete', types)
        self.assertNotIn('implementation-material-finding', types)


if __name__ == '__main__':
    unittest.main()
