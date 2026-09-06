import { strict as assert } from 'node:assert';
import { readFileSync, readdirSync, mkdtempSync, cpSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { spawnSync } from 'node:child_process';

// Deterministic graph regression checks. Never invoke live model or git backends.
const root = resolve('.');
const read = (p: string) => JSON.parse(readFileSync(p, 'utf8'));
const bundle = (id: string) => join(root, 'packages', id, 'workflows', id);
mkdirSync(join(root, 'tmp'), { recursive: true });
const scratch = mkdtempSync(join(root, 'tmp', 'compact-regression.'));
const catalog = join(scratch, 'workflows');
mkdirSync(catalog);
for (const id of readdirSync(join(root, 'packages'))) {
  const dir = join(root, 'packages', id, 'workflows');
  try {
    for (const workflow of readdirSync(dir)) cpSync(join(dir, workflow), join(catalog, workflow), { recursive: true });
  } catch (error: any) { if (error.code !== 'ENOENT') throw error; }
}
const codex = 'codex-design-and-implement-review-loop';
const refactor = 'codex-refactoring-divide-and-conquer';
const expected = new Map([[codex, 23], [refactor, 6], ['fable-and-improve-codex', 24], ['fable-and-improve-opus', 24]]);
for (const [id, count] of expected) {
  const w = read(join(bundle(id), 'workflow.json'));
  assert.equal(w.steps.length, count);
  const ids = new Set(w.steps.map((s: any) => s.id));
  for (const s of w.steps) {
    if (s.sessionPolicy?.inheritFromStepId) assert(ids.has(s.sessionPolicy.inheritFromStepId));
    for (const t of s.transitions ?? []) if (!t.toWorkflowId) assert(ids.has(t.toStepId));
  }
}
// Inherited node overrides must reference retained registry nodes.
for (const id of readdirSync(catalog)) {
  const w = read(join(catalog, id, 'workflow.json'));
  if (!expected.has(w.extends?.workflowId)) continue;
  const base = read(join(catalog, w.extends.workflowId, 'workflow.json'));
  const nodes = new Set(base.nodes.map((n: any) => n.id));
  for (const node of Object.keys(w.extends.nodePatch ?? {})) assert(nodes.has(node), `${id}: stale override ${node}`);
}
const graph = read(join(bundle(codex), 'workflow.json'));
assert.equal(graph.loop.gates.length, 6);
assert.equal(graph.loop.gates.find((g: any) => g.id === 'implementation-plan-completion-check').stepId, 'step9-commit-message');
const output = (payload: any, when = { always: true }) => ({ provider: 'scenario-mock', model: 'gpt-5.6-sol', when, payload });
let total = 0;
function run(id: string, name: string, mutate: (m: any) => void, verify: (steps: string[]) => void, fixture = 'mock-scenario.json', branchEntry?: string) {
  const m = read(join(bundle(id), fixture));
  mutate(m);
  const dir = join(scratch, name); mkdirSync(dir);
  const mock = join(dir, 'mock.json'); writeFileSync(mock, JSON.stringify(m));
  const store = join(dir, 'sessions');
  const args = ['workflow', 'run', id, '--workflow-definition-dir', catalog, '--mock-scenario', mock, '--session-store', store, '--artifact-root', join(dir, 'artifacts'), '--variables', JSON.stringify({ memoryRoot: join(dir, 'memory'), noteRoot: join(dir, 'notes') }), '--output', 'json'];
  if (branchEntry) {
    const local = join(dir, 'workflows'); cpSync(catalog, local, { recursive: true });
    const path = join(local, id, 'workflow.json'); const w = read(path);
    w.entryStepId = branchEntry; delete w.managerStepId;
    for (const s of w.steps) if (s.role === 'manager') s.role = 'worker';
    const last = w.steps.find((s: any) => s.id === (branchEntry === 'fable-design' ? 'base-branch-integrate' : 'branch-evidence')); delete last.transitions;
    writeFileSync(path, JSON.stringify(w));
    args[args.indexOf('--workflow-definition-dir') + 1] = local;
  }
  const r = spawnSync(process.env.RIELA_BIN ?? 'riela', args, { encoding: 'utf8' });
  assert.equal(r.status, 0, `${name}: ${r.stdout}\n${r.stderr}`);
  const result = JSON.parse(r.stdout); assert.equal(result.status, 'completed');
  const steps = result.session.executions.map((e: any) => e.stepId);
  verify(steps); total++; console.log(`${name}: passed (${steps.length} executions)`);
}
run(codex, 'completion-revision', m => {
  const accepted = m['step9-commit-message'];
  m['step9-commit-message'] = [output({ decision: 'needs-revision', needs_revision: true, findings: [{ severity: 'mid', message: 'Documentation index needs reconciliation.' }] }, { needs_revision: true } as any), accepted];
}, steps => {
  const first = steps.indexOf('step9-commit-message');
  assert.deepEqual(steps.slice(first, first + 4), ['step9-commit-message', 'step8-docs-refresh', 'step9-commit-message', 'step10-git-commit']);
  assert.equal(steps.filter(s => s === 'step10-git-commit').length, 1);
});
run(codex, 'planning-only', () => {}, steps => {
  assert(!steps.includes('step6-implement')); assert(!steps.includes('step8-docs-refresh'));
}, 'mock-scenario-planning-only.json');
run(codex, 'two-branch-native-fanout', () => {}, steps => {
  assert(steps.indexOf('plan-git-commit') < steps.indexOf('dispatch-plans'));
  assert(steps.indexOf('dispatch-plans') < steps.indexOf('reconcile-implementations'));
  assert(steps.indexOf('integration-review') < steps.indexOf('step10-git-commit'));
  assert.equal(steps.filter(s => s === 'step10-git-commit').length, 1);
  assert(!steps.includes('feature-local-plan'));
}, 'mock-scenario-fanout.json');
run(codex, 'integration-overwrite-repair', m => {
  m['integration-review'] = [output({ accepted: false, needs_revision: true, plans_remaining: false, findings: [{ severity: 'mid', message: 'Restore overwritten behavior.' }] }, { needs_revision: true, plans_remaining: false } as any), m['integration-review']];
}, steps => {
  const i = steps.indexOf('integration-review');
  assert.deepEqual(steps.slice(i, i + 3), ['integration-review', 'reconcile-implementations', 'integration-review']);
  assert(steps.indexOf('step10-git-commit') > i + 2);
});
run(codex, 'dependency-waves', m => {
  const prototype = m['dispatch-plans'].payload.implementationItems[0];
  const items = ['a', 'b', 'c'].map(planId => ({ ...prototype, planId, planPath: `impl-plans/active/${planId}.md`, dependsOn: planId === 'c' ? ['a', 'b'] : [], trackedPaths: [`${planId}.txt`, 'shared.txt'] }));
  m['dispatch-plans'] = [output({ implementationItems: items, acceptedPlanIds: [] }), output({ implementationItems: items, acceptedPlanIds: ['a', 'b'] })];
  m['integration-review'] = [output({ accepted: true, needs_revision: false, plans_remaining: true, acceptedPlanIds: ['a', 'b'] }, { needs_revision: false, plans_remaining: true } as any), m['integration-review']];
}, steps => {
  assert.equal(steps.filter(s => s === 'dispatch-plans').length, 2);
  assert.equal(steps.filter(s => s === 'reconcile-implementations').length, 2);
  assert(steps.indexOf('step10-git-commit') > steps.lastIndexOf('integration-review'));
});
for (const flavor of ['codex', 'opus']) run(`fable-and-improve-${flavor}`, `fable-${flavor}-native-fanout`, () => {}, steps => {
  assert(steps.indexOf('plan-git-commit') < steps.indexOf('dispatch-plans'));
  assert(steps.indexOf('integration-review') < steps.indexOf('step10-git-commit'));
  assert.equal(steps.at(-1), 'base-branch-integrate');
}, 'mock-scenario.json', 'fable-design');
run(codex, 'test-integrity-revision', m => {
  const accepted = m['step6-test-integrity-check'];
  m['step6-test-integrity-check'] = [output({ needs_revision: true, findings: [{ severity: 'mid', message: 'Restore weakened assertion.' }] }, { needs_revision: true } as any), accepted];
}, steps => { const i = steps.indexOf('step6-test-integrity-check'); assert.equal(steps[i + 1], 'step6-implement'); }, 'mock-scenario.json', 'step6-implement');
for (const flavor of ['codex', 'opus']) run(`fable-and-improve-${flavor}`, `fable-${flavor}-revision`, m => {
  assert(m['fable-design'].payload.designMarkdown); assert(m['fable-design'].payload.planMarkdown);
  const review = `${flavor}-review`;
  m[review] = [output({ findings: [{ severity: 'mid', message: 'Missing acceptance criterion.' }] }, { needs_revision: true } as any), m[review]];
}, steps => { const i = steps.indexOf(`${flavor}-review`); assert.equal(steps[i + 1], `${flavor}-implementation`); assert(!steps.includes('fable-impl-plan')); }, 'mock-scenario.json', `${flavor}-implementation`);
run(refactor, 'refactoring-revision', m => {
  const plan = m['step3-merge-review-plan'];
  plan.when = { plan_only: false, no_plan_tasks: false, implementation_ready: true };
  Object.assign(plan.payload, plan.when, { planOnly: false });
  m['step4-implement-next-task'] = output({ taskId: 'REF-001', changedFiles: [], verification: ['mock verification'], authorSelfCheck: { findings: [] } });
  m['step6-post-refactor-review'] = [output({ findings: [{ severity: 'mid', message: 'Preserve public behavior.' }] }, { needs_revision: true, plan_remaining: false, workflow_complete: false } as any), output({ findings: [], accepted: true }, { needs_revision: false, plan_remaining: false, workflow_complete: true } as any)];
}, steps => { const i = steps.indexOf('step6-post-refactor-review'); assert.equal(steps[i + 1], 'step4-implement-next-task'); assert(!steps.includes('step5-self-review')); });
console.log(`${total} regressions passed; isolated evidence: ${scratch}`);
