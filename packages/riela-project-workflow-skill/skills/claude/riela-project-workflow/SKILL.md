---
name: riela-project-workflow
description: Use when requested work should first be converted into a project-scope Riela workflow and then executed through Riela. Applies to workflow-first implementation, review, refactoring, documentation, or maintenance tasks where no existing package workflow exactly fits, and to requests that explicitly say to work through a project-scope workflow.
metadata:
  short-description: Create and run project-scope Riela workflows
---

# Riela Project Workflow

Use this skill when the user wants the work shaped into a project-scope
Riela workflow before execution, or when the task explicitly requires a
workflow-first process.

## Apply This Skill When

- the user asks to create a workflow for the work before doing the work
- the user says to use a project-scope workflow, `.riela/workflows`, or
  Riela as the execution path
- the task is specific enough to encode as repeatable workflow steps, but no
  installed or packaged workflow is a closer match
- the work benefits from explicit workflow gates such as intake, plan,
  implementation, review, verification, and final output

## Do Not Apply This Skill When

- the user explicitly says not to use Riela or not to create a workflow
- an existing installed workflow package already exactly fits the task; run
  that workflow directly and do not create a duplicate project workflow
- the request is a tiny one-command answer or a local edit where workflow setup
  would be disproportionate
- the user asked for a temporary inline workflow; use
  `riela-temporary-workflow` instead
- the task is only to author a reusable workflow bundle without running the
  requested work; use `riela-workflow` instead

## Default Project-Scope Flow

1. Inspect the repository and current Riela inventory.
2. Choose an existing project/user/package workflow if one clearly matches.
3. Otherwise create a bounded workflow under:

```text
.riela/workflows/<workflow-id>/
  workflow.json
  nodes/
  prompts/
```

4. Validate the workflow with project-scope lookup.
5. Run the workflow with the user's task encoded in `workflowInput`.
6. Continue by following the workflow output and session state, not by doing
   unrelated manual work outside the workflow.
7. Report the workflow id, project-scope path, validation command, run command,
   changed files, verification, and remaining risks.

## Project Workflow Authoring Rules

- Use step-addressed `workflow.json` bundles.
- Keep workflow ids lowercase and filesystem safe, for example
  `project-task-<short-topic>`.
- Prefer `promptTemplateFile` for prompts longer than a few lines.
- Use `executionBackend: "claude-code-agent"` and
  `model: "claude-opus-4-8"` for Claude Code agent nodes.
- Include at least these steps for non-trivial work:
  `intake-or-plan`, `work`, `review`, and `workflow-output`.
- Add dedicated verification, security, migration, release, or documentation
  steps when the task requires them.
- Preserve unrelated dirty worktree changes. Do not stage, commit, push,
  delete, or broadly rewrite files unless the user requested that behavior or
  the generated workflow explicitly includes an accepted gate for it.
- Avoid machine-local absolute paths in workflow files. Use repository-relative
  paths and pass local details through `workflowInput` when needed.

Minimal Claude Code worker node:

```json
{
  "id": "work",
  "description": "Perform the requested project work.",
  "executionBackend": "claude-code-agent",
  "model": "claude-opus-4-8",
  "promptTemplateFile": "prompts/work.md",
  "variables": {}
}
```

## Commands

Inspect available workflows:

```bash
riela workflow list --scope project --output json
riela package list --scope project --output json
```

Validate the project workflow:

```bash
riela workflow validate <workflow-id> --scope project --output json
```

Run the project workflow:

```bash
riela workflow run <workflow-id> \
  --scope project \
  --variables '{"workflowInput":{"requestedWork":"Describe the requested work.","acceptanceCriteria":["Workflow output confirms completion."],"constraints":["Preserve unrelated dirty worktree changes."]}}' \
  --output json
```

If lookup cannot discover project scope, validate and run with the explicit
workflow root:

```bash
riela workflow validate <workflow-id> --workflow-definition-dir .riela/workflows --output json
riela workflow run <workflow-id> --workflow-definition-dir .riela/workflows --output json
```

## Expected Output

The final answer should include:

- workflow id and `.riela/workflows/<workflow-id>` path
- validation and run commands with pass/fail results
- session id or artifact location when Riela reports one
- changed files and verification evidence
- accepted residual risks or blocked workflow steps

## Package Maintenance

After changing this packaged skill or its install-check workflow, refresh its
manifest and validate the registry:

```bash
bun .agents/skills/riela-package-release/scripts/update-package-digests.ts riela-project-workflow-skill
task check
```
