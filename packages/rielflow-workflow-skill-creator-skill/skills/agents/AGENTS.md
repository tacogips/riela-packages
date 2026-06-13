# Rielflow Workflow Use Skill

Use this instruction when creating or updating packaged skills that teach agents
how to use a Rielflow workflow package.

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
- Cursor-only workflow: `skills/cursor/<skill-name>.mdc`
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

## Agent-Specific Workflow Variants

For packages that provide Codex, Claude Code, and Cursor CLI variants of the
same workflow, treat the Codex workflow as the source variant unless the package
explicitly documents another source. Claude Code and Cursor CLI variants should
normally inherit or extend the Codex variant through backend-specific
replacement and patch metadata, so the workflow content and behavior remain the
same except for agent names, backend identifiers, models, dependency workflow
ids, package ids, skill placement, and command examples.

Do not fork prompt text, node behavior, or workflow routing separately for
Claude Code or Cursor CLI unless the backend requires a real behavior
difference. When such a difference is required, document it in the variant so
future package maintainers do not assume the contents are still identical.

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
points validation and run commands at the right lookup mode, verifies Cursor
`.mdc` basename/name/H1 consistency when applicable, and includes digest refresh
instructions for changed packaged payloads.

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
