---
name: codex-task-watchdog
description: Use when configuring, validating, starting, stopping, or inspecting the packaged codex-task-watchdog background task watcher.
user-invocable: true
---

# Codex Task Watchdog

Use this skill to run the packaged `codex-task-watchdog` workflow as a background
task watcher. The event server stays alive, a cron source triggers polling
passes, and each pass claims at most one newly added active task. After a task
completes, the workflow reviews the completed Codex log for reusable lessons,
creates or updates project-scope skills under `.agents/skills`, reviews those
skill changes, and commits the accepted queue and skill updates.

This is not an OS service registration flow. Do not install systemd units,
launchd plists, or login items unless the user explicitly asks for that.

## Default Layout

In the project that should own the task queue:

- workflow definition directory: `.riela/workflows`
- event root: `.riela-events`
- queue file: `./tasks/list.jsonl`

The `codex-task-watchdog` workflow must be installed or checked out under the workflow
definition directory together with its dependency workflows:

- `codex-design-and-implement-review-loop`
- `codex-deepdesign`
- `codex-recent-change-quality-loop`

The project should allow repository-local skills under `.agents/skills`; the
watchdog uses that directory for post-task skill extraction.

## Event Config

Create:

```text
.riela-events/sources/codex-task-watchdog-cron.json
.riela-events/bindings/codex-task-watchdog-cron-to-workflow.json
```

Source example:

```json
{
  "id": "codex-task-watchdog-cron",
  "kind": "cron",
  "schedule": "*/30 * * * * *",
  "timezone": "Asia/Tokyo"
}
```

Binding example:

```json
{
  "id": "codex-task-watchdog-cron-to-workflow",
  "sourceId": "codex-task-watchdog-cron",
  "workflowName": "codex-task-watchdog",
  "match": {
    "eventType": "cron.tick"
  },
  "inputMapping": {
    "mode": "template",
    "template": {
      "taskListPath": "./tasks/list.jsonl",
      "request": "Run one codex task watchdog polling pass.",
      "scheduledAt": "{{event.input.scheduledAt}}",
      "sourceId": "{{event.sourceId}}",
      "scheduleId": "{{event.input.scheduleId}}",
      "timezone": "{{event.input.timezone}}"
    },
    "mirrorToHumanInput": false
  },
  "execution": {
    "async": true,
    "dedupeWindowMs": 30000,
    "maxConcurrentPerKey": 1,
    "concurrencyKey": "codex-task-watchdog"
  }
}
```

## Validate

```bash
riela workflow validate codex-task-watchdog --workflow-definition-dir .riela/workflows
riela events validate --workflow-definition-dir .riela/workflows --event-root .riela-events
```

## Run In Background

Start the riela event server with `nohup` from the project directory:

```bash
mkdir -p .riela/logs
nohup riela events serve \
  --workflow-definition-dir .riela/workflows \
  --event-root .riela-events \
  > .riela/logs/codex-task-watchdog-events.log 2>&1 &
echo $! > .riela/logs/codex-task-watchdog-events.pid
```

Inspect:

```bash
tail -f .riela/logs/codex-task-watchdog-events.log
riela events list --event-root .riela-events --output json
```

Stop:

```bash
kill "$(cat .riela/logs/codex-task-watchdog-events.pid)"
rm .riela/logs/codex-task-watchdog-events.pid
```

## One-Shot Smoke Test

Use an emitted cron payload when you want to test without waiting for the
schedule:

```bash
riela events emit codex-task-watchdog-cron \
  --workflow-definition-dir .riela/workflows \
  --event-root .riela-events \
  --event-file payload.json \
  --output json
```
