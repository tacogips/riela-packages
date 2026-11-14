#!/usr/bin/env bun
import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { spawnSync } from "node:child_process";

type Manifest = {
  name?: string;
  version?: string;
  description?: string;
  [key: string]: unknown;
};

type ArchiveEntry = {
  packageId: string;
  packageName: string;
  version: string;
  archiveFile: string;
  archivePath: string;
  archiveURL?: string;
  archiveSHA256: string;
};

const usage = `Usage:
  bun .agents/skills/riela-package-release/scripts/pack-release-archives.ts [<package-id>...]
  bun .agents/skills/riela-package-release/scripts/pack-release-archives.ts --all

Options:
  --all                 Pack every package under packages/*.
  --output-dir <dir>    Archive output directory. Default: dist/rielapkg.
  --manifest <path>     JSON manifest output path. Default: dist/package-archives.json.
  --archive-base-url <url>
                        Stamp archiveURL fields using this release asset base URL.
  --check               Repack into a temp dir and fail if manifest output is stale.
  --help                Show this help.
`;

const args = process.argv.slice(2);
let all = false;
let check = false;
let outputDir = "dist/rielapkg";
let manifestPath = "dist/package-archives.json";
let archiveBaseURL: string | undefined;
const packageIds: string[] = [];

for (let index = 0; index < args.length; index += 1) {
  const arg = args[index];
  if (arg === "--help" || arg === "-h") {
    console.log(usage);
    process.exit(0);
  }
  if (arg === "--all") {
    all = true;
    continue;
  }
  if (arg === "--check") {
    check = true;
    continue;
  }
  if (arg === "--output-dir") {
    outputDir = requiredArg(args[++index], "--output-dir");
    continue;
  }
  if (arg === "--manifest") {
    manifestPath = requiredArg(args[++index], "--manifest");
    continue;
  }
  if (arg === "--archive-base-url") {
    archiveBaseURL = requiredArg(args[++index], "--archive-base-url").replace(/\/+$/, "");
    continue;
  }
  if (arg.startsWith("--")) {
    console.error(`unknown option: ${arg}`);
    console.error(usage);
    process.exit(2);
  }
  packageIds.push(arg);
}

if (!all && packageIds.length === 0) {
  console.error(usage);
  process.exit(2);
}

const repoRoot = process.cwd();
const packagesRoot = path.join(repoRoot, "packages");
const selectedPackageIds = all
  ? readdirSync(packagesRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .filter((packageId) => existsSync(path.join(packagesRoot, packageId, "riela-package.json")))
      .sort()
  : packageIds;

const actualOutputDir = path.resolve(repoRoot, check ? `.tmp-release-archives-${process.pid}` : outputDir);
const actualManifestPath = path.resolve(repoRoot, check ? `.tmp-package-archives-${process.pid}.json` : manifestPath);

try {
  if (existsSync(actualOutputDir)) {
    await rm(actualOutputDir, { recursive: true, force: true });
  }
  await mkdir(actualOutputDir, { recursive: true });

  const archives: ArchiveEntry[] = [];
  for (const packageId of selectedPackageIds) {
    const packageRoot = path.join(packagesRoot, packageId);
    const manifest = await readManifest(packageRoot, packageId);
    validatePackageTree(packageRoot, packageId);
    const archiveFile = `${safeArchiveToken(packageId)}.rielapkg`;
    const archivePath = path.join(actualOutputDir, archiveFile);
    createZipArchive(packageRoot, archivePath);
    const archiveSHA256 = `sha256:${sha256File(archivePath)}`;
    const relativeArchivePath = path.relative(repoRoot, archivePath).split(path.sep).join("/");
    archives.push({
      packageId,
      packageName: requiredString(manifest.name, `${packageId}: name`),
      version: requiredString(manifest.version, `${packageId}: version`),
      archiveFile,
      archivePath: relativeArchivePath,
      archiveURL: archiveBaseURL ? `${archiveBaseURL}/${encodeURIComponent(archiveFile)}` : undefined,
      archiveSHA256,
    });
    console.log(`${packageId}\t${archiveFile}\t${archiveSHA256}`);
  }

  archives.sort((left, right) => left.packageName.localeCompare(right.packageName) || left.packageId.localeCompare(right.packageId));
  const rendered = `${JSON.stringify({ schemaVersion: 1, archives }, null, 2)}\n`;

  if (check) {
    const expectedPath = path.resolve(repoRoot, manifestPath);
    const existing = existsSync(expectedPath) ? await readFile(expectedPath, "utf8") : "";
    if (existing !== rendered) {
      console.error(`${manifestPath}\tstale`);
      process.exitCode = 1;
    } else {
      console.log(`${manifestPath}\tok`);
    }
  } else {
    await mkdir(path.dirname(path.resolve(repoRoot, manifestPath)), { recursive: true });
    await writeFile(path.resolve(repoRoot, manifestPath), rendered);
    console.log(`${manifestPath}\twrote ${archives.length} archives`);
  }
} finally {
  if (check) {
    await rm(actualOutputDir, { recursive: true, force: true });
    await rm(actualManifestPath, { force: true });
  }
}

function requiredArg(value: string | undefined, flag: string): string {
  if (!value || value.startsWith("--")) {
    console.error(`${flag} requires a value`);
    process.exit(2);
  }
  return value;
}

async function readManifest(packageRoot: string, packageId: string): Promise<Manifest> {
  const manifestPath = path.join(packageRoot, "riela-package.json");
  if (!existsSync(manifestPath)) {
    throw new Error(`${packageId}: missing riela-package.json`);
  }
  return JSON.parse(await readFile(manifestPath, "utf8")) as Manifest;
}

function validatePackageTree(packageRoot: string, packageId: string): void {
  const entries = readdirSync(packageRoot, { recursive: true, withFileTypes: true });
  for (const entry of entries) {
    if (entry.isSymbolicLink()) {
      throw new Error(`${packageId}: symbolic links are not allowed in package archives: ${entry.name}`);
    }
    if (!entry.isDirectory() && !entry.isFile()) {
      throw new Error(`${packageId}: unsupported archive entry type: ${entry.name}`);
    }
  }
}

function createZipArchive(packageRoot: string, archivePath: string): void {
  const result = spawnSync("zip", ["-qry", archivePath, "."], {
    cwd: packageRoot,
    encoding: "utf8",
  });
  if (result.status !== 0) {
    throw new Error([result.stderr, result.stdout].filter(Boolean).join("\n") || `zip failed with status ${result.status}`);
  }
}

function sha256File(filePath: string): string {
  const hash = createHash("sha256");
  hash.update(readFileSync(filePath));
  return hash.digest("hex");
}

function safeArchiveToken(value: string): string {
  const token = value
    .toLowerCase()
    .replace(/^@/, "")
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^[._-]+|[._-]+$/g, "");
  return token.length === 0 ? "package" : token;
}

function requiredString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`${label} must be a non-empty string`);
  }
  return value;
}
