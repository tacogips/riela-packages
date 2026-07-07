#!/usr/bin/env bun
import { existsSync, readdirSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";

type JsonObject = Record<string, unknown>;

type Addon = {
  name?: string;
  version?: string;
  sourcePath?: string;
  contentDigest?: string;
  execution?: {
    kind?: string;
    containerfilePath?: string;
    image?: string;
    imageDigest?: string;
  };
};

type Manifest = {
  name?: string;
  version?: string;
  kind?: string;
  addons?: Addon[];
};

type ContainerImageEntry = {
  packageId: string;
  packageName: string;
  packageVersion: string;
  addonName: string;
  addonVersion: string;
  context: string;
  file: string;
  imageBase: string;
  image: string;
  expectedImage: string;
  contentDigest?: string;
  imageDigest?: string;
};

const usage = `Usage:
  bun .agents/skills/riela-package-release/scripts/container-image-matrix.ts [--format entries|matrix]
  bun .agents/skills/riela-package-release/scripts/container-image-matrix.ts --check

Options:
  --format entries  Print a JSON array of container image entries. Default.
  --format matrix   Print {"include":[...]} for GitHub Actions matrix use.
  --check           Verify every container add-on has a GHCR image and valid Containerfile.
  --help            Show this help.
`;

const args = process.argv.slice(2);
let format: "entries" | "matrix" = "entries";
let check = false;

for (let index = 0; index < args.length; index += 1) {
  const arg = args[index];
  if (arg === "--help" || arg === "-h") {
    console.log(usage);
    process.exit(0);
  }
  if (arg === "--check") {
    check = true;
    continue;
  }
  if (arg === "--format") {
    const value = args[index + 1];
    if (value !== "entries" && value !== "matrix") {
      console.error("--format requires entries or matrix");
      process.exit(2);
    }
    format = value;
    index += 1;
    continue;
  }
  console.error(`unknown option: ${arg}`);
  console.error(usage);
  process.exit(2);
}

const repoRoot = process.cwd();
const packagesRoot = path.join(repoRoot, "packages");
const owner = process.env.GITHUB_REPOSITORY_OWNER?.toLowerCase() || "tacogips";
const imageNamespace = `ghcr.io/${owner}/riela-packages`;

if (!existsSync(packagesRoot)) {
  console.error(`Missing packages directory: ${packagesRoot}`);
  process.exit(2);
}

function safeImageSegment(value: string): string {
  const normalized = value
    .toLowerCase()
    .replace(/^@/, "")
    .replace(/[^a-z0-9._/-]+/g, "-")
    .replace(/\/+/g, "-")
    .replace(/^[._-]+|[._-]+$/g, "");
  return normalized.length === 0 ? "addon" : normalized;
}

function packageImageBase(packageId: string): string {
  return `${imageNamespace}/${safeImageSegment(packageId)}`;
}

function packageImage(packageId: string, version: string): string {
  return `${packageImageBase(packageId)}:${version}`;
}

function requireString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`${label} must be a non-empty string`);
  }
  return value;
}

function packageRelative(...segments: string[]): string {
  return path.join(...segments).split(path.sep).join("/");
}

function compactObject<T extends JsonObject>(value: T): T {
  return Object.fromEntries(
    Object.entries(value).filter(([, entry]) => entry !== undefined),
  ) as T;
}

async function readManifest(packageId: string): Promise<Manifest> {
  const manifestPath = path.join(packagesRoot, packageId, "riela-package.json");
  return JSON.parse(await readFile(manifestPath, "utf8")) as Manifest;
}

async function collectEntries(): Promise<ContainerImageEntry[]> {
  const packageIds = readdirSync(packagesRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((packageId) =>
      existsSync(path.join(packagesRoot, packageId, "riela-package.json")),
    )
    .sort();

  const entries: ContainerImageEntry[] = [];
  for (const packageId of packageIds) {
    const manifest = await readManifest(packageId);
    if (manifest.kind !== "node-addon" || !Array.isArray(manifest.addons)) {
      continue;
    }
    const packageName = requireString(manifest.name, `${packageId}: name`);
    const packageVersion = requireString(manifest.version, `${packageId}: version`);
    for (const addon of manifest.addons) {
      if (addon.execution?.kind !== "container") {
        continue;
      }
      const addonName = requireString(addon.name, `${packageId}: add-on name`);
      const addonVersion = requireString(addon.version, `${packageId}: ${addonName}: version`);
      const sourcePath = requireString(addon.sourcePath, `${packageId}: ${addonName}: sourcePath`);
      const containerfilePath = requireString(
        addon.execution.containerfilePath,
        `${packageId}: ${addonName}: execution.containerfilePath`,
      );
      const context = packageRelative("packages", packageId, sourcePath);
      const file = packageRelative(context, containerfilePath);
      const imageBase = packageImageBase(packageId);
      const expectedImage = packageImage(packageId, packageVersion);
      entries.push(compactObject({
        packageId,
        packageName,
        packageVersion,
        addonName,
        addonVersion,
        context,
        file,
        imageBase,
        image: addon.execution.image ?? expectedImage,
        expectedImage,
        contentDigest: addon.contentDigest,
        imageDigest: addon.execution.imageDigest,
      }));
    }
  }
  return entries;
}

const entries = await collectEntries();

if (check) {
  let failed = false;
  for (const entry of entries) {
    let entryFailed = false;
    if (!existsSync(path.join(repoRoot, entry.context))) {
      console.error(`${entry.packageId}\tmissing context: ${entry.context}`);
      entryFailed = true;
    }
    if (!existsSync(path.join(repoRoot, entry.file))) {
      console.error(`${entry.packageId}\tmissing Containerfile: ${entry.file}`);
      entryFailed = true;
    }
    if (entry.image !== entry.expectedImage) {
      console.error(`${entry.packageId}\timage mismatch: expected ${entry.expectedImage}, found ${entry.image}`);
      entryFailed = true;
    }
    if (!entry.contentDigest?.startsWith("sha256:")) {
      console.error(`${entry.packageId}\tmissing sha256 contentDigest for ${entry.addonName}`);
      entryFailed = true;
    }
    console.log(`${entry.packageId}\t${entryFailed ? "failed" : "ok"}`);
    failed = failed || entryFailed;
  }
  process.exit(failed ? 1 : 0);
}

if (format === "matrix") {
  console.log(JSON.stringify({ include: entries }));
} else {
  console.log(JSON.stringify(entries, null, 2));
}
