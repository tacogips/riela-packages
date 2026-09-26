import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { basename, dirname, isAbsolute, join, relative, resolve } from 'node:path';

type Mode = 'manifests' | 'workflows' | 'scenarios' | 'assets';
type Package = { id: string; dir: string; manifest: any; workflows: Workflow[]; dependencies: string[] };
type Workflow = { id: string; dir: string; definition: any; fixture?: string; owner: string };
const repo = resolve(import.meta.dir, '../../../..');
const args = process.argv.slice(2);
function option(name: string): string | undefined {
  const index = args.indexOf(name);
  if (index < 0) return undefined;
  if (!args[index + 1] || args[index + 1].startsWith('--')) throw Error(`${name} needs a value`);
  return args[index + 1];
}
const mode = option('--mode') as Mode;
if (!['manifests', 'workflows', 'scenarios', 'assets'].includes(mode)) throw Error('--mode must be manifests|workflows|scenarios|assets');
const source = resolve(option('--source-root') ?? repo);
const evidenceBase = resolve(repo, 'tmp/registry-contract-migration/verification/compat-verification');
const evidence = resolve(option('--evidence-root') ?? mkdtempSync(join(evidenceBase, `${mode}-`)));
if (relative(resolve(repo, 'tmp'), evidence).startsWith('..') || evidence === resolve(repo, 'tmp')) throw Error('evidence must be under repository tmp/');
mkdirSync(evidence, { recursive: true });
const cli = process.env.RIELA_COMPAT_CLI ?? 'riela';
const inventoryPath = resolve(option('--inventory') ?? join(repo, 'impl-plans/active/riela-021-inventory.json'));
const inventory = JSON.parse(readFileSync(inventoryPath, 'utf8'));
const records: any[] = [];
let failures = 0;
const sha = (value: Buffer | string) => createHash('sha256').update(value).digest('hex');
function command(label: string, argv: string[], cwd = source) {
  const result = spawnSync(cli, argv, { cwd, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
  const log = join(evidence, `${String(records.length + 1).padStart(4, '0')}-${label.replace(/[^a-z0-9.-]/gi, '_')}.log`);
  writeFileSync(log, `${result.stdout ?? ''}${result.stderr ?? ''}${result.error ? String(result.error) : ''}`);
  const record = { command: [cli, ...argv], cwd, exitCode: result.status ?? 127, log, label };
  records.push(record);
  if (record.exitCode !== 0) failures++;
  return { ...record, output: result.stdout ?? '' };
}
function packageInventory(): Package[] {
  const packageRoot = join(source, 'packages');
  const actual = readdirSync(packageRoot, { withFileTypes: true }).filter(entry => entry.isDirectory() && existsSync(join(packageRoot, entry.name, 'riela-package.json'))).map(entry => `packages/${entry.name}`);
  const expected = inventory.packages.map((entry: any) => entry.packagePath);
  const missing = expected.filter((path: string) => !actual.includes(path));
  const unexpected = actual.filter(path => !expected.includes(path));
  if (missing.length || unexpected.length) throw Error(`inventory drift: missing=${missing.join(',')} unexpected=${unexpected.join(',')}`);
  const actualWorkflows = actual.flatMap(packagePath => {
    const workflowRoot = join(source, packagePath, 'workflows');
    if (!existsSync(workflowRoot)) return [];
    return readdirSync(workflowRoot, { recursive: true }).filter((path: any) => typeof path === 'string' && basename(path) === 'workflow.json').map((path: string) => `${packagePath}/workflows/${path}`);
  });
  const expectedWorkflows = inventory.packages.flatMap((entry: any) => (entry.workflows ?? []).map((workflow: any) => workflow.path));
  const missingWorkflows = expectedWorkflows.filter((path: string) => !actualWorkflows.includes(path));
  const unexpectedWorkflows = actualWorkflows.filter(path => !expectedWorkflows.includes(path));
  if (missingWorkflows.length || unexpectedWorkflows.length) throw Error(`workflow inventory drift: missing=${missingWorkflows.join(',')} unexpected=${unexpectedWorkflows.join(',')}`);
  return inventory.packages.map((entry: any) => {
    const dir = join(source, entry.packagePath);
    const manifest = JSON.parse(readFileSync(join(dir, 'riela-package.json'), 'utf8'));
    const workflows = (entry.workflows ?? []).map((item: any) => {
      const workflowPath = join(source, item.path);
      const definition = JSON.parse(readFileSync(workflowPath, 'utf8'));
      const workflowDir = dirname(workflowPath);
      return { id: item.workflowId, dir: workflowDir, definition, fixture: existsSync(join(workflowDir, 'mock-scenario.json')) ? join(workflowDir, 'mock-scenario.json') : undefined, owner: manifest.name };
    });
    const dependencies = (manifest.dependencies ?? []).map((dep: any) => typeof dep === 'string' ? dep : dep.packageId);
    return { id: manifest.name, dir, manifest, workflows, dependencies };
  });
}
const packages = packageInventory();
const byPackage = new Map(packages.map(pkg => [pkg.id, pkg]));
const workflows = packages.flatMap(pkg => pkg.workflows);
const byWorkflow = new Map<string, Workflow>();
for (const workflow of workflows) {
  if (byWorkflow.has(workflow.id)) throw Error(`duplicate workflow ID: ${workflow.id}`);
  byWorkflow.set(workflow.id, workflow);
}
function effectiveSteps(workflow: Workflow, seen = new Set<string>()): Set<string> {
  if (seen.has(workflow.id)) throw Error(`inheritance cycle: ${workflow.id}`);
  const next = new Set(seen).add(workflow.id);
  const baseId = workflow.definition.extends?.workflowId;
  if (!baseId) return new Set((workflow.definition.steps ?? []).map((step: any) => step.id));
  const base = byWorkflow.get(baseId);
  if (!base) throw Error(`unresolved inherited base: ${workflow.id} -> ${baseId}`);
  const replacements = workflow.definition.extends?.stringReplacements ?? {};
  const inherited = [...effectiveSteps(base, next)].map(id => {
    let result = id;
    for (const [from, to] of Object.entries(replacements)) result = result.replaceAll(from, String(to));
    return result;
  });
  return new Set([...inherited, ...(workflow.definition.steps ?? []).map((step: any) => step.id)]);
}
type RouteEntry = { workflowId: string; fixture: string; route: string[]; sources: string[] };
const routeMapPath = resolve(option('--expected-routes') ?? join(repo, '.agents/skills/riela-package-release/fixtures/expected-routes.json'));
const routeEntries: RouteEntry[] = JSON.parse(readFileSync(routeMapPath, 'utf8')).routes;
if (!Array.isArray(routeEntries)) throw Error(`invalid expected-routes map: ${routeMapPath}`);
function selectedRoute(selection: any, mock: any, workflow: Workflow, fixture: string) {
  const fixturePath = relative(source, fixture);
  const key = `${workflow.id} / ${fixturePath}`;
  const entry = routeEntries.find(item => item.workflowId === workflow.id && item.fixture === fixturePath);
  let origin: string;
  let value: unknown;
  if (selection && typeof selection === 'object' && Object.hasOwn(selection, 'expectedRoute')) {
    origin = 'selection'; value = selection.expectedRoute;
  } else if (Object.hasOwn(mock, 'expectedRoute')) {
    origin = 'fixture'; value = mock.expectedRoute;
  } else if (entry) {
    origin = 'map'; value = entry.route;
  } else {
    throw Error(`missing expected route for ${key}`);
  }
  if (!Array.isArray(value) || !value.length || !value.every(step => typeof step === 'string' && step.trim().length > 0))
    throw Error(`invalid expected route from ${origin} for ${key}`);
  const validSteps = effectiveSteps(workflow);
  const absent = value.filter(step => !validSteps.has(step));
  if (absent.length) throw Error(`expected route from ${origin} has steps absent from effective graph for ${key}: ${absent.join(', ')}`);
  // Reuse fixture metadata through inheritance only when wrappers retain the
  // base step graph. A changed graph needs an effective-workflow route.
  if (workflow.fixture !== fixture && origin === 'fixture') {
    let current = workflow;
    while (current.fixture !== fixture) {
      const inherited = current.definition.extends;
      const graphOverride = current.definition.steps?.length || current.definition.entryStepId ||
        Object.keys(inherited ?? {}).some(field => !['workflowId', 'stringReplacements', 'agentNodePatch', 'nodePatch'].includes(field));
      if (graphOverride) throw Error(`incompatible inherited fixture route for ${key}; use an effective-workflow route`);
      current = byWorkflow.get(inherited.workflowId)!;
    }
  }
  return { route: value as string[], origin, fixturePath };
}
for (const pkg of packages) for (const dependency of pkg.dependencies) if (!byPackage.has(dependency)) throw Error(`unresolved local dependency: ${pkg.id} -> ${dependency}`);
for (const workflow of workflows) {
  const base = workflow.definition.extends?.workflowId;
  if (base && !byWorkflow.has(base)) throw Error(`unresolved inherited base: ${workflow.id} -> ${base}`);
}
const coverage = {
  source, sourceIdentity: sha(packages.map(pkg => readFileSync(join(pkg.dir, 'riela-package.json'))).concat(workflows.map(w => readFileSync(join(w.dir, 'workflow.json')))).map(x => sha(x)).join('\n')),
  inventorySourceHead: inventory.sourceHead, packages: packages.map(pkg => ({ id: pkg.id, path: relative(source, pkg.dir), dependencies: pkg.dependencies, workflows: pkg.workflows.map(w => w.id) })),
  workflows: workflows.map(w => ({ id: w.id, path: relative(source, w.dir), base: w.definition.extends?.workflowId ?? null, fixture: w.fixture ? relative(source, w.fixture) : null })),
  assets: readdirSync(join(source, 'packages'), { recursive: true }).filter((name: any) => typeof name === 'string' && /(SKILL\.md|AGENTS\.md|README\.md|EXPECTED_RESULTS\.md|addon\.json)$/i.test(name)),
};
writeFileSync(join(evidence, 'coverage.json'), JSON.stringify(coverage, null, 2) + '\n');
const cliVersion = command('version', ['--version']);
function contains(actual: any, expected: any): boolean {
  if (Array.isArray(expected)) return Array.isArray(actual) && expected.length === actual.length && expected.every((item, index) => contains(actual[index], item));
  if (expected && typeof expected === 'object') return actual && typeof actual === 'object' && Object.entries(expected).every(([key, value]) => contains(actual[key], value));
  return actual === expected;
}

function installCatalog() {
  const install = join(evidence, 'isolated-project');
  const catalog = join(evidence, 'catalog');
  mkdirSync(install, { recursive: true });
  mkdirSync(catalog, { recursive: true });
  for (const workflow of workflows) cpSync(workflow.dir, join(catalog, workflow.id), { recursive: true });
  const installed = new Set<string>();
  function installPackage(pkg: Package) {
    if (installed.has(pkg.id)) return;
    const result = command(`install-${basename(pkg.dir)}`, ['package', 'install', pkg.id, '--source', pkg.dir, '--scope', 'project', '--output', 'json'], install);
    if (result.exitCode === 0) installed.add(pkg.id);
  }
  // Workflow bases and callees are supplied by the catalog. External add-on
  // executables need project installation so validation resolves their source.
  for (const pkg of packages) if (pkg.manifest.kind === 'node-addon') installPackage(pkg);
  return { install, catalog, installed: [...installed] };
}

try {
  if (mode === 'manifests') {
    for (const pkg of packages) command(`manifest-${basename(pkg.dir)}`, ['package', 'validate', pkg.dir, '--output', 'json']);
  } else if (mode === 'workflows') {
    const { install, catalog, installed } = installCatalog();
    for (const workflow of workflows) {
      command(`validate-${workflow.id}`, ['workflow', 'validate', workflow.id, '--workflow-definition-dir', catalog, '--scope', 'project', '--output', 'json'], install);
      command(`inspect-${workflow.id}`, ['workflow', 'inspect', workflow.id, '--workflow-definition-dir', catalog, '--scope', 'project', '--output', 'json'], install);
    }
    writeFileSync(join(evidence, 'installed-dependencies.json'), JSON.stringify({ installed, install, catalog }, null, 2) + '\n');
  } else if (mode === 'scenarios') {
    const { install, catalog } = installCatalog();
    const selected = option('--workflow-list') ? JSON.parse(readFileSync(resolve(option('--workflow-list')!), 'utf8')) : workflows.filter(w => w.fixture).map(w => w.id);
    if (!Array.isArray(selected)) throw Error('--workflow-list must contain a JSON array');
    for (const [selectionIndex, selection] of selected.entries()) {
      const id = typeof selection === 'string' ? selection : selection?.workflowId;
      const workflow = byWorkflow.get(id);
      if (!workflow) throw Error(`unknown workflow: ${id}`);
      let fixture = workflow.fixture;
      let base = workflow;
      const seen = new Set<string>();
      while (!fixture && base.definition.extends?.workflowId) {
        if (seen.has(base.id)) throw Error(`inheritance cycle: ${id}`);
        seen.add(base.id);
        base = byWorkflow.get(base.definition.extends.workflowId)!;
        fixture = base.fixture;
      }
      if (!fixture) throw Error(`no scenario fixture for ${id}`);
      let routeSpec: ReturnType<typeof selectedRoute>;
      try {
        const mock = JSON.parse(readFileSync(fixture, 'utf8'));
        routeSpec = selectedRoute(selection, mock, workflow, fixture);
      } catch (error) {
        failures++;
        records.push({ label: `scenario-assert-${id}`, exitCode: 1, fixture: relative(source, fixture), error: String(error) });
        continue;
      }
      const caseId = `${id}-${selectionIndex}`;
      const run = command(`scenario-${id}`, ['workflow', 'run', id, '--workflow-definition-dir', catalog, '--scope', 'project', '--working-dir', source, '--mock-scenario', fixture, '--session-store', join(evidence, 'sessions', caseId), '--artifact-root', join(evidence, 'artifacts', caseId), '--output', 'json'], install);
      if (run.exitCode === 0) {
        try {
          const parsed = JSON.parse(run.output);
          const executions = parsed.session?.executions ?? [];
          const route = executions.map((item: any) => item.stepId);
          const mock = JSON.parse(readFileSync(fixture, 'utf8'));
          const expectedRoute = routeSpec.route;
          const routeMatches = route.length === expectedRoute.length && route.every((step: string, index: number) => step === expectedRoute[index]);
          let payloadChecks = 0;
          let mismatch = false;
          for (const execution of executions) {
            const entry = mock.steps?.[execution.stepId]?.output ?? mock[execution.stepId];
            const expected = Array.isArray(entry) ? entry[0] : entry;
            const payload = expected?.payload ?? (expected?.output?.payload ?? null);
            if (payload) { payloadChecks++; if (!contains(execution.acceptedOutput?.payload, payload)) mismatch = true; }
          }
          const passed = parsed.status === 'completed' && route.length > 0 && routeMatches && payloadChecks > 0 && !mismatch;
          if (!passed) failures++;
          records.push({ label: `scenario-assert-${id}`, exitCode: passed ? 0 : 1, fixture: routeSpec.fixturePath, routeOrigin: routeSpec.origin, expected: 'completed with fixture-backed payloads and selected route', observed: parsed.status, route, expectedRoute, routeMatches, payloadChecks, payloadMismatch: mismatch });
        } catch (error) { failures++; records.push({ label: `scenario-assert-${id}`, exitCode: 1, error: String(error) }); }
      } else {
        records.push({ label: `scenario-assert-${id}`, exitCode: 1, fixture: routeSpec.fixturePath, routeOrigin: routeSpec.origin, expectedRoute: routeSpec.route, observed: 'CLI exit nonzero', commandExitCode: run.exitCode });
      }
    }
  } else {
    const assets = coverage.assets as string[];
    const installHelp = command('package-install-help', ['package', 'install', '--help']).output;
    for (const asset of assets) {
      const path = join(source, 'packages', asset);
      const body = readFileSync(path, 'utf8');
      const issues: string[] = [];
      if (asset.endsWith('SKILL.md') && (!body.startsWith('---\n') || !body.slice(4).includes('\n---\n'))) issues.push('missing YAML frontmatter');
      if (asset.endsWith('addon.json')) {
        try {
          const descriptor = JSON.parse(body);
          for (const field of ['name', 'version', 'execution', 'inputSchema']) if (!descriptor[field]) issues.push(`missing descriptor ${field}`);
        } catch { issues.push('invalid add-on descriptor JSON'); }
      }
      if (asset.endsWith('README.md')) {
        for (const line of body.split('\n').filter(line => line.includes('riela package install'))) {
          for (const flag of line.match(/--[a-z][a-z-]*/g) ?? []) if (!installHelp.includes(flag)) issues.push(`undocumented install flag ${flag}`);
        }
      }
      if (issues.length) failures++;
      records.push({ label: `asset-${asset}`, exitCode: issues.length ? 1 : 0, issues });
    }
    records.push({ label: 'assets', exitCode: 0, checked: assets.length, exclusions: ['live credentialed examples', 'remote services'] });
  }
} catch (error) {
  failures++;
  records.push({ label: 'harness-error', exitCode: 1, error: String(error) });
}
writeFileSync(join(evidence, 'commands.json'), JSON.stringify({ mode, cliVersion: cliVersion.output.trim(), records }, null, 2) + '\n');
writeFileSync(join(evidence, 'baseline.json'), JSON.stringify({ mode, sourceIdentity: coverage.sourceIdentity, failures, results: records.filter(r => r.exitCode !== 0) }, null, 2) + '\n');
console.log(JSON.stringify({ mode, packages: packages.length, workflows: workflows.length, failures, evidence }));
process.exit(failures ? 1 : 0);
