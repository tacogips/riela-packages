import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve, join } from "node:path";

export function checkRequiredOutput(workflowId: string, nodeId: string, requiredField: string): void {
  const repo = resolve(import.meta.dir, "../../..");
  const catalog = process.env.RIELA_COMPAT_CATALOG;
  const evidence = process.env.RIELA_COMPAT_EVIDENCE_ROOT;
  const cli = process.env.RIELA_COMPAT_CLI;
  if (!catalog || !evidence || !cli) throw new Error("Set RIELA_COMPAT_CATALOG, RIELA_COMPAT_EVIDENCE_ROOT, and RIELA_COMPAT_CLI");
  const workflow = join(repo, "packages", workflowId, "workflows", workflowId);
  const node = JSON.parse(readFileSync(join(workflow, "nodes", `node-${nodeId}.json`), "utf8"));
  const schema = node.output?.jsonSchema;
  if (!schema?.required?.includes(requiredField)) throw new Error(`${nodeId} no longer requires ${requiredField}`);
  const fixture = JSON.parse(readFileSync(join(workflow, "mock-scenario.json"), "utf8"));
  const entries = Array.isArray(fixture[nodeId]) ? fixture[nodeId] : [fixture[nodeId]];
  if (!entries.length || entries.some((entry: unknown) => !entry || typeof entry !== "object")) throw new Error(`missing mock producer ${nodeId}`);
  for (const entry of entries) {
    const response = entry as Record<string, any>;
    const payload = response.payload ?? response.output?.payload;
    if (!payload || !Object.hasOwn(payload, requiredField)) throw new Error(`fixture lacks ${nodeId}.${requiredField}`);
    delete payload[requiredField];
  }
  const output = join(evidence, workflowId, nodeId);
  mkdirSync(output, { recursive: true });
  const mutatedFixture = join(output, "missing-required-field.json");
  writeFileSync(mutatedFixture, JSON.stringify(fixture, null, 2) + "\n");
  const cmd = [cli, "workflow", "run", workflowId, "--workflow-definition-dir", catalog,
    "--scope", "project", "--working-dir", repo, "--mock-scenario", mutatedFixture,
    "--session-store", join(output, "sessions"), "--artifact-root", join(output, "artifacts"), "--output", "json"];
  const run = Bun.spawnSync({ cmd, cwd: resolve(catalog, "../isolated-project"), env: process.env });
  const stdout = new TextDecoder().decode(run.stdout);
  const stderr = new TextDecoder().decode(run.stderr);
  writeFileSync(join(output, "run.log"), stdout + stderr);
  const result = JSON.parse(stdout);
  const rejected = run.exitCode !== 0 && result.status === "failed" &&
    String(result.error ?? "").includes("validationRejected") &&
    String(result.error ?? "").includes(requiredField);
  const receipt = { workflowId, nodeId, requiredField, command: cmd, exitCode: run.exitCode,
    rejected, status: result.status, error: result.error, log: join(output, "run.log") };
  writeFileSync(join(output, "receipt.json"), JSON.stringify(receipt, null, 2) + "\n");
  if (!rejected) throw new Error(JSON.stringify(receipt));
  console.log(JSON.stringify({ workflowId, testsRun: 1, testsPassed: 1, failureCount: 0, rejectedField: requiredField }));
}
