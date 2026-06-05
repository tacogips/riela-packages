---
name: rielflow-workflow-skill
description: Use when creating or updating packaged skills that teach agents how to use a Rielflow workflow package, including agent-specific placement under skills/agents, skills/codex, skills/claude, or skills/cursor.
---

# Rielflow Workflow Skill

Use this skill when creating or updating packaged skills that teach agents how
to use a Rielflow workflow package.

This skill owns the user-facing skill payload, not the workflow bundle itself.
Use `rielflow-workflow` for `workflow.json`, node payloads, prompts, scripts,
add-ons, transitions, and workflow validation.

## Placement Rules

Use the package manager's vendor layout. Do not put Codex-only or Claude-only
workflow skills under `skills/agents`.

- Codex-only workflow: `skills/codex/<skill-name>/SKILL.md`
- Claude Code-only workflow: `skills/claude/<skill-name>/SKILL.md`
- Cursor-only workflow: `skills/cursor/<rule-name>.mdc`
- Mixed Codex and Claude workflow: create both Codex and Claude skills.
- Invocable agent-independent maintainer or package-management skill: create
  `skills/codex/<skill-name>/SKILL.md` and
  `skills/claude/<skill-name>/SKILL.md`; add `skills/agents/AGENTS.md` only
  when broad project guidance should also be projected to root `AGENTS.md`.

Project-scope projection paths are:

- `skills/agents/AGENTS.md` -> `AGENTS.md`
- `skills/codex/<name>/SKILL.md` -> `.codex/skills/<name>/SKILL.md`
- `skills/claude/<name>/SKILL.md` -> `.claude/skills/<name>/SKILL.md`
- `skills/cursor/<name>.mdc` -> `.cursor/rules/<name>.mdc`

## Usage Skill Content

Each workflow usage skill should include package id, workflow id, install/run
commands, required variables, expected outputs, scope rules, verification
commands, and digest refresh instructions.
