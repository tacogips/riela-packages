---
name: rielflow-workflow-use-skill
description: Use when creating or updating packaged skills that teach agents how to use a Rielflow workflow package, including agent-specific placement under skills/agents, skills/codex, skills/claude, or skills/cursor.
---

# Rielflow Workflow Use Skill

Use this skill when creating or updating packaged skills that teach agents how
to use a Rielflow workflow package.

This skill owns the user-facing skill payload, not the workflow bundle itself.
Use `rielflow-workflow` for `workflow.json`, node payloads, prompts, scripts,
add-ons, transitions, and workflow validation.

## Required Inputs

Before authoring a workflow usage skill, inspect:

- the package `rielflow-package.json`
- the workflow `workflow.json`
- all LLM node `executionBackend` values
- the expected user operation: run, monitor, resume, troubleshoot, maintain, or
  package-install

## Placement Rules

Use the package manager's vendor layout. Do not put Codex-only or Claude-only
workflow skills under `skills/agents`.

- Codex-only workflow: `skills/codex/<skill-name>/SKILL.md`
- Claude Code-only workflow: `skills/claude/<skill-name>/SKILL.md`
- Cursor-only workflow: `skills/cursor/<rule-name>.mdc`
- Mixed Codex and Claude workflow: create both Codex and Claude skills, each
  naming the backend-specific workflow id and runtime expectations.
- Invocable agent-independent maintainer or package-management skill: create
  `skills/codex/<skill-name>/SKILL.md` and
  `skills/claude/<skill-name>/SKILL.md`; add `skills/agents/AGENTS.md` only
  when broad project guidance should also be projected to root `AGENTS.md`.

Projection paths after project-scope install are:

- `skills/agents/AGENTS.md` -> `AGENTS.md`
- `skills/codex/<name>/SKILL.md` -> `.codex/skills/<name>/SKILL.md`
- `skills/claude/<name>/SKILL.md` -> `.claude/skills/<name>/SKILL.md`
- `skills/cursor/<name>.mdc` -> `.cursor/rules/<name>.mdc`

User-scope installs project Codex and Claude skills to user skill roots. Agent
and Cursor skills are managed-only in user scope in the current package manager.
Because `skills/agents/AGENTS.md` projects to root `AGENTS.md` in project scope,
do not use it as the only carrier for reusable named skills.

## Usage Skill Content

Each workflow usage skill should include:

- package id and workflow id
- default checkout/install command
- default run command with required `--variables`
- scope rules for project vs user installs
- workflow inputs and expected outputs
- when to use a more specific skill instead
- verification commands for package maintainers
- digest refresh instructions when packaged skill or workflow payload changes

Keep workflow execution backend names explicit. `codex-agent`,
`claude-code-agent`, and `cursor-cli-agent` are backend identifiers and should
not be generalized away in workflow usage instructions.

## Post-Authoring Self Review

Before finishing a workflow usage skill, self-review that it names the correct
package id and workflow id, uses the correct vendor placement, preserves
project/user scope behavior, documents required variables and expected outputs,
points validation and run commands at the right lookup mode, and includes digest
refresh instructions for changed packaged payloads.

## Coordination With Workflow Authoring

When both the workflow bundle and its usage skill are requested:

1. Use `rielflow-workflow` to create or update the workflow bundle.
2. Validate the workflow bundle.
3. Use this skill to create the package skill payload in the correct vendor
   directories.
4. Self-review the workflow usage skill.
5. Refresh `rielflow-package.json` digests.
6. Verify install JSON `skills[]` contains only the intended vendors and
   projection paths.
