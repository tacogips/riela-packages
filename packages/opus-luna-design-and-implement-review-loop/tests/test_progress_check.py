"""Recognize package test runners as behavioral verification."""
import importlib.util
from pathlib import Path
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / 'workflows/opus-luna-design-and-implement-review-loop'

spec = importlib.util.spec_from_file_location(
    'luna_progress_check', WORKFLOW / 'scripts' / 'implementation-progress-check.py')
progress = importlib.util.module_from_spec(spec)
spec.loader.exec_module(progress)


class BehavioralEvidenceTests(unittest.TestCase):
    def test_python_unittest_with_positive_count_is_behavioral_evidence(self):
        for command in (
            "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v",
            'python -m unittest tests/test_wave_outcome.py',
            'python3.15 -m unittest tests.test_progress_check',
        ):
            record = {'command': command, 'exitCode': 0, 'testsRun': 12, 'failureCount': 0}
            self.assertEqual(progress.behavioral_kind(record), 'test', command)
            self.assertTrue(progress.successful_behavioral_verification(record), command)

    def test_python_unittest_with_zero_tests_is_not_success(self):
        record = {'command': 'python3 -m unittest discover -s tests', 'exitCode': 0, 'testsRun': 0}
        self.assertFalse(progress.successful_behavioral_verification(record))

    def test_non_test_python_commands_stay_non_behavioral(self):
        for command in ('python3 -m json.tool mock-scenario.json', 'python3 scripts/unittest_report.py'):
            self.assertIsNone(progress.behavioral_kind({'command': command}), command)


class MaterialFindingTests(unittest.TestCase):
    def test_open_mid_finding_blocks(self):
        payload = {'findings': [{'severity': 'mid', 'status': 'open', 'summary': 'x'}]}
        self.assertEqual(len(progress.material_findings(payload)), 1)

    def test_finding_without_status_still_blocks(self):
        self.assertEqual(len(progress.material_findings({'risks': [{'severity': 'high'}]})), 1)

    def test_resolved_or_downstream_owned_findings_do_not_block(self):
        for status in ('resolved', 'Fixed', 'pending_downstream', 'pending-downstream', 'owned elsewhere'):
            payload = {'findings': [{'severity': 'mid', 'status': status}]}
            self.assertEqual(progress.material_findings(payload), [], status)

    def test_severity_prefixed_strings_still_block(self):
        self.assertEqual(len(progress.material_findings({'risks': ['high: data loss on retry']})), 1)


if __name__ == '__main__':
    unittest.main()
