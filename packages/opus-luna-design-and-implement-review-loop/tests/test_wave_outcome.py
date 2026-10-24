import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

PACKAGE = Path(__file__).resolve().parents[1]
WORKFLOW = PACKAGE / 'workflows/opus-luna-design-and-implement-review-loop'
SCRIPT = WORKFLOW / 'scripts/implementation-wave-outcome.py'
spec = importlib.util.spec_from_file_location('luna_wave_outcome', SCRIPT)
wave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)


def envelope(join=None, messages=None, session='session-test'):
    messages = list(messages or [])
    if join is not None:
        messages.append({'fromStepId': 'dispatch-plans', 'createdOrder': 2, 'payload': {'fanoutJoin': join}})
    return {'input': {'_rielaInput': {'workflowExecutionId': session, 'messages': messages}}}


def branch(plan, status='completed', **output):
    return {'branchId': plan, 'status': status, 'output': output}


def run(join, root, session='session-test'):
    return wave.classify(envelope(join, session=session), root)


class WaveOutcomeTests(unittest.TestCase):
    def test_large_join_is_bounded_and_totals_are_exact(self):
        branches = [branch(x, evidencePaths=['evidence/'+x], changedFiles=['src/'+x], reviewDecisions={'feedback': 'r'*300000}, continuation='c'*300000) for x in 'abc']
        branches.append(branch('d', implementation_blocked=True, blockerType='test-failure', blockers=['fix tests'], resumeCriteria=['rerun tests']))
        observations = []
        for i in range(5200):
            observations.append({'path': f'pkg/file-{i%1100:04}.py', 'selection': 'source' if i%2 == 0 else 'artifact', 'kind': 'content' if i%3 else 'membership', 'branchId': 'd' if i%4==0 else 'a', 'contents': 'z'*1800})
        join = {'branches': branches, 'dispatchedBranchIds': list('abcd'), 'pendingBranchIds': [], 'completedBranchIds': list('abcd'), 'changeEvidence': {'complete': True, 'hasDrift': True, 'observations': observations, 'captureFailures': [{'contents':'secret'}], 'reduceFailures': []}}
        self.assertGreaterEqual(len(wave.compact(join)), 8*1024*1024)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); result=run(join,root)
            summary_path=next(root.glob('tmp/opus-luna-waves/session-test/wave-*/wave-summary.json'))
            summary=json.loads(summary_path.read_text())
            raw_path=summary_path.with_name('fanout-join.json')
            raw=raw_path.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), summary['rawJoinSha256'])
            self.assertEqual(raw,wave.compact(join))
            self.assertLessEqual(len(summary_path.read_bytes())+len(wave.compact(result['payload'])),65536)
            self.assertEqual(summary['verdict'],result['payload'])
            self.assertEqual(result['payload']['blockedPlanIds'],['d'])
            self.assertEqual(result['payload']['successfulPlanIds'],list('abc'))
            self.assertTrue(result['when']['partial_success'])
            self.assertEqual(summary['changeEvidence']['observationTotal'],5200)
            self.assertEqual(summary['changeEvidence']['pathTotal'],1100)
            self.assertTrue(summary['changeEvidence']['hasDrift'])
            self.assertEqual(summary['changeEvidence']['captureFailuresTotal'],1)
            self.assertEqual(summary['changeEvidence']['reduceFailuresTotal'],0)
            self.assertEqual(len(summary['plans']),4)
            self.assertEqual({plan['planId']:plan['classification'] for plan in summary['plans']},{'a':'successful','b':'successful','c':'successful','d':'blocked'})
            self.assertEqual({plan['planId']:plan['status'] for plan in summary['plans']},{'a':'completed','b':'completed','c':'completed','d':'completed'})
            blocked=next(plan for plan in summary['plans'] if plan['planId']=='d')
            self.assertEqual(blocked['blockers'],['fix tests'])
            self.assertEqual(blocked['resumeCriteria'],['rerun tests'])
            self.assertEqual(blocked['blockerType'],'test-failure')
            payload_blocker=next(item for item in result['payload']['blockers'] if item['planId']=='d')
            self.assertEqual(payload_blocker['message'],'fix tests')
            self.assertEqual(payload_blocker['blockerType'],'test-failure')
            self.assertIn('rerun tests',result['payload']['resumeCriteria'])
            self.assertEqual(summary['changeEvidence']['paths'][0]['selection'],'source')
            self.assertIn('content',[kind for kind,_ in summary['changeEvidence']['paths'][0]['kinds']])
            self.assertNotIn(b'contents',summary_path.read_bytes())

    def test_runtime_reason_observations_rank_removed_first(self):
        branches=[branch(plan,evidencePaths=['e'],changedFiles=[]) for plan in ('a','b')]
        observations=[
            {'branchId':'a','path':f'src/f{i:03}.py','selection':'source','snapshotPath':None,'stepId':'s','reason':'content-or-mode-drift'}
            for i in range(200) for _ in range(3)
        ]
        observations.append({'branchId':'b','path':'src/zz-deleted.py','selection':'source','snapshotPath':None,'stepId':'s','reason':'entry-removed'})
        join={'branches':branches,'dispatchedBranchIds':['a','b'],'completedBranchIds':['a','b'],'changeEvidence':{'complete':True,'hasDrift':True,'observations':observations}}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); result=run(join,root)
            summary=json.loads(next(root.glob('tmp/opus-luna-waves/session-test/wave-*/wave-summary.json')).read_text())
        self.assertEqual(summary['changeEvidence']['byKind'],{'content-or-mode-drift':600,'entry-removed':1})
        self.assertNotIn('unknown',summary['changeEvidence']['byKind'])
        self.assertEqual(summary['changeEvidence']['paths'][0]['path'],'src/zz-deleted.py')
        self.assertEqual(summary['changeEvidence']['paths'][0]['kinds'],[['entry-removed',1]])
        self.assertEqual(summary['changeEvidence']['pathsOmitted'],161)
        self.assertEqual(summary['changeEvidence']['observationTotal'],601)
        self.assertEqual(summary['verdict'],result['payload'])

    def test_removed_artifact_path_ranks_before_many_source_content_paths(self):
        branches=[branch('a',evidencePaths=['e'],changedFiles=[])]
        observations=[
            {'branchId':'a','path':f'src/f{i:03}.py','selection':'source','reason':'content-or-mode-drift'}
            for i in range(60) for _ in range(3)
        ]
        observations.append({'branchId':'a','path':'art/removed.json','selection':'artifact','reason':'entry-removed'})
        join={'branches':branches,'dispatchedBranchIds':['a'],'completedBranchIds':['a'],'changeEvidence':{'complete':True,'hasDrift':True,'observations':observations}}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); run(join,root)
            summary=json.loads(next(root.glob('tmp/opus-luna-waves/session-test/wave-*/wave-summary.json')).read_text())
        self.assertEqual(summary['changeEvidence']['paths'][0]['path'],'art/removed.json')
        self.assertEqual(summary['changeEvidence']['paths'][0]['selection'],'artifact')

    def test_resume_criteria_are_capped_per_plan_in_blocked_order(self):
        join={'branches':[branch('a',evidencePaths=['e'],changedFiles=[])]}
        join['branches'].extend(branch(plan,implementation_blocked=True,blockerType='test-failure',blockers=['blocked'],resumeCriteria=[f'rerun {plan}']) for plan in 'pqrs')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); result=run(join,root)
            summary=json.loads(next(root.glob('tmp/opus-luna-waves/session-test/wave-*/wave-summary.json')).read_text())
        self.assertEqual(result['payload']['resumeCriteria'],[f'rerun {plan}' for plan in 'pqrs'])
        self.assertEqual(summary['verdict'],result['payload'])

    def test_resume_criteria_cap_is_three_for_one_plan(self):
        join={'branches':[branch('p',implementation_blocked=True,blockerType='test-failure',blockers=['blocked'],resumeCriteria=[f'rerun {i}' for i in range(5)])]}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); result=run(join,root)
            summary=json.loads(next(root.glob('tmp/opus-luna-waves/session-test/wave-*/wave-summary.json')).read_text())
        self.assertEqual(result['payload']['resumeCriteria'],['rerun 0','rerun 1','rerun 2'])
        self.assertEqual(summary['verdict'],result['payload'])

    def test_shared_tracking_resume_criterion_is_deduplicated(self):
        join={'branches':[
            {'branchId':'p','status':'failed','failureReason':wave.POLICY_PREFIXES[0]+' violation','output':{}},
            {'branchId':'q','status':'failed','failureReason':wave.POLICY_PREFIXES[1]+' violation','output':{}},
            branch('a',evidencePaths=['e'],changedFiles=[]),
        ]}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); result=run(join,root)
            summary=json.loads(next(root.glob('tmp/opus-luna-waves/session-test/wave-*/wave-summary.json')).read_text())
        self.assertEqual(result['payload']['resumeCriteria'],[wave.TRACKING_RESUME_CRITERION])
        self.assertEqual(summary['verdict'],result['payload'])

    def test_tracking_contract_prefixes_block_and_keep_exact_resume(self):
        for prefix in wave.POLICY_PREFIXES:
            join={'branches':[{'branchId':'a','status':'failed','failureReason':prefix+' violation','output':{}},branch('b',evidencePaths=['e'],changedFiles=[])]}
            with self.subTest(prefix=prefix), tempfile.TemporaryDirectory() as d:
                result=run(join,Path(d))
                self.assertEqual(result['payload']['blockedPlanIds'],['a'])
                self.assertIn(wave.TRACKING_RESUME_CRITERION,result['payload']['resumeCriteria'])
                self.assertTrue(result['when']['partial_success'])

    def test_incomplete_evidence_attributable_or_global(self):
        for diagnostic, expected in [([{'branchId':'b','path':'x'}],['b']),([],['a','b'])]:
            join={'branches':[branch('a',evidencePaths=['e'],changedFiles=[]),branch('b',evidencePaths=['e'],changedFiles=[])], 'dispatchedBranchIds':['a','b'], 'changeEvidence':{'complete':False,'captureFailures':diagnostic}}
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as d:
                result=run(join,Path(d))
                self.assertEqual(result['payload']['blockedPlanIds'],expected)
                self.assertIn(wave.TRACKING_RESUME_CRITERION,result['payload']['resumeCriteria'])

    def test_pending_undispatched_plan_has_no_raw_pointer(self):
        join={'branches':[branch('a',evidencePaths=['e'],changedFiles=[])],'dispatchedBranchIds':['a'],'pendingBranchIds':['e'],'completedBranchIds':['a'],'changeEvidence':{'complete':True,'observations':[],'captureFailures':[],'reduceFailures':[]}}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); result=run(join,root)
            summary=json.loads(next(root.glob('tmp/opus-luna-waves/session-test/wave-*/wave-summary.json')).read_text())
        self.assertEqual(result['payload']['successfulPlanIds'],['a'])
        self.assertEqual([(p['classification'],p['rawPointer']) for p in summary['plans'] if p['planId']=='e'],[('pending',None)])

    def test_blocked_only_is_not_partial_success(self):
        with tempfile.TemporaryDirectory() as d:
            result=run({'branches':[branch('a',implementation_blocked=True)]},Path(d))
            self.assertEqual(result['when'],{'implementation_blocked':True,'partial_success':False})

    def test_failed_and_cancelled_are_not_blocked_or_successful(self):
        with tempfile.TemporaryDirectory() as d:
            result=run({'branches':[{'branchId':'a','status':'failed','failureReason':'provider_error: x'},branch('b','cancelled')]},Path(d))
            self.assertFalse(result['when']['implementation_blocked'])
            self.assertEqual(result['payload']['blockedPlanIds'],[])
            self.assertEqual(result['payload']['successfulPlanIds'],[])

    def test_all_success_and_closed_payload_contract(self):
        with tempfile.TemporaryDirectory() as d:
            result=run({'branches':[branch('a',evidencePaths=['e'],changedFiles=[])]},Path(d))
        self.assertEqual(result['payload']['partial_success'],False)
        self.assertEqual(result['payload']['blockers'],[])
        self.assertEqual(result['payload']['resumeCriteria'],[])
        self.assertEqual(set(result['payload']),set(wave.SCHEMA_KEYS))

    def test_node_schema_prompt_and_transitions(self):
        node=json.loads((WORKFLOW/'nodes/node-implementation-wave-outcome.json').read_text())
        self.assertEqual(node['nodeType'],'command')
        self.assertEqual(node['command']['scriptPath'],'scripts/implementation-wave-outcome.py')
        self.assertNotIn('model',node)
        self.assertEqual(set(node['output']['jsonSchema']['properties']),set(wave.SCHEMA_KEYS))
        self.assertEqual(set(node['output']['jsonSchema']['required']),set(wave.SCHEMA_KEYS))
        self.assertFalse(node['output']['jsonSchema']['additionalProperties'])
        self.assertFalse((WORKFLOW/'prompts/implementation-wave-outcome.md').exists())
        workflow=json.loads((WORKFLOW/'workflow.json').read_text())
        step=next(s for s in workflow['steps'] if s['id']=='implementation-wave-outcome')
        self.assertEqual(step['transitions'],[{'toStepId':'implementation-blocked-output','label':'implementation_blocked && !(partial_success)'},{'toStepId':'reconcile-implementations','label':'!(implementation_blocked) || partial_success'}])

    def test_repeated_join_preserves_previous_and_allocates_next(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); join={'branches':[]}
            run(join,root); first=next(root.glob('tmp/opus-luna-waves/session-test/wave-001/fanout-join.json')).read_bytes()
            run(join,root)
            self.assertEqual(first,(root/'tmp/opus-luna-waves/session-test/wave-001/fanout-join.json').read_bytes())
            self.assertTrue((root/'tmp/opus-luna-waves/session-test/wave-002').is_dir())

    def test_unsafe_ids_and_symlink_directories_fail_closed(self):
        for session in ('../x',''):
            with self.subTest(session=session), tempfile.TemporaryDirectory() as d:
                with self.assertRaises(ValueError): run({'branches':[]},Path(d),session=session)
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as other:
            (Path(d)/'tmp').symlink_to(other)
            with self.assertRaises(ValueError): run({'branches':[]},Path(d))

    def test_deterministic_summaries_ignoring_locator_fields(self):
        join={'branches':[branch('a',evidencePaths=['e'],changedFiles=[])], 'changeEvidence':{'observations':[{'path':'x','kind':'content','selection':'source'}]}}
        summaries=[]
        for _ in range(2):
            with tempfile.TemporaryDirectory() as d:
                run(join,Path(d)); summary=json.loads(next(Path(d).glob('tmp/opus-luna-waves/session-test/wave-*/wave-summary.json')).read_text())
                for key in ('waveOrdinal','summaryPath','rawJoinPath'): summary.pop(key)
                summaries.append(summary)
        self.assertEqual(summaries[0],summaries[1])

    def test_tiny_summary_limit_and_invalid_main_input(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(wave,'SUMMARY_BYTE_LIMIT',1):
            with self.assertRaises(ValueError): run({'branches':[]},Path(d))
        old_stdin, old_stderr = wave.sys.stdin, wave.sys.stderr
        from io import StringIO
        try:
            wave.sys.stdin=StringIO('{bad\n'); wave.sys.stderr=StringIO()
            self.assertEqual(wave.main(),1)
            self.assertIn('error',json.loads(wave.sys.stderr.getvalue()))
        finally:
            wave.sys.stdin, wave.sys.stderr = old_stdin, old_stderr

    def test_standalone_fallback(self):
        msg={'fromStepId':'implementation-progress-check','createdOrder':1,'payload':{'implementation_blocked':True,'planId':'p'}}
        with tempfile.TemporaryDirectory() as d:
            result=wave.classify(envelope(messages=[msg]),Path(d))
            self.assertEqual(result['payload']['blockedPlanIds'],['p'])
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
            wave.classify(envelope(messages=[]),Path(d))


if __name__ == '__main__':
    unittest.main()
