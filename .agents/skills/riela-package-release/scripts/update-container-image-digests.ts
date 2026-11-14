#!/usr/bin/env bun
import { existsSync, readdirSync } from "node:fs";
import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";

type Addon = {
  name?: string;
  version?: string;
  sourcePath?: string;
  execution?: {
    kind?: string;
    image?: string;
    imageDigest?: string;
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

type Manifest = {
  name?: string;
  version?: string;
  kind?: string;
  addons?: Addon[];
  [key: string]: unknown;
};

type DigestEntry = {
  packageId: string;
  addonName: string;
  image: string;
  manifestPath: string;
  addonIndex: number;
};

const usage = `Usage:
  bun .agents/skills/riela-package-release/scripts/update-container-image-digests.ts [<package-id>...]
  bun .agents/skills/riela-package-release/scripts/update-container-image-digests.ts --all

Options:
  --all                   Update every container node add-on package.
  --digest-file <json>    Read image digest pins from JSON instead of querying GHCR.
                          Accepts {"image":"sha256:..."} or [{"image":"...","digest":"sha256:..."}].
  --check                 Fail if manifests are missing or stale instead of writing.
  --dry-run               Report changes without writing.
  --allow-missing         Skip images that cannot be resolved from the registry.
  --help                  Show this help.
`;

const args = process.argv.slice(2);
let all = false;
let check = false;
let dryRun = false;
let allowMissing = false;
let digestFile: string | undefined;
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
  if (arg === "--dry-run") {
    dryRun = true;
    continue;
  }
  if (arg === "--allow-missing") {
    allowMissing = true;
    continue;
  }
  if (arg === "--digest-file") {
    digestFile = args[index + 1];
    if (!digestFile || digestFile.startsWith("--")) {
      console.error("--digest-file requires a value");
      process.exit(2);
    }
    index += 1;
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
const manifestFile = "riela-package.json";
const manifestAccept = [
  "application/vnd.oci.image.index.v1+json",
  "application/vnd.oci.image.manifest.v1+json",
  "application/vnd.docker.distribution.manifest.list.v2+json",
  "application/vnd.docker.distribution.manifest.v2+json",
].join(", ");

if (!existsSync(packagesRoot)) {
  console.error(`Missing packages directory: ${packagesRoot}`);
  process.exit(2);
}

const selectedPackageIds = all
  ? readdirSync(packagesRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .filter((packageId) => existsSync(path.join(packagesRoot, packageId, manifestFile)))
      .sort()
  : packageIds;

const digestPins = digestFile === undefined
  ? new Map<string, string>()
  : parseDigestPins(JSON.parse(await readFile(path.resolve(digestFile), "utf8")));

let failed = false;
let changed = false;

for (const packageId of selectedPackageIds) {
  const manifestPath = path.join(packagesRoot, packageId, manifestFile);
  if (!existsSync(manifestPath)) {
    console.error(`${packageId}\tmissing ${manifestFile}`);
    failed = true;
    continue;
  }
  const manifest = JSON.parse(await readFile(manifestPath, "utf8")) as Manifest;
  const entries = containerDigestEntries(packageId, manifest, manifestPath);
  if (entries.length === 0) {
    console.log(`${packageId}\tno container images`);
    continue;
  }

  let packageChanged = false;
  for (const entry of entries) {
    let digest = digestPins.get(entry.image);
    if (digest === undefined) {
      try {
        digest = await resolveImageDigest(entry.image);
      } catch (error) {
        if (!allowMissing) {
          throw error;
        }
      }
    }
    if (digest === undefined) {
      const message = `${packageId}\tmissing remote digest for ${entry.image}`;
      if (allowMissing) {
        console.log(message);
        continue;
      }
      console.error(message);
      failed = true;
      continue;
    }
    validateDigest(digest, `${packageId}: ${entry.image}`);
    const current = manifest.addons?.[entry.addonIndex]?.execution?.imageDigest;
    if (current === digest) {
      console.log(`${packageId}\t${entry.addonName}\tok`);
      continue;
    }
    changed = true;
    packageChanged = true;
    const action = current === undefined ? "set" : "update";
    console.log(`${packageId}\t${entry.addonName}\t${action} imageDigest ${current ?? "-"} -> ${digest}`);
    if (!check && !dryRun) {
      manifest.addons![entry.addonIndex].execution!.imageDigest = digest;
    }
  }

  if (packageChanged && !check && !dryRun) {
    await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  }
}

if (check && changed) {
  failed = true;
}

process.exit(failed || (dryRun && changed) ? 1 : 0);

function containerDigestEntries(packageId: string, manifest: Manifest, manifestPath: string): DigestEntry[] {
  if (manifest.kind !== "node-addon" || !Array.isArray(manifest.addons)) {
    return [];
  }
  const entries: DigestEntry[] = [];
  for (const [addonIndex, addon] of manifest.addons.entries()) {
    if (addon.execution?.kind !== "container") {
      continue;
    }
    const image = requireString(addon.execution.image, `${packageId}: addons[${addonIndex}].execution.image`);
    entries.push({
      packageId,
      addonName: requireString(addon.name, `${packageId}: addons[${addonIndex}].name`),
      image,
      manifestPath,
      addonIndex,
    });
  }
  return entries;
}

function parseDigestPins(value: unknown): Map<string, string> {
  const pins = new Map<string, string>();
  if (Array.isArray(value)) {
    for (const [index, entry] of value.entries()) {
      if (!entry || typeof entry !== "object") {
        throw new Error(`digest-file[${index}] must be an object`);
      }
      const image = requireString((entry as { image?: unknown }).image, `digest-file[${index}].image`);
      const digest = requireString((entry as { digest?: unknown }).digest, `digest-file[${index}].digest`);
      validateDigest(digest, `digest-file[${index}].digest`);
      pins.set(image, digest);
    }
    return pins;
  }
  if (value && typeof value === "object") {
    for (const [image, digest] of Object.entries(value)) {
      const parsedDigest = requireString(digest, `digest-file.${image}`);
      validateDigest(parsedDigest, `digest-file.${image}`);
      pins.set(image, parsedDigest);
    }
    return pins;
  }
  throw new Error("digest-file must be an object or array");
}

async function resolveImageDigest(image: string): Promise<string | undefined> {
  const parsed = parseImageReference(image);
  let response = await fetchManifest(parsed);
  if (response.status === 401) {
    const authenticate = response.headers.get("www-authenticate");
    if (!authenticate) {
      return undefined;
    }
    const token = await fetchBearerToken(authenticate);
    response = await fetchManifest(parsed, token);
  }
  if (!response.ok) {
    return undefined;
  }
  return response.headers.get("docker-content-digest") ?? undefined;
}

function parseImageReference(image: string): { registry: string; repository: string; reference: string } {
  const atIndex = image.indexOf("@");
  const withoutDigest = atIndex >= 0 ? image.slice(0, atIndex) : image;
  const slashIndex = withoutDigest.indexOf("/");
  if (slashIndex < 0) {
    throw new Error(`image must include registry and repository: ${image}`);
  }
  const registry = withoutDigest.slice(0, slashIndex);
  const repositoryWithReference = withoutDigest.slice(slashIndex + 1);
  const colonIndex = repositoryWithReference.lastIndexOf(":");
  if (colonIndex < 0 || repositoryWithReference.slice(colonIndex + 1).includes("/")) {
    throw new Error(`image must include a tag reference: ${image}`);
  }
  return {
    registry,
    repository: repositoryWithReference.slice(0, colonIndex),
    reference: repositoryWithReference.slice(colonIndex + 1),
  };
}

async function fetchManifest(
  image: { registry: string; repository: string; reference: string },
  token?: string,
): Promise<Response> {
  const headers: Record<string, string> = { Accept: manifestAccept };
  if (token !== undefined) {
    headers.Authorization = `Bearer ${token}`;
  }
  return fetch(`https://${image.registry}/v2/${image.repository}/manifests/${image.reference}`, {
    method: "HEAD",
    headers,
  });
}

async function fetchBearerToken(header: string): Promise<string> {
  const challenge = parseAuthenticateHeader(header);
  const realm = requireString(challenge.realm, "WWW-Authenticate realm");
  const url = new URL(realm);
  for (const key of ["service", "scope"]) {
    if (challenge[key]) {
      url.searchParams.set(key, challenge[key]);
    }
  }
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`token request failed: HTTP ${response.status}`);
  }
  const payload = await response.json() as { token?: string; access_token?: string };
  return requireString(payload.token ?? payload.access_token, "token response token");
}

function parseAuthenticateHeader(header: string): Record<string, string> {
  const result: Record<string, string> = {};
  const bearer = header.replace(/^Bearer\s+/i, "");
  for (const part of bearer.matchAll(/([A-Za-z_]+)="([^"]*)"/g)) {
    result[part[1]] = part[2];
  }
  return result;
}

function requireString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`${label} must be a non-empty string`);
  }
  return value;
}

function validateDigest(value: string, label: string): void {
  if (!/^sha256:[a-f0-9]{64}$/.test(value)) {
    throw new Error(`${label} must be sha256:<64 lowercase hex>`);
  }
}
