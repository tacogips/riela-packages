#!/usr/bin/env bun
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";

type ArchiveRecord = {
  packageId?: string;
  archiveFile?: string;
  archiveURL?: string;
  archiveSHA256?: string;
};

type ArchiveManifest = {
  archives?: ArchiveRecord[];
};

type GitHubRelease = {
  html_url?: string;
  assets?: Array<{ name?: string; browser_download_url?: string }>;
};

const usage = `Usage:
  bun .agents/skills/riela-package-release/scripts/check-release-publication.ts [options]

Options:
  --repo <owner/name>          GitHub repository. Default: tacogips/riela-packages.
  --release-tag <tag>         Release tag. Default: registry-packages.
  --archive-manifest <path>   Local package archive manifest. Default: dist/package-archives.json.
  --help                      Show this help.
`;

const args = process.argv.slice(2);
let repo = process.env.GITHUB_REPOSITORY || "tacogips/riela-packages";
let releaseTag = "registry-packages";
let archiveManifest = "dist/package-archives.json";

for (let index = 0; index < args.length; index += 1) {
  const arg = args[index];
  if (arg === "--help" || arg === "-h") {
    console.log(usage);
    process.exit(0);
  }
  if (arg === "--repo") {
    repo = requiredValue(args, index, arg);
    index += 1;
    continue;
  }
  if (arg === "--release-tag") {
    releaseTag = requiredValue(args, index, arg);
    index += 1;
    continue;
  }
  if (arg === "--archive-manifest") {
    archiveManifest = requiredValue(args, index, arg);
    index += 1;
    continue;
  }
  console.error(`unknown option: ${arg}`);
  console.error(usage);
  process.exit(2);
}

const manifestPath = path.resolve(archiveManifest);
if (!existsSync(manifestPath)) {
  console.error(`missing archive manifest: ${archiveManifest}`);
  console.error("run `task package:generate-release-index` first");
  process.exit(2);
}

const manifest = JSON.parse(await readFile(manifestPath, "utf8")) as ArchiveManifest;
const archives = Array.isArray(manifest.archives) ? manifest.archives : [];
if (archives.length === 0) {
  console.error(`${archiveManifest} does not contain archives[]`);
  process.exit(2);
}

let release: GitHubRelease;
try {
  release = await fetchRelease(repo, releaseTag);
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
const assetNames = new Set((release.assets ?? []).map((asset) => asset.name).filter(isNonEmptyString));
const requiredAssets = [
  "package-archives.json",
  "registry-index.json",
  ...archives.map((archive) => requireString(archive.archiveFile, `${archive.packageId ?? "archive"}.archiveFile`)),
];

let failed = false;
for (const assetName of requiredAssets) {
  if (assetNames.has(assetName)) {
    console.log(`${assetName}\tok`);
  } else {
    console.error(`${assetName}\tmissing`);
    failed = true;
  }
}

for (const archive of archives) {
  const packageId = requireString(archive.packageId, "archives[].packageId");
  validateReleaseURL(
    requireString(archive.archiveURL, `${packageId}.archiveURL`),
    repo,
    releaseTag,
    requireString(archive.archiveFile, `${packageId}.archiveFile`),
  );
  validateSHA256(requireString(archive.archiveSHA256, `${packageId}.archiveSHA256`), packageId);
}

if (failed) {
  console.error(`release ${repo}@${releaseTag} is missing required package assets`);
  process.exit(1);
}

console.log(`release ${repo}@${releaseTag} published ${requiredAssets.length} required assets`);

function requiredValue(values: string[], index: number, option: string): string {
  const value = values[index + 1];
  if (!isNonEmptyString(value) || value.startsWith("--")) {
    console.error(`${option} requires a value`);
    process.exit(2);
  }
  return value;
}

async function fetchRelease(ownerRepo: string, tag: string): Promise<GitHubRelease> {
  const response = await fetch(`https://api.github.com/repos/${ownerRepo}/releases/tags/${tag}`, {
    headers: {
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (response.status === 404) {
    throw new Error(`release not found: ${ownerRepo}@${tag}`);
  }
  if (!response.ok) {
    throw new Error(`release lookup failed for ${ownerRepo}@${tag}: HTTP ${response.status}`);
  }
  return await response.json() as GitHubRelease;
}

function validateReleaseURL(value: string, ownerRepo: string, tag: string, archiveFile: string): void {
  const expected = `https://github.com/${ownerRepo}/releases/download/${tag}/${archiveFile}`;
  if (value !== expected) {
    throw new Error(`${archiveFile}.archiveURL mismatch: expected ${expected}, found ${value}`);
  }
}

function validateSHA256(value: string, label: string): void {
  if (!/^sha256:[a-f0-9]{64}$/.test(value)) {
    throw new Error(`${label}.archiveSHA256 must be sha256:<64 lowercase hex>`);
  }
}

function requireString(value: unknown, label: string): string {
  if (!isNonEmptyString(value)) {
    throw new Error(`${label} must be a non-empty string`);
  }
  return value;
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}
