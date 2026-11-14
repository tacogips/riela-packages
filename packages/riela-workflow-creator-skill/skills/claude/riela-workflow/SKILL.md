---
name: riela-workflow
description: Use when creating, modifying, reviewing, or validating riela workflow bundles. Applies to step-addressed workflow.json authoring, node payload files, prompt files, built-in node add-ons, cross-workflow transitions, manager/worker routing, and portable workflows under a workflow root.
metadata:
  short-description: Create riela workflow bundles
---

# Riela Workflow

Use this skill to author portable riela workflow bundles that validate against the current implementation.

This skill owns the workflow bundle itself: `workflow.json`, node payloads,
prompts, scripts, containers, add-on usage, transitions, and validation. Do not
use it to design or package the user-facing skill that teaches agents how to run
the workflow. Use `riela-workflow-use-skill` for packaged workflow usage skills.

## Required Workflow

1. Determine the workflow root and workflow name. If unspecified, use a local workflow root such as `.riela/workflows` or `examples` only when that matches the repository convention.
2. Create or update `<workflow-root>/<workflow-name>/workflow.json`.
3. Create `nodes/node-<id>.json` files only for file-backed nodes.
4. Put long prompts in `prompts/*.md` and reference them with `promptTemplateFile`, `systemPromptTemplateFile`, or `sessionStartPromptTemplateFile`.
5. Self-review the authored bundle before validation. Check that the executable step graph reaches the intended work, node ids and node files line up, prompts and variables are workflow-relative, backends and models are valid, transitions use step ids, and the bundle avoids repo-specific absolute paths unless explicitly required.
6. Validate with the available riela command and the same lookup mode the workflow will use: `--workflow-definition-dir <workflow-root>` for unpacked bundles, default/project scope for project installs, or `--scope user` for user-scope installs. Do not assume `./riela` exists.

## Out Of Scope

- Do not create `skills/codex`, `skills/claude`, `skills/agents`, or
  `skills/cursor` package payloads from this skill unless the user explicitly
  asks to ignore the separation.
- Do not decide agent-specific skill projection from workflow backends here.
  Delegate that to `riela-workflow-use-skill`.

Read `references/workflow-format.md` when authoring anything beyond a one-step worker or when validation errors mention schema, steps, transitions, add-ons, node payloads, or legacy fields.

## Current Authored Model

Author step-addressed bundles only:

- `workflow.json.nodes[]` is a reusable node registry.
- `workflow.json.steps[]` is the executable graph.
- `entryStepId` always names a step.
- `managerStepId` is optional; when omitted and exactly one step has `role: "manager"`, the implementation infers it.
- Local routing, branching, loops, and cross-workflow calls belong in `steps[].transitions`.
- Do not author legacy top-level routing fields: `managerRuntimeId`, `managerNodeId`, `entryNodeId`, `subWorkflows`, `workflowCalls`, `subWorkflowConversations`, `edges`, `loops`, or `branching`.

## Minimal Patterns

Managed workflow:

```json
{
  "workflowId": "example-managed",
  "description": "Managed workflow with one manager and one worker step.",
  "defaults": {
    "maxLoopIterations": 3,
    "nodeTimeoutMs": 120000
  },
  "prompts": {
    "rielaPromptTemplate": "Coordinate {{workflowId}} and route work to the worker.",
    "workerSystemPromptTemplate": "Return concise business JSON for the next step."
  },
  "managerStepId": "manager",
  "entryStepId": "manager",
  "nodes": [
    { "id": "manager", "nodeFile": "nodes/node-manager.json" },
    { "id": "worker", "nodeFile": "nodes/node-worker.json" }
  ],
  "steps": [
    {
      "id": "manager",
      "nodeId": "manager",
      "role": "manager",
      "transitions": [{ "toStepId": "worker" }]
    },
    {
      "id": "worker",
      "nodeId": "worker",
      "role": "worker"
    }
  ]
}
```

Worker-only workflow:

```json
{
  "workflowId": "example-worker-only",
  "description": "Worker-only workflow with one explicit entry step.",
  "defaults": {
    "maxLoopIterations": 3,
    "nodeTimeoutMs": 120000
  },
  "entryStepId": "main-worker",
  "nodes": [
    { "id": "main-worker", "nodeFile": "nodes/node-main-worker.json" }
  ],
  "steps": [
    { "id": "main-worker", "nodeId": "main-worker", "role": "worker" }
  ]
}
```

Agent node payload:

```json
{
  "id": "worker",
  "description": "Performs the requested worker task.",
  "executionBackend": "codex-agent",
  "model": "gpt-5.5",
  "promptTemplateFile": "prompts/worker.md",
  "variables": {}
}
```

## Authoring Rules

- Node registry ids must match `^[a-z0-9][a-z0-9-]{1,63}$`.
- Each registry entry declares exactly one of `nodeFile` or `addon`.
- Manager steps must reference file-backed nodes; add-on-backed nodes are worker-only.
- Prefer DRY workflow composition over combined one-off nodes. If behavior can be expressed as reusable primitive nodes chained by `steps[].transitions`, author it that way; for example, model commit-and-push as a git commit step followed by a git push step instead of duplicating commit logic in a separate commit-and-push node.
- Agent nodes require `executionBackend`, backend-specific `model`, `promptTemplate` or `promptTemplateFile`, and `variables`.
- Valid `executionBackend` values are `codex-agent`, `claude-code-agent`, `official/openai-sdk`, and `official/anthropic-sdk`.
- Do not encode backend identifiers in `model`; `model` should be a provider/backend model name.
- Valid authored `nodeType` values are `agent`, `command`, `container`, and `user-action`. Do not author `nodeType: "addon"`.
- A cross-workflow transition uses `toWorkflowId`, `toStepId`, and `resumeStepId`; `resumeStepId` must name a step in the current workflow.
- A step may have at most one cross-workflow transition.

## Scope And Runner Portability

- Do not write workflow docs, expected results, prompts, or helper scripts that require `nix run ./riela`, `./riela`, or any repository-local riela checkout unless that checkout is explicitly part of the target repository contract.
- Prefer examples that start with `riela ...`; mention `bun run packages/riela/src/bin.ts ...` only as a source-checkout alternative.
- Preserve the workflow lookup mode in examples and verification notes:
  - packaged project install: `riela workflow validate <workflow-name>`
  - packaged user install: `riela workflow validate <workflow-name> --scope user`
  - direct workflow directory: `riela workflow validate <workflow-name> --workflow-definition-dir <workflow-root>`
- If documenting package-managed workflows, keep package commands separate from raw workflow checkout commands. `workflow checkout` can make a workflow runnable without creating a `package list` / `package status` record.

## Built-In Add-Ons

Use object form with explicit version:

```json
{
  "id": "reply",
  "addon": {
    "name": "riela/chat-reply-worker",
    "version": "1",
    "config": {
      "textTemplate": "Thanks {{event.actor.displayName}}.",
      "visibility": "public",
      "threadPolicy": "same-thread"
    }
  }
}
```

Current built-ins include `riela/chat-reply-worker`, `riela/codex-worker`, `riela/claude-code-worker`, `riela/x-gateway-read`, `riela/x-gateway`, `riela/mail-gateway-read`, `riela/mail-gateway`, `riela/git-commit`, and `riela/git-push`, all version `1`.

## External Portability

When creating workflows for users outside the riela repository:

- Avoid repo-specific absolute paths in workflow files.
- Keep node payload and prompt paths workflow-relative.
- Prefer `promptTemplateFile` for prompts users may edit.
- Include enough `description` fields for UI inspection and validation output to be understandable.
- If the riela CLI is not available, still produce the bundle but state that validation could not be run.
