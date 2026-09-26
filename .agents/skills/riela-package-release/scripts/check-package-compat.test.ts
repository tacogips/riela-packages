import { describe, expect, test } from 'bun:test';
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
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
    writeFileSync(join(w, 'workflow.json'), JSON.stringify({ workflowId, ...(base ? { extends: { workflowId: base } } : {}) }));
    if (scenario) writeFileSync(join(w, 'mock-scenario.json'), '{}');
    return { packagePath: `packages/${dir}`, workflows: [{ path: `packages/${dir}/workflows/${workflowId}/workflow.json`, workflowId }] };
  };
  const entries = [pkg('alpha', 'alpha', 'alpha', undefined, [], true), pkg('beta', 'beta', 'beta', 'alpha')];
  const inventory = join(root, 'inventory.json');
  const save = () => writeFileSync(inventory, JSON.stringify({ sourceHead: 'fixture', packages: entries }));
  save();
  const run = (mode: string, extras: string[] = [], env: Record<string, string> = {}) => spawnSync('bun', [script, '--mode', mode, '--source-root', source, '--evidence-root', evidence, '--inventory', inventory, ...extras], { cwd: repo, encoding: 'utf8', env: { ...process.env, RIELA_COMPAT_CLI: cli, ...env } });
  return { root, source, evidence, cli, pkg, entries, inventory, save, run };
}

describe('compatibility harness', () => {
  test('inventory omissions fail', () => {
    const f = fixture(); f.entries.pop(); f.save();
    const result = f.run('manifests');
    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain('inventory drift');
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
  test('installed runtime validates a real package', () => {
    const result = spawnSync('riela', ['package', 'validate', join(repo, 'packages/greeting-shell'), '--output', 'json'], { cwd: repo, encoding: 'utf8' });
    expect(result.status).toBe(0);
    expect(JSON.parse(result.stdout).packages[0].valid).toBe(true);
  });
});
