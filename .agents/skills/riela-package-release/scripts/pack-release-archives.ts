#!/usr/bin/env bun
import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";

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

type ZipEntry = {
  absolutePath: string;
  archivePath: string;
  mode: number;
};

const crc32Table = Array.from({ length: 256 }, (_, index) => {
  let value = index;
  for (let bit = 0; bit < 8; bit += 1) {
    value = value & 1 ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
  }
  return value >>> 0;
});

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
  const entries = collectZipEntries(packageRoot);
  const fileParts: Buffer[] = [];
  const centralParts: Buffer[] = [];
  let offset = 0;

  for (const entry of entries) {
    const name = Buffer.from(entry.archivePath, "utf8");
    const content = readFileSync(entry.absolutePath);
    const crc = crc32(content);
    const localHeader = Buffer.alloc(30);
    localHeader.writeUInt32LE(0x04034b50, 0);
    localHeader.writeUInt16LE(20, 4);
    localHeader.writeUInt16LE(0x0800, 6);
    localHeader.writeUInt16LE(0, 8);
    localHeader.writeUInt16LE(0, 10);
    localHeader.writeUInt16LE(33, 12);
    localHeader.writeUInt32LE(crc, 14);
    localHeader.writeUInt32LE(content.length, 18);
    localHeader.writeUInt32LE(content.length, 22);
    localHeader.writeUInt16LE(name.length, 26);
    localHeader.writeUInt16LE(0, 28);
    fileParts.push(localHeader, name, content);

    const centralHeader = Buffer.alloc(46);
    centralHeader.writeUInt32LE(0x02014b50, 0);
    centralHeader.writeUInt16LE(0x031e, 4);
    centralHeader.writeUInt16LE(20, 6);
    centralHeader.writeUInt16LE(0x0800, 8);
    centralHeader.writeUInt16LE(0, 10);
    centralHeader.writeUInt16LE(0, 12);
    centralHeader.writeUInt16LE(33, 14);
    centralHeader.writeUInt32LE(crc, 16);
    centralHeader.writeUInt32LE(content.length, 20);
    centralHeader.writeUInt32LE(content.length, 24);
    centralHeader.writeUInt16LE(name.length, 28);
    centralHeader.writeUInt16LE(0, 30);
    centralHeader.writeUInt16LE(0, 32);
    centralHeader.writeUInt16LE(0, 34);
    centralHeader.writeUInt16LE(0, 36);
    centralHeader.writeUInt32LE(((entry.mode & 0xffff) << 16) >>> 0, 38);
    centralHeader.writeUInt32LE(offset, 42);
    centralParts.push(centralHeader, name);

    offset += localHeader.length + name.length + content.length;
  }

  const centralDirectoryOffset = offset;
  const centralDirectory = Buffer.concat(centralParts);
  offset += centralDirectory.length;

  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(0, 4);
  end.writeUInt16LE(0, 6);
  end.writeUInt16LE(entries.length, 8);
  end.writeUInt16LE(entries.length, 10);
  end.writeUInt32LE(centralDirectory.length, 12);
  end.writeUInt32LE(centralDirectoryOffset, 16);
  end.writeUInt16LE(0, 20);

  writeFileSync(archivePath, Buffer.concat([...fileParts, centralDirectory, end]));
}

function collectZipEntries(root: string): ZipEntry[] {
  const entries: ZipEntry[] = [];
  visit(root);
  return entries.sort((left, right) => left.archivePath.localeCompare(right.archivePath));

  function visit(directory: string): void {
    const children = readdirSync(directory, { withFileTypes: true })
      .sort((left, right) => left.name.localeCompare(right.name));
    for (const child of children) {
      const absolutePath = path.join(directory, child.name);
      if (child.isDirectory()) {
        visit(absolutePath);
        continue;
      }
      if (!child.isFile()) {
        continue;
      }
      const relativePath = path.relative(root, absolutePath).split(path.sep).join("/");
      if (!shouldArchivePath(relativePath)) {
        continue;
      }
      const mode = statSync(absolutePath).mode & 0o111 ? 0o100755 : 0o100644;
      entries.push({ absolutePath, archivePath: relativePath, mode });
    }
  }
}

function shouldArchivePath(relativePath: string): boolean {
  const segments = relativePath.split("/");
  if (segments.some((segment) => segment === "__pycache__" || segment === ".DS_Store")) {
    return false;
  }
  if (relativePath.endsWith(".pyc") || relativePath.endsWith(".pyo")) {
    return false;
  }
  return true;
}

function crc32(buffer: Buffer): number {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc = (crc >>> 8) ^ crc32Table[(crc ^ byte) & 0xff];
  }
  return (crc ^ 0xffffffff) >>> 0;
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
