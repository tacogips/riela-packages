#!/usr/bin/env bun
import { createHash } from "node:crypto";
import { existsSync, readdirSync } from "node:fs";
import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

type Addon = {
  name?: string;
  version?: string;
  sourcePath?: string;
  contentDigest?: string;
  execution?: {
    kind?: string;
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

type DependencyAddonLock = {
  name?: string;
  version?: string;
  contentDigest?: string;
  [key: string]: unknown;
};

type Dependency = {
  packageId?: string;
  addons?: DependencyAddonLock[];
  [key: string]: unknown;
};

type Manifest = {
  name?: string;
  kind?: string;
  addons?: Addon[];
  dependencies?: (Dependency | string)[];
  [key: string]: unknown;
};

const manifestFile = "riela-package.json";

const usage = `Usage:
  bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts <package-id> [<package-id>...]
  bun .agents/skills/riela-package-release/scripts/update-addon-content-digests.ts --all

Recomputes addons[].contentDigest as sha256 over the add-on sourcePath files
(same file-walk recipe as update-package-digests.ts), then syncs matching
dependencies[].addons[].contentDigest locks in every package manifest.

Options:
  --all      Update every packages/*/riela-package.json manifest with add-ons.
  --dry-run  Print stale digests without writing files. Exits non-zero when stale.
  --check    Alias for --dry-run.
  --help     Show this help.
`;

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run") || args.includes("--check");
const all = args.includes("--all");
const help = args.includes("--help") || args.includes("-h");
const packageIds = args.filter((arg) => !arg.startsWith("--"));

if (help) {
  console.log(usage);
  process.exit(0);
}

if (!all && packageIds.length === 0) {
  console.error(usage);
  process.exit(2);
}

const repoRoot = process.cwd();
const packagesRoot = path.join(repoRoot, "packages");

if (!existsSync(packagesRoot)) {
  console.error(`Missing packages directory: ${packagesRoot}`);
  process.exit(2);
}

const allPackageIds = readdirSync(packagesRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .filter((packageId) => existsSync(path.join(packagesRoot, packageId, manifestFile)))
  .sort();

const selectedPackageIds = all ? allPackageIds : packageIds;

function shouldExclude(relativePath: string): boolean {
  const entryNames = relativePath.split("/");
  return (
    relativePath.startsWith(".git/") ||
    relativePath.endsWith(".pyc") ||
    relativePath.endsWith(".pyo") ||
    entryNames.includes(".DS_Store") ||
    entryNames.includes("__MACOSX") ||
    entryNames.includes("__pycache__") ||
    entryNames.includes(".git") ||
    entryNames.includes(".hg") ||
    entryNames.includes(".svn")
  );
}

async function collectFiles(root: string): Promise<string[]> {
  const files: string[] = [];

  async function visit(directory: string): Promise<void> {
    const entries = await readdir(directory, { withFileTypes: true });
    for (const entry of entries) {
      const absolute = path.join(directory, entry.name);
      const relative = path.relative(root, absolute).split(path.sep).join("/");
      if (shouldExclude(relative)) {
        continue;
      }
      if (entry.isDirectory()) {
        await visit(absolute);
      } else if (entry.isFile()) {
        files.push(relative);
      }
    }
  }

  await visit(root);
  return files.sort((left, right) => (left < right ? -1 : left > right ? 1 : 0));
}

async function computeAddonContentDigest(addonRoot: string): Promise<string> {
  const files = await collectFiles(addonRoot);
  if (files.length === 0) {
    throw new Error(`add-on source directory has no files: ${addonRoot}`);
  }
  const hash = createHash("sha256");
  for (const relativePath of files) {
    const content = await readFile(path.join(addonRoot, relativePath));
    hash.update(`path:${relativePath}\n`);
    hash.update(content);
    hash.update("\n");
  }
  return `sha256:${hash.digest("hex")}`;
}

function addonLockKey(name: string, version: string): string {
  return `${name}@${version}`;
}

let staleCount = 0;
let failed = false;
const computedDigests = new Map<string, string>();

for (const packageId of selectedPackageIds) {
  const packageRoot = path.join(packagesRoot, packageId);
  const manifestPath = path.join(packageRoot, manifestFile);

  if (!existsSync(manifestPath)) {
    console.error(`${packageId}\tmissing ${manifestFile}`);
    failed = true;
    continue;
  }

  const manifest = JSON.parse(await readFile(manifestPath, "utf8")) as Manifest;
  const addons = Array.isArray(manifest.addons) ? manifest.addons : [];
  const digestAddons = addons.filter(
    (addon) => addon.execution?.kind !== undefined || addon.contentDigest !== undefined,
  );
  if (digestAddons.length === 0) {
    if (!all) {
      console.log(`${packageId}\tno add-on content digests`);
    }
    continue;
  }

  let packageChanged = false;
  for (const addon of digestAddons) {
    const addonName = addon.name;
    const addonVersion = addon.version;
    const sourcePath = addon.sourcePath;
    if (!addonName || !addonVersion || !sourcePath) {
      console.error(`${packageId}\tadd-on requires name, version, and sourcePath`);
      failed = true;
      continue;
    }
    const addonRoot = path.join(packageRoot, sourcePath);
    if (!existsSync(addonRoot)) {
      console.error(`${packageId}\t${addonName}\tmissing sourcePath: ${sourcePath}`);
      failed = true;
      continue;
    }
    let digest: string;
    try {
      digest = await computeAddonContentDigest(addonRoot);
    } catch (error) {
      console.error(`${packageId}\t${addonName}\tdigest failed`);
      console.error(error);
      failed = true;
      continue;
    }
    computedDigests.set(addonLockKey(addonName, addonVersion), digest);
    if (addon.contentDigest === digest) {
      console.log(`${packageId}\t${addonName}\tok`);
      continue;
    }
    staleCount += 1;
    packageChanged = true;
    console.log(`${packageId}\t${addonName}\tupdate contentDigest ${addon.contentDigest ?? "-"} -> ${digest}`);
    addon.contentDigest = digest;
  }

  if (packageChanged && !dryRun) {
    await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  }
}

for (const packageId of allPackageIds) {
  const manifestPath = path.join(packagesRoot, packageId, manifestFile);
  const manifest = JSON.parse(await readFile(manifestPath, "utf8")) as Manifest;
  const dependencies = Array.isArray(manifest.dependencies) ? manifest.dependencies : [];
  let packageChanged = false;
  for (const dependency of dependencies) {
    if (!dependency || typeof dependency !== "object" || !Array.isArray(dependency.addons)) {
      continue;
    }
    for (const lock of dependency.addons) {
      if (!lock.name || !lock.version) {
        continue;
      }
      const digest = computedDigests.get(addonLockKey(lock.name, lock.version));
      if (digest === undefined || lock.contentDigest === digest) {
        continue;
      }
      staleCount += 1;
      packageChanged = true;
      console.log(`${packageId}\t${lock.name}\tupdate dependency lock ${lock.contentDigest ?? "-"} -> ${digest}`);
      lock.contentDigest = digest;
    }
  }
  if (packageChanged && !dryRun) {
    await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  }
}

if (failed) {
  process.exit(1);
}

if (dryRun && staleCount > 0) {
  process.exit(1);
}
