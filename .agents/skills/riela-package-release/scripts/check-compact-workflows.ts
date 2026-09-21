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
// Codex implementation and lost-work repair use Terra low effort.
for (const [id, nodes] of [
  [codex, ['step6-implement', 'reconcile-implementations']],
  ['fable-and-improve-codex', ['codex-implementation', 'reconcile-implementations']],
  ['codex-simple-work-package', ['implement']],
  [refactor, ['step4-implement-next-task']],
] as const) {
  for (const node of nodes) {
    const payload = read(join(bundle(id), 'nodes', `node-${node}.json`));
    assert.equal(payload.executionBackend, 'codex-agent');
    assert.equal(payload.model, id === codex ? 'gpt-5.6-terra' : 'gpt-5.6-sol', `${id}/${node}: implementation model`);
    assert.equal(payload.effort, 'low', `${id}/${node}: implementation effort`);
  }
}
// Sol review gates use medium effort and do not spend high-effort passes
// generating optional improvements.
for (const [id, nodes] of [
  [codex, ['step3-design-review', 'step5-impl-plan-review', 'step6-test-integrity-check', 'step7-adversarial-review']],
  ['fable-and-improve-codex', ['codex-review', 'integration-review']],
  ['codex-simple-work-package', ['review']],
  [refactor, ['step6-post-refactor-review']],
  ['codex-refactoring-slice-review', ['slice-review']],
] as const) {
  for (const node of nodes) {
    const payload = read(join(bundle(id), 'nodes', `node-${node}.json`));
    assert.equal(payload.executionBackend, 'codex-agent');
    assert.equal(payload.model, 'gpt-5.6-sol', `${id}/${node}: review model`);
    assert.equal(payload.effort, 'medium', `${id}/${node}: review effort`);
  }
}
assert.equal(read(join(bundle(codex), 'nodes/node-step2-design-doc-update.json')).model, 'gpt-6-astra');
assert.equal(read(join(bundle(codex), 'nodes/node-step4-impl-plan-create.json')).model, 'gpt-6-astra');
assert.equal(read(join(bundle(codex), 'nodes/node-integration-review.json')).model, 'gpt-6-astra');
assert.equal(read(join(bundle(codex), 'nodes/node-dispatch-plans.json')).model, 'gpt-5.6-sol');
const expected = new Map([[codex, 22], [refactor, 6], ['fable-and-improve-codex', 24], ['fable-and-improve-opus', 24]]);
for (const [id, count] of expected) {
  const w = read(join(bundle(id), 'workflow.json'));
  assert.equal(w.steps.length, count);
  const ids = new Set(w.steps.map((s: any) => s.id));
  for (const s of w.steps) {
    if (s.sessionPolicy?.inheritFromStepId) assert(ids.has(s.sessionPolicy.inheritFromStepId));
    for (const t of s.transitions ?? []) if (!t.toWorkflowId) assert(ids.has(t.toStepId));
  }
}
// Parallel analysis stays read-only; shared-workspace implementation is
// dependency-aware and bounded more conservatively.
for (const [id, groupId, concurrency] of [
  ['codex-deepdesign', 'design-review-lenses', 3],
  ['codex-recent-change-quality-loop', 'recent-change-review', 6],
  ['codex-source-security-check-loop', 'security-focus-area-review', 8],
  ['codex-adversarial-implementation-review-loop', 'implementation-review-lenses', 3],
  ['codex-website-builder', 'website-review-lenses', 3],
] as const) {
  const w = read(join(bundle(id), 'workflow.json'));
  const fanouts = w.steps.flatMap((s: any) => (s.transitions ?? []).map((t: any) => t.fanout).filter(Boolean));
  const fanout = fanouts.find((candidate: any) => candidate.groupId === groupId);
  assert(fanout, `${id}: missing ${groupId}`);
  assert.equal(fanout.concurrency, concurrency, `${id}: bounded concurrency`);
  assert.equal(fanout.writeOwnership?.mode, 'read-only', `${id}: review fanout must be read-only`);
}
{
  const w = read(join(bundle(refactor), 'workflow.json'));
  const fanouts = w.steps.flatMap((s: any) => (s.transitions ?? []).map((t: any) => t.fanout).filter(Boolean));
  const implementation = fanouts.find((candidate: any) => candidate.groupId === 'refactoring-implementation-wave');
  assert(implementation, `${refactor}: missing implementation wave`);
  assert.equal(implementation.concurrency, 4);
  assert.equal(implementation.writeOwnership?.mode, 'shared-workspace');
  assert.equal(implementation.dependencies?.branchIdFrom, '/dispatchId');
  assert.equal(implementation.dependencies?.completedBranchIdsFrom, '/acceptedDispatchIds');
  assert.equal(implementation.changeTracking?.pathsFrom, '/trackedPaths');
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
assert(!graph.nodes.some((node: any) => node.id === 'step7-review'));
assert(!graph.steps.some((step: any) => step.id === 'step7-review'));
assert.equal(graph.steps.find((step: any) => step.id === 'step6-test-integrity-check').transitions.find((transition: any) => transition.label === '!(needs_revision)')?.toStepId, 'step7-adversarial-review');
assert.equal(graph.loop.gates.find((g: any) => g.id === 'implementation-plan-completion-check').stepId, 'step9-commit-message');
assert.equal(graph.loop.gates.find((g: any) => g.id === 'integration-review').stepId, 'integration-review');
const integrationTransitions = graph.steps.find((step: any) => step.id === 'integration-review').transitions;
assert.equal(integrationTransitions.find((transition: any) => transition.label === 'needs_revision && repair_in_place')?.toStepId, 'reconcile-implementations');
assert.equal(integrationTransitions.find((transition: any) => transition.label === 'needs_revision && !(repair_in_place)')?.toStepId, 'dispatch-plans');
const output = (payload: any, when = { always: true }) => ({ provider: 'scenario-mock', model: 'gpt-5.6-sol', when, payload });
const integrationLoopGate = (findings: any[], accepted = false) => ({
  gateId: 'integration-review',
  decision: accepted ? 'accepted' : 'needs-work',
  severityCounts: {
    high: findings.filter(finding => finding.severity === 'high').length,
    medium: findings.filter(finding => finding.severity === 'mid' || finding.severity === 'medium').length,
    low: findings.filter(finding => finding.severity === 'low').length,
    informational: 0,
  },
  blockingFindings: findings
    .filter(finding => finding.severity === 'high' || finding.severity === 'mid' || finding.severity === 'medium')
    .map(finding => ({ id: `${finding.file}:${finding.line ?? 0}:${finding.message}`, severity: finding.severity === 'mid' ? 'medium' : finding.severity, filePath: finding.file, line: finding.line, message: finding.message })),
});
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
function runExpectFailure(id: string, name: string, mutate: (m: any) => void, expectedError: RegExp, fixture = 'mock-scenario.json') {
  const m = read(join(bundle(id), fixture));
  mutate(m);
  const dir = join(scratch, name); mkdirSync(dir);
  const mock = join(dir, 'mock.json'); writeFileSync(mock, JSON.stringify(m));
  const args = ['workflow', 'run', id, '--workflow-definition-dir', catalog, '--mock-scenario', mock, '--session-store', join(dir, 'sessions'), '--artifact-root', join(dir, 'artifacts'), '--variables', JSON.stringify({ memoryRoot: join(dir, 'memory'), noteRoot: join(dir, 'notes') }), '--output', 'json'];
  const r = spawnSync(process.env.RIELA_BIN ?? 'riela', args, { encoding: 'utf8' });
  assert.notEqual(r.status, 0, `${name}: expected convergence failure`);
  assert.match(`${r.stdout}\n${r.stderr}`, expectedError, `${name}: expected convergence diagnostic`);
  total++; console.log(`${name}: passed (terminated with convergence diagnostic)`);
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
  const accepted = m['integration-review'];
  const revision = output({
    accepted: false,
    needs_revision: true,
    redispatch_required: false,
    repair_in_place: true,
    plans_remaining: false,
    reviewBasis: accepted.payload.reviewBasis,
    findings: [{
      severity: 'mid',
      file: 'shared.txt',
      message: 'Restore overwritten behavior.',
      intentReference: 'The accepted plan requires the shared behavior to survive reconciliation.',
      materialImpact: 'The combined tree loses required behavior.',
      fixCostBenefit: 'A focused restoration is low cost and restores an accepted outcome.',
    }],
  }, { needs_revision: true, redispatch_required: false, repair_in_place: true, plans_remaining: false } as any);
  revision.payload.loopGate = integrationLoopGate(revision.payload.findings);
  m['integration-review'] = [revision, accepted];
}, steps => {
  const i = steps.indexOf('integration-review');
  assert.deepEqual(steps.slice(i, i + 3), ['integration-review', 'reconcile-implementations', 'integration-review']);
  assert(steps.indexOf('step10-git-commit') > i + 2);
});
run(codex, 'integration-selective-redispatch', m => {
  const firstDispatch = m['dispatch-plans'];
  const firstItem = firstDispatch.payload.implementationItems[0];
  const retryItem = {
    ...firstItem,
    planId: 'retry-plan',
    planPath: 'impl-plans/active/retry-plan.md',
    dependsOn: [],
    trackedPaths: ['retry.txt'],
  };
  m['dispatch-plans'] = [
    firstDispatch,
    output({
      ...firstDispatch.payload,
      implementationItems: [firstItem, retryItem],
      acceptedPlanIds: [firstItem.planId],
    }),
  ];
  const accepted = m['integration-review'];
  const revision = output({
    ...accepted.payload,
    accepted: false,
    needs_revision: true,
    redispatch_required: true,
    plans_remaining: true,
    acceptedPlanIds: [firstItem.planId],
    pendingPlanIds: ['retry-plan'],
    findings: [{
      severity: 'mid',
      file: 'impl-plans/progress/retry-plan.md',
      message: 'The pending plan lacks worker-owned evidence.',
      intentReference: 'Pending plans require successful native worker evidence.',
      materialImpact: 'The plan cannot be accepted or unlock downstream work.',
      fixCostBenefit: 'A selective native redispatch provides the required evidence without rewriting accepted work.',
    }],
    repair_in_place: false,
  }, { needs_revision: true, redispatch_required: true, repair_in_place: false, plans_remaining: true } as any);
  revision.payload.loopGate = integrationLoopGate(revision.payload.findings);
  m['integration-review'] = [revision, accepted];
}, steps => {
  const review = steps.indexOf('integration-review');
  assert.equal(steps[review + 1], 'dispatch-plans');
  assert.equal(steps.filter(step => step === 'dispatch-plans').length, 2);
  assert.equal(steps.filter(step => step === 'reconcile-implementations').length, 2);
  assert(steps.indexOf('step10-git-commit') > steps.lastIndexOf('integration-review'));
});
run(codex, 'integration-missing-when-discriminator-redispatches', m => {
  const accepted = m['integration-review'];
  const revision = output({
    ...accepted.payload,
    accepted: false,
    needs_revision: true,
    redispatch_required: true,
    repair_in_place: false,
    plans_remaining: true,
    findings: [{
      severity: 'mid',
      file: 'impl-plans/active/a.md',
      message: 'The failed branch has no native worker provenance.',
      intentReference: 'A plan requires successful worker-owned evidence before acceptance.',
      materialImpact: 'The combined tree cannot prove required behavior for the plan.',
      fixCostBenefit: 'Redispatching the bounded failed plan produces the missing evidence without speculative repair.',
    }],
  }, { needs_revision: true, plans_remaining: true } as any);
  revision.payload.loopGate = integrationLoopGate(revision.payload.findings);
  m['integration-review'] = [revision, accepted];
}, steps => {
  const firstReview = steps.indexOf('integration-review');
  assert.equal(steps[firstReview + 1], 'dispatch-plans');
  assert.equal(steps.filter(step => step === 'integration-review').length, 2);
  assert(steps.indexOf('step10-git-commit') > steps.lastIndexOf('integration-review'));
});
runExpectFailure(codex, 'integration-identical-in-place-state-converges', m => {
  const accepted = m['integration-review'];
  const unchanged = output({
    ...accepted.payload,
    accepted: false,
    needs_revision: true,
    redispatch_required: false,
    repair_in_place: true,
    plans_remaining: true,
    findings: [{
      severity: 'mid',
      file: 'shared.txt',
      message: 'The same combined-tree behavior remains missing.',
      intentReference: 'The accepted plan requires the shared behavior to survive reconciliation.',
      materialImpact: 'The combined tree still loses required behavior.',
      fixCostBenefit: 'A repair must change the retained behavior before another review.',
    }],
  }, { needs_revision: true, redispatch_required: false, repair_in_place: true, plans_remaining: true } as any);
  unchanged.payload.loopGate = integrationLoopGate(unchanged.payload.findings);
  m['integration-review'] = [unchanged, structuredClone(unchanged), structuredClone(unchanged), structuredClone(unchanged)];
}, /maxRepeatedFindingRounds|maxGateVisits|convergence/i);
run(codex, 'dependency-waves', m => {
  const prototype = m['dispatch-plans'].payload.implementationItems[0];
  const items = ['a', 'b', 'c'].map(planId => ({ ...prototype, planId, planPath: `impl-plans/active/${planId}.md`, dependsOn: planId === 'c' ? ['a', 'b'] : [], trackedPaths: [`${planId}.txt`, 'shared.txt'] }));
  const dispatch = m['dispatch-plans'].payload;
  m['dispatch-plans'] = [
    output({ ...dispatch, implementationItems: items, acceptedPlanIds: [] }),
    output({ ...dispatch, implementationItems: items, acceptedPlanIds: ['a', 'b'] }),
  ];
  const acceptedReview = m['integration-review'];
  m['integration-review'] = [output({ ...acceptedReview.payload, plans_remaining: true, acceptedPlanIds: ['a', 'b'] }, { needs_revision: false, plans_remaining: true } as any), acceptedReview];
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
  m['step6-test-integrity-check'] = [output({
    ...accepted.payload,
    needs_revision: true,
    accepted: false,
    findings: [{
      severity: 'mid',
      file: 'packages/riela/src/workflow/review-findings.test.ts',
      message: 'Restore weakened assertion.',
      intentReference: 'The accepted plan requires regression coverage for review replay.',
      materialImpact: 'The weakened assertion can conceal loss of required rerun behavior.',
      fixCostBenefit: 'Restoring the focused assertion is low cost and verifies the required outcome.',
    }],
  }, { needs_revision: true } as any), accepted];
}, steps => { const i = steps.indexOf('step6-test-integrity-check'); assert.equal(steps[i + 1], 'step6-implement'); }, 'mock-scenario.json', 'step6-implement');
for (const flavor of ['codex', 'opus']) run(`fable-and-improve-${flavor}`, `fable-${flavor}-revision`, m => {
  assert(m['fable-design'].payload.designMarkdown); assert(m['fable-design'].payload.planMarkdown);
  const review = `${flavor}-review`;
  const accepted = m[review];
  m[review] = [output({
    ...accepted.payload,
    reviewStatus: 'needs-revision',
    findings: [{
      severity: 'mid',
      file: 'impl-plans/active/a.md',
      message: 'Missing acceptance criterion.',
      intentReference: 'The Fable-authored plan must cover the required user outcome.',
      materialImpact: 'The implementation cannot be verified against an omitted criterion.',
      fixCostBenefit: 'Adding the missing criterion is low cost and makes acceptance auditable.',
    }],
  }, { needs_revision: true } as any), accepted];
}, steps => { const i = steps.indexOf(`${flavor}-review`); assert.equal(steps[i + 1], `${flavor}-implementation`); assert(!steps.includes('fable-impl-plan')); }, 'mock-scenario.json', `${flavor}-implementation`);
run(refactor, 'refactoring-revision', m => {
  const plan = m['step3-merge-review-plan'];
  plan.when = { plan_only: false, no_plan_tasks: false, implementation_ready: true };
  const task = { ...plan.payload.tasks[0], dispatchId: 'REF-001-attempt-1', dependsOnDispatchIds: [], trackedPaths: ['packages/riela/src'] };
  Object.assign(plan.payload, plan.when, { planOnly: false, implementationItems: [task], acceptedTaskIds: [], acceptedDispatchIds: [] });
  const repairPlan = structuredClone(plan);
  repairPlan.payload.implementationItems[0].dispatchId = 'REF-001-attempt-2';
  m['step3-merge-review-plan'] = [plan, repairPlan];
  m['step4-implement-next-task'] = [
    output({ taskId: 'REF-001', changedFiles: [], verification: ['mock verification'], authorSelfCheck: { findings: [] } }),
    output({ taskId: 'REF-001', changedFiles: [], verification: ['mock repair verification'], authorSelfCheck: { findings: [] } }),
  ];
  m['step6-post-refactor-review'] = [output({ findings: [{ severity: 'mid', message: 'Preserve public behavior.' }] }, { needs_revision: true, plan_remaining: false, workflow_complete: false } as any), output({ findings: [], accepted: true }, { needs_revision: false, plan_remaining: false, workflow_complete: true } as any)];
}, steps => {
  const i = steps.indexOf('step6-post-refactor-review');
  assert.deepEqual(steps.slice(i, i + 3), ['step6-post-refactor-review', 'step3-merge-review-plan', 'step6-post-refactor-review']);
  assert.equal(steps.filter(s => s === 'step3-merge-review-plan').length, 2);
  assert.equal(steps.filter(s => s === 'step6-post-refactor-review').length, 2);
  assert(!steps.includes('step5-self-review'));
});
console.log(`${total} regressions passed; isolated evidence: ${scratch}`);
