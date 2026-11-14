import { strict as assert } from 'node:assert';
import { spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';

const workflowId = 'fable-astra-design-plan-review-loop';
const source = resolve('packages', workflowId, 'workflows', workflowId);
const flag = process.argv.indexOf('--evidence-root');
assert(flag >= 0 && process.argv[flag + 1]?.startsWith('/'), 'absolute --evidence-root required');
const evidence = process.argv[flag + 1];
const original = JSON.parse(readFileSync(join(source, 'mock-scenario.json'), 'utf8'));
let assertions = 0;
const check = (value: unknown, message: string) => { assertions++; assert(value, message); };
const results = [];

for (const name of ['revision-accepted', 'author-missing-design', 'review-missing-decision']) {
  const directory = join(evidence, name);
  const definitionDir = join(directory, 'workflows');
  const target = join(definitionDir, workflowId);
  mkdirSync(definitionDir, { recursive: true });
  cpSync(source, target, { recursive: true });
  const scenario = structuredClone(original);
  if (name === 'author-missing-design') for (const response of scenario['fable-author']) delete response.payload.designMarkdown;
  if (name === 'review-missing-decision') for (const response of scenario['astra-review']) delete response.payload.decision;
  writeFileSync(join(target, 'mock-scenario.json'), JSON.stringify(scenario, null, 2) + '\n');
  const command = ['workflow', 'run', workflowId, '--workflow-definition-dir', definitionDir,
    '--mock-scenario', join(target, 'mock-scenario.json'), '--session-store', join(directory, 'sessions'),
    '--artifact-root', join(directory, 'artifacts'), '--output', 'json'];
  const run = spawnSync('riela', command, { encoding: 'utf8', maxBuffer: 50_000_000 });
  writeFileSync(join(directory, 'stdout.log'), run.stdout || '');
  writeFileSync(join(directory, 'stderr.log'), run.stderr || '');
  const output = JSON.parse(run.stdout || '{}');
  const snapshot = JSON.parse(readFileSync(join(directory, 'artifacts', output.sessionId || `${workflowId}-session-1`, 'runtime-snapshot.json'), 'utf8'));
  const executions = snapshot.session.executions;
  const steps = executions.map((item: any) => item.stepId);
  if (name === 'revision-accepted') {
    check(run.status === 0 && snapshot.session.status === 'completed', 'revision route completes');
    check(steps.filter((step: string) => step === 'fable-author').length === 2, 'author revises once');
    check(steps.filter((step: string) => step === 'astra-review').length === 2, 'Astra reviews both revisions');
    check(steps.at(-1) === 'workflow-output', 'accepted output runs last');
    check(executions.filter((item: any) => item.stepId === 'astra-review').map((item: any) => item.acceptedOutput?.payload?.accepted).join(',') === 'false,true', 'observed reject then accept');
  } else {
    const producer = name === 'author-missing-design' ? 'fable-author' : 'astra-review';
    check(run.status !== 0 && snapshot.session.status === 'failed', `${name} fails`);
    check(executions.some((item: any) => item.stepId === producer && item.status === 'failed' && String(item.failureReason).includes('output contract')), `${producer} schema rejection`);
    check(!steps.includes('workflow-output'), 'no accepted output after malformed producer');
  }
  results.push({ name, exitCode: run.status, sessionStatus: snapshot.session.status, steps, stdoutLog: join(directory, 'stdout.log'), stderrLog: join(directory, 'stderr.log') });
}
const summary = { testsRun: results.length, testsPassed: results.length, failureCount: 0, assertions, results };
mkdirSync(evidence, { recursive: true });
writeFileSync(join(evidence, 'summary.json'), JSON.stringify(summary, null, 2));
console.log(`PASS ${summary.testsPassed} cases, ${assertions} assertions, 0 failures`);
