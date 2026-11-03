import itertools
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("wave_tests", Path(__file__).with_name("test_wave_outcome.py"))
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
WORKFLOW, branch, run, wave = helpers.WORKFLOW, helpers.branch, helpers.run, helpers.wave


class BlockedWaveAmendmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git('init', '-q')
        (self.root / 'intake').write_text('intake')
        self.commit('intake')
        self.original = self.git('rev-parse', 'HEAD')
        self.manifest = self.root / 'impl-plans/active/t-dispatch.json'
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_text(json.dumps({'taskId':'t','originalHead':self.original,'plans':[{'planId':'a','writePaths':['src/a.py']}]}))
        self.commit('checkpoint')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        self.git('add', 'intake' if message == 'intake' else 'impl-plans/active/t-dispatch.json')
        self.git('-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', message)

    def checkpoint(self):
        self.manifest.write_text(self.manifest.read_text() + ' ')
        self.commit('amendment')

    def evaluate(self, blocker=None, **output):
        if blocker is None:
            blocker = {'paths':['src/b.py'], 'dependency':'b.py outside writePaths', 'evidence':'e', 'resumeCriterion':'authorize src/b.py in writePaths'}
        marker = {'type':'implementation-dependency','evidenceFingerprint':'fingerprint'}
        data = {'implementation_blocked':True,'blockerType':'implementation-dependency','blockers':[blocker, marker]}
        data.update(output)
        result = run({'branches':[{'branchId':'a', 'status':'completed', 'output':data}]}, self.root)
        summary = json.loads(sorted(self.root.glob('tmp/opus-terra-waves/session-test/wave-*/wave-summary.json'))[-1].read_text())
        self.assertEqual(summary['verdict'], result['payload'])
        return result, summary['amendmentDecision']

    def test_eligible_and_shared_budget(self):
        head = self.git('rev-parse', 'HEAD')
        result, decision = self.evaluate()
        amendment = result['payload']['checkpointAmendment']
        self.assertEqual(result['when'], {'implementation_blocked':True,'partial_success':False,'amendment_required':True})
        self.assertEqual(amendment['blockers'], [{'planId':'a','paths':['src/b.py'],'dependency':'b.py outside writePaths','evidence':'e','resumeCriterion':'authorize src/b.py in writePaths'}])
        self.assertEqual((amendment['manifestPath'], amendment['previousCheckpointCommit'], amendment['amendmentRound'], amendment['maxAmendmentRounds']), ('impl-plans/active/t-dispatch.json', head, 0, 2))
        self.assertEqual(amendment['reason'], 'blocked-wave-scope-or-contract')
        self.assertTrue(decision['eligible'])
        self.assertEqual(wave.MAX_CHECKPOINT_AMENDMENTS, wave._dispatch_wave.MAX_CHECKPOINT_AMENDMENTS)
        self.checkpoint()
        self.assertEqual(self.evaluate()[0]['payload']['checkpointAmendment']['amendmentRound'], 1)
        self.checkpoint()
        result, decision = self.evaluate()
        self.assertFalse(result['when']['amendment_required'])
        self.assertTrue(decision['eligible'])
        self.assertTrue(any('amendment-budget-exhausted' in r for r in decision['ineligibleReasons']))

    def test_exclusions_and_scope(self):
        markers = ['network failure','external service unavailable','review rejection','test-integrity failure: restore skipped test']
        for marker in markers:
            for field in ('message','resumeCriteria'):
                blocker={'paths':['tests/test_contract.py'],'dependency':'missing additive field',field: [marker] if field == 'resumeCriteria' else marker}
                with self.subTest(marker=marker, field=field):
                    self.assertFalse(self.evaluate(blocker)[0]['when']['amendment_required'])
            self.assertFalse(self.evaluate(resumeCriteria=[marker])[0]['when']['amendment_required'])
        self.assertTrue(self.evaluate({'paths':['tests/test_contract.py'],'dependency':'missing additive field','resumeCriteria':['Authorize tests/test_contract.py in writePaths via checkpoint amendment.']})[0]['when']['amendment_required'])
        for blocker in ('text only', {'resumeCriteria':[42]}, {'paths':['src/x'],'resumeCriteria':[42]}):
            self.assertFalse(self.evaluate(blocker)[0]['when']['amendment_required'])
        self.assertFalse(self.evaluate(blockers=[{'type':'implementation-dependency','evidenceFingerprint':'x'}])[0]['when']['amendment_required'])

    def test_gate_types_and_environment(self):
        for gate in ('implementation-material-finding','implementation-materially-unverified','implementation-no-progress','implementation-incomplete','implementation-invalid-evidence'):
            self.assertFalse(self.evaluate(blockerType=gate)[0]['when']['amendment_required'])
        for flags in ({'environmentBlocked':True}, {'status':'blocked-environment'}):
            self.assertFalse(self.evaluate(**flags)[0]['when']['amendment_required'])

    def test_oversize_and_non_git(self):
        result, decision = self.evaluate({'paths':['src/x'],'evidence':'x'*17000})
        self.assertFalse(result['when']['amendment_required'])
        self.assertIn('amendment-oversize', decision['ineligibleReasons'])
        with tempfile.TemporaryDirectory() as directory:
            result = run({'branches':[branch('a',implementation_blocked=True,blockerType='implementation-dependency',blockers=[{'path':'src/a'}])]}, Path(directory))
            self.assertFalse(result['when']['amendment_required'])
            summary=json.loads(next(Path(directory).glob('tmp/opus-terra-waves/*/wave-*/wave-summary.json')).read_text())
            self.assertTrue(any(x.startswith('checkpoint-unresolved') for x in summary['amendmentDecision']['ineligibleReasons']))

    def test_wave_shape_and_routes(self):
        blocked=branch('a', implementation_blocked=True, blockerType='implementation-dependency', blockers=[{'path':'src/a'}])
        for other in (branch('b', 'failed'), {'branchId':'b','status':'failed','failureReason':'policy_blocked: fanout snapshot bad'}, branch('b',evidencePaths=['e'],changedFiles=[])):
            self.assertFalse(run({'branches':[blocked,other]},self.root)['when']['amendment_required'])
        self.assertFalse(run({'branches':[blocked], 'changeEvidence':{'complete':False}},self.root)['when']['amendment_required'])
        step=next(s for s in json.loads((WORKFLOW/'workflow.json').read_text())['steps'] if s['id']=='implementation-wave-outcome')
        self.assertEqual([t['label'] for t in step['transitions']], ['implementation_blocked && !(partial_success) && amendment_required','implementation_blocked && !(partial_success || amendment_required)','!(implementation_blocked) || partial_success'])
        for b,p,a in itertools.product((False,True), repeat=3):
            matches = [b and not p and a, b and not (p or a), not b or p]
            self.assertLessEqual(sum(matches),1)
            if not a or (b and not p):
                self.assertEqual(sum(matches),1)


if __name__ == '__main__':
    unittest.main()
