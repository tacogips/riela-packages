import { strict as assert } from 'node:assert';
import { cpSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { spawnSync } from 'node:child_process';

const packageName = 'fable-and-improve-codex';
const source = resolve('packages', packageName, 'workflows', packageName);
const argumentsList = process.argv.slice(2);
const evidenceFlag = argumentsList.indexOf('--evidence-root');
assert(evidenceFlag >= 0 && argumentsList[evidenceFlag + 1], 'absolute --evidence-root is required');
const evidence = argumentsList[evidenceFlag + 1];
assert(evidence.startsWith('/'), '--evidence-root must be absolute');
const receiptFlag = argumentsList.indexOf('--happy-receipt');
assert(receiptFlag < 0, 'prior happy receipt lacks source-input hashes; run a fresh happy case');
mkdirSync(evidence, { recursive: true });

const authored = JSON.parse(readFileSync(join(source, 'mock-scenario.json'), 'utf8'));
const workflow = JSON.parse(readFileSync(join(source, 'workflow.json'), 'utf8'));
let assertions = 0;
function check(condition: unknown, message: string): void {
  assert(condition, message);
  assertions++;
}
function eq(actual: unknown, expected: unknown, message: string): void {
  assert.deepEqual(actual, expected, message);
  assertions++;
}
function output(step: string): any {
  return JSON.parse(readFileSync(join(source, 'nodes', `node-${step}.json`), 'utf8')).output;
}

const agentNodes = workflow.nodes.filter((item: any) => item.nodeFile).map((item: any) =>
  JSON.parse(readFileSync(join(source, item.nodeFile), 'utf8')));
eq(agentNodes.length, 16, 'agent count');
for (const node of agentNodes) check(['read-only', 'workspace-write', 'danger-full-access'].includes(node.agentSandbox), `${node.id} sandbox`);
for (const id of ['fable-analysis', 'kb-self-review', 'kb-merge-judge', 'kb-archive-brief',
  'codex-review', 'fable-goal-review', 'integration-review', 'plan-checkpoint', 'step9-commit-message']) {
  check(!!output(id)?.jsonSchema, `${id} required schema`);
  eq(output(id).maxValidationAttempts, 2, `${id} retry budget`);
}
for (const id of ['codex-implementation', 'fable-design', 'branch-evidence', 'base-branch-integrate']) {
  check(!!output(id)?.jsonSchema, `${id} required schema`);
  eq(output(id).maxValidationAttempts, 2, `${id} retry budget`);
}
eq(workflow.entryStepId, 'fable-analysis', 'production entry');
const checkpoint = spawnSync('git', ['show', `b5cf797:packages/${packageName}/workflows/${packageName}/workflow.json`],
  { cwd: process.cwd(), encoding: 'utf8' });
eq(checkpoint.status, 0, 'checkpoint workflow read');
eq(workflow, JSON.parse(checkpoint.stdout), 'production graph and settings equal checkpoint');
const cases = ['happy', 'completion-revision', 'planning-only', 'checkpoint-empty-message',
  'commit-missing-message', 'commit-empty-message', 'knowledge-create',
  'knowledge-merge-archive', 'knowledge-merge-no-archive', 'knowledge-skip'] as const;
type Case = typeof cases[number];
let passed = 0;
const summaries: any[] = [];

function run(testCase: Case): void {
  const directory = join(evidence, testCase);
  const bundle = join(directory, packageName);
  mkdirSync(directory, { recursive: true });
  cpSync(source, bundle, { recursive: true });
  const scenario = structuredClone(authored);
  const graph = structuredClone(workflow);
  if (testCase.startsWith('knowledge-')) graph.entryStepId = 'kb-self-review';
  if (testCase === 'completion-revision') {
    const revision = structuredClone(scenario['step9-commit-message']);
    revision.when.needs_revision = true;
    revision.payload.decision = 'needs-revision';
    revision.payload.needs_revision = true;
    revision.payload.accepted = false;
    revision.payload.findings = ['Complete the plan evidence.'];
    delete revision.payload.commitMessage;
    delete revision.payload.committedFiles;
    delete revision.payload.changeSummary;
    scenario['step9-commit-message'] = [revision, structuredClone(authored['step9-commit-message'])];
  }
  if (testCase === 'planning-only') {
    scenario['step9-commit-message'].payload.workflowMode = 'planning-only';
    scenario['step9-commit-message'].payload.archivedImplPlanPaths = [];
    scenario['kb-merge-judge'].payload.decision = 'skip';
    scenario['kb-merge-judge'].payload.create_knowledge = false;
    scenario['kb-merge-judge'].payload.merge_knowledge = false;
    scenario['kb-merge-judge'].when = { create_knowledge: false, merge_knowledge: false };
  }
  if (testCase === 'checkpoint-empty-message') scenario['plan-checkpoint'].payload.commitMessage = '';
  if (testCase === 'commit-missing-message') delete scenario['step9-commit-message'].payload.commitMessage;
  if (testCase === 'commit-empty-message') scenario['step9-commit-message'].payload.commitMessage = '';
  if (testCase.startsWith('knowledge-') && testCase !== 'knowledge-create') {
    const judge = scenario['kb-merge-judge'];
    judge.when = { create_knowledge: false, merge_knowledge: testCase !== 'knowledge-skip' };
    judge.payload.decision = testCase === 'knowledge-skip' ? 'skip' : 'merge';
    judge.payload.create_knowledge = false;
    judge.payload.merge_knowledge = testCase !== 'knowledge-skip';
    if (testCase === 'knowledge-skip') {
      delete judge.payload.mergeNoteId;
      delete judge.payload.mergedBody;
      delete judge.payload.archiveNoteId;
      delete judge.payload.archivedPointerBody;
    } else {
      judge.payload.mergeNoteId = 'mock-existing-note';
      judge.payload.mergedBody = 'Merged durable documentation guidance.';
      const archive = testCase === 'knowledge-merge-archive';
      scenario['kb-archive-brief'] = { provider: 'scenario-mock', model: 'claude-fable-5',
        when: { archive_note: archive }, payload: { archive_note: archive } };
      scenario['kb-archive-brief'].when = { archive_note: archive };
      scenario['kb-archive-brief'].payload.archive_note = archive;
      if (archive) {
        scenario['kb-archive-brief'].payload.archiveNoteId = 'mock-old-note';
        scenario['kb-archive-brief'].payload.archivedPointerBody = 'See mock-existing-note.';
      } else {
        delete scenario['kb-archive-brief'].payload.archiveNoteId;
        delete scenario['kb-archive-brief'].payload.archivedPointerBody;
      }
    }
  }
  writeFileSync(join(bundle, 'workflow.json'), JSON.stringify(graph, null, 2) + '\n');
  writeFileSync(join(bundle, 'mock-scenario.json'), JSON.stringify(scenario, null, 2) + '\n');
  const command = ['workflow', 'run', packageName, '--workflow-definition-dir', directory,
    '--mock-scenario', join(bundle, 'mock-scenario.json'), '--session-store', join(directory, 'sessions'),
    '--artifact-root', join(directory, 'artifacts'), '--output', 'jsonl'];
  const result = spawnSync('riela', command, { cwd: process.cwd(), encoding: 'utf8', maxBuffer: 100 * 1024 * 1024 });
  const log = join(directory, 'run.jsonl');
  writeFileSync(log, `${result.stdout ?? ''}${result.stderr ?? ''}`);
  writeFileSync(join(directory, 'command.json'), JSON.stringify({ command: `riela ${command.join(' ')}`, cwd: process.cwd(), exitCode: result.status, log }, null, 2));
  check(result.error === undefined, `${testCase} spawn`);
  const lines = (result.stdout ?? '').split('\n').flatMap(line => { try { return [JSON.parse(line)]; } catch { return []; } });
  const starts = lines.filter(x => x.type === 'step_started');
  const rootId = lines.find(x => x.type === 'session_started')?.sessionId;
  const rootSteps = starts.filter(x => x.sessionId === rootId).map(x => x.stepId);
  const completion = lines.findLast(x => x.type === 'session_completed' && x.sessionId === rootId);
  const failure = lines.findLast(x => x.type === 'session_failed' && x.sessionId === rootId);
  const runResult = lines.findLast(x => x.type === 'run_result');
  const executions = runResult?.result?.session?.executions ?? [];
  const negative = ['checkpoint-empty-message', 'commit-missing-message', 'commit-empty-message'].includes(testCase);
  if (negative) {
    check(result.status !== 0, `${testCase} must fail`);
    check(completion?.status === 'failed' || !!failure || !completion, `${testCase} failed root`);
    const producer = testCase === 'checkpoint-empty-message' ? 'plan-checkpoint' : 'step9-commit-message';
    const consumer = testCase === 'checkpoint-empty-message' ? 'plan-git-commit' : 'step10-git-commit';
    check(rootSteps.includes(producer), `${testCase} producer reached`);
    eq(rootSteps.filter(x => x === producer).length, 2, `${testCase} two validation attempts`);
    check(!rootSteps.includes(consumer), `${testCase} consumer blocked`);
    check(/validationRejected/.test(result.stdout + result.stderr), `${testCase} schema rejection diagnostic`);
  } else {
    eq(result.status, 0, `${testCase} CLI exit`);
    eq(completion?.status, 'completed', `${testCase} root completion`);
    eq(completion?.exitCode, 0, `${testCase} root exit`);
    check((completion?.nodeExecutions ?? 0) > 0, `${testCase} positive executions`);
  }
  const index = (step: string) => rootSteps.indexOf(step);
  if (!negative) {
    check(executions.length > 0, `${testCase} published executions`);
    const published = (step: string) => executions.filter((x: any) => x.stepId === step)
      .map((x: any) => x.acceptedOutput?.payload);
    for (const [step, response] of Object.entries(scenario)) {
      const observed = published(step);
      if (observed.length === 0) continue;
      const responses = Array.isArray(response) ? response : [response];
      const expected = responses[responses.length - 1]?.payload;
      if (expected) for (const [key, value] of Object.entries(expected))
        eq(observed[observed.length - 1]?.[key], value, `${testCase} ${step}.${key} published`);
    }
  }
  if (testCase === 'happy' || testCase === 'planning-only' || testCase === 'completion-revision') {
    check(index('plan-checkpoint') < index('plan-git-commit'), `${testCase} checkpoint order`);
    check(index('reconcile-implementations') < index('integration-review'), `${testCase} integration order`);
    check(index('integration-review') < index('step9-commit-message'), `${testCase} completion order`);
    eq(rootSteps.filter(x => x === 'step10-git-commit').length, 1, `${testCase} one final commit`);
  }
  if (testCase === 'completion-revision') {
    eq(rootSteps.filter(x => x === 'step9-commit-message').length, 2, 'revision rechecks completion');
    eq(rootSteps.filter(x => x === 'fable-goal-review').length, 2, 'revision returns to goal review');
    const outputs = executions.filter((x: any) => x.stepId === 'step9-commit-message').map((x: any) => x.acceptedOutput);
    eq(outputs[0]?.when?.needs_revision, true, 'revision routing label');
    eq(outputs[0]?.payload?.decision, 'needs-revision', 'published revision decision');
    check(!('commitMessage' in outputs[0]?.payload), 'revision omits commit message');
    eq(outputs[1]?.when?.needs_revision, false, 'acceptance routing label');
    check(outputs[1]?.payload?.commitMessage?.length > 0, 'acceptance publishes commit message');
  }
  if (testCase.startsWith('knowledge-') || testCase === 'planning-only') {
    const expected = testCase === 'knowledge-create' ? 'kb-create' : testCase === 'knowledge-skip' || testCase === 'planning-only' ? null : 'kb-merge';
    if (expected) check(rootSteps.includes(expected), `${testCase} write route`);
    else check(!rootSteps.includes('kb-merge') && !rootSteps.includes('kb-create'), `${testCase} no write route`);
    eq(rootSteps.includes('kb-archive'), testCase === 'knowledge-merge-archive', `${testCase} archive route`);
  }
  passed++;
  summaries.push({ case: testCase, outcome: negative ? 'expected-schema-rejection' : 'completed', exitCode: result.status,
    nodeExecutions: completion?.nodeExecutions ?? failure?.nodeExecutions ?? 0, log });
}

try {
  for (const testCase of cases) run(testCase);
  const summary = { casesRun: cases.length, casesPassed: passed, failureCount: 0, assertions, cases: summaries };
  writeFileSync(join(evidence, 'summary.json'), JSON.stringify(summary, null, 2) + '\n');
  console.log(JSON.stringify(summary));
} catch (error) {
  writeFileSync(join(evidence, 'summary.json'), JSON.stringify({ casesRun: cases.length, casesPassed: passed,
    failureCount: 1, assertions, cases: summaries, error: String(error) }, null, 2) + '\n');
  console.error(error);
  process.exitCode = 1;
}
