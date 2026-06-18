---
name: riela-temporary-workflow
description: Use when creating, validating, or running temporary riela workflows from inline JSON or JSON files without installing a project/user-scope workflow bundle. Applies to --workflow-json, --workflow-json-file, embedded prompt-only payloads, temp workflow payload logs, and dry-run smoke checks.
metadata:
  short-description: Create and run temporary riela workflows
---

# Riela Temporary Workflow

Use this skill when the user wants a one-off riela workflow that can run
directly from a JSON string or JSON file, without creating or installing a
workflow bundle under project or user scope.

## Temporary Payload Shape

Temporary workflows use one JSON object with this shape:

```json
{
  "workflow": {
    "workflowId": "temporary-example",
    "description": "One-off workflow loaded from temporary JSON.",
    "defaults": {
      "maxLoopIterations": 3,
      "nodeTimeoutMs": 120000
    },
    "entryStepId": "main-worker",
    "nodes": [
      {
        "id": "main-worker",
        "nodeFile": "nodes/node-main-worker.json"
      }
    ],
    "steps": [
      {
        "id": "main-worker",
        "nodeId": "main-worker",
        "role": "worker"
      }
    ]
  },
  "nodePayloads": {
    "nodes/node-main-worker.json": {
      "id": "main-worker",
      "description": "Do the one-off task.",
      "executionBackend": "codex-agent",
      "model": "gpt-5.5",
      "promptTemplate": "Return one concise JSON object with the requested result.",
      "variables": {}
    }
  }
}
```

## Authoring Rules

- Use step-addressed `workflow.steps[]` and `workflow.nodes[]`.
- Keep every node payload embedded under `nodePayloads`.
- Match `workflow.nodes[].nodeFile` to a `nodePayloads` key.
- Embed prompt content directly in `promptTemplate`,
  `systemPromptTemplate`, `sessionStartPromptTemplate`, or prompt variants.
- Do not use `promptTemplateFile`, `systemPromptTemplateFile`,
  `sessionStartPromptTemplateFile`, `stepFile`, or unresolved external node
  files.
- Avoid absolute paths and machine-local values in reusable examples.
- Use `--dry-run` first when checking structure or demonstrating the workflow
  without calling an agent backend.

## Run Commands

Run from a JSON file:

```bash
riela workflow run \
  --workflow-json-file ./temp-workflow.json \
  --dry-run \
  --output json
```

Run from inline JSON:

```bash
temporary_workflow_json="$(cat ./temp-workflow.json)"

riela workflow run \
  --workflow-json "$temporary_workflow_json" \
  --dry-run \
  --output json
```

Inside the riela source checkout, use:

```bash
riela workflow run \
  --workflow-json-file ./temp-workflow.json \
  --dry-run \
  --output json
```

## Payload Log Verification

Temporary workflow runs persist the submitted and normalized payload under the
run artifact tree:

```bash
find ./tmp -path '*/temporary-workflow-payload/*' -type f | sort
```

Expected files:

- `temporary-workflow-payload/input.json`
- `temporary-workflow-payload/normalized.json`
- `temporary-workflow-payload/metadata.json`

The JSON run output should report:

- `source.scope: "temporary"`
- `source.input: "inline-json"` for `--workflow-json`
- `source.input: "json-file"` for `--workflow-json-file`

Normal project, user, explicit-directory, manifest, and registry workflow runs
do not create `temporary-workflow-payload/`.

## Recommended Creation Workflow

1. Draft the temporary JSON payload in a file first.
2. Run it with `--workflow-json-file ... --dry-run --output json`.
3. Confirm `source.scope` is `temporary` and `exitCode` is `0`.
4. Inspect `temporary-workflow-payload/metadata.json` for `schemaVersion` and
   `contentDigest`.
5. Convert to inline JSON only when the payload is small enough to be readable
   on the command line.
6. Remove `--dry-run` only when the selected backends and models should execute.
