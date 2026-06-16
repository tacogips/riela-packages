#!/usr/bin/env sh

set -eu

TASK_LIST_PATH="${TASK_LIST_PATH:-./tasks/list.jsonl}" \
TASK_RUN_ID="${TASK_RUN_ID:-}" \
TASK_EVENT_SCHEDULED_AT="${TASK_EVENT_SCHEDULED_AT:-}" \
TASK_EVENT_SOURCE_ID="${TASK_EVENT_SOURCE_ID:-}" \
bun -e '
const fs = require("fs");
const path = require("path");

const taskListPath = process.env.TASK_LIST_PATH?.trim() || "./tasks/list.jsonl";
const now = new Date().toISOString();

function emit(payload, when = {}) {
  process.stdout.write(`${JSON.stringify({ when, payload })}\n`);
}

function normalizeKind(kind) {
  const value = String(kind ?? "adhoc").trim().toLowerCase();
  if (["design-and-impl", "design_and_impl", "design-impl", "impl", "implement"].includes(value)) {
    return "design-and-impl";
  }
  if (["design-deepthin", "design-deepthink", "deepdesign", "deep-design", "design"].includes(value)) {
    return "deepdesign";
  }
  if (["review", "quality-review", "recent-change-review"].includes(value)) {
    return "review";
  }
  if (["adhoc", "ad-hoc", "codex", "codex-adhoc"].includes(value)) {
    return "adhoc";
  }
  return value;
}

function readTasks(filePath) {
  if (!fs.existsSync(filePath)) {
    return [];
  }
  const text = fs.readFileSync(filePath, "utf8");
  return text
    .split(/\r?\n/)
    .map((line, index) => ({ line, index }))
    .filter((entry) => entry.line.trim().length > 0)
    .map((entry) => {
      try {
        const task = JSON.parse(entry.line);
        return { task, index: entry.index };
      } catch (error) {
        throw new Error(`invalid JSONL at ${filePath}:${entry.index + 1}: ${error.message}`);
      }
    });
}

function writeTasks(filePath, rows) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  const temporaryPath = `${filePath}.${process.pid}.tmp`;
  fs.writeFileSync(
    temporaryPath,
    `${rows.map((row) => JSON.stringify(row.task)).join("\n")}${rows.length === 0 ? "" : "\n"}`,
  );
  fs.renameSync(temporaryPath, filePath);
}

const rows = readTasks(taskListPath);
const tasks = rows.map((row) => row.task);
const running = tasks.find((task) => task.status === "running");
if (running !== undefined) {
  emit(
    {
      action: "skip",
      reason: "running-task-exists",
      taskListPath,
      runningTaskId: running.id ?? null,
      runningTask: running,
      taskCount: tasks.length,
    },
    { skip: true },
  );
  process.exit(0);
}

if (tasks.length === 0) {
  emit(
    {
      action: "skip",
      reason: "task-list-empty-or-missing",
      taskListPath,
      taskCount: 0,
    },
    { skip: true },
  );
  process.exit(0);
}

if (tasks.every((task) => task.status === "done")) {
  emit(
    {
      action: "skip",
      reason: "all-tasks-done",
      taskListPath,
      taskCount: tasks.length,
    },
    { skip: true },
  );
  process.exit(0);
}

const activeRow = rows.find((row) => row.task.status === "active");
if (activeRow === undefined) {
  emit(
    {
      action: "skip",
      reason: "no-active-task",
      taskListPath,
      taskCount: tasks.length,
      statuses: tasks.map((task) => ({ id: task.id ?? null, status: task.status ?? null })),
    },
    { skip: true },
  );
  process.exit(0);
}

const originalTask = activeRow.task;
const kind = normalizeKind(originalTask.kind);
const supportedKinds = ["design-and-impl", "deepdesign", "review", "adhoc"];
const run = {
  id: process.env.TASK_RUN_ID || `${originalTask.id ?? "task"}:${now}`,
  sourceId: process.env.TASK_EVENT_SOURCE_ID || null,
  scheduledAt: process.env.TASK_EVENT_SCHEDULED_AT || null,
  claimedAt: now,
};

if (!supportedKinds.includes(kind)) {
  activeRow.task = {
    ...originalTask,
    kind,
    status: "failed",
    completedAt: now,
    attempts: Number.isFinite(Number(originalTask.attempts)) ? Number(originalTask.attempts) + 1 : 1,
    run,
    result: {
      status: "failed",
      reason: "unsupported-kind",
      supportedKinds,
      completedAt: now,
    },
  };
  writeTasks(taskListPath, rows);
  emit(
    {
      action: "unsupported",
      reason: "unsupported-kind",
      taskListPath,
      task: activeRow.task,
      originalTask,
      kind,
      supportedKinds,
    },
    { skip: false, unsupported: true },
  );
  process.exit(0);
}

activeRow.task = {
  ...originalTask,
  kind,
  status: "running",
  startedAt: now,
  attempts: Number.isFinite(Number(originalTask.attempts)) ? Number(originalTask.attempts) + 1 : 1,
  run,
};
writeTasks(taskListPath, rows);

const when = {
  skip: false,
  design_and_impl: kind === "design-and-impl",
  deepdesign: kind === "deepdesign",
  review: kind === "review",
  adhoc: kind === "adhoc",
  unsupported: false,
};

emit(
  {
    action: "claimed",
    taskListPath,
    task: activeRow.task,
    originalTask,
    kind,
    claimedAt: now,
    dispatch: when,
  },
  when,
);
'
