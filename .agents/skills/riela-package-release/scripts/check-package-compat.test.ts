import { describe, expect, test } from 'bun:test';
import { chmodSync, existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const repo = resolve(import.meta.dir, '../../../..');
const script = join(import.meta.dir, 'check-package-compat.ts');
const scratch = join(repo, 'tmp/registry-contract-migration/verification/compat-verification/tests');
mkdirSync(scratch, { recursive: true });
function fixture() {
  const root = mkdtempSync(join(scratch, 'case-'));
  const source = join(root, 'source');
  const evidence = join(root, 'evidence');
  const cli = join(root, 'riela-stub');
  writeFileSync(cli, '#!/bin/sh\ncase "$*" in\n  "--version") echo 0.2.1;;\n  *"workflow run"*) echo \'{"status":"failed"}\';;\n  *) echo \'{"valid":true,"status":"completed"}\';;\nesac\n');
  chmodSync(cli, 0o755);
  const pkg = (dir: string, id: string, workflowId = id, base?: string, deps: string[] = [], scenario = false) => {
    const p = join(source, 'packages', dir);
    const w = join(p, 'workflows', workflowId);
    mkdirSync(w, { recursive: true });
    writeFileSync(join(p, 'riela-package.json'), JSON.stringify({ name: id, dependencies: deps, workflowDirectory: `workflows/${workflowId}` }));
    writeFileSync(join(w, 'workflow.json'), JSON.stringify({ workflowId, ...(base ? { extends: { workflowId: base } } : {}), steps: [{ id: workflowId }] }));
    if (scenario) writeFileSync(join(w, 'mock-scenario.json'), '{}');
    return { packagePath: `packages/${dir}`, workflows: [{ path: `packages/${dir}/workflows/${workflowId}/workflow.json`, workflowId }] };
  };
  const entries = [pkg('alpha', 'alpha', 'alpha', undefined, [], true), pkg('beta', 'beta', 'beta', 'alpha')];
  const inventory = join(root, 'inventory.json');
  const routes = join(root, 'expected-routes.json');
  const saveRoutes = (entries: any[] = [
    { workflowId: 'alpha', fixture: 'packages/alpha/workflows/alpha/mock-scenario.json', route: ['alpha'], sources: [] },
    { workflowId: 'beta', fixture: 'packages/alpha/workflows/alpha/mock-scenario.json', route: ['alpha', 'beta'], sources: [] },
  ]) => writeFileSync(routes, JSON.stringify({ routes: entries }));
  const save = () => writeFileSync(inventory, JSON.stringify({ sourceHead: 'fixture', packages: entries }));
  save(); saveRoutes();
  const run = (mode: string, extras: string[] = [], env: Record<string, string> = {}) => spawnSync('bun', [script, '--mode', mode, '--source-root', source, '--evidence-root', evidence, '--inventory', inventory, '--expected-routes', routes, ...extras], { cwd: repo, encoding: 'utf8', env: { ...process.env, RIELA_COMPAT_CLI: cli, ...env } });
  return { root, source, evidence, cli, pkg, entries, inventory, routes, saveRoutes, save, run };
}

describe('compatibility harness', () => {
  test('inventory omissions fail', () => {
    const f = fixture(); f.entries.pop(); f.save();
    const result = f.run('manifests');
    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain('inventory drift');
  });
  test('workflow omitted within an inventoried package fails', () => {
    const f = fixture();
    const added = join(f.source, 'packages/alpha/workflows/added');
    mkdirSync(added, { recursive: true });
    writeFileSync(join(added, 'workflow.json'), JSON.stringify({ workflowId: 'added' }));
    const result = f.run('manifests');
    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain('workflow inventory drift');
    expect(result.stderr).toContain('packages/alpha/workflows/added/workflow.json');
  });
  test('duplicate workflow IDs fail', () => {
    const f = fixture(); f.pkg('gamma', 'gamma', 'alpha'); f.entries.push({ packagePath: 'packages/gamma', workflows: [{ path: 'packages/gamma/workflows/alpha/workflow.json', workflowId: 'alpha' }] }); f.save();
    const result = f.run('manifests');
    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain('duplicate workflow ID');
  });
  test('unresolved dependency fails', () => {
    const f = fixture();
    writeFileSync(join(f.source, 'packages/alpha/riela-package.json'), JSON.stringify({ name: 'alpha', dependencies: ['absent'] }));
    const result = f.run('workflows');
    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain('unresolved local dependency');
  });
  test('add-on installation failure propagates', () => {
    const f = fixture();
    writeFileSync(join(f.source, 'packages/alpha/riela-package.json'), JSON.stringify({ name: 'alpha', kind: 'node-addon' }));
    writeFileSync(f.cli, '#!/bin/sh\ncase "$*" in *"package install"*) echo install-failed >&2; exit 7;; *) echo \'{"valid":true}\';; esac\n');
    const result = f.run('workflows');
    expect(result.status).not.toBe(0);
    const records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => record.label === 'install-alpha' && record.exitCode === 7)).toBe(true);
  });
  test('inherited workflow is validated and inspected', () => {
    const f = fixture();
    const result = f.run('workflows');
    expect(result.status).toBe(0);
    const records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => record.label === 'validate-beta')).toBe(true);
    expect(records.some((record: any) => record.label === 'inspect-beta')).toBe(true);
  });
  test('CLI nonzero exit propagates', () => {
    const f = fixture();
    writeFileSync(f.cli, '#!/bin/sh\necho rejected >&2\nexit 7\n');
    const result = f.run('manifests');
    expect(result.status).not.toBe(0);
    const summary = JSON.parse(readFileSync(join(f.evidence, 'baseline.json'), 'utf8'));
    expect(summary.failures).toBeGreaterThan(0);
  });
  test('scenario terminal assertion fails', () => {
    const f = fixture();
    const list = join(f.root, 'list.json'); writeFileSync(list, '["beta"]');
    const result = f.run('scenarios', ['--workflow-list', list]);
    expect(result.status).not.toBe(0);
    const records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => record.label === 'scenario-assert-beta')).toBe(true);
  });
  test('completed scenario on a wrong route fails despite a matching payload', () => {
    const f = fixture();
    writeFileSync(join(f.source, 'packages/alpha/workflows/alpha/mock-scenario.json'), JSON.stringify({ steps: { alpha: { output: { payload: { value: 1 } } } } }));
    const list = join(f.root, 'list.json');
    writeFileSync(list, JSON.stringify([{ workflowId: 'beta', expectedRoute: ['alpha', 'beta'] }]));
    const completed = { status: 'completed', session: { executions: [{ stepId: 'alpha', acceptedOutput: { payload: { value: 1 } } }, { stepId: 'gamma', acceptedOutput: { payload: {} } }] } };
    writeFileSync(f.cli, `#!/bin/sh\ncat <<'JSON'\n${JSON.stringify(completed)}\nJSON\n`);
    const result = f.run('scenarios', ['--workflow-list', list]);
    expect(result.status).not.toBe(0);
    const records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => record.label === 'scenario-assert-beta' && record.routeMatches === false && record.payloadChecks === 1)).toBe(true);
    completed.session.executions[1].stepId = 'beta';
    writeFileSync(f.cli, `#!/bin/sh\ncat <<'JSON'\n${JSON.stringify(completed)}\nJSON\n`);
    const matching = f.run('scenarios', ['--workflow-list', list]);
    expect(matching.status).toBe(0);
  });
  test('default selection requires its mapped route and matching payload', () => {
    const f = fixture();
    writeFileSync(join(f.source, 'packages/alpha/workflows/alpha/mock-scenario.json'), JSON.stringify({ steps: { alpha: { output: { payload: { value: 1 } } }, beta: { output: { payload: { value: 1 } } } } }));
    const completed = { status: 'completed', session: { executions: [{ stepId: 'beta', acceptedOutput: { payload: { value: 1 } } }] } };
    writeFileSync(f.cli, `#!/bin/sh\necho '${JSON.stringify(completed)}'\n`);
    const wrong = f.run('scenarios');
    expect(wrong.status).not.toBe(0);
    let records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => record.label === 'scenario-assert-alpha' && record.routeOrigin === 'map' && record.routeMatches === false && record.payloadChecks === 1)).toBe(true);
    completed.session.executions[0].stepId = 'alpha';
    writeFileSync(f.cli, `#!/bin/sh\necho '${JSON.stringify(completed)}'\n`);
    expect(f.run('scenarios').status).toBe(0);
    records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => record.label === 'scenario-assert-alpha' && record.exitCode === 0 && record.payloadChecks === 1)).toBe(true);
  });
  test('missing and malformed default routes fail closed', () => {
    const f = fixture();
    f.saveRoutes([]);
    expect(f.run('scenarios').status).not.toBe(0);
    let records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => String(record.error).includes('missing expected route for alpha / packages/alpha/workflows/alpha/mock-scenario.json'))).toBe(true);
    writeFileSync(join(f.source, 'packages/alpha/workflows/alpha/mock-scenario.json'), JSON.stringify({ expectedRoute: [] }));
    f.saveRoutes();
    expect(f.run('scenarios').status).not.toBe(0);
    records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => String(record.error).includes('invalid expected route from fixture'))).toBe(true);
  });
  test('selection precedence rejects malformed routes without fallback', () => {
    const f = fixture();
    const list = join(f.root, 'list.json');
    writeFileSync(list, JSON.stringify([{ workflowId: 'alpha', expectedRoute: null }]));
    expect(f.run('scenarios', ['--workflow-list', list]).status).not.toBe(0);
    const records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => String(record.error).includes('invalid expected route from selection'))).toBe(true);
  });
  test('inherited fixture uses effective wrapper route', () => {
    const f = fixture();
    writeFileSync(join(f.source, 'packages/alpha/workflows/alpha/mock-scenario.json'), JSON.stringify({ steps: { alpha: { output: { payload: { value: 1 } } } } }));
    const list = join(f.root, 'list.json'); writeFileSync(list, '["beta"]');
    const completed = { status: 'completed', session: { executions: [{ stepId: 'alpha', acceptedOutput: { payload: { value: 1 } } }, { stepId: 'beta', acceptedOutput: { payload: {} } }] } };
    writeFileSync(f.cli, `#!/bin/sh\necho '${JSON.stringify(completed)}'\n`);
    expect(f.run('scenarios', ['--workflow-list', list]).status).toBe(0);
    const records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => record.label === 'scenario-assert-beta' && record.routeOrigin === 'map' && record.fixture === 'packages/alpha/workflows/alpha/mock-scenario.json' && record.exitCode === 0)).toBe(true);
  });
  test('inherited wrapper rejects incompatible base route', () => {
    const f = fixture();
    f.saveRoutes([{ workflowId: 'alpha', fixture: 'packages/alpha/workflows/alpha/mock-scenario.json', route: ['alpha'], sources: [] }]);
    const list = join(f.root, 'list.json'); writeFileSync(list, '["beta"]');
    const result = f.run('scenarios', ['--workflow-list', list]);
    expect(result.status).not.toBe(0);
    const records = JSON.parse(readFileSync(join(f.evidence, 'commands.json'), 'utf8')).records;
    expect(records.some((record: any) => String(record.error).includes('missing expected route for beta / packages/alpha/workflows/alpha/mock-scenario.json'))).toBe(true);
  });
  test('repository map covers every packaged default fixture with source evidence', () => {
    const inventory = JSON.parse(readFileSync(join(repo, 'impl-plans/active/riela-021-inventory.json'), 'utf8'));
    const map = JSON.parse(readFileSync(join(repo, '.agents/skills/riela-package-release/fixtures/expected-routes.json'), 'utf8'));
    const selected = inventory.packages.flatMap((pkg: any) => pkg.workflows ?? []).filter((item: any) => existsSync(join(repo, item.path.replace(/workflow\.json$/, 'mock-scenario.json'))));
    expect(selected.length).toBeGreaterThan(0);
    for (const item of selected) {
      const fixturePath = item.path.replace(/workflow\.json$/, 'mock-scenario.json');
      const entry = map.routes.find((route: any) => route.workflowId === item.workflowId && route.fixture === fixturePath);
      expect(entry).toBeDefined();
      expect(entry.route.length).toBeGreaterThan(0);
      expect(entry.sources).toContain(item.path);
      expect(entry.sources).toContain(fixturePath);
      for (const path of entry.sources) expect(existsSync(join(repo, path))).toBe(true);
    }
  });
  test('website routes project fanout children out of the parent session', () => {
    const map = JSON.parse(readFileSync(join(repo, '.agents/skills/riela-package-release/fixtures/expected-routes.json'), 'utf8'));
    const graph = JSON.parse(readFileSync(join(repo, 'packages/codex-website-builder/workflows/codex-website-builder/workflow.json'), 'utf8'));
    const dispatch = graph.steps.find((step: any) => step.id === 'review-dispatch');
    expect(dispatch.transitions[0].toStepId).toBe('review-node');
    expect(dispatch.transitions[0].fanout.joinStepId).toBe('review-reducer');
    for (const workflowId of ['codex-website-builder', 'claude-code-website-builder', 'cursor-cli-website-builder']) {
      const entry = map.routes.find((route: any) => route.workflowId === workflowId);
      expect(entry).toBeDefined();
      const index = entry.route.indexOf('review-dispatch');
      expect(index).toBeGreaterThan(-1);
      expect(entry.route[index + 1]).toBe('review-reducer');
      expect(entry.route).not.toContain('review-node');
    }
  });
  test('installed runtime validates a real package', () => {
    const result = spawnSync('riela', ['package', 'validate', join(repo, 'packages/greeting-shell'), '--output', 'json'], { cwd: repo, encoding: 'utf8' });
    expect(result.status).toBe(0);
    expect(JSON.parse(result.stdout).packages[0].valid).toBe(true);
  });
});
