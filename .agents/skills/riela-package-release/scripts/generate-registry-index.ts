#!/usr/bin/env bun
import { existsSync, readdirSync } from "node:fs";
import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";

type JsonObject = Record<string, unknown>;

type PackageDependency = {
  packageId: string;
  registry?: string;
  branch?: string;
  kind?: string;
  addons?: unknown[];
};

type Manifest = {
  name?: string;
  version?: string;
  kind?: string;
  title?: string;
  description?: string;
  tags?: string[];
  registry?: string;
  repository?: string;
  checksum?: string;
  checksumAlgorithm?: string;
  workflowDirectory?: string;
  workflow?: {
    title?: string;
    description?: string;
    tags?: string[];
    backends?: string[];
  };
  backends?: string[];
  dependencies?: unknown[];
  environmentVariables?: unknown[];
  addons?: unknown[];
  skills?: unknown[];
  skillDirectory?: string;
  integrity?: {
    digestAlgorithm?: string;
    digest?: string;
  };
};

type RegistryIndexPackage = {
  name: string;
  directory: string;
  archiveURL?: string;
  archiveSHA256?: string;
  version: string;
  kind: string;
  title?: string;
  description: string;
  tags: string[];
  registry?: string;
  repository?: string;
  workflow?: {
    directory?: string;
    title?: string;
    description?: string;
    tags: string[];
    backends: string[];
  };
  backends: string[];
  dependencies: PackageDependency[];
  requiredEnvironment: unknown[];
  addons: unknown[];
  skills: unknown[];
  skillDirectory?: string;
  checksum?: {
    algorithm: string;
    value: string;
  };
  integrity?: {
    digestAlgorithm: string;
    digest: string;
  };
};

type ArchiveManifest = {
  archives?: ArchiveManifestEntry[];
};

type ArchiveManifestEntry = {
  packageId?: string;
  packageName?: string;
  archiveURL?: string;
  archiveSHA256?: string;
};

const manifestFile = "riela-package.json";
const defaultOutput = "registry-index.json";
const registryId = "default";
const registryUrl = "https://github.com/tacogips/riela-packages";

const usage = `Usage:
  bun .agents/skills/riela-package-release/scripts/generate-registry-index.ts [--output <path>]
  bun .agents/skills/riela-package-release/scripts/generate-registry-index.ts --check [--output <path>]

Options:
  --check                  Verify the index is current without writing it.
  --output PATH            Write or check a custom index path. Defaults to registry-index.json.
  --archive-manifest PATH  Add archiveURL and archiveSHA256 pins from package-archives.json.
  --help                   Show this help.
`;

const args = process.argv.slice(2);
let check = false;
let outputPath = defaultOutput;
let archiveManifestPath: string | undefined;

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
  if (arg === "--output") {
    const value = args[index + 1];
    if (!value || value.startsWith("--")) {
      console.error("--output requires a path");
      process.exit(2);
    }
    outputPath = value;
    index += 1;
    continue;
  }
  if (arg === "--archive-manifest") {
    const value = args[index + 1];
    if (!value || value.startsWith("--")) {
      console.error("--archive-manifest requires a path");
      process.exit(2);
    }
    archiveManifestPath = value;
    index += 1;
    continue;
  }
  console.error(`unknown option: ${arg}`);
  console.error(usage);
  process.exit(2);
}

const repoRoot = process.cwd();
const packagesRoot = path.join(repoRoot, "packages");

if (!existsSync(packagesRoot)) {
  console.error(`Missing packages directory: ${packagesRoot}`);
  process.exit(2);
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is string => typeof item === "string");
}

function compareStrings(left: string, right: string): number {
  return left < right ? -1 : left > right ? 1 : 0;
}

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values.filter((value) => value.length > 0))).sort(compareStrings);
}

function compactObject<T extends JsonObject>(value: T): T {
  return Object.fromEntries(
    Object.entries(value).filter(([, entry]) => entry !== undefined),
  ) as T;
}

function normalizeDependencies(value: unknown): PackageDependency[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((dependency) => {
      if (typeof dependency === "string") {
        return { packageId: dependency };
      }
      if (!dependency || typeof dependency !== "object") {
        return undefined;
      }
      const object = dependency as JsonObject;
      const packageId = object.packageId;
      if (typeof packageId !== "string" || packageId.length === 0) {
        return undefined;
      }
      return compactObject({
        packageId,
        registry:
          typeof object.registry === "string" ? object.registry : undefined,
        branch: typeof object.branch === "string" ? object.branch : undefined,
        kind: typeof object.kind === "string" ? object.kind : undefined,
        addons: Array.isArray(object.addons) ? object.addons : undefined,
      });
    })
    .filter((dependency): dependency is PackageDependency => dependency !== undefined);
}

function normalizeManifest(
  manifest: Manifest,
  directoryName: string,
  archive: ArchiveManifestEntry | undefined,
): RegistryIndexPackage {
  if (!manifest.name || !manifest.version || !manifest.description) {
    throw new Error(`${directoryName}: manifest requires name, version, and description`);
  }

  const kind = manifest.kind ?? "workflow";
  if (kind !== "workflow" && kind !== "node-addon") {
    throw new Error(`${directoryName}: unsupported package kind ${kind}`);
  }

  const workflowTags = asStringArray(manifest.workflow?.tags);
  const workflowBackends = asStringArray(manifest.workflow?.backends);
  const tags = uniqueSorted([...asStringArray(manifest.tags), ...workflowTags]);
  const backends = uniqueSorted([...asStringArray(manifest.backends), ...workflowBackends]);
  const checksum =
    manifest.checksum && manifest.checksumAlgorithm
      ? {
          algorithm: manifest.checksumAlgorithm,
          value: manifest.checksum,
        }
      : undefined;
  const integrity =
    manifest.integrity?.digest && manifest.integrity.digestAlgorithm
      ? {
          digestAlgorithm: manifest.integrity.digestAlgorithm,
          digest: manifest.integrity.digest,
        }
      : undefined;

  return compactObject({
    name: manifest.name,
    directory: `packages/${directoryName}`,
    archiveURL: archive?.archiveURL,
    archiveSHA256: archive?.archiveSHA256,
    version: manifest.version,
    kind,
    title: manifest.title ?? manifest.workflow?.title,
    description: manifest.description,
    tags,
    registry: manifest.registry,
    repository: manifest.repository,
    workflow:
      manifest.workflowDirectory || manifest.workflow
        ? compactObject({
            directory: manifest.workflowDirectory,
            title: manifest.workflow?.title,
            description: manifest.workflow?.description,
            tags: workflowTags,
            backends: workflowBackends,
          })
        : undefined,
    backends,
    dependencies: normalizeDependencies(manifest.dependencies),
    requiredEnvironment: Array.isArray(manifest.environmentVariables)
      ? manifest.environmentVariables
      : [],
    addons: Array.isArray(manifest.addons) ? manifest.addons : [],
    skills: Array.isArray(manifest.skills) ? manifest.skills : [],
    skillDirectory: manifest.skillDirectory,
    checksum,
    integrity,
  });
}

const packageDirectories = readdirSync(packagesRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .filter((directoryName) =>
    existsSync(path.join(packagesRoot, directoryName, manifestFile)),
  )
  .sort(compareStrings);

const packages: RegistryIndexPackage[] = [];
const archivesByPackage = archiveManifestPath === undefined
  ? new Map<string, ArchiveManifestEntry>()
  : await loadArchiveManifest(path.resolve(repoRoot, archiveManifestPath));

for (const directoryName of packageDirectories) {
  const manifestPath = path.join(packagesRoot, directoryName, manifestFile);
  const manifest = JSON.parse(await readFile(manifestPath, "utf8")) as Manifest;
  const archive = archivesByPackage.get(directoryName) ?? (manifest.name ? archivesByPackage.get(manifest.name) : undefined);
  packages.push(normalizeManifest(manifest, directoryName, archive));
}

packages.sort((left, right) => {
  const byName = compareStrings(left.name, right.name);
  return byName === 0 ? compareStrings(left.directory, right.directory) : byName;
});

const index = {
  schemaVersion: 1,
  registry: {
    id: registryId,
    url: registryUrl,
  },
  packages,
};

const rendered = `${JSON.stringify(index, null, 2)}\n`;
const absoluteOutputPath = path.resolve(repoRoot, outputPath);

if (check) {
  if (!existsSync(absoluteOutputPath)) {
    console.error(`registry index missing: ${outputPath}`);
    process.exit(1);
  }
  const existing = await readFile(absoluteOutputPath, "utf8");
  if (existing !== rendered) {
    console.error(`registry index is stale: ${outputPath}`);
    process.exit(1);
  }
  console.log(`${outputPath}\tok`);
} else {
  await writeFile(absoluteOutputPath, rendered);
  console.log(`${outputPath}\twrote ${packages.length} packages`);
}

async function loadArchiveManifest(manifestPath: string): Promise<Map<string, ArchiveManifestEntry>> {
  if (!existsSync(manifestPath)) {
    throw new Error(`archive manifest missing: ${manifestPath}`);
  }
  const manifest = JSON.parse(await readFile(manifestPath, "utf8")) as ArchiveManifest;
  const archives = Array.isArray(manifest.archives) ? manifest.archives : [];
  const result = new Map<string, ArchiveManifestEntry>();
  for (const archive of archives) {
    if (!archive.archiveURL || !archive.archiveSHA256) {
      continue;
    }
    if (!/^sha256:[a-f0-9]{64}$/.test(archive.archiveSHA256)) {
      throw new Error(`invalid archiveSHA256 for ${archive.packageId ?? archive.packageName ?? "unknown"}`);
    }
    if (archive.packageId) {
      result.set(archive.packageId, archive);
    }
    if (archive.packageName) {
      result.set(archive.packageName, archive);
    }
  }
  return result;
}
