"""Route commits to push or a local-only finish through workflowInput.gitPush."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / 'workflows/opus-luna-design-and-implement-review-loop'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, WORKFLOW / 'scripts' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate = load('luna_push_gate', 'git-push-gate.py')
dispatch = load('luna_dispatch_for_gate', 'dispatch-plans.py')

COMMIT = {'git': {'operation': 'commit', 'status': 'committed', 'commitHash': 'a' * 40,
                  'committedFiles': ['impl-plans/active/dispatch.json']}}


def envelope(variables, messages=None):
    messages = messages if messages is not None else [
        {'fromStepId': 'plan-git-commit', 'createdOrder': 1, 'payload': COMMIT}]
    return {'variables': variables, 'input': {'_rielaInput': {'messages': messages}}}


class GitPushGateTests(unittest.TestCase):
    def test_push_is_the_default(self):
        result = gate.route(envelope({'workflowInput': {}}))
        self.assertTrue(result['payload']['push'])
        self.assertFalse(result['payload']['local_only'])
        self.assertEqual(result['payload']['git'], COMMIT['git'])

    def test_git_push_false_routes_local_only_and_keeps_commit_evidence(self):
        result = gate.route(envelope({'workflowInput': {'gitPush': False}}))
        self.assertEqual(result['when'], {'push': False, 'local_only': True})
        self.assertEqual((result['payload']['push'], result['payload']['local_only'], result['payload']['gitPush']),
                         (False, True, False))
        self.assertEqual(result['payload']['git']['commitHash'], 'a' * 40)

    def test_called_workflow_input_wins_over_parent_defaults(self):
        variables = {'workflowInput': {'gitPush': True},
                     'workflowCall': {'input': {'workflowInput': {'gitPush': 'false'}}}}
        self.assertFalse(gate.route(envelope(variables))['payload']['push'])

    def test_unknown_value_fails_closed(self):
        with self.assertRaises(ValueError):
            gate.route(envelope({'workflowInput': {'gitPush': 'no'}}))

    def test_requires_a_commit_and_uses_the_newest_one(self):
        with self.assertRaises(ValueError):
            gate.route(envelope({}, messages=[]))
        newer = {'git': dict(COMMIT['git'], commitHash='b' * 40)}
        messages = [{'fromStepId': 'step10-git-commit', 'createdOrder': 9, 'payload': newer},
                    {'fromStepId': 'step10-git-commit', 'createdOrder': 2, 'payload': COMMIT}]
        self.assertEqual(gate.route(envelope({}, messages))['payload']['git']['commitHash'], 'b' * 40)

    def test_workflow_routes_both_commits_through_gates(self):
        workflow = json.loads((WORKFLOW / 'workflow.json').read_text())
        steps = {step['id']: step for step in workflow['steps']}
        self.assertEqual(steps['plan-git-commit']['transitions'], [{'toStepId': 'plan-push-gate'}])
        self.assertEqual(steps['plan-push-gate']['transitions'], [
            {'toStepId': 'plan-git-push', 'label': 'push'}, {'toStepId': 'dispatch-plans', 'label': 'local_only'}])
        self.assertEqual(steps['step10-git-commit']['transitions'], [{'toStepId': 'final-push-gate'}])
        self.assertEqual(steps['final-push-gate']['transitions'], [
            {'toStepId': 'step11-git-push', 'label': 'push'}, {'toStepId': 'workflow-output', 'label': 'local_only'}])
        local = json.loads((WORKFLOW / 'mock-scenario-local.json').read_text())
        for skipped in ('plan-git-push', 'step11-git-push', 'base-branch-integrate'):
            self.assertNotIn(skipped, local)

    def test_dispatch_accepts_the_local_only_checkpoint(self):
        scratch = PACKAGE.parents[1] / 'tmp'
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            root = Path(directory)
            manifest = root / 'impl-plans/active/dispatch.json'
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({'plans': []}))
            forwarded = dict(COMMIT, gitPush=False, push=False, local_only=True)
            messages = [{'fromStepId': 'plan-push-gate', 'createdOrder': 1, 'payload': forwarded}]
            with mock.patch.object(dispatch.Path, 'cwd', return_value=root):
                self.assertEqual(dispatch.checkpoint_source(messages, root),
                                 ('impl-plans/active/dispatch.json', 'a' * 40))


if __name__ == '__main__':
    unittest.main()
