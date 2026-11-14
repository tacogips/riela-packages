---
name: riela-workflow-use-skill
description: Use when creating or updating packaged skills that teach agents how to use a Riela workflow package, including agent-specific placement under skills/agents, skills/codex, skills/claude, or skills/cursor.
---

# Riela Workflow Use Skill

Use this skill when creating or updating packaged skills that teach agents how
to use a Riela workflow package.

This skill owns the user-facing skill payload, not the workflow bundle itself.
Use `riela-workflow` for `workflow.json`, node payloads, prompts, scripts,
add-ons, transitions, and workflow validation.

## Placement Rules

Use the package manager's vendor layout. Do not put Codex-only or Claude-only
workflow skills under `skills/agents`.

- Codex-only workflow: `skills/codex/<skill-name>/SKILL.md`
- Claude Code-only workflow: `skills/claude/<skill-name>/SKILL.md`
- Cursor-only workflow: `skills/cursor/<skill-name>.mdc`
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

User-scope projection paths are:

- `skills/codex/<name>/SKILL.md` -> `~/.codex/skills/<name>/SKILL.md`
- `skills/claude/<name>/SKILL.md` -> `~/.claude/skills/<name>/SKILL.md`
- `skills/cursor/<name>.mdc` -> `~/.cursor/skills/<name>/SKILL.md`

Agent-wide `skills/agents/AGENTS.md` is managed-only in user scope. Do not use
it as the only carrier for reusable named skills.

## Cursor Skill File Rules

For a Cursor package skill, the source file remains
`skills/cursor/<skill-name>.mdc` so project-scope installs can project it to a
Cursor rule. The same file is copied to `SKILL.md` for user-scope Cursor skills,
so author it in a form that needs no install-time rewrite:

- the file basename, frontmatter `name`, and first Markdown H1 must all equal
  the same `<skill-name>`
- use `# <skill-name>` as the first H1, not a title-cased display name
- include Cursor CLI-specific workflow ids, package ids, backend names, and
  command examples when the workflow is Cursor CLI-only

## Usage Skill Content

Each workflow usage skill should include package id, workflow id, install/run
commands, required variables, expected outputs, scope rules, verification
commands, and digest refresh instructions.

## Post-Authoring Self Review

Before finishing a workflow usage skill, self-review that it names the correct
package id and workflow id, uses the correct vendor placement, preserves
project/user scope behavior, documents required variables and expected outputs,
points validation and run commands at the right lookup mode, verifies Cursor
`.mdc` basename/name/H1 consistency when applicable, and includes digest refresh
instructions for changed packaged payloads.
