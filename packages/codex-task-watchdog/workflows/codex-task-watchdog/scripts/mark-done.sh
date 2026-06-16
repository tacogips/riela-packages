#!/usr/bin/env sh

set -eu

TASK_LIST_PATH="${TASK_LIST_PATH:-./tasks/list.jsonl}" \
TASK_EVENT_SCHEDULED_AT="${TASK_EVENT_SCHEDULED_AT:-}" \
bun -e '
const fs = require("fs");
const path = require("path");

const taskListPath = process.env.TASK_LIST_PATH?.trim() || "./tasks/list.jsonl";
const now = new Date().toISOString();

function emit(payload, when = {}) {
  process.stdout.write(`${JSON.stringify({ when, payload })}\n`);
}

function readTasks(filePath) {
  if (!fs.existsSync(filePath)) {
    return [];
  }
  return fs
    .readFileSync(filePath, "utf8")
    .split(/\r?\n/)
    .map((line, index) => ({ line, index }))
    .filter((entry) => entry.line.trim().length > 0)
    .map((entry) => {
      try {
        return { task: JSON.parse(entry.line), index: entry.index };
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
const runningRow = rows.find((row) => row.task.status === "running");
if (runningRow === undefined) {
  emit(
    {
      action: "skip",
      reason: "no-running-task",
      taskListPath,
      taskCount: rows.length,
    },
    { no_running_task: true },
  );
  process.exit(0);
}

const previousTask = runningRow.task;
runningRow.task = {
  ...previousTask,
  status: "done",
  completedAt: now,
  result: {
    status: "completed",
    completedAt: now,
    scheduledAt: process.env.TASK_EVENT_SCHEDULED_AT || null,
    note: "Task completed by codex-task-watchdog workflow. Inspect rielflow session status/export output and SQLite workflow_messages for full delegated workflow or adhoc output.",
  },
};
writeTasks(taskListPath, rows);

emit(
  {
    action: "marked-done",
    taskListPath,
    taskId: runningRow.task.id ?? null,
    previousStatus: previousTask.status,
    task: runningRow.task,
  },
  { task_done: true },
);
'
