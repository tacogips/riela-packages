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
// Codex implementation and lost-work repair use Sol medium effort. Other
// compact workflows retain their deliberately cheaper implementation setting.
for (const [id, nodes] of [
  [codex, ['step6-implement', 'reconcile-implementations']],
  ['fable-and-improve-codex', ['codex-implementation', 'reconcile-implementations']],
  ['codex-simple-work-package', ['implement']],
  [refactor, ['step4-implement-next-task']],
] as const) {
  for (const node of nodes) {
    const payload = read(join(bundle(id), 'nodes', `node-${node}.json`));
    assert.equal(payload.executionBackend, 'codex-agent');
    assert.equal(payload.model, id === codex ? 'gpt-6-sol' : 'gpt-5.6-sol', `${id}/${node}: implementation model`);
    assert.equal(payload.effort, id === codex ? 'medium' : 'low', `${id}/${node}: implementation effort`);
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
    assert.equal(payload.model, id === codex ? 'gpt-6-sol' : 'gpt-5.6-sol', `${id}/${node}: review model`);
    assert.equal(payload.effort, 'medium', `${id}/${node}: review effort`);
  }
}
assert.equal(read(join(bundle(codex), 'nodes/node-step2-design-doc-update.json')).model, 'gpt-6-astra');
assert.equal(read(join(bundle(codex), 'nodes/node-step4-impl-plan-create.json')).model, 'gpt-6-astra');
assert.equal(read(join(bundle(codex), 'nodes/node-integration-review.json')).model, 'gpt-6-astra');
assert.deepEqual(
  read(join(bundle(codex), 'nodes/node-dispatch-plans.json')).command,
  { scriptPath: 'scripts/dispatch-plans.py' },
);
assert.equal(read(join(bundle(codex), 'nodes/node-implementation-wave-outcome.json')).model, 'gpt-6-sol');
assert.equal(read(join(bundle(codex), 'nodes/node-implementation-blocked-output.json')).model, 'gpt-6-sol');
const codexGraph = read(join(bundle(codex), 'workflow.json'));
const baseIntegration = read(join(bundle(codex), 'nodes/node-base-branch-integrate.json'));
assert.equal(baseIntegration.agentSandbox, 'danger-full-access', 'base integration needs remote and shared Git worktree access');
for (const field of ['implementationBranch', 'baseBranch', 'remote', 'implementationCommit', 'mergeStatus', 'basePushStatus', 'verification']) {
  assert(baseIntegration.output.jsonSchema.required.includes(field), `base integration output must require ${field}`);
}
assert.deepEqual(baseIntegration.output.jsonSchema.properties.mergeStatus.enum, ['merged', 'already-on-base', 'already-merged', 'pr-open']);
assert.deepEqual(baseIntegration.output.jsonSchema.properties.basePushStatus.enum, ['pushed', 'already-pushed', 'not-requested']);
for (const field of ['pullRequestURL', 'pullRequestNumber', 'pullRequestDraft', 'pullRequestBaseBranch']) {
  assert(baseIntegration.output.jsonSchema.properties[field], `PR handoff output must provide ${field}`);
}
const finalPrompt = readFileSync(join(bundle(codex), 'prompts/workflow-output.md'), 'utf8');
const planningOutputContract = finalPrompt.split('If Step 5 accepted a planning-only run,')[1]?.split('If the workflow continued through Step 8,')[0];
const issueOutputContract = finalPrompt.split('If the workflow continued through Step 8,')[1]?.split('Copy `commitMessage`')[0];
for (const [mode, section] of [['planning-only', planningOutputContract], ['issue-resolution', issueOutputContract]] as const) {
  assert(section, `${mode}: final output contract is missing`);
  for (const field of ['commitMessage', 'commitHash', 'committedFiles', 'pushedRemote', 'pushedBranch', 'baseBranch', 'mergeStatus', 'basePushStatus']) {
    assert(section.includes(`- \`${field}\``), `${mode}: final output prompt omits ${field}`);
  }
}
for (const node of ['step6-implement', 'reconcile-implementations', 'step3-design-review', 'step5-impl-plan-review', 'step6-test-integrity-check', 'step7-adversarial-review', 'integration-review']) {
  assert.deepEqual(read(join(bundle(codex), 'nodes', `node-${node}.json`)).sessionPolicy, { mode: 'reuse' }, `${node}: role-local session reuse`);
}
for (const step of ['step4-impl-plan-create', 'integration-review']) {
  assert.deepEqual(
    codexGraph.steps.find((candidate: any) => candidate.id === step).sessionPolicy,
    { mode: 'reuse', inheritFromStepId: 'step2-design-doc-update' },
    `${step}: inherit Astra design session`,
  );
}
for (const entry of codexGraph.nodes.filter((node: any) => node.nodeFile)) {
  const payload = read(join(bundle(codex), entry.nodeFile));
  if (payload.executionBackend !== 'codex-agent') continue;
  assert.equal(payload.effort, 'medium', `${codex}/${entry.id}: all agent effort`);
}
const dispatchNodePayload = read(join(bundle(codex), 'nodes/node-dispatch-plans.json'));
assert.equal(dispatchNodePayload.nodeType, 'command');
assert.equal(dispatchNodePayload.executionBackend, undefined);
assert.equal(dispatchNodePayload.model, undefined);
const dispatchScript = join(bundle(codex), 'scripts/dispatch-plans.py');
const dispatchScriptRepo = join(scratch, 'dispatch-script-repo');
mkdirSync(join(dispatchScriptRepo, 'impl-plans/active'), { recursive: true });
const dispatchManifest = {
  implementationBranch: 'feature/test', baseBranch: 'main', remote: 'origin', evidenceRoot: 'tmp/evidence',
  reviewContext: {
    issueReference: { communicationId: 'comm-1', title: 'Deterministic dispatch' },
    userProblem: 'Dispatch accepted plans without model reinterpretation.',
    requiredOutcomes: ['Project the exact manifest.'], nonGoals: [], constraints: [],
    designDecisionsAndRationale: [], intentionalTradeoffs: [], supportedEdgeCases: [], outOfScopeEdgeCases: [],
    sourcePaths: ['impl-plans/active/mock-dispatch.json'],
  },
  plans: [
    { planId: 'a', planPath: 'impl-plans/active/a.md', dependsOn: [], writePaths: ['a.txt'], sharedPaths: [], acceptanceCriteria: ['a accepted'], verification: [] },
    { planId: 'b', planPath: 'impl-plans/active/b.md', dependsOn: ['a'], writePaths: ['b.txt'], sharedPaths: ['shared.txt'], acceptanceCriteria: ['b accepted'], verification: ['test b'] },
  ],
};
writeFileSync(join(dispatchScriptRepo, 'impl-plans/active/mock-dispatch.json'), JSON.stringify(dispatchManifest));
writeFileSync(join(dispatchScriptRepo, 'impl-plans/active/old-dispatch.json'), JSON.stringify({ ...dispatchManifest, plans: [{ ...dispatchManifest.plans[0], planId: 'obsolete' }] }));
for (const arguments_ of [
  ['init'], ['add', 'impl-plans/active/mock-dispatch.json', 'impl-plans/active/old-dispatch.json'],
  ['-c', 'user.name=Riela Test', '-c', 'user.email=riela@example.invalid', 'commit', '-m', 'test: checkpoint manifest'],
]) {
  const git = spawnSync('git', arguments_, { cwd: dispatchScriptRepo, encoding: 'utf8' });
  assert.equal(git.status, 0, git.stderr);
}
const dispatchCheckpoint = spawnSync('git', ['rev-parse', 'HEAD'], { cwd: dispatchScriptRepo, encoding: 'utf8' }).stdout.trim();
const dispatchEnvelope = {
  input: { _rielaInput: { messages: [
    { fromStepId: 'plan-git-commit', createdOrder: 1, payload: { git: {
      operation: 'commit', commitHash: dispatchCheckpoint, committedFiles: ['impl-plans/active/mock-dispatch.json'],
    } } },
    { fromStepId: 'integration-review', createdOrder: 2,
      payload: { manifestPath: 'impl-plans/active/old-dispatch.json', acceptedPlanIds: ['a'], checkpointCommit: '2'.repeat(40) } },
  ] } },
};
const dispatchProjection = spawnSync('python3', [dispatchScript], { cwd: dispatchScriptRepo, input: JSON.stringify(dispatchEnvelope), encoding: 'utf8' });
assert.equal(dispatchProjection.status, 0, dispatchProjection.stderr);
const dispatchProjectionOutput = JSON.parse(dispatchProjection.stdout);
assert.deepEqual(dispatchProjectionOutput.payload.implementationItems.map((item: any) => item.planId), ['a', 'b']);
assert.deepEqual(dispatchProjectionOutput.payload.implementationItems.map((item: any) => item.acceptedPlanIds), [['a'], ['a']]);
assert.deepEqual(dispatchProjectionOutput.payload.implementationItems[1].trackedPaths, ['b.txt', 'shared.txt']);
assert.equal(dispatchProjectionOutput.payload.implementationItems[0].reviewContext.issueReference, 'comm-1: Deterministic dispatch');
assert.equal(dispatchProjectionOutput.payload.manifestPath, 'impl-plans/active/mock-dispatch.json');
assert.equal(dispatchProjectionOutput.payload.checkpointCommit, dispatchCheckpoint);
const missingCheckpoint = structuredClone(dispatchEnvelope);
missingCheckpoint.input._rielaInput.messages.shift();
const missingCheckpointDispatch = spawnSync('python3', [dispatchScript], { cwd: dispatchScriptRepo, input: JSON.stringify(missingCheckpoint), encoding: 'utf8' });
assert.notEqual(missingCheckpointDispatch.status, 0);
assert.match(missingCheckpointDispatch.stderr, /exactly one checkpoint commit or push message/);
const ambiguousManifest = structuredClone(dispatchEnvelope);
ambiguousManifest.input._rielaInput.messages[0].payload.git.committedFiles.push('impl-plans/active/old-dispatch.json');
const ambiguousDispatch = spawnSync('python3', [dispatchScript], { cwd: dispatchScriptRepo, input: JSON.stringify(ambiguousManifest), encoding: 'utf8' });
assert.notEqual(ambiguousDispatch.status, 0);
assert.match(ambiguousDispatch.stderr, /exactly one dispatch manifest/);
const staleEnvelope = structuredClone(dispatchEnvelope);
staleEnvelope.input._rielaInput.messages[0].payload.git.commitHash = '1'.repeat(40);
const staleDispatch = spawnSync('python3', [dispatchScript], { cwd: dispatchScriptRepo, input: JSON.stringify(staleEnvelope), encoding: 'utf8' });
assert.notEqual(staleDispatch.status, 0);
assert.match(staleDispatch.stderr, /checkpointCommit must equal the current HEAD/);
writeFileSync(join(dispatchScriptRepo, 'impl-plans/active/mock-dispatch.json'), `${JSON.stringify(dispatchManifest)}\n`);
const modifiedDispatch = spawnSync('python3', [dispatchScript], { cwd: dispatchScriptRepo, input: JSON.stringify(dispatchEnvelope), encoding: 'utf8' });
assert.notEqual(modifiedDispatch.status, 0);
assert.match(modifiedDispatch.stderr, /differs from the committed checkpoint/);
writeFileSync(join(dispatchScriptRepo, 'impl-plans/active/mock-dispatch.json'), JSON.stringify(dispatchManifest));
const completedEnvelope = structuredClone(dispatchEnvelope);
completedEnvelope.input._rielaInput.messages[1].payload.acceptedPlanIds = ['a', 'b'];
const completedDispatch = spawnSync('python3', [dispatchScript], { cwd: dispatchScriptRepo, input: JSON.stringify(completedEnvelope), encoding: 'utf8' });
assert.notEqual(completedDispatch.status, 0);
assert.match(completedDispatch.stderr, /every manifest plan was accepted/);
const richVerificationManifest = structuredClone(dispatchManifest);
richVerificationManifest.plans[1].verification = {
  commands: ['test b', 'build b'], evidenceRequirements: ['record the exit code'],
} as any;
writeFileSync(join(dispatchScriptRepo, 'impl-plans/active/mock-dispatch.json'), JSON.stringify(richVerificationManifest));
for (const arguments_ of [
  ['add', 'impl-plans/active/mock-dispatch.json'],
  ['-c', 'user.name=Riela Test', '-c', 'user.email=riela@example.invalid', 'commit', '-m', 'test: rich checkpoint verification'],
]) {
  const git = spawnSync('git', arguments_, { cwd: dispatchScriptRepo, encoding: 'utf8' });
  assert.equal(git.status, 0, git.stderr);
}
const richCheckpoint = spawnSync('git', ['rev-parse', 'HEAD'], { cwd: dispatchScriptRepo, encoding: 'utf8' }).stdout.trim();
const richEnvelope = structuredClone(dispatchEnvelope);
richEnvelope.input._rielaInput.messages[0].payload.git.commitHash = richCheckpoint;
const richDispatch = spawnSync('python3', [dispatchScript], { cwd: dispatchScriptRepo, input: JSON.stringify(richEnvelope), encoding: 'utf8' });
assert.equal(richDispatch.status, 0, richDispatch.stderr);
assert.deepEqual(JSON.parse(richDispatch.stdout).payload.implementationItems[1].verification, ['test b', 'build b']);
const checkpointPrompt = readFileSync(join(bundle(codex), 'prompts/plan-checkpoint.md'), 'utf8');
assert.match(checkpointPrompt, /`verification` MUST be an array of non-empty command strings, not an object/);
assert.match(checkpointPrompt, /manifest must reference every accepted design document and every accepted plan.*unchanged from HEAD/i);
assert.match(checkpointPrompt, /committedFiles.*exactly the new or modified dispatch manifest plus only those accepted design\/plan files with actual changes/i);
assert.match(checkpointPrompt, /unchanged paths.*cause `riela\/git-commit` to reject the prepared staged set as a mismatch/i);
assert.match(checkpointPrompt, /`committedFiles` would be empty.*`checkpoint_blocked: true`/i);
const fanoutScenario = read(join(bundle(codex), 'mock-scenario-fanout.json'));
assert.deepEqual(fanoutScenario['plan-checkpoint'].payload.committedFiles, [
  'impl-plans/active/mock-dispatch.json',
  'impl-plans/active/a.md',
]);
assert.deepEqual(
  fanoutScenario['plan-git-commit'].payload.git.committedFiles,
  fanoutScenario['plan-checkpoint'].payload.committedFiles,
);
assert(fanoutScenario['dispatch-plans'].payload.implementationItems.some((item: any) => item.planPath === 'impl-plans/active/b.md'));
assert(!fanoutScenario['plan-checkpoint'].payload.committedFiles.includes('impl-plans/active/b.md'));
const dispatchNode = read(join(bundle(codex), 'nodes/node-dispatch-plans.json'));
const implementationItemSchema = dispatchNode.output.jsonSchema.properties.implementationItems.items;
assert(implementationItemSchema.required.includes('acceptedPlanIds'));
assert.deepEqual(implementationItemSchema.properties.acceptedPlanIds, { type: 'array', items: { type: 'string' } });
const implementationPrompt = readFileSync(join(bundle(codex), 'prompts/step6-implement.md'), 'utf8');
assert.match(implementationPrompt, /membership in the fanout item's runtime-owned `acceptedPlanIds` is the authoritative accepted integration decision/i);
assert.match(implementationPrompt, /do not override or downgrade that decision.*stale progress files.*old evidence artifacts/i);
assert.match(implementationPrompt, /work explicitly assigned to a pending downstream dependent plan is not an incomplete task, blocker, material finding, verification gap, or residual risk for the current predecessor/i);
assert.match(implementationPrompt, /Do not set it for downstream dependent plans/i);
assert.match(implementationPrompt, /behavioral test command.*structured nonnegative integer `testsRun` or `testCount`.*`failureCount`/is);
assert.match(implementationPrompt, /canonical prose parsing exists only as a legacy fallback/i);
assert.match(implementationPrompt, /fresh `--scratch-path`.*resolved checkout.*`CLANG_MODULE_CACHE_PATH`.*`SWIFTPM_MODULECACHE_OVERRIDE`.*`--disable-sandbox --skip-update`/is);
const implementationNode = read(join(bundle(codex), 'nodes/node-step6-implement.json'));
const verificationProperties = implementationNode.output.jsonSchema.properties.verification.items.properties;
for (const property of ['testCount', 'testsRun', 'testsPassed', 'positiveTestCount', 'passedTestCount', 'failureCount', 'failedTestCount', 'testsFailed']) {
  assert.deepEqual(verificationProperties[property], { type: 'integer', minimum: 0 }, `step6 verification.${property}`);
}
const testIntegrityPrompt = readFileSync(join(bundle(codex), 'prompts/step6-test-integrity-check.md'), 'utf8');
assert.match(testIntegrityPrompt, /same selected suites.*existing resolved checkout.*positive test count/is);
assert.match(testIntegrityPrompt, /missing behavior or tests explicitly assigned to a pending downstream dependent plan are not a finding or verification gap against the current predecessor/i);
const selectedSwiftLintContract = /if \[ -s "\$changed_swift_manifest" \]; then xargs -0 swiftlint lint --strict --quiet --no-cache < "\$changed_swift_manifest"; else.*No Swift files changed; selected-file SwiftLint not run/is;
assert.match(implementationPrompt, selectedSwiftLintContract);
assert.match(testIntegrityPrompt, /manifest was nonempty before `swiftlint lint --strict` ran/i);
const adversarialPrompt = readFileSync(join(bundle(codex), 'prompts/step7-adversarial-review.md'), 'utf8');
assert.match(adversarialPrompt, /do not reject a predecessor because final wiring, host injection, or another behavior is explicitly assigned to a pending downstream dependent plan/i);
const provenanceSystemPromptPath = 'prompts/runtime-provenance-system.md';
const provenanceSystemPrompt = readFileSync(join(bundle(codex), provenanceSystemPromptPath), 'utf8');
for (const node of ['step1-issue-intake', 'step2-design-doc-update', 'step3-design-review', 'step4-impl-plan-create', 'step5-impl-plan-review']) {
  assert.equal(read(join(bundle(codex), 'nodes', `node-${node}.json`)).systemPromptTemplateFile, provenanceSystemPromptPath);
}
assert.match(provenanceSystemPrompt, /runner has already resolved and validated this workflow package/i);
assert.match(provenanceSystemPrompt, /runtime-resolved workflow provenance.*effective `workflowInput`.*authoritative/is);
assert.match(provenanceSystemPrompt, /do not run `riela workflow inspect`.*`riela workflow list`.*`riela workflow validate`/is);
assert.match(provenanceSystemPrompt, /cannot access a user-scope registry.*expected isolation boundary.*not a workflow readiness blocker/is);
assert.match(provenanceSystemPrompt, /runner fails before this node starts/i);
const intakePrompt = readFileSync(join(bundle(codex), 'prompts/step1-issue-intake.md'), 'utf8');
const designPrompt = readFileSync(join(bundle(codex), 'prompts/step2-design-doc-update.md'), 'utf8');
assert.match(intakePrompt, /do not re-run scoped Riela workflow\/package discovery from the sandbox/i);
assert.match(designPrompt, /do not write a sandbox home-registry access failure.*into the design/is);
const integrationReviewPrompt = readFileSync(join(bundle(codex), 'prompts/integration-review.md'), 'utf8');
assert.match(integrationReviewPrompt, /return the immutable wave acceptance record in the node payload/i);
assert.match(integrationReviewPrompt, /runtime persists this read-only node output/i);
assert.match(integrationReviewPrompt, /do not write or modify repository or evidenceRoot files/i);
assert.doesNotMatch(integrationReviewPrompt, /persist an immutable wave acceptance record under the run evidenceRoot/i);
assert.match(integrationReviewPrompt, /immediately preceding serial reconciliation output's `verification` and `evidencePaths`/i);
assert.match(integrationReviewPrompt, /current-tree aggregate command as qualifying passing evidence/i);
assert.match(integrationReviewPrompt, /nonzero aggregate is never green.*baselineReviewPending/is);
assert.match(integrationReviewPrompt, /do not require this read-only review to recreate writable caches or an isolated dependency checkout/i);
assert.match(integrationReviewPrompt, /predecessor is eligible for wave acceptance.*pending downstream dependent plan/is);
assert.match(integrationReviewPrompt, /retain the downstream plan in `pendingPlanIds`.*expanded `acceptedPlanIds`.*unlock it/is);
const reconcilePrompt = readFileSync(join(bundle(codex), 'prompts/reconcile-implementations.md'), 'utf8');
assert.match(reconcilePrompt, /already-resolved dependency checkout and normal build products/i);
assert.match(reconcilePrompt, /do not select a new isolated scratch build that must fetch dependencies/i);
assert.match(reconcilePrompt, /direct `verification` and `evidencePaths` output/i);
assert.match(reconcilePrompt, /do not mark a predecessor candidate incomplete or repair downstream wiring into it.*pending dependent plan/is);
assert.match(reconcilePrompt, /only after checking `\[ -s "\$changed_swift_manifest" \]`/i);
// BSD and GNU xargs both invoke their command once for an empty stream unless
// explicitly guarded. The guard is the portable false-positive boundary.
const emptySwiftManifest = join(scratch, 'empty-swift-files.nul');
writeFileSync(emptySwiftManifest, '');
const guardedLint = spawnSync('sh', ['-c', 'if [ -s "$1" ]; then xargs -0 printf selected < "$1"; else printf skipped; fi', 'selected-swiftlint', emptySwiftManifest], { encoding: 'utf8' });
assert.equal(guardedLint.status, 0, guardedLint.stderr);
assert.equal(guardedLint.stdout, 'skipped');
const waveOutcomePrompt = readFileSync(join(bundle(codex), 'prompts/implementation-wave-outcome.md'), 'utf8');
assert.match(waveOutcomePrompt, /never add a wave blocker merely because a downstream-owned plan remains pending/i);
const expected = new Map([[codex, 26], [refactor, 6], ['fable-and-improve-codex', 24], ['fable-and-improve-opus', 24]]);
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
const manager = read(join(bundle(codex), 'nodes/node-riela-manager.json'));
const managerPrompt = readFileSync(join(bundle(codex), 'prompts/riela-manager.md'), 'utf8');
assert.equal(manager.agentSandbox, 'read-only');
assert.match(manager.output.description, /does not author, inspect, review, write files, run tests, commit, push, or declare completion/i);
assert.match(managerPrompt, /immediately return concise business JSON exactly shaped/i);
assert.match(managerPrompt, /dispatch.*step1-issue-intake/i);
assert.match(managerPrompt, /do not perform any repository work yourself/i);
const checkpointTransitions = graph.steps.find((step: any) => step.id === 'plan-checkpoint').transitions;
assert.deepEqual(checkpointTransitions, [{ toStepId: 'plan-git-commit', label: '!(checkpoint_blocked)' }]);
assert.deepEqual(graph.steps.find((step: any) => step.id === 'plan-git-commit').transitions, [
  { toStepId: 'plan-git-push' },
]);
assert.deepEqual(graph.steps.find((step: any) => step.id === 'plan-git-push').transitions, [
  { toStepId: 'dispatch-plans' },
]);
const checkpointPush = graph.nodes.find((node: any) => node.id === 'plan-git-push')?.addon;
assert.equal(checkpointPush?.name, 'riela/git-push');
assert.equal(checkpointPush?.version, '1');
assert.equal(checkpointPush?.config?.allowPush, true);
assert.equal(checkpointPush?.config?.expectedCommitHashTemplate, '{{inbox.latest.output.payload.git.commitHash}}');
assert.equal(graph.loop.gates.length, 6);
assert(!graph.nodes.some((node: any) => node.id === 'step7-review'));
assert(!graph.steps.some((step: any) => step.id === 'step7-review'));
const implementationTransitions = graph.steps.find((step: any) => step.id === 'step6-implement').transitions;
assert.deepEqual(implementationTransitions, [{ toStepId: 'implementation-progress-check' }]);
const progressNode = read(join(bundle(codex), 'nodes/node-implementation-progress-check.json'));
assert.equal(progressNode.nodeType, 'command');
assert.equal(progressNode.command.scriptPath, 'scripts/implementation-progress-check.py');
assert.equal(progressNode.executionBackend, undefined);
const progressScript = join(bundle(codex), progressNode.command.scriptPath);
const invokeProgressGate = (payloads: any[]) => {
  const messages = payloads.map((payload, index) => ({
    fromStepId: 'step6-implement',
    createdOrder: index + 1,
    payload,
  }));
  const invocation = { input: { _rielaInput: { messages } } };
  const result = spawnSync(progressScript, [], { input: `${JSON.stringify(invocation)}\n`, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
};
const noProgressEvidence = { implementation_blocked: false, implementationIncomplete: false, blockers: [], changedFiles: [], verification: [], implPlanUpdates: [], risks: [], authorSelfCheck: { findings: [], verificationGaps: [], residualRisks: [] } };
assert.equal(invokeProgressGate([noProgressEvidence, noProgressEvidence]).payload.blockerType, 'implementation-no-progress');
const firstProgress = { ...noProgressEvidence, changedFiles: ['Sources/A.swift'], verification: [{ command: 'swift test', exitCode: 0, testCount: 12 }] };
const revisedProgress = { ...firstProgress, verification: [{ command: 'swift test', exitCode: 0, testCount: 12 }, { command: 'swiftlint', status: 'passed' }], implPlanUpdates: ['Completed lint acceptance criterion.'] };
assert.equal(invokeProgressGate([firstProgress, revisedProgress]).payload.implementation_blocked, false);
assert.equal(invokeProgressGate([firstProgress, firstProgress]).payload.blockerType, 'implementation-no-progress');
const reorderedProgress = { ...revisedProgress, verification: [...revisedProgress.verification].reverse(), implPlanUpdates: [...revisedProgress.implPlanUpdates].reverse() };
assert.equal(invokeProgressGate([revisedProgress, reorderedProgress]).payload.blockerType, 'implementation-no-progress');
const removedEvidence = { ...revisedProgress, verification: [revisedProgress.verification[0]], implPlanUpdates: [] };
assert.equal(invokeProgressGate([revisedProgress, removedEvidence]).payload.blockerType, 'implementation-no-progress');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: ['swift test'] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, implementationIncomplete: true }]).payload.blockerType, 'implementation-incomplete');
const productivePartial = { ...revisedProgress, implementationIncomplete: true };
assert.equal(invokeProgressGate([productivePartial]).payload.implementation_continue, true);
assert.equal(invokeProgressGate([productivePartial, { ...productivePartial, implPlanUpdates: ['Completed a second seam.'] }]).payload.continuationAttempt, 2);
assert.equal(invokeProgressGate([productivePartial, { ...productivePartial, implPlanUpdates: ['Completed a second seam.'] }, { ...productivePartial, implPlanUpdates: ['Completed a third seam.'] }]).payload.blockerType, 'implementation-incomplete');
assert.equal(invokeProgressGate([{ ...firstProgress, risks: [{ severity: 'high', message: 'Accepted behavior remains broken.' }] }]).payload.blockerType, 'implementation-material-finding');
assert.equal(invokeProgressGate([{ ...firstProgress, authorSelfCheck: { findings: [{ severity: 'mid', message: 'Required branch is untested.' }], verificationGaps: [], residualRisks: [] } }]).payload.blockerType, 'implementation-material-finding');
const failedBehavioral = { ...firstProgress, verification: [
  { command: 'swift test --filter CapabilityTests', exitStatus: 1, testCount: 0 },
  { command: 'swiftlint', exitStatus: 0 },
  { command: 'git diff --check', exitStatus: 0 },
] };
assert.equal(invokeProgressGate([failedBehavioral]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ command: 'swift test', exitStatus: 0, testCount: 0 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ command: 'swift build', exitStatus: 0 }] }]).payload.blockerType, 'implementation-materially-unverified');
const selectedTestOutcome = { command: 'swift test --filter CapabilityTests', exitCode: 0, outcome: 'Passed 33 selected tests, 0 failures; current tree verified.' };
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [selectedTestOutcome] }]).payload.implementation_blocked, false);
const reorderedSelectedTestOutcome = { ...selectedTestOutcome, outcome: '55 selected tests passed with 0 failures; current tree verified.' };
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [reorderedSelectedTestOutcome] }]).payload.implementation_blocked, false);
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, outcome: '33 selected tests passed with 0 failures; current tree verified.' }] }]).payload.implementation_blocked, false);
const countFirstSelectedTestOutcome = { ...selectedTestOutcome, outcome: '58 selected tests, 0 failures; current tree verified.' };
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [countFirstSelectedTestOutcome] }]).payload.implementation_blocked, false);
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...countFirstSelectedTestOutcome, outcome: '23 selected tests, 0 failures; current tree verified.' }] }]).payload.implementation_blocked, false);
const colonSelectedTestOutcome = { ...selectedTestOutcome, outcome: 'Passed: 35 tests, 0 failures; current tree verified.' };
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [colonSelectedTestOutcome] }]).payload.implementation_blocked, false);
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...countFirstSelectedTestOutcome, outcome: '0 selected tests, 0 failures.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...countFirstSelectedTestOutcome, outcome: '58 selected tests, 1 failure.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...countFirstSelectedTestOutcome, outcome: 'Reported 58 selected tests, 0 failures.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...countFirstSelectedTestOutcome, exitCode: 1 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...countFirstSelectedTestOutcome, environmentBlocked: true }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...countFirstSelectedTestOutcome, testCount: 0, testsPassed: 58 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ command: 'swift test --filter CapabilityTests', exitCode: 0, testsRun: 35, testsPassed: 35, failureCount: 0 }] }]).payload.implementation_blocked, false);
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ command: 'swift test --filter CapabilityTests', exitCode: 0, testsRun: 35, testsPassed: 35, failureCount: 1 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ command: 'swift test --filter CapabilityTests', exitCode: 0, testsRun: 35, testsPassed: 35, failureCount: '0' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, outcome: '0 selected tests passed with 0 failures.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, outcome: '55 selected tests passed with 1 failure.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, outcome: 'Reported 55 selected tests passed with 0 failures.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, exitCode: 1 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, environmentBlocked: true }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, status: 'blocked' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, testCount: 0 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, testCount: 0, testsPassed: 55 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...reorderedSelectedTestOutcome, command: 'swift build' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, outcome: 'Passed 0 selected tests, 0 failures; no tests selected.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, outcome: 'Passed selected tests, 0 failures; count unavailable.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, outcome: 'Not passed 33 selected tests, 0 failures.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, exitCode: 1 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, outcome: 'Passed 33 selected tests, 1 failure.' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, environmentBlocked: true }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, status: 'blocked' }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, testCount: 0 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, testCount: 0, testsPassed: 33 }] }]).payload.blockerType, 'implementation-materially-unverified');
assert.equal(invokeProgressGate([{ ...firstProgress, verification: [{ ...selectedTestOutcome, command: 'swift build' }] }]).payload.blockerType, 'implementation-materially-unverified');
const priorBehavioral = { ...firstProgress, verification: [{ command: 'swift test --filter CapabilityTests', exitStatus: 0, testCount: 12, sourceHash: 'tree-123' }] };
const matchingEnvironmentBlock = { ...revisedProgress, verification: [{ command: 'swift test --filter CapabilityTests', exitStatus: 1, environmentBlocked: true, sourceHash: 'tree-123' }, { command: 'swiftlint', exitStatus: 0 }] };
assert.equal(invokeProgressGate([priorBehavioral, matchingEnvironmentBlock]).payload.implementation_blocked, false);
assert.equal(invokeProgressGate([priorBehavioral, { ...matchingEnvironmentBlock, verification: [{ command: 'swift test --filter CapabilityTests', exitStatus: 1, environmentBlocked: true, sourceHash: 'tree-other' }] }]).payload.blockerType, 'implementation-materially-unverified');
const progressTransitions = graph.steps.find((step: any) => step.id === 'implementation-progress-check').transitions;
assert.equal(progressTransitions.find((transition: any) => transition.label === 'implementation_continue')?.toStepId, 'step6-implement');
assert.equal(progressTransitions.find((transition: any) => transition.label === 'implementation_blocked')?.toStepId, 'implementation-wave-outcome');
assert.equal(progressTransitions.find((transition: any) => transition.label === '!(implementation_blocked || implementation_continue)')?.toStepId, 'step6-test-integrity-check');
const implementationFanout = graph.steps.find((step: any) => step.id === 'dispatch-plans').transitions[0].fanout;
assert.equal(implementationFanout.joinStepId, 'implementation-wave-outcome');
assert.equal(graph.steps.find((step: any) => step.id === 'branch-evidence').transitions[0].toStepId, 'implementation-wave-outcome');
const outcomeTransitions = graph.steps.find((step: any) => step.id === 'implementation-wave-outcome').transitions;
assert.equal(outcomeTransitions.find((transition: any) => transition.label === 'implementation_blocked && !(partial_success)')?.toStepId, 'implementation-blocked-output');
assert.equal(outcomeTransitions.find((transition: any) => transition.label === '!(implementation_blocked) || partial_success')?.toStepId, 'reconcile-implementations');
assert.match(readFileSync(join(bundle(codex), 'prompts/implementation-wave-outcome.md'), 'utf8'), /fanoutJoin\.branches\[\].*implementation_blocked.*status: \"blocked\"/i);
assert.match(readFileSync(join(bundle(codex), 'prompts/implementation-wave-outcome.md'), 'utf8'), /partial_success.*acceptedPlanIds.*blocked/i);
assert.match(readFileSync(join(bundle(codex), 'prompts/implementation-blocked-output.md'), 'utf8'), /implementation_blocked:true,status:\"blocked\"/i);
assert.equal(graph.steps.find((step: any) => step.id === 'step6-test-integrity-check').transitions.find((transition: any) => transition.label === '!(needs_revision)')?.toStepId, 'step7-adversarial-review');
assert.equal(graph.loop.gates.find((g: any) => g.id === 'implementation-plan-completion-check').stepId, 'step9-commit-message');
const docsNode = JSON.parse(readFileSync(join(bundle(codex), 'nodes/node-step8-docs-refresh.json'), 'utf8'));
const completionNode = JSON.parse(readFileSync(join(bundle(codex), 'nodes/node-step9-commit-message.json'), 'utf8'));
const docsPrompt = readFileSync(join(bundle(codex), 'prompts/step8-docs-refresh.md'), 'utf8');
const completionPrompt = readFileSync(join(bundle(codex), 'prompts/step9-commit-message.md'), 'utf8');
assert.equal(docsNode.agentSandbox, 'workspace-write');
assert.equal(completionNode.agentSandbox, 'read-only');
assert.match(docsPrompt, /Own the writable completion-state cleanup.*Move only plans/is);
assert.match(docsPrompt, /update `impl-plans\/README\.md`/i);
assert.match(completionPrompt, /This node is read-only.*Verify that Step 8 moved/is);
assert.match(completionPrompt, /Never\s+attempt the move or index edit from this node/i);
assert.equal(graph.loop.gates.find((g: any) => g.id === 'integration-review').stepId, 'integration-review');
const integrationTransitions = graph.steps.find((step: any) => step.id === 'integration-review').transitions;
assert.equal(integrationTransitions.find((transition: any) => transition.label === 'needs_revision && repair_in_place')?.toStepId, 'reconcile-implementations');
assert.equal(integrationTransitions.find((transition: any) => transition.label === 'needs_revision && !(repair_in_place)')?.toStepId, 'dispatch-plans');
const output = (payload: any, when = { always: true }) => ({ provider: 'scenario-mock', model: 'gpt-6-sol', when, payload });
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
function run(id: string, name: string, mutate: (m: any) => void, verify: (steps: string[], result: any) => void, fixture = 'mock-scenario.json', branchEntry?: string) {
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
  verify(steps, result); total++; console.log(`${name}: passed (${steps.length} executions)`);
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
runExpectFailure(codex, 'planning-base-integration-blocked-is-not-success', m => {
  m['base-branch-integrate'].payload.mergeStatus = 'blocked';
  m['base-branch-integrate'].payload.basePushStatus = 'not-attempted';
}, /invalid_output|schema|enum|base integration/i, 'mock-scenario-planning-only.json');
run(codex, 'checkpoint-no-op-blocked', m => {
  m['plan-checkpoint'] = output({
    checkpoint_blocked: true,
    status: 'blocked',
    commitMessage: '',
    committedFiles: [],
    manifestPath: 'impl-plans/active/mock-dispatch.json',
    evidenceRoot: 'tmp/mock',
    blockers: [{ message: 'No accepted checkpoint path differs from HEAD.' }],
  }, { checkpoint_blocked: true } as any);
}, steps => {
  assert.deepEqual(steps, ['plan-checkpoint']);
  assert(!steps.includes('plan-git-commit'));
  assert(!steps.includes('plan-git-push'));
  assert(!steps.includes('dispatch-plans'));
}, 'mock-scenario.json', 'plan-checkpoint');
run(codex, 'implementation-dependency-blocked', m => {
  m['step6-implement'] = { ...output({
    implementation_blocked: true,
    implementationIncomplete: true,
    blockers: [{
      dependency: 'impl-plans/active/prerequisite.md',
      evidenceChecked: 'No accepted implementation evidence exists.',
      impact: 'The assigned implementation cannot start safely.',
      resumeCriterion: 'Complete and verify the prerequisite plan.',
    }],
    issueReference: 'tacogips/cursor-agent#123',
    changedFiles: [],
    implementationSummary: 'Implementation did not start because an external prerequisite is not ready.',
    implPlanPaths: ['impl-plans/active/workflow-review-findings.md'],
    implPlanUpdates: [],
    verification: [],
    addressedFeedback: [],
    risks: ['External prerequisite remains incomplete.'],
  }, { implementation_blocked: true } as any), model: 'gpt-6-sol' };
  m['implementation-wave-outcome'] = output({
    implementation_blocked: true,
    partial_success: false,
    blockedPlanIds: ['a'],
    successfulPlanIds: [],
    blockers: [{ dependency: 'impl-plans/active/prerequisite.md' }],
    resumeCriteria: ['Complete and verify the prerequisite plan.'],
  }, { implementation_blocked: true } as any);
  m['implementation-blocked-output'] = output({
    implementation_blocked: true,
    status: 'blocked',
    workflowMode: 'issue-resolution',
    issueReference: 'tacogips/cursor-agent#123',
    blockedPlanIds: ['a'],
    successfulPlanIds: [],
    blockers: [{ dependency: 'impl-plans/active/prerequisite.md' }],
    resumeCriteria: ['Complete and verify the prerequisite plan.'],
    nextStep: 'Implement the prerequisite, then rerun this plan.',
    residualRisks: [],
  });
}, steps => {
  assert.deepEqual(steps, ['step6-implement', 'implementation-progress-check', 'implementation-wave-outcome', 'implementation-blocked-output']);
  assert(!steps.includes('step6-test-integrity-check'));
  assert(!steps.includes('step7-adversarial-review'));
  assert(!steps.includes('reconcile-implementations'));
  assert(!steps.includes('integration-review'));
}, 'mock-scenario.json', 'step6-implement');
run(codex, 'implementation-failed-required-gate-terminal', m => {
  m['step6-implement'] = [output({
    implementation_blocked: false,
    implementationIncomplete: true,
    blockers: [],
    changedFiles: ['Tests/RielaCLITests/TaskDispatcherIntegrationTests.swift'],
    implementationSummary: 'Required before-removal V1 failed; the deletion barrier remains closed.',
    implPlanPaths: ['impl-plans/active/a.md'],
    implPlanUpdates: ['Recorded the failed barrier and exact ownership gap.'],
    verification: [
      { command: 'swift test --filter ReplayTests', exitCode: 0, testsRun: 1, failureCount: 0 },
      { command: 'swift test --filter RequiredBeforeRemovalSuite', exitCode: 1, testsRun: 60, failureCount: 4 },
    ],
    authorSelfCheck: { findings: ['High: canonical failure kind is missing'], verificationGaps: [] },
  }), output({ implementation_blocked: false, implementationIncomplete: false })];
  m['implementation-wave-outcome'] = output({
    implementation_blocked: true, partial_success: false, blockedPlanIds: ['a'],
    successfulPlanIds: [], blockers: [{ type: 'implementation-material-finding' }],
    resumeCriteria: ['Review the additional canonical persistence owner.'],
  }, { implementation_blocked: true } as any);
  m['implementation-blocked-output'] = output({
    implementation_blocked: true, status: 'blocked', workflowMode: 'issue-resolution',
    issueReference: 'comm-1', blockedPlanIds: ['a'], successfulPlanIds: [],
    blockers: [{ type: 'implementation-material-finding' }],
    resumeCriteria: ['Review the additional canonical persistence owner.'],
    nextStep: 'Amend the exact write paths and rerun.', residualRisks: [],
  });
}, steps => {
  assert.deepEqual(steps, ['step6-implement', 'implementation-progress-check', 'implementation-wave-outcome', 'implementation-blocked-output']);
}, 'mock-scenario.json', 'step6-implement');
run(codex, 'implementation-no-progress-terminal', m => {
  const unchanged = {
    ...output({
      implementation_blocked: false,
      implementationIncomplete: false,
      blockers: [],
      planId: 'a',
      changedFiles: [],
      implementationSummary: 'No additional implementation was necessary.',
      implPlanPaths: ['impl-plans/active/a.md'],
      implPlanUpdates: [],
      verification: [],
      addressedFeedback: [],
      risks: ['An accepted requirement remains unresolved.'],
    }),
    model: 'gpt-6-sol',
  };
  // Queue two identical no-change attempts. The deterministic gate must stop
  // after the first, leaving the second attempt unconsumed.
  m['step6-implement'] = [unchanged, structuredClone(unchanged)];
  m['implementation-wave-outcome'] = output({
    implementation_blocked: true,
    partial_success: false,
    blockedPlanIds: ['a'],
    successfulPlanIds: [],
    blockers: [{ type: 'implementation-no-progress' }],
    resumeCriteria: ['Make a concrete source/test/plan change and report verification evidence.'],
  }, { implementation_blocked: true } as any);
  m['implementation-blocked-output'] = output({
    implementation_blocked: true,
    status: 'blocked',
    workflowMode: 'issue-resolution',
    issueReference: 'tacogips/cursor-agent#123',
    blockedPlanIds: ['a'],
    successfulPlanIds: [],
    blockers: [{ type: 'implementation-no-progress' }],
    resumeCriteria: ['Make a concrete source/test/plan change and report verification evidence.'],
    nextStep: 'Implement concrete progress and rerun this plan.',
    residualRisks: [],
  });
}, steps => {
  assert.deepEqual(steps, ['step6-implement', 'implementation-progress-check', 'implementation-wave-outcome', 'implementation-blocked-output']);
  assert.equal(steps.filter(step => step === 'step6-implement').length, 1);
  assert(!steps.includes('step6-test-integrity-check'));
  assert(!steps.includes('step7-adversarial-review'));
  assert(!steps.includes('reconcile-implementations'));
}, 'mock-scenario.json', 'step6-implement');
run(codex, 'implementation-materially-unverified-terminal', m => {
  m['step6-implement'] = {
    ...output({
      implementation_blocked: false,
      implementationIncomplete: false,
      blockers: [],
      planId: 'a',
      changedFiles: ['Sources/Capability.swift'],
      implementationSummary: 'Capability code changed but behavioral suites did not execute.',
      implPlanPaths: ['impl-plans/active/a.md'],
      implPlanUpdates: ['Recorded the attempted verification.'],
      verification: [
        { command: 'swift test --filter CapabilityTests', exitStatus: 1, testCount: 0 },
        { command: 'swiftlint', exitStatus: 0 },
        { command: 'git diff --check', exitStatus: 0 },
      ],
      addressedFeedback: [],
      risks: [],
      authorSelfCheck: { findings: [], verificationGaps: [], residualRisks: [] },
    }),
    model: 'gpt-6-sol',
  };
  m['implementation-wave-outcome'] = output({
    implementation_blocked: true,
    partial_success: false,
    blockedPlanIds: ['a'],
    successfulPlanIds: [],
    blockers: [{ type: 'implementation-materially-unverified' }],
    resumeCriteria: ['Run behavioral verification with a positive test count.'],
  }, { implementation_blocked: true } as any);
  m['implementation-blocked-output'] = output({
    implementation_blocked: true,
    status: 'blocked',
    workflowMode: 'issue-resolution',
    issueReference: 'tacogips/cursor-agent#123',
    blockedPlanIds: ['a'],
    successfulPlanIds: [],
    blockers: [{ type: 'implementation-materially-unverified' }],
    resumeCriteria: ['Run behavioral verification with a positive test count.'],
    nextStep: 'Run the selected behavioral suites, then rerun the plan.',
    residualRisks: [],
  });
}, steps => {
  assert.deepEqual(steps, ['step6-implement', 'implementation-progress-check', 'implementation-wave-outcome', 'implementation-blocked-output']);
  assert(!steps.includes('step6-test-integrity-check'));
  assert(!steps.includes('step7-adversarial-review'));
  assert(!steps.includes('reconcile-implementations'));
}, 'mock-scenario.json', 'step6-implement');
run(codex, 'productive-implementation-revision', m => {
  const accepted = m['step6-test-integrity-check'];
  const revision = structuredClone(accepted);
  revision.when = { needs_revision: true };
  revision.payload.needs_revision = true;
  revision.payload.accepted = false;
  revision.payload.findings = [{
    severity: 'mid',
    file: 'packages/riela/src/workflow/review-findings.test.ts',
    message: 'Complete the planned typecheck evidence.',
    intentReference: 'The accepted plan requires typecheck evidence.',
    materialImpact: 'The implementation is not yet verified against the required static check.',
    fixCostBenefit: 'Running the planned check is bounded and directly verifies acceptance.',
  }];
  revision.payload.feedback = ['Run and report the planned typecheck.'];
  m['step6-test-integrity-check'] = [revision, accepted];
}, steps => {
  const first = steps.indexOf('step6-implement');
  assert.deepEqual(steps.slice(first, first + 7), [
    'step6-implement', 'implementation-progress-check', 'step6-test-integrity-check',
    'step6-implement', 'implementation-progress-check', 'step6-test-integrity-check',
    'step7-adversarial-review',
  ]);
  assert.equal(steps.filter(step => step === 'implementation-progress-check').length, 2);
}, 'mock-scenario.json', 'step6-implement');
run(codex, 'productive-incomplete-continuation', m => {
  m['step6-implement'][0].payload.implementationIncomplete = true;
}, steps => {
  assert.deepEqual(steps.slice(0, 7), [
    'step6-implement', 'implementation-progress-check',
    'step6-implement', 'implementation-progress-check',
    'step6-test-integrity-check', 'step7-adversarial-review', 'branch-evidence',
  ]);
  assert.equal(steps.filter(step => step === 'step6-implement').length, 2);
}, 'mock-scenario.json', 'step6-implement');
run(codex, 'native-fanout-dependency-blocked', m => {
  const blocked = {
    ...output({
      implementation_blocked: true,
      implementationIncomplete: true,
      blockers: [{
        dependency: 'impl-plans/active/prerequisite.md',
        evidenceChecked: 'No accepted implementation evidence exists.',
        impact: 'The assigned implementation cannot start safely.',
        resumeCriterion: 'Complete and verify the prerequisite plan.',
      }],
      issueReference: 'tacogips/cursor-agent#123',
      changedFiles: [],
      implementationSummary: 'Implementation did not start because an external prerequisite is not ready.',
      implPlanPaths: ['impl-plans/active/workflow-review-findings.md'],
      implPlanUpdates: [],
      verification: [],
      addressedFeedback: [],
      risks: ['External prerequisite remains incomplete.'],
    }, { implementation_blocked: true } as any),
    model: 'gpt-6-sol',
  };
  m['step6-implement'] = [blocked, structuredClone(blocked)];
  m['implementation-wave-outcome'] = output({
    implementation_blocked: true,
    partial_success: false,
    blockedPlanIds: ['a', 'b'],
    successfulPlanIds: [],
    blockers: [{ dependency: 'impl-plans/active/prerequisite.md' }],
    resumeCriteria: ['Complete and verify the prerequisite plan.'],
  }, { implementation_blocked: true } as any);
  m['implementation-blocked-output'] = output({
    implementation_blocked: true,
    status: 'blocked',
    workflowMode: 'issue-resolution',
    issueReference: 'tacogips/cursor-agent#123',
    blockedPlanIds: ['a', 'b'],
    successfulPlanIds: [],
    blockers: [{ dependency: 'impl-plans/active/prerequisite.md' }],
    resumeCriteria: ['Complete and verify the prerequisite plan.'],
    nextStep: 'Implement the prerequisite, then rerun this plan.',
    residualRisks: [],
  });
}, (steps, result) => {
  const outcome = steps.indexOf('implementation-wave-outcome');
  assert(outcome > steps.indexOf('dispatch-plans'));
  assert.equal(steps[outcome + 1], 'implementation-blocked-output');
  const outcomeExecution = result.session.executions.find((execution: any) => execution.stepId === 'implementation-wave-outcome');
  const joinedBranches = outcomeExecution?.inputSnapshot?.mergedVariables?.runtimeVariables?.fanoutJoin?.branches;
  assert.equal(joinedBranches?.length, 2, 'blocked native fanout must expose both terminal branch outputs at the parent join');
  assert(joinedBranches.every((branch: any) => branch.status === 'completed' && branch.output?.implementation_blocked === true));
  assert(joinedBranches.every((branch: any) => Array.isArray(branch.output?.changedFiles) && branch.output.changedFiles.length === 0));
  assert.equal(steps.filter(step => step === 'dispatch-plans').length, 1);
  assert(!steps.includes('reconcile-implementations'));
  assert(!steps.includes('integration-review'));
  assert(!steps.includes('step7b-e2e-evidence'));
  assert(!steps.includes('step10-git-commit'));
}, 'mock-scenario-fanout.json');
run(codex, 'native-fanout-partial-success-selective-redispatch', m => {
  const successful = structuredClone(m['step6-implement'][1]);
  const blocked = structuredClone(successful);
  blocked.when = { implementation_blocked: true };
  blocked.payload.implementation_blocked = true;
  blocked.payload.implementationIncomplete = true;
  blocked.payload.changedFiles = [];
  blocked.payload.verification = [];
  blocked.payload.implPlanUpdates = [];
  blocked.payload.blockers = [{ dependency: 'impl-plans/active/p1-capabilities.md', resumeCriterion: 'Repair the unavailable capability prerequisite.' }];
  m['step6-implement'] = [successful, blocked, structuredClone(successful)];

  const initialDispatch = structuredClone(m['dispatch-plans']);
  const retryDispatch = structuredClone(initialDispatch);
  retryDispatch.payload.acceptedPlanIds = ['a'];
  retryDispatch.payload.implementationItems = retryDispatch.payload.implementationItems.map((item: any) => ({ ...item, acceptedPlanIds: ['a'] }));
  m['dispatch-plans'] = [initialDispatch, retryDispatch];

  const partialOutcome = output({
    implementation_blocked: true,
    partial_success: true,
    blockedPlanIds: ['b'],
    successfulPlanIds: ['a'],
    blockers: [{ dependency: 'impl-plans/active/p1-capabilities.md' }],
    resumeCriteria: ['Repair and verify p1-capabilities.'],
  }, { implementation_blocked: true, partial_success: true } as any);
  const completedOutcome = structuredClone(m['implementation-wave-outcome']);
  completedOutcome.payload.partial_success = false;
  m['implementation-wave-outcome'] = [partialOutcome, completedOutcome];

  const finalReview = structuredClone(m['integration-review']);
  const partialReview = structuredClone(finalReview);
  partialReview.when = { needs_revision: false, redispatch_required: false, plans_remaining: true, repair_in_place: false };
  partialReview.payload.plans_remaining = true;
  partialReview.payload.acceptedPlanIds = ['a'];
  partialReview.payload.pendingPlanIds = ['b'];
  m['integration-review'] = [partialReview, finalReview];
}, (steps, result) => {
  assert.equal(steps.filter(step => step === 'dispatch-plans').length, 2);
  assert.equal(steps.filter(step => step === 'implementation-blocked-output').length, 0);
  assert.equal(steps.filter(step => step === 'integration-review').length, 2);
  const outcomes = result.session.executions.filter((execution: any) => execution.stepId === 'implementation-wave-outcome');
  assert.equal(outcomes.length, 2);
  const retryJoin = outcomes[1]?.inputSnapshot?.mergedVariables?.runtimeVariables?.fanoutJoin;
  assert.deepEqual(retryJoin?.dispatchedBranchIds, ['b'], 'accepted candidate must not be redispatched');
}, 'mock-scenario-fanout.json');
run(codex, 'two-branch-native-fanout', () => {}, steps => {
  assert(steps.indexOf('plan-git-commit') < steps.indexOf('plan-git-push'));
  assert(steps.indexOf('plan-git-push') < steps.indexOf('dispatch-plans'));
  assert.equal(steps.filter(step => step === 'plan-git-push').length, 1);
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
  const firstWaveItems = ['a', 'b', 'c'].map(planId => ({ ...prototype, planId, planPath: `impl-plans/active/${planId}.md`, dependsOn: planId === 'c' ? ['a', 'b'] : [], acceptedPlanIds: [], trackedPaths: [`${planId}.txt`, 'shared.txt'] }));
  const secondWaveItems = firstWaveItems.map(item => ({ ...item, acceptedPlanIds: ['a', 'b'] }));
  const dispatch = m['dispatch-plans'].payload;
  m['dispatch-plans'] = [
    output({ ...dispatch, implementationItems: firstWaveItems, acceptedPlanIds: [] }),
    output({ ...dispatch, implementationItems: secondWaveItems, acceptedPlanIds: ['a', 'b'] }),
  ];
  const acceptedReview = m['integration-review'];
  m['integration-review'] = [output({ ...acceptedReview.payload, plans_remaining: true, acceptedPlanIds: ['a', 'b'] }, { needs_revision: false, plans_remaining: true } as any), acceptedReview];
}, steps => {
  assert.equal(steps.filter(s => s === 'dispatch-plans').length, 2);
  assert.equal(steps.filter(s => s === 'reconcile-implementations').length, 2);
  assert.equal(steps.filter(s => s === 'implementation-blocked-output').length, 0);
  const firstDispatch = steps.indexOf('dispatch-plans');
  const firstReview = steps.indexOf('integration-review', firstDispatch);
  const secondDispatch = steps.indexOf('dispatch-plans', firstDispatch + 1);
  assert(firstDispatch < firstReview && firstReview < secondDispatch, 'accepted predecessor must unlock its downstream dependency wave');
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
