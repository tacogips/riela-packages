# Awesome Rielflow Packages

A curated package index for reusable Rielflow workflows and agent skills.

This repository is the default Rielflow package registry:

```text
https://github.com/tacogips/rielflow-packages
```

## Install

Search the registry:

```bash
rielflow package search "<keyword>" --refresh
```

Install a package into the current project:

```bash
rielflow package install <package-id>
```

Install a package for the current user:

```bash
rielflow package install <package-id> --user-scope
```

Inspect installed packages:

```bash
rielflow package list
rielflow package status <package-id>
```

## Packages

### Node Add-on Packages

- [release-note-node-addon](packages/release-note-node-addon) -
  Declarative node add-on package that installs `examples/release-note@1`, a
  reusable Codex worker template for drafting concise release notes.
- [greeting-node-addon](packages/greeting-node-addon) -
  Executable node add-on package that installs `examples/greeting-shell@1`, a
  reusable Bash command node template for jq-encoded JSON greetings.

### Native Runtime Example Workflows

- [greeting-container](packages/greeting-container) -
  Example workflow package with a native container node that builds a small
  Node.js image and outputs a greeting with the current datetime.
- [greeting-shell](packages/greeting-shell) -
  Example workflow package with a native Bash command node that outputs a
  greeting with the current datetime without using a container.

### Codex Agent Workflows

- [codex-deepdesign](packages/codex-deepdesign) -
  Creates or revises `design-docs/` specifications with one design author, a
  deep edge-case reviewer, and a broad integration reviewer. It loops back to
  the author until both reviewers report no high or middle findings, and it
  records provisional decisions when user confirmation would normally be
  required. `backend: codex-agent`; includes Codex skills.
- [codex-design-and-implement-review-loop](packages/codex-design-and-implement-review-loop) -
  Shared Codex workflow for issue resolution or planning-only design and
  implementation-plan handoff. It supports a sequential path, bounded
  feature-local fanout, implementation, review, documentation refresh, and
  commit-message preparation. `backend: codex-agent`; includes Codex skills.
- [codex-impl-plan-completion-loop](packages/codex-impl-plan-completion-loop) -
  Finds incomplete implementation plans under `impl-plans/active`, delegates
  each selected plan to `codex-design-and-implement-review-loop`, and repeats
  until no incomplete active plans remain. `backend: codex-agent`.
- [codex-recent-change-quality-loop](packages/codex-recent-change-quality-loop) -
  Reviews recent code changes, including uncommitted changes, delegates
  blocking findings to `codex-design-and-implement-review-loop`, and re-reviews
  until no high or medium findings remain. `backend: codex-agent`.
- [codex-source-security-check-loop](packages/codex-source-security-check-loop) -
  Runs deterministic source-code security checks, including secrets, optional
  `gitleaks`, static heuristics, dependency manifests, and supply-chain config,
  then triages findings with Codex and delegates high or medium fixes to
  `codex-design-and-implement-review-loop`. `backend: native-command,
  codex-agent`; includes Codex skills.
- [codex-simple-work-package](packages/codex-simple-work-package) -
  Lightweight workflow for small code or documentation changes when no
  dedicated workflow applies. It implements with Codex GPT-5.5 high effort,
  reviews the diff, and loops back only for high or middle findings.
  `backend: codex-agent`; includes Codex skills.
- [codex-task-watchdog](packages/codex-task-watchdog) -
  Runs a background task watcher for `./tasks/list.jsonl`, repeatedly polling
  for newly added active tasks, skipping while another task is running,
  dispatching dependency workflows by task kind, or executing ad hoc Codex work.
  `backend: codex-agent`; includes Codex skills.
- [codex-refactoring-divide-and-conquer](packages/codex-refactoring-divide-and-conquer) -
  Splits a codebase into package or processing-group slices, reviews slices
  concurrently, merges findings into a refactoring plan, implements bounded
  tasks, self-reviews, independently post-reviews, and loops until completion or
  accepted residual risk. `backend: codex-agent`; includes Codex skills.
- [codex-refactoring-slice-review](packages/codex-refactoring-slice-review) -
  Read-only review workflow for one codebase slice produced by
  `codex-refactoring-divide-and-conquer`, including duplicate-scavenge review
  when requested by the parent workflow. `backend: codex-agent`.

### Claude Code Agent Workflows

- [claude-code-design-and-implement-review-loop](packages/claude-code-design-and-implement-review-loop) -
  Shared Claude Code workflow for issue resolution or planning-only design and
  implementation-plan handoff. It supports a sequential path, bounded
  feature-local fanout, implementation, review, documentation refresh, and
  commit-message preparation. `backend: claude-code-agent`; includes Claude
  skills.
- [claude-code-impl-plan-completion-loop](packages/claude-code-impl-plan-completion-loop) -
  Finds incomplete implementation plans under `impl-plans/active`, delegates
  each selected plan to `claude-code-design-and-implement-review-loop`, and
  repeats until no incomplete active plans remain.
  `backend: claude-code-agent`.
- [claude-code-recent-change-quality-loop](packages/claude-code-recent-change-quality-loop) -
  Reviews recent code changes, including uncommitted changes, delegates
  blocking findings to `claude-code-design-and-implement-review-loop`, and
  re-reviews until no high or medium findings remain.
  `backend: claude-code-agent`.
- [claude-code-refactoring-divide-and-conquer](packages/claude-code-refactoring-divide-and-conquer) -
  Splits a codebase into package or processing-group slices, reviews slices
  concurrently, merges findings into a refactoring plan, implements bounded
  tasks, self-reviews, independently post-reviews, and loops until completion or
  accepted residual risk. `backend: claude-code-agent`; includes Claude skills.
- [claude-code-refactoring-slice-review](packages/claude-code-refactoring-slice-review) -
  Read-only review workflow for one codebase slice produced by
  `claude-code-refactoring-divide-and-conquer`, including duplicate-scavenge
  review when requested by the parent workflow.
  `backend: claude-code-agent`.
- [claude-code-worker-only-single-step](packages/claude-code-worker-only-single-step) -
  Minimal manager-less reference workflow that starts directly at one Claude
  Code worker step through explicit `entryStepId` authoring.
  `backend: claude-code-agent`; includes Claude skills.

### Skill Packages

- [rielflow-package-manager-skill](packages/rielflow-package-manager-skill) -
  Installs Codex and Claude skills for searching Rielflow package registries,
  installing packages into project or user scope, listing installed packages,
  updating packages, and removing packages.
- [rielflow-package-release-skill](packages/rielflow-package-release-skill) -
  Installs agent-generic, Codex, and Claude maintainer guidance for refreshing
  package digests, validating packaged workflows, and preparing registry
  releases.
- [rielflow-package-installer-skill](packages/rielflow-package-installer-skill) -
  Installs Codex and Claude bootstrap skills for installing
  `rielflow-package-manager-skill` from `tacogips/rielflow-packages`.
- [rielflow-temporary-workflow-skill](packages/rielflow-temporary-workflow-skill) -
  Installs Codex and Claude skills for creating and running temporary
  workflows from inline JSON or JSON files without project/user-scope
  installation.
- [rielflow-workflow-creator-skill](packages/rielflow-workflow-creator-skill) -
  Installs Codex and Claude skills for creating, modifying, validating, and
  running portable Rielflow workflow bundles.
- [rielflow-workflow-skill-creator-skill](packages/rielflow-workflow-skill-creator-skill) -
  Installs agent-generic, Codex, and Claude guidance for creating packaged
  skills that teach agents how to use Rielflow workflow packages.

## Package Summary

| Package | Type | Backend | Skills |
| --- | --- | --- | --- |
| [release-note-node-addon](packages/release-note-node-addon) | node-addon | `codex-agent` | - |
| [greeting-node-addon](packages/greeting-node-addon) | node-addon | `native-command` | - |
| [greeting-container](packages/greeting-container) | workflow | `native-container` | - |
| [greeting-shell](packages/greeting-shell) | workflow | `native-command` | - |
| [codex-deepdesign](packages/codex-deepdesign) | workflow | `codex-agent` | Codex |
| [codex-design-and-implement-review-loop](packages/codex-design-and-implement-review-loop) | workflow | `codex-agent` | Codex |
| [codex-impl-plan-completion-loop](packages/codex-impl-plan-completion-loop) | workflow | `codex-agent` | - |
| [codex-recent-change-quality-loop](packages/codex-recent-change-quality-loop) | workflow | `codex-agent` | - |
| [codex-source-security-check-loop](packages/codex-source-security-check-loop) | workflow | `native-command`, `codex-agent` | Codex |
| [codex-simple-work-package](packages/codex-simple-work-package) | workflow | `codex-agent` | Codex |
| [codex-task-watchdog](packages/codex-task-watchdog) | workflow | `codex-agent` | Codex |
| [codex-refactoring-divide-and-conquer](packages/codex-refactoring-divide-and-conquer) | workflow | `codex-agent` | Codex |
| [codex-refactoring-slice-review](packages/codex-refactoring-slice-review) | workflow | `codex-agent` | - |
| [claude-code-design-and-implement-review-loop](packages/claude-code-design-and-implement-review-loop) | workflow | `claude-code-agent` | Claude |
| [claude-code-impl-plan-completion-loop](packages/claude-code-impl-plan-completion-loop) | workflow | `claude-code-agent` | - |
| [claude-code-recent-change-quality-loop](packages/claude-code-recent-change-quality-loop) | workflow | `claude-code-agent` | - |
| [claude-code-refactoring-divide-and-conquer](packages/claude-code-refactoring-divide-and-conquer) | workflow | `claude-code-agent` | Claude |
| [claude-code-refactoring-slice-review](packages/claude-code-refactoring-slice-review) | workflow | `claude-code-agent` | - |
| [claude-code-worker-only-single-step](packages/claude-code-worker-only-single-step) | workflow | `claude-code-agent` | Claude |
| [rielflow-package-manager-skill](packages/rielflow-package-manager-skill) | skill | - | Codex, Claude |
| [rielflow-package-release-skill](packages/rielflow-package-release-skill) | skill | - | Agents, Codex, Claude |
| [rielflow-package-installer-skill](packages/rielflow-package-installer-skill) | skill | - | Codex, Claude |
| [rielflow-temporary-workflow-skill](packages/rielflow-temporary-workflow-skill) | skill | - | Codex, Claude |
| [rielflow-workflow-creator-skill](packages/rielflow-workflow-creator-skill) | skill | - | Codex, Claude |
| [rielflow-workflow-skill-creator-skill](packages/rielflow-workflow-skill-creator-skill) | skill | - | Agents, Codex, Claude |

## Package Layout

Each package directory can include:

- `rielflow-package.json` - package manifest consumed by the package manager.
- `workflows/<workflow-id>/workflow.json` - Rielflow workflow bundle.
- `skills/agents/AGENTS.md` - agent-generic project guidance projected to
  `AGENTS.md` for project-scope installs.
- `skills/codex/**/SKILL.md` - Codex skills projected by the package.
- `skills/claude/**/SKILL.md` - Claude skills projected by the package.
- `skills/cursor/*.mdc` - Cursor rules projected to `.cursor/rules/*.mdc`
  for project-scope installs.

Use backend-specific skill directories for workflow-specific usage skills:
Codex-only workflows use `skills/codex`, Claude Code-only workflows use
`skills/claude`, and Cursor-only workflows use `skills/cursor`. Invocable
agent-independent maintainer or package-management skills should include named
Codex and Claude skills; add `skills/agents/AGENTS.md` only when broad project
guidance should also be projected to root `AGENTS.md`.

Packages that call another workflow declare it in `dependencies` inside
`rielflow-package.json`; the package manager checks those out before validating
the caller workflow.
