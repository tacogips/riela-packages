#!/usr/bin/env bun
import { createHash } from "node:crypto";
import { existsSync, readdirSync } from "node:fs";
import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

type Manifest = {
  kind?: string;
  checksum?: string;
  checksumAlgorithm?: string;
  integrity?: {
    digestAlgorithm?: string;
    digest?: string;
    signatures?: unknown[];
    [key: string]: unknown;
  };
  workflowDirectory?: string;
  [key: string]: unknown;
};

const manifestFile = "riela-package.json";

const usage = `Usage:
  bun .riela/workflows/riela-package-release-skill/scripts/update-package-digests.ts <package-id> [<package-id>...]
  bun .riela/workflows/riela-package-release-skill/scripts/update-package-digests.ts --all

Options:
  --all      Update every packages/*/riela-package.json manifest.
  --dry-run  Print stale manifests without writing files.
  --help     Show this help.
`;

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
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

const selectedPackageIds = all
  ? readdirSync(packagesRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .filter((packageId) =>
        existsSync(path.join(packagesRoot, packageId, manifestFile)),
      )
      .sort()
  : packageIds;

function shouldExclude(relativePath: string): boolean {
  const entryNames = relativePath.split("/");
  return (
    relativePath === manifestFile ||
    relativePath.startsWith(".git/") ||
    entryNames.includes(".DS_Store") ||
    entryNames.includes("__MACOSX") ||
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

async function computePackageDigest(input: {
  packageRoot: string;
  workflowDirectory?: string;
  hashAlgorithm: "md5" | "sha256";
  requireWorkflowBundle: boolean;
}): Promise<string> {
  const files = await collectFiles(input.packageRoot);
  const hasManifest = existsSync(path.join(input.packageRoot, manifestFile));
  const workflowJson =
    input.workflowDirectory === undefined
      ? undefined
      : path
          .join(input.workflowDirectory, "workflow.json")
          .split(path.sep)
          .join("/");
  if (
    !hasManifest ||
    (input.requireWorkflowBundle &&
      (workflowJson === undefined || !files.includes(workflowJson)))
  ) {
    throw new Error(
      input.requireWorkflowBundle
        ? `package checksum requires ${manifestFile} and workflow.json`
        : `package checksum requires ${manifestFile}`,
    );
  }

  const hash = createHash(input.hashAlgorithm);
  for (const relativePath of files) {
    const content = await readFile(path.join(input.packageRoot, relativePath));
    hash.update(`path:${relativePath}\n`);
    hash.update(content);
    hash.update("\n");
  }
  return hash.digest("hex");
}

let staleCount = 0;
let failed = false;

for (const packageId of selectedPackageIds) {
  const packageRoot = path.join(packagesRoot, packageId);
  const manifestPath = path.join(packageRoot, manifestFile);

  if (!existsSync(manifestPath)) {
    console.error(`${packageId}\tmissing ${manifestFile}`);
    failed = true;
    continue;
  }

  const manifest = JSON.parse(await readFile(manifestPath, "utf8")) as Manifest;
  const kind = manifest.kind ?? "workflow";

  if (kind !== "workflow" && kind !== "node-addon") {
    console.error(`${packageId}\tunsupported package kind: ${kind}`);
    failed = true;
    continue;
  }

  const requireWorkflowBundle = kind === "workflow";
  if (requireWorkflowBundle && !manifest.workflowDirectory) {
    console.error(`${packageId}\tmissing workflowDirectory`);
    failed = true;
    continue;
  }

  let checksum: string;
  let digest: string;
  try {
    checksum = await computePackageDigest({
      packageRoot,
      workflowDirectory: manifest.workflowDirectory,
      hashAlgorithm: "md5",
      requireWorkflowBundle,
    });
    digest = await computePackageDigest({
      packageRoot,
      workflowDirectory: manifest.workflowDirectory,
      hashAlgorithm: "sha256",
      requireWorkflowBundle,
    });
  } catch (error) {
    console.error(`${packageId}\tdigest failed`);
    console.error(error);
    failed = true;
    continue;
  }

  const nextManifest: Manifest = {
    ...manifest,
    checksum,
    checksumAlgorithm: "md5",
    integrity: {
      ...(manifest.integrity ?? {}),
      digestAlgorithm: "sha256",
      digest,
    },
  };

  const changedFields = [
    manifest.checksum !== nextManifest.checksum ? "checksum" : null,
    manifest.checksumAlgorithm !== nextManifest.checksumAlgorithm
      ? "checksumAlgorithm"
      : null,
    manifest.integrity?.digestAlgorithm !== nextManifest.integrity?.digestAlgorithm
      ? "integrity.digestAlgorithm"
      : null,
    manifest.integrity?.digest !== nextManifest.integrity?.digest
      ? "integrity.digest"
      : null,
  ].filter(Boolean);

  if (changedFields.length === 0) {
    console.log(`${packageId}\tok`);
    continue;
  }

  staleCount += 1;
  console.log(`${packageId}\tupdate ${changedFields.join(",")}`);

  if (!dryRun) {
    await writeFile(manifestPath, `${JSON.stringify(nextManifest, null, 2)}\n`);
  }
}

if (failed) {
  process.exit(1);
}

if (dryRun && staleCount > 0) {
  process.exit(1);
}
