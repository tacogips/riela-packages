#!/usr/bin/env bun
import { existsSync, readdirSync } from "node:fs";
import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

type ChecksumResult = {
  ok: boolean;
  value?: {
    checksum: string;
  };
  error?: unknown;
};

type IntegrityResult = {
  ok: boolean;
  value?: {
    digest: string;
  };
  error?: unknown;
};

type Manifest = {
  checksum?: string;
  checksumAlgorithm?: string;
  integrity?: {
    digestAlgorithm?: string;
    digest?: string;
  };
  workflowDirectory?: string;
  [key: string]: unknown;
};

const usage = `Usage:
  bun .agents/skills/rielflow-package-release/scripts/update-package-digests.ts <package-id> [<package-id>...]
  bun .agents/skills/rielflow-package-release/scripts/update-package-digests.ts --all

Options:
  --all      Update every packages/*/rielflow-package.json manifest.
  --dry-run  Print stale manifests without writing files.
  --help     Show this help.

Environment:
  RIELFLOW_ROOT defaults to ../rielflow.
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
const rielflowRoot = path.resolve(repoRoot, process.env.RIELFLOW_ROOT ?? "../rielflow");
const checksumModulePath = path.join(
  rielflowRoot,
  "packages/rielflow/src/workflow/packages/checksum.ts",
);

if (!existsSync(packagesRoot)) {
  console.error(`Missing packages directory: ${packagesRoot}`);
  process.exit(2);
}

if (!existsSync(checksumModulePath)) {
  console.error(`Missing rielflow checksum module: ${checksumModulePath}`);
  console.error("Set RIELFLOW_ROOT to the local rielflow source checkout.");
  process.exit(2);
}

const {
  computeWorkflowPackageChecksum,
  computeWorkflowPackageIntegrityDigest,
} = await import(pathToFileURL(checksumModulePath).href);

const selectedPackageIds = all
  ? readdirSync(packagesRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .filter((packageId) =>
        existsSync(path.join(packagesRoot, packageId, "rielflow-package.json")),
      )
      .sort()
  : packageIds;

let staleCount = 0;
let failed = false;

for (const packageId of selectedPackageIds) {
  const packageRoot = path.join(packagesRoot, packageId);
  const manifestPath = path.join(packageRoot, "rielflow-package.json");

  if (!existsSync(manifestPath)) {
    console.error(`${packageId}\tmissing rielflow-package.json`);
    failed = true;
    continue;
  }

  const manifest = JSON.parse(await readFile(manifestPath, "utf8")) as Manifest;
  if (!manifest.workflowDirectory) {
    console.error(`${packageId}\tmissing workflowDirectory`);
    failed = true;
    continue;
  }

  const checksum = (await computeWorkflowPackageChecksum({
    packageRoot,
    workflowDirectory: manifest.workflowDirectory,
  })) as ChecksumResult;
  const integrity = (await computeWorkflowPackageIntegrityDigest({
    packageRoot,
    workflowDirectory: manifest.workflowDirectory,
  })) as IntegrityResult;

  if (!checksum.ok || !checksum.value) {
    console.error(`${packageId}\tchecksum failed`);
    console.error(checksum.error);
    failed = true;
    continue;
  }

  if (!integrity.ok || !integrity.value) {
    console.error(`${packageId}\tintegrity failed`);
    console.error(integrity.error);
    failed = true;
    continue;
  }

  const nextManifest: Manifest = {
    ...manifest,
    checksum: checksum.value.checksum,
    checksumAlgorithm: "md5",
    integrity: {
      ...(manifest.integrity ?? {}),
      digestAlgorithm: "sha256",
      digest: integrity.value.digest,
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
