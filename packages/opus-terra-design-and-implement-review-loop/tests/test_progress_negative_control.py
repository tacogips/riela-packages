"""Regression coverage for D2 negative-control and exit-status handling."""
import importlib.util
from pathlib import Path
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / 'workflows/opus-terra-design-and-implement-review-loop'
SPEC = importlib.util.spec_from_file_location(
    'terra_progress_negative_control',
    WORKFLOW / 'scripts/implementation-progress-check.py',
)
progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(progress)


MESSAGE = (
    'Step 6 reported a negative-control record that did not fail as declared '
    'or names a committed verification command.'
)


def envelope(payload, planned):
    return {
        'variables': {'implementation': {'planId': 'NEGATIVE-CONTROL', 'verification': planned}},
        'input': {'_rielaInput': {'messages': [
            {'fromStepId': 'step6-implement', 'createdOrder': 1, 'payload': payload},
        ]}},
    }


def payload(records):
    return {
        'implementation_blocked': False,
        'implementationIncomplete': False,
        'blockers': [],
        'changedFiles': ['script.py'],
        'implPlanUpdates': ['progress updated'],
        'verification': records,
        'risks': [],
        'authorSelfCheck': {'findings': [], 'verificationGaps': [], 'residualRisks': []},
    }


def passing(command='cargo nextest run'):
    return {
        'command': command, 'exitStatus': 0, 'testsRun': 12,
        'testsPassed': 12, 'failureCount': 0,
    }


def control(command='cargo mutants --file x', **extra):
    return {
        'command': command, 'negativeControl': True, 'exitStatus': 100,
        'expectedExitStatus': 100, 'testsRun': 1, 'failureCount': 1, **extra,
    }


class ExitStatusTests(unittest.TestCase):
    def test_outcome_leading_exit_status_forms(self):
        for outcome, expected in (
            ('exit=0 in 1010.466 seconds', 0),
            ('exit 1 after 3s', 1),
            ('exit: 2', 2),
            ('exit code 3', 3),
            ('exit status 4', 4),
        ):
            with self.subTest(outcome=outcome):
                record = {'command': 'cargo nextest run', 'outcome': outcome, 'failureCount': 0}
                self.assertEqual(progress.record_exit_status(record), expected)
                self.assertEqual(progress.verification_succeeded(record), expected == 0)

    def test_structured_exit_values_and_conflicts_fail_closed(self):
        self.assertEqual(progress.record_exit_status({'exitCode': '0'}), 0)
        self.assertTrue(progress.exit_status_invalid({'exitStatus': True}))
        self.assertFalse(progress.verification_succeeded({'exitStatus': True, 'outcome': 'Passed'}))
        self.assertFalse(progress.verification_succeeded({'exitStatus': 0, 'outcome': 'exit 1'}))
        self.assertFalse(progress.verification_succeeded({'exitStatus': 0, 'exitCode': 1}))
        self.assertFalse(progress.verification_succeeded({'exitStatus': 'passed'}))
        self.assertTrue(progress.verification_succeeded({'exitStatus': '0'}))
        self.assertEqual(progress.record_exit_status({'outcome': 'Exit code 2'}), 2)
        self.assertIsNone(progress.record_exit_status({'outcome': 'tests passed; exit 0'}))


class NegativeControlTests(unittest.TestCase):
    def test_valid_controls_are_forwarded_and_excluded_from_failure_gate(self):
        records = [
            passing(),
            {'command': 'vitest run', 'exitStatus': 0, 'testsRun': 703, 'failureCount': 0},
            control('cargo mutants --file x'),
            control('cargo mutants --file y'),
        ]
        result = progress.classify(envelope(payload(records), ['cargo nextest run']))
        self.assertEqual(result['when'], {'implementation_blocked': False})
        self.assertEqual(result['payload']['status'], 'ready-for-test-integrity')
        self.assertEqual(len(result['payload']['negativeControlEvidence']), 2)

    def test_outcome_exit_zero_allows_behavioral_gate(self):
        record = {
            'command': 'cargo nextest run', 'failureCount': 0,
            'outcome': 'exit 0 in 1010.466 seconds; 3 skipped',
            'testsPassed': 2816, 'testsRun': 2816,
        }
        result = progress.classify(envelope(payload([record]), ['cargo nextest run']))
        self.assertTrue(progress.verification_succeeded(record))
        self.assertEqual(result['payload']['status'], 'ready-for-test-integrity')

    def test_invalid_controls_block_with_exact_message_and_command(self):
        invalid_records = (
            {'command': 'bad control', 'negativeControl': True, 'exitStatus': 0},
            {'command': 'missing status', 'negativeControl': True},
            {'negativeControl': True},
            control('wrong expected', expectedExitStatus=2),
            control('cargo  nextest run'),
            control('cargo nextest run'),
            {'command': 'bool expected', 'negativeControl': True, 'exitStatus': 100, 'expectedExitStatus': True},
        )
        for record in invalid_records:
            with self.subTest(record=record):
                result = progress.classify(envelope(payload([passing(), record]), ['cargo nextest run']))
                self.assertEqual(result['when'], {'implementation_blocked': True})
                blocker = result['payload']['blockers'][-1]
                self.assertEqual(blocker['type'], 'implementation-materially-unverified')
                self.assertEqual(blocker['message'], MESSAGE)
                if isinstance(record.get('command'), str):
                    self.assertIn(record['command'], blocker['failingCommands'])
                else:
                    self.assertNotIn('failingCommands', blocker)

    def test_valid_control_alone_never_satisfies_positive_evidence(self):
        result = progress.classify(envelope(payload([control()]), ['cargo nextest run']))
        self.assertEqual(result['when'], {'implementation_blocked': True})
        blocker = result['payload']['blockers'][-1]
        self.assertIn('positive test count', blocker['message'])
        self.assertNotIn('failingCommands', blocker)

    def test_unflagged_failed_behavioral_command_is_still_reported(self):
        failed = {
            'command': 'cargo nextest run --filter broken', 'exitStatus': 1,
            'testsRun': 12, 'failureCount': 3,
        }
        result = progress.classify(envelope(payload([passing(), failed]), ['cargo nextest run']))
        blocker = result['payload']['blockers'][-1]
        self.assertIn('failed, blocked, skipped, or zero-count', blocker['message'])
        self.assertEqual(blocker['failingCommands'], [failed['command']])

    def test_static_plan_success_check_excludes_valid_control(self):
        static = {
            'command': 'python script.py --expect-failure', 'negativeControl': True,
            'exitStatus': 5, 'expectedExitStatus': 5,
        }
        verification = [static]
        data = payload(verification)
        result = progress.classify(envelope(data, ['python -m json.tool config.json']))
        self.assertEqual(result['when'], {'implementation_blocked': True})
        self.assertIn('no successful verification', result['payload']['blockers'][-1]['message'])

    def test_empty_control_evidence_is_omitted_from_ready_payload(self):
        data = payload([passing()])
        data['negativeControlEvidence'] = []
        result = progress.classify(envelope(data, ['cargo nextest run']))
        self.assertEqual(result['payload']['status'], 'ready-for-test-integrity')
        self.assertNotIn('negativeControlEvidence', result['payload'])


if __name__ == '__main__':
    unittest.main()
