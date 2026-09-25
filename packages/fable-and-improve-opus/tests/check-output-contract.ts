import { strict as assert } from "node:assert";
import { isDeepStrictEqual } from "node:util";
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";
import { createHash } from "node:crypto";

const repo = process.cwd();
const bundle = resolve(repo, "packages/fable-and-improve-opus/workflows/fable-and-improve-opus");
const args = process.argv.slice(2);
const option = (name: string) => { const i = args.indexOf(name); return i < 0 ? undefined : args[i + 1]; };
const evidence = option("--evidence-root");
assert(evidence && evidence.startsWith("/"), "--evidence-root must be absolute");
assert(existsSync(bundle), "run from repository root");
mkdirSync(evidence, { recursive: true });
const original = JSON.parse(readFileSync(join(bundle, "mock-scenario.json"), "utf8"));
const workflow = JSON.parse(readFileSync(join(bundle, "workflow.json"), "utf8"));
let assertions = 0;
const check = (condition: unknown, message: string) => { assertions++; assert(condition, message); };
const hash = (path: string) => createHash("sha256").update(readFileSync(path)).digest("hex");
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value));
const cases = ["happy", "completion-revision", "planning-only", "checkpoint-empty-message", "commit-missing-message", "commit-empty-message", "knowledge-create", "knowledge-merge-archive", "knowledge-merge-no-archive", "knowledge-skip"] as const;
type Case = typeof cases[number];
function configure(name: Case, fixture: any, graph: any) {
  if (name === "completion-revision") {
    const revision = clone(fixture["step9-commit-message"]);
    revision.when.needs_revision = true;
    revision.payload = { ...revision.payload, accepted: false, decision: "needs-revision", needs_revision: true, findings: ["Complete remaining work."] };
    delete revision.payload.commitMessage; delete revision.payload.committedFiles; delete revision.payload.changeSummary;
    fixture["step9-commit-message"] = [revision, fixture["step9-commit-message"]];
  }
  if (name === "planning-only") fixture["step9-commit-message"].payload.workflowMode = "planning-only";
  if (name === "checkpoint-empty-message") fixture["plan-checkpoint"].payload.commitMessage = "";
  if (name === "commit-missing-message" || name === "commit-empty-message") {
    graph.entryStepId = "step9-commit-message";
    if (name === "commit-missing-message") delete fixture["step9-commit-message"].payload.commitMessage;
    else fixture["step9-commit-message"].payload.commitMessage = "";
  }
  if (name.startsWith("knowledge-")) {
    graph.entryStepId = "kb-self-review";
    const judge = fixture["kb-merge-judge"];
    if (name.includes("merge")) {
      Object.assign(judge.payload, { decision: "merge", create_knowledge: false, merge_knowledge: true, mergeNoteId: "mock-existing-note", mergedBody: "Merged durable note.", archive_note: name === "knowledge-merge-archive" });
      if (name === "knowledge-merge-archive") Object.assign(judge.payload, { archiveNoteId: "mock-old-note", archivedPointerBody: "See mock-existing-note." });
      else { delete judge.payload.archiveNoteId; delete judge.payload.archivedPointerBody; }
      fixture["kb-archive-brief"] = { provider: "scenario-mock", model: "claude-fable-5", when: { archive_note: name === "knowledge-merge-archive" }, payload: { archive_note: name === "knowledge-merge-archive", ...(name === "knowledge-merge-archive" ? { archiveNoteId: "mock-old-note", archivedPointerBody: "See mock-existing-note." } : {}) } };
    } else if (name === "knowledge-skip") {
      Object.assign(judge.payload, { decision: "skip", create_knowledge: false, merge_knowledge: false, archive_note: false });
      delete judge.payload.mergeNoteId; delete judge.payload.mergedBody;
      delete judge.payload.archiveNoteId; delete judge.payload.archivedPointerBody;
    } else {
      delete judge.payload.mergeNoteId; delete judge.payload.mergedBody;
      delete judge.payload.archiveNoteId; delete judge.payload.archivedPointerBody;
    }
  }
}
function inspect(name: Case, snapshot: any, log: string, exit: number) {
  const expectedFailure = ["checkpoint-empty-message", "commit-missing-message", "commit-empty-message"].includes(name);
  check((exit !== 0) === expectedFailure, `${name}: expected exit kind`);
  if (expectedFailure) {
    const producer = name === "checkpoint-empty-message" ? "plan-checkpoint" : "step9-commit-message";
    const consumer = name === "checkpoint-empty-message" ? "plan-git-commit" : "step10-git-commit";
    check(log.includes("validationRejected") && (log.includes("commitMessage") || (name === "commit-missing-message" && log.includes("anyOf branch"))), `${name}: producer schema rejection`);
    check(!snapshot || !snapshot.session.executions.some((x: any) => x.stepId === consumer), `${name}: consumer not reached`);
    return;
  }
  check(snapshot?.session?.status === "completed" && exit === 0, `${name}: completed session`);
  const records: any[] = snapshot.session.executions;
  const steps = records.map(x => x.stepId);
  const at = (id: string) => steps.indexOf(id);
  const ordered = (ids: string[]) => { for (let i = 1; i < ids.length; i++) check(at(ids[i - 1]) >= 0 && at(ids[i]) > at(ids[i - 1]), `${name}: ${ids[i - 1]} precedes ${ids[i]}`); };
  const payload = (id: string) => records.find(x => x.stepId === id)?.acceptedOutput?.payload;
  if (name === "happy" || name === "planning-only" || name === "completion-revision") {
    ordered(["fable-design", "plan-checkpoint", "plan-git-commit", "dispatch-plans", "reconcile-implementations", "integration-review", "fable-goal-review", "step9-commit-message", "step10-git-commit", "step11-git-push", "base-branch-integrate", "kb-self-review", "final-output"]);
    check(payload("step9-commit-message")?.commitMessage?.length > 0 || name === "completion-revision", `${name}: accepted commit message`);
    if (name === "completion-revision") {
      const outputs = records.filter(x => x.stepId === "step9-commit-message").map(x => x.acceptedOutput?.payload);
      check(outputs.length === 2 && outputs[0].decision === "needs-revision" && !Object.hasOwn(outputs[0], "commitMessage") && outputs[1].decision === "accepted", "revision then acceptance without revision commit fields");
      check(steps.filter(x => x === "fable-goal-review").length === 2 && steps.filter(x => x === "step10-git-commit").length === 1, "revision routes through goal review and commits once");
    }
    if (name === "planning-only") check(payload("step9-commit-message")?.workflowMode === "planning-only" && !steps.includes("kb-archive"), "planning-only skips archive");
  }
  if (name.startsWith("knowledge-")) {
    ordered(["kb-self-review", "kb-recall-related", "kb-merge-judge", "final-output"]);
    check(payload("kb-merge-judge")?.decision === name.split("-")[1], `${name}: actual judge decision`);
    check(steps.includes("kb-create") === (name === "knowledge-create"), `${name}: create path`);
    check(steps.includes("kb-merge") === name.includes("merge"), `${name}: merge path`);
    check(steps.includes("kb-archive") === (name === "knowledge-merge-archive"), `${name}: archive path`);
    if (name.includes("merge")) ordered(["kb-merge-judge", "kb-merge", "kb-archive-brief", ...(name === "knowledge-merge-archive" ? ["kb-archive"] : []), "final-output"]);
    if (name === "knowledge-skip") check(!steps.includes("kb-create") && !steps.includes("kb-merge") && !steps.includes("kb-archive"), "skip bypasses writes");
  }
}
// Static contract checks use the production bundle and committed graph baseline.
const agents = workflow.nodes.filter((n: any) => {
  if (!n.nodeFile) return false;
  const node = JSON.parse(readFileSync(join(bundle, n.nodeFile), "utf8"));
  return node.executionBackend === "claude-code-agent";
});
check(agents.length === 16, "16 sandbox consumers");
for (const n of agents) {
  const node = JSON.parse(readFileSync(join(bundle, n.nodeFile), "utf8"));
  check(["read-only", "workspace-write", "danger-full-access"].includes(node.agentSandbox), `${n.id}: supported sandbox`);
}
for (const id of ["fable-analysis", "kb-self-review", "kb-merge-judge", "kb-archive-brief", "opus-review", "fable-goal-review", "integration-review", "plan-checkpoint", "step9-commit-message", "dispatch-plans", "reconcile-implementations"]) {
  const node = JSON.parse(readFileSync(join(bundle, `nodes/node-${id}.json`), "utf8"));
  check(!!node.output?.jsonSchema && node.output?.maxValidationAttempts === 2, `${id}: schema and retry budget`);
}
const git = spawnSync("git", ["show", "b5cf79770a8c5c218057d470b0b1a68d16c52901:packages/fable-and-improve-opus/workflows/fable-and-improve-opus/workflow.json"], { cwd: repo, encoding: "utf8" });
check(git.status === 0 && git.stdout === readFileSync(join(bundle, "workflow.json"), "utf8"), "production graph/settings equal checkpoint");
const results: any[] = [];
for (const name of cases) {
  const dir = join(evidence, name);
  mkdirSync(dir, { recursive: true });
  const definitionDir = join(dir, "workflows");
  const target = join(definitionDir, "fable-and-improve-opus");
  cpSync(bundle, target, { recursive: true });
  const fixture = clone(original), graph = clone(workflow);
  configure(name, fixture, graph);
  writeFileSync(join(target, "mock-scenario.json"), JSON.stringify(fixture, null, 2) + "\n");
  writeFileSync(join(target, "workflow.json"), JSON.stringify(graph, null, 2) + "\n");
  const command = ["workflow", "run", "fable-and-improve-opus", "--workflow-definition-dir", definitionDir, "--mock-scenario", join(target, "mock-scenario.json"), "--session-store", join(dir, "sessions"), "--artifact-root", join(dir, "artifacts"), "--output", "json"];
  const run = spawnSync("riela", command, { cwd: repo, encoding: "utf8", maxBuffer: 50_000_000 });
  writeFileSync(join(dir, "stdout.log"), run.stdout || "");
  writeFileSync(join(dir, "stderr.log"), run.stderr || "");
  const log = (run.stdout || "") + (run.stderr || "");
  const out = JSON.parse(run.stdout || "{}");
  const snapshotPath = join(dir, "artifacts", out.sessionId || "fable-and-improve-opus-session-1", "runtime-snapshot.json");
  const snapshot = existsSync(snapshotPath) ? JSON.parse(readFileSync(snapshotPath, "utf8")) : null;
  inspect(name, snapshot, log, run.status ?? -1);
  if (snapshot) {
    for (const execution of snapshot.session.executions) {
      const response = fixture[execution.stepId];
      check(!!response, `${name}: mocked response exists for ${execution.stepId}`);
      const selected = Array.isArray(response) ? response[Math.min((execution.attempt ?? 1) - 1, response.length - 1)] : response;
      if (execution.status === "completed" && !Array.isArray(response)) {
        for (const [key, value] of Object.entries(selected.payload ?? {})) check(isDeepStrictEqual(execution.acceptedOutput?.payload?.[key], value), `${name}: consumed ${execution.stepId}.${key}`);
      }
    }
  }
  const item = { name, command: ["riela", ...command], cwd: repo, exitCode: run.status, sessionStatus: snapshot?.session?.status ?? out.status, nodeExecutions: snapshot?.session?.executions?.length ?? 0, stdoutLog: join(dir, "stdout.log"), stderrLog: join(dir, "stderr.log"), sourceHash: hash(join(target, "workflow.json")), fixtureHash: hash(join(target, "mock-scenario.json")) };
  writeFileSync(join(dir, "result.json"), JSON.stringify(item, null, 2));
  results.push(item);
  console.log(`${name}: ${item.sessionStatus}, exit ${run.status}, ${item.nodeExecutions} executions`);
}
const summary = { scenariosRun: results.length, scenariosPassed: results.length, failures: 0, assertions, reused: 0, newlyExecuted: results.length, results };
writeFileSync(join(evidence, "summary.json"), JSON.stringify(summary, null, 2));
console.log(`PASS ${results.length} scenarios, ${assertions} assertions, 0 failures; ${join(evidence, "summary.json")}`);
