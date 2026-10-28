"""Regression coverage for D1 structured behavioral runner records."""
import importlib.util
from pathlib import Path
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / 'workflows/opus-terra-design-and-implement-review-loop'
SPEC = importlib.util.spec_from_file_location(
    'terra_progress_structured_runner',
    WORKFLOW / 'scripts/implementation-progress-check.py',
)
progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(progress)


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


def envelope(value, planned=None):
    implementation = {'planId': 'STRUCTURED-RUNNER'}
    if planned is not None:
        implementation['verification'] = planned
    return {
        'variables': {'implementation': implementation},
        'input': {'_rielaInput': {'messages': [
            {'fromStepId': 'step6-implement', 'createdOrder': 1, 'payload': value},
        ]}},
    }


def smoke(**extra):
    return {
        'command': 'node tmp/fst/FST-22/wasm-smoke-rerun.mjs',
        'kind': 'behavioral-test', 'exitStatus': 0, 'testsRun': 2,
        'testsPassed': 2, 'failureCount': 0, **extra,
    }


class StructuredRunnerTests(unittest.TestCase):
    def test_session_222_structured_runner_is_behavioral_and_ready(self):
        record = smoke(kind=' Behavioral-Test ')
        self.assertEqual(progress.behavioral_kind(record), 'test')
        self.assertTrue(progress.successful_behavioral_verification(record))
        result = progress.classify(envelope(payload([record]), ['cargo test']))
        self.assertEqual(result['when'], {'implementation_blocked': False})
        self.assertEqual(result['payload']['status'], 'ready-for-test-integrity')

    def test_unmarked_custom_runner_does_not_become_behavioral(self):
        record = {key: value for key, value in smoke().items() if key != 'kind'}
        self.assertIsNone(progress.behavioral_kind(record))
        result = progress.classify(envelope(payload([record]), ['cargo test']))
        self.assertEqual(result['when'], {'implementation_blocked': True})
        self.assertIn('positive test count', result['payload']['blockers'][-1]['message'])

    def test_kind_only_record_requires_strict_success_fields(self):
        invalid_records = (
            smoke(testsRun=0),
            {key: value for key, value in smoke().items() if key != 'testsRun'},
            {key: value for key, value in smoke().items() if key != 'failureCount'},
            smoke(failureCount=1),
            smoke(exitStatus=1),
            {**{key: value for key, value in smoke().items() if key != 'exitStatus'}, 'outcome': 'passed'},
            smoke(testsRun='2'),
            smoke(testsRun=True),
            smoke(failureCount=False),
        )
        for record in invalid_records:
            with self.subTest(record=record):
                result = progress.classify(envelope(payload([record]), ['cargo test']))
                self.assertEqual(result['when'], {'implementation_blocked': True})
                self.assertEqual(result['payload']['blockerType'], 'implementation-materially-unverified')

    def test_non_test_commands_are_excluded_from_kind_path(self):
        commands = (
            'cargo build', 'cargo clippy --all-targets -- -D warnings',
            'cargo fmt --check', 'npm run lint', 'git diff --stat', 'tsc --noEmit',
            'make check', 'python3 -m compileall src', 'tree-sitter generate',
            'node smoke.mjs && cargo fmt --check',
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertIsNone(progress.behavioral_kind(smoke(command=command)))

    def test_allowlisted_commands_keep_existing_semantics(self):
        record = {
            'command': 'node --test x.mjs', 'kind': 'behavioral-test',
            'outcome': 'passed', 'testsRun': 3,
        }
        self.assertEqual(progress.behavioral_kind(record), 'test')
        self.assertTrue(progress.successful_behavioral_verification(record))

    def test_non_string_command_is_safe_for_retained_negative_control(self):
        for command in (None, 17, []):
            with self.subTest(command=command):
                record = {
                    'command': command, 'negativeControl': True,
                    'kind': 'behavioral-test',
                }
                self.assertEqual(progress.behavioral_kind(record), 'test')
                self.assertFalse(progress.successful_behavioral_verification(record))
        prior = {
            'command': None, 'negativeControl': True, 'exitStatus': 0,
            'testsRun': 1, 'failureCount': 0, 'sourceIdentity': 'tree-1',
        }
        current = {
            'command': 'node --test x.mjs', 'environmentBlocked': True,
            'sourceIdentity': 'tree-1',
        }
        self.assertFalse(progress.inherited_behavioral_evidence(
            [current], [prior], 'tree-1', 'tree-1'
        ))

    def test_unverified_resume_criterion_names_accepted_and_rejected_forms(self):
        incomplete = payload([{'command': 'node tmp/smoke.mjs', 'exitStatus': 0}])
        incomplete['implementationIncomplete'] = True
        result = progress.classify(envelope(incomplete, ['cargo test']))
        criterion = result['payload']['resumeCriteria'][-1]
        self.assertIn('behavioral-test', criterion)
        self.assertIn('node --test', criterion)
        self.assertIn('Build, lint, format and diff commands never count.', criterion)


if __name__ == '__main__':
    unittest.main()
