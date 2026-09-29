import { strict as assert } from 'node:assert';
import { spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';

const id = 'claude-code-worker-only-single-step';
const source = resolve('packages', id, 'workflows', id);
const flag = process.argv.indexOf('--evidence-root');
assert(flag >= 0 && process.argv[flag + 1]?.startsWith('/'), 'absolute --evidence-root required');
const evidence = process.argv[flag + 1];
const results = [];
let assertions = 0;
const check = (value: unknown, message: string) => { assertions++; assert(value, message); };

for (const name of ['valid-worker', 'invalid-sandbox']) {
  const dir = join(evidence, name);
  const definitions = join(dir, 'workflows');
  const target = join(definitions, id);
  mkdirSync(definitions, { recursive: true });
  cpSync(source, target, { recursive: true });
  if (name === 'invalid-sandbox') {
    const path = join(target, 'nodes', 'node-main-worker.json');
    const node = JSON.parse(readFileSync(path, 'utf8'));
    node.agentSandbox = 'invalid-authority';
    writeFileSync(path, JSON.stringify(node, null, 2) + '\n');
  }
  const command = name === 'valid-worker'
    ? ['workflow', 'run', id, '--workflow-definition-dir', definitions, '--mock-scenario', join(target, 'mock-scenario.json'), '--session-store', join(dir, 'sessions'), '--artifact-root', join(dir, 'artifacts'), '--output', 'json']
    : ['workflow', 'validate', id, '--workflow-definition-dir', definitions, '--output', 'json'];
  const run = spawnSync('riela', command, { encoding: 'utf8', maxBuffer: 50_000_000 });
  writeFileSync(join(dir, 'stdout.log'), run.stdout || '');
  writeFileSync(join(dir, 'stderr.log'), run.stderr || '');
  if (name === 'valid-worker') {
    const output = JSON.parse(run.stdout || '{}');
    const snapshot = JSON.parse(readFileSync(join(dir, 'artifacts', output.sessionId || `${id}-session-1`, 'runtime-snapshot.json'), 'utf8'));
    check(run.status === 0 && snapshot.session.status === 'completed', 'worker mock completes');
    check(snapshot.session.executions[0]?.acceptedOutput?.payload?.status === 'ready', 'observed worker status');
  } else {
    check(run.status !== 0, 'invalid authority rejected');
    check((run.stdout + run.stderr).includes('agentSandbox'), 'validator identifies sandbox');
  }
  results.push({ name, exitCode: run.status, stdoutLog: join(dir, 'stdout.log'), stderrLog: join(dir, 'stderr.log') });
}
const summary = { testsRun: 2, testsPassed: 2, failureCount: 0, assertions, results };
writeFileSync(join(evidence, 'summary.json'), JSON.stringify(summary, null, 2));
console.log(`PASS 2 cases, ${assertions} assertions, 0 failures`);
