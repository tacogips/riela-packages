# Awesome Riela Packages

A curated package index for reusable Riela workflows and agent skills.

This repository is the default Riela package registry:

```text
https://github.com/tacogips/riela-packages
```

## Install

Search the registry:

```bash
riela package search "<keyword>" --refresh
```

Install a package into the current project:

```bash
riela package install <package-id>
```

Install a package for the current user:

```bash
riela package install <package-id> --user-scope
```

Inspect installed packages:

```bash
riela package list
riela package status <package-id>
```

## Which Package Should I Install?

Riela installs workflows and skills at package granularity. A package can
also declare dependencies, so installing one package may install the workflows
and skills that it needs.

Use the package structure this way:

- Install a meta package when you want a standard toolset for an agent surface.
  Meta packages are install bundles and dispatcher-skill carriers; they do not
  replace the individual workflow packages.
- Install an individual workflow package when you want only one workflow, want a
  workflow as a dependency of another package, or are maintaining that workflow.
- Install a skill package when you only need agent guidance for package
  management or workflow authoring, not a developer workflow bundle.

Current developer workflow install pattern:

- Cursor CLI standard developer setup:
  install `cursor-cli-developer-workflows`. It depends on the standard
  `cursor-cli-*` developer workflows and projects one Cursor dispatcher rule,
  `riel-cursor-cli-developer-workflows`, that chooses among them.
- Codex setup:
  install the needed `codex-*` workflow packages directly, such as
  `codex-design-and-implement-review-loop`, `codex-simple-work-package`, or
  `codex-source-security-check-loop`. There is intentionally no Codex developer
  meta package yet.
- Claude Code setup:
  install the needed `claude-code-*` workflow packages directly, such as
  `claude-code-design-and-implement-review-loop`,
  `claude-code-simple-work-package`, or
  `claude-code-source-security-check-loop`. There is intentionally no Claude
  Code developer meta package yet.

This means a Cursor install can use one top-level package for the standard
developer workflow set, while Codex and Claude Code installs remain explicit
per-workflow installs for now. The individual Cursor packages remain available
for single-workflow use and for package dependencies.

## Packages

### Node Add-on Packages

- [release-note-node-addon](packages/release-note-node-addon) -
  Declarative node add-on package that installs `examples/release-note@1`, a
  reusable Codex worker template for drafting concise release notes.
- [greeting-node-addon](packages/greeting-node-addon) -
  Executable node add-on package that installs `examples/greeting-shell@1`, a
  reusable Bash command node template for jq-encoded JSON greetings.
- [youtube-mp4-download-addon](packages/youtube-mp4-download-addon) -
  Node add-on package that downloads a YouTube URL to an MP4 file using
  `yt-dlp`.
- [mp4-audio-extract-addon](packages/mp4-audio-extract-addon) -
  Node add-on package that extracts speech-ready FLAC audio from an MP4 file
  using `ffmpeg`.
- [google-speech-to-text-addon](packages/google-speech-to-text-addon) -
  Node add-on package that transcribes local audio with Google Cloud
  Speech-to-Text v1 long-running recognition; includes a Codex setup skill.

### Native Runtime Example Workflows

- [greeting-container](packages/greeting-container) -
  Example workflow package with a native container node that builds a small
  Node.js image and outputs a greeting with the current datetime.
- [greeting-shell](packages/greeting-shell) -
  Example workflow package with a native Bash command node that outputs a
  greeting with the current datetime without using a container.
- [youtube-mp4-to-text-workflow](packages/youtube-mp4-to-text-workflow) -
  Example workflow package that downloads a YouTube MP4, extracts speech-ready
  audio, and transcribes it with Google Speech-to-Text through node add-ons.

### Codex Agent Workflows

- [codex-deepdesign](packages/codex-deepdesign) -
  Creates or revises `design-docs/` specifications with one design author, a
  deep edge-case reviewer, a broad integration reviewer, and an adversarial
  failure-mode reviewer. It loops back to the author until all reviewers report
  no high or middle findings, and it records provisional decisions when user
  confirmation would normally be required. `backend: codex-agent`; includes
  Codex skills.
- [codex-adversarial-implementation-review-loop](packages/codex-adversarial-implementation-review-loop) -
  Runs a scoped implementation request, adversarially reviews the implemented
  result against explicit target paths and evidence, delegates blocking fixes,
  and repeats until no high or medium findings remain. `backend: codex-agent`;
  includes Codex skills.
- [codex-deep-creation](packages/codex-deep-creation) -
  Runs deep design, adversarial implementation-plan completion, and source
  security checks as one full creation workflow. `backend: codex-agent`;
  includes Codex skills.
- [codex-design-and-implement-review-loop](packages/codex-design-and-implement-review-loop) -
  Shared Codex workflow for issue resolution or planning-only design and
  implementation-plan handoff. It supports a sequential path, bounded
  feature-local fanout, implementation, review, documentation refresh, and
  commit-message preparation. `backend: codex-agent`; includes Codex skills.
- [codex-goal](packages/codex-goal) -
  Generic Codex GPT-5.5 workflow that actively investigates available Riela
  workflows at each step, creates and reviews a testable goal, creates and
  reviews an in-session plan without writing plan files, performs the work, may
  delegate to a more specific workflow when appropriate, and reviews whether the
  goal is achieved before looping back to work or planning. `backend:
  codex-agent`; includes Codex skills.
- [codex-impl-plan-completion-loop](packages/codex-impl-plan-completion-loop) -
  Finds incomplete implementation plans under `impl-plans/active`, delegates
  each selected plan to `codex-adversarial-implementation-review-loop`, and repeats
  until no incomplete active plans remain. `backend: codex-agent`.
- [codex-impl-plan-completion-review-loop](packages/codex-impl-plan-completion-review-loop) -
  Runs `codex-impl-plan-completion-loop` first, then runs
  `codex-recent-change-quality-loop` so completed implementation work is
  reviewed and improved before final output. `backend: codex-agent`; includes
  Codex skills.
- [codex-recent-change-quality-loop](packages/codex-recent-change-quality-loop) -
  Reviews recent code changes, including uncommitted changes, delegates
  blocking findings to `codex-design-and-implement-review-loop`, and re-reviews
  until no high or medium findings remain. `backend: codex-agent`.
- [codex-source-security-check-loop](packages/codex-source-security-check-loop) -
  Runs deterministic source-code security checks, including secrets, optional
  `gitleaks`, static heuristics, dependency manifests, and supply-chain config,
  then derives harness-style focus areas, triages and adversarially verifies
  findings with Codex, and delegates verified high or medium fixes to
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
  dispatching dependency workflows by task kind, executing ad hoc Codex work,
  mining completed task logs for project-scope skills, reviewing those skills,
  and committing accepted queue and skill changes.
  `backend: codex-agent`; includes Codex skills.
- [codex-website-builder](packages/codex-website-builder) -
  Builds and iterates SolidJS websites with Bun through separate Codex nodes for
  site design, pinned CSS/library selection, asset generation, implementation,
  Docker-contained Bun server operation, Playwright review, chat feedback
  routing, and git snapshot commits. `backend: codex-agent, native-command`;
  includes Codex skills.
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

These packages use `claude-code-agent`. The Codex-derived variants inherit the matching Codex workflow with `workflow.json` `extends`, then patch agent nodes to Claude Code Opus 4.8 and rewrite same-family workflow calls.

- [claude-code-deepdesign](packages/claude-code-deepdesign) -
  Create and iteratively review design-doc specifications with one Claude Code author, one deep edge-case reviewer, and one broad integration reviewer until no high or middle findings remain. `backend: claude-code-agent`; includes Claude skills.
- [claude-code-adversarial-implementation-review-loop](packages/claude-code-adversarial-implementation-review-loop) -
  Run a scoped Claude Code implementation request, adversarially review the implemented result, delegate blocking fixes, and repeat until no high or medium findings remain. `backend: claude-code-agent`.
- [claude-code-design-and-implement-review-loop](packages/claude-code-design-and-implement-review-loop) -
  Shared Claude Code workflow for issue resolution or planning-only design and implementation-plan handoff. The workflow owns both the sequential path and the bounded feature-local fanout path, then joins accepted plans before implementation or planning-only completion. `backend: claude-code-agent`; includes Claude skills.
- [claude-code-goal](packages/claude-code-goal) -
  Generic Claude Code Opus 4.8 workflow that actively investigates available
  Riela workflows at each step, creates and reviews a testable goal, creates
  and reviews an in-session plan without writing plan files, performs the work,
  may delegate to a more specific workflow when appropriate, and reviews whether
  the goal is achieved before looping back to work or planning. `backend:
  claude-code-agent`; includes Claude skills.
- [claude-code-impl-plan-completion-loop](packages/claude-code-impl-plan-completion-loop) -
  Find incomplete implementation plans under impl-plans/active, delegate each selected plan to claude-code-adversarial-implementation-review-loop, and repeat sequentially until no incomplete active plans remain. `backend: claude-code-agent`.
- [claude-code-impl-plan-completion-review-loop](packages/claude-code-impl-plan-completion-review-loop) -
  Runs `claude-code-impl-plan-completion-loop` first, then runs
  `claude-code-recent-change-quality-loop` so completed implementation work is
  reviewed and improved before final output. Uses Claude Code Opus 4.8.
  `backend: claude-code-agent`.
- [claude-code-recent-change-quality-loop](packages/claude-code-recent-change-quality-loop) -
  Review code changes introduced within a configurable recent time window, including uncommitted changes, and delegate any blocking findings into the design-and-implement workflow before re-reviewing until no high or mid findings remain. `backend: claude-code-agent`.
- [claude-code-refactoring-divide-and-conquer](packages/claude-code-refactoring-divide-and-conquer) -
  Divide the codebase into package or related processing-group slices, review slices concurrently, merge findings into a refactoring plan, implement one bounded task at a time, self-review, independently post-review, and loop until the plan is complete or only accepted residual risks remain. Duplicate-scavenge is an additive mode of this same workflow; detailed phase behavior lives in the step prompts. `backend: claude-code-agent`; includes Claude skills.
- [claude-code-refactoring-slice-review](packages/claude-code-refactoring-slice-review) -
  Read-only review workflow for one codebase slice produced by claude-code-refactoring-divide-and-conquer fanout, including duplicate-scavenge review when the parent workflow requests duplicate implementations or parallel custom implementations of the same concept. `backend: claude-code-agent`.
- [claude-code-simple-work-package](packages/claude-code-simple-work-package) -
  Lightweight Claude Code workflow for small code or documentation changes when no dedicated workflow applies. It implements with Claude Code Sonnet 4.5 high effort, reviews the diff, and loops back only for high or middle findings. `backend: claude-code-agent`; includes Claude skills.
- [claude-code-source-security-check-loop](packages/claude-code-source-security-check-loop) -
  Run deterministic source-code security checks, derive harness-style focus areas, triage and adversarially verify findings with Claude Code, delegate blocking fixes, and rescan until verified high and medium findings are resolved. `backend: claude-code-agent`; includes Claude skills.
- [claude-code-task-watchdog](packages/claude-code-task-watchdog) -
  Long-running Claude Code task watcher backed by ./tasks/list.jsonl, with cron/event polling, dependency workflow dispatch, ad hoc Claude Code execution, post-task skill mining, skill review, and commit. `backend: claude-code-agent`; includes Claude skills.
- [claude-code-website-builder](packages/claude-code-website-builder) -
  Event-ready Claude Code workflow that designs, assets, implements, runs Bun inside Docker, reviews, iterates, and snapshots SolidJS websites. `backend: claude-code-agent`; includes Claude skills.
- [claude-code-worker-only-single-step](packages/claude-code-worker-only-single-step) -
  Minimal manager-less reference workflow that starts directly at one worker step through explicit entryStepId authoring. `backend: claude-code-agent`; includes Claude skills.

### Cursor CLI Agent Workflows

These packages use `cursor-cli-agent`. Each one inherits the matching Codex workflow with `workflow.json` `extends`, then patches implementation steps to Composer 2.5, non-implementation agent steps to GPT-5.5, and rewrites same-family workflow calls.

- [cursor-cli-developer-workflows](packages/cursor-cli-developer-workflows) -
  Meta package that installs the standard Cursor CLI developer workflow set and
  one Cursor rule for choosing among design, implementation, simple work,
  implementation-plan completion, recent-change review, refactoring, security,
  task watchdog, and website workflows. Install this package when a Cursor
  environment should have the full standard developer workflow set available
  without separate per-workflow installs. `backend: cursor-cli-agent`; includes
  Cursor skills.
- [cursor-cli-deepdesign](packages/cursor-cli-deepdesign) -
  Create and iteratively review design-doc specifications with one Cursor CLI author, one deep edge-case reviewer, and one broad integration reviewer until no high or middle findings remain. `backend: cursor-cli-agent`; includes Cursor skills.
- [cursor-cli-adversarial-implementation-review-loop](packages/cursor-cli-adversarial-implementation-review-loop) -
  Run a scoped Cursor CLI implementation request, adversarially review the implemented result, delegate blocking fixes, and repeat until no high or medium findings remain. `backend: cursor-cli-agent`.
- [cursor-cli-design-and-implement-review-loop](packages/cursor-cli-design-and-implement-review-loop) -
  Shared Cursor CLI workflow for issue resolution or planning-only design and implementation-plan handoff. The workflow uses GPT-5.5 for design and review agent steps, uses Composer 2.5 for implementation, and owns both the sequential path and the bounded feature-local fanout path before implementation or planning-only completion. `backend: cursor-cli-agent`; includes Cursor skills.
- [cursor-cli-fable-design-and-implement-review-loop](packages/cursor-cli-fable-design-and-implement-review-loop) -
  Explicit Claude Fable 5 variant of the Cursor CLI implementation workflow. It uses Claude Fable 5 for review agent steps, Composer 2.5 for implementation, and Claude Opus 4.8 for design and other agent steps. The default implementation skill remains the GPT-5.5 plus Composer workflow unless the user explicitly requests the Fable variant. `backend: cursor-cli-agent`; includes Cursor skills.
- [cursor-cli-goal](packages/cursor-cli-goal) -
  Generic Cursor CLI workflow that actively investigates available Riela
  workflows at each step, creates and reviews a testable goal, creates and
  reviews an in-session plan without writing plan files, performs the work with
  Composer 2.5, uses GPT-5.5 for other agent steps, may delegate to a more
  specific workflow when appropriate, and reviews whether the goal is achieved
  before looping back to work or planning. `backend: cursor-cli-agent`; includes
  Cursor skills.
- [cursor-cli-hydra-codex-design-and-implement-review-loop](packages/cursor-cli-hydra-codex-design-and-implement-review-loop) -
  Explicit hydra Codex variant of the implementation workflow. It uses Codex GPT-5.5 for design, review, and all non-implementation agent steps, and Cursor Composer 2.5 for implementation. It is selected only when the user explicitly requests the hydra Codex workflow. `backend: codex-agent,cursor-cli-agent`; includes Cursor skills.
- [cursor-cli-hydra-claude-design-and-implement-review-loop](packages/cursor-cli-hydra-claude-design-and-implement-review-loop) -
  Explicit hydra Claude variant of the implementation workflow. It uses Claude Code Fable 5 for design and review agent steps, Cursor Composer 2.5 for implementation, and Claude Code Opus 4.8 for other agent steps. It is selected only when the user explicitly requests the hydra Claude workflow. `backend: claude-code-agent,cursor-cli-agent`; includes Cursor skills.
- [cursor-cli-impl-plan-completion-loop](packages/cursor-cli-impl-plan-completion-loop) -
  Find incomplete implementation plans under impl-plans/active, delegate each selected plan to cursor-cli-adversarial-implementation-review-loop, and repeat sequentially until no incomplete active plans remain. `backend: cursor-cli-agent`.
- [cursor-cli-impl-plan-completion-review-loop](packages/cursor-cli-impl-plan-completion-review-loop) -
  Runs `cursor-cli-impl-plan-completion-loop` first, then runs
  `cursor-cli-recent-change-quality-loop` so completed implementation work is
  reviewed and improved before final output. Uses GPT-5.5 for wrapper and
  review steps, while delegated implementation steps use Composer 2.5.
  `backend: cursor-cli-agent`.
- [cursor-cli-recent-change-quality-loop](packages/cursor-cli-recent-change-quality-loop) -
  Review code changes introduced within a configurable recent time window, including uncommitted changes, and delegate any blocking findings into the design-and-implement workflow before re-reviewing until no high or mid findings remain. `backend: cursor-cli-agent`.
- [cursor-cli-refactoring-divide-and-conquer](packages/cursor-cli-refactoring-divide-and-conquer) -
  Divide the codebase into package or related processing-group slices, review slices concurrently, merge findings into a refactoring plan, implement one bounded task at a time, self-review, independently post-review, and loop until the plan is complete or only accepted residual risks remain. Duplicate-scavenge is an additive mode of this same workflow; detailed phase behavior lives in the step prompts. `backend: cursor-cli-agent`; includes Cursor skills.
- [cursor-cli-refactoring-slice-review](packages/cursor-cli-refactoring-slice-review) -
  Read-only review workflow for one codebase slice produced by cursor-cli-refactoring-divide-and-conquer fanout, including duplicate-scavenge review when the parent workflow requests duplicate implementations or parallel custom implementations of the same concept. `backend: cursor-cli-agent`.
- [cursor-cli-simple-work-package](packages/cursor-cli-simple-work-package) -
  Lightweight Cursor CLI workflow for small code or documentation changes when no dedicated workflow applies. It implements with Cursor CLI Sonnet 4.5 high effort, reviews the diff, and loops back only for high or middle findings. `backend: cursor-cli-agent`; includes Cursor skills.
- [cursor-cli-source-security-check-loop](packages/cursor-cli-source-security-check-loop) -
  Run deterministic source-code security checks, derive harness-style focus areas, triage and adversarially verify findings with Cursor CLI, delegate blocking fixes, and rescan until verified high and medium findings are resolved. `backend: cursor-cli-agent`; includes Cursor skills.
- [cursor-cli-task-watchdog](packages/cursor-cli-task-watchdog) -
  Long-running Cursor CLI task watcher backed by ./tasks/list.jsonl, with cron/event polling, dependency workflow dispatch, ad hoc Cursor CLI execution, post-task skill mining, skill review, and commit. `backend: cursor-cli-agent`; includes Cursor skills.
- [cursor-cli-website-builder](packages/cursor-cli-website-builder) -
  Event-ready Cursor CLI workflow that designs, assets, implements, runs Bun inside Docker, reviews, iterates, and snapshots SolidJS websites. `backend: cursor-cli-agent`; includes Cursor skills.

### Skill Packages

- [riela-package-manager-skill](packages/riela-package-manager-skill) -
  Installs Codex and Claude skills for searching Riela package registries,
  installing packages into project or user scope, listing installed packages,
  updating packages, and removing packages.
- [riela-package-release-skill](packages/riela-package-release-skill) -
  Installs agent-generic, Codex, and Claude maintainer guidance for refreshing
  package digests, validating packaged workflows, and preparing registry
  releases.
- [riela-package-installer-skill](packages/riela-package-installer-skill) -
  Installs Codex and Claude bootstrap skills for installing
  `riela-package-manager-skill` from `tacogips/riela-packages`.
- [riela-temporary-workflow-skill](packages/riela-temporary-workflow-skill) -
  Installs Codex and Claude skills for creating and running temporary
  workflows from inline JSON or JSON files without project/user-scope
  installation.
- [riela-project-workflow-skill](packages/riela-project-workflow-skill) -
  Installs Codex, Claude, and Cursor guidance for turning requested work into a
  project-scope Riela workflow and then executing that workflow.
- [riela-workflow-creator-skill](packages/riela-workflow-creator-skill) -
  Installs Codex and Claude skills for creating, modifying, validating, and
  running portable Riela workflow bundles.
- [riela-workflow-skill-creator-skill](packages/riela-workflow-skill-creator-skill) -
  Installs agent-generic, Codex, and Claude guidance for creating packaged
  skills that teach agents how to use Riela workflow packages.

## Package Summary

| Package | Type | Backend | Skills |
| --- | --- | --- | --- |
| [release-note-node-addon](packages/release-note-node-addon) | node-addon | `codex-agent` | - |
| [greeting-node-addon](packages/greeting-node-addon) | node-addon | `native-command` | - |
| [youtube-mp4-download-addon](packages/youtube-mp4-download-addon) | node-addon | `native-command` | - |
| [mp4-audio-extract-addon](packages/mp4-audio-extract-addon) | node-addon | `native-command` | - |
| [google-speech-to-text-addon](packages/google-speech-to-text-addon) | node-addon | `native-command` | Codex |
| [greeting-container](packages/greeting-container) | workflow | `native-container` | - |
| [greeting-shell](packages/greeting-shell) | workflow | `native-command` | - |
| [youtube-mp4-to-text-workflow](packages/youtube-mp4-to-text-workflow) | workflow | `native-command` | - |
| [codex-adversarial-implementation-review-loop](packages/codex-adversarial-implementation-review-loop) | workflow | `codex-agent` | Codex |
| [codex-deep-creation](packages/codex-deep-creation) | workflow | `codex-agent` | Codex |
| [codex-deepdesign](packages/codex-deepdesign) | workflow | `codex-agent` | Codex |
| [codex-design-and-implement-review-loop](packages/codex-design-and-implement-review-loop) | workflow | `codex-agent` | Codex |
| [codex-impl-plan-completion-loop](packages/codex-impl-plan-completion-loop) | workflow | `codex-agent` | - |
| [codex-impl-plan-completion-review-loop](packages/codex-impl-plan-completion-review-loop) | workflow | `codex-agent` | Codex |
| [codex-recent-change-quality-loop](packages/codex-recent-change-quality-loop) | workflow | `codex-agent` | - |
| [codex-refactoring-divide-and-conquer](packages/codex-refactoring-divide-and-conquer) | workflow | `codex-agent` | Codex |
| [codex-refactoring-slice-review](packages/codex-refactoring-slice-review) | workflow | `codex-agent` | - |
| [codex-simple-work-package](packages/codex-simple-work-package) | workflow | `codex-agent` | Codex |
| [codex-source-security-check-loop](packages/codex-source-security-check-loop) | workflow | `native-command`, `codex-agent` | Codex |
| [codex-task-watchdog](packages/codex-task-watchdog) | workflow | `codex-agent` | Codex |
| [codex-website-builder](packages/codex-website-builder) | workflow | `codex-agent`, `native-command` | Codex |
| [claude-code-adversarial-implementation-review-loop](packages/claude-code-adversarial-implementation-review-loop) | workflow | `claude-code-agent` | - |
| [claude-code-deepdesign](packages/claude-code-deepdesign) | workflow | `claude-code-agent` | Claude |
| [claude-code-design-and-implement-review-loop](packages/claude-code-design-and-implement-review-loop) | workflow | `claude-code-agent` | Claude |
| [claude-code-impl-plan-completion-loop](packages/claude-code-impl-plan-completion-loop) | workflow | `claude-code-agent` | - |
| [claude-code-impl-plan-completion-review-loop](packages/claude-code-impl-plan-completion-review-loop) | workflow | `claude-code-agent` | - |
| [claude-code-recent-change-quality-loop](packages/claude-code-recent-change-quality-loop) | workflow | `claude-code-agent` | - |
| [claude-code-refactoring-divide-and-conquer](packages/claude-code-refactoring-divide-and-conquer) | workflow | `claude-code-agent` | Claude |
| [claude-code-refactoring-slice-review](packages/claude-code-refactoring-slice-review) | workflow | `claude-code-agent` | - |
| [claude-code-simple-work-package](packages/claude-code-simple-work-package) | workflow | `claude-code-agent` | Claude |
| [claude-code-source-security-check-loop](packages/claude-code-source-security-check-loop) | workflow | `claude-code-agent` | Claude |
| [claude-code-task-watchdog](packages/claude-code-task-watchdog) | workflow | `claude-code-agent` | Claude |
| [claude-code-website-builder](packages/claude-code-website-builder) | workflow | `claude-code-agent` | Claude |
| [claude-code-worker-only-single-step](packages/claude-code-worker-only-single-step) | workflow | `claude-code-agent` | Claude |
| [cursor-cli-adversarial-implementation-review-loop](packages/cursor-cli-adversarial-implementation-review-loop) | workflow | `cursor-cli-agent` | - |
| [cursor-cli-deepdesign](packages/cursor-cli-deepdesign) | workflow | `cursor-cli-agent` | Cursor |
| [cursor-cli-design-and-implement-review-loop](packages/cursor-cli-design-and-implement-review-loop) | workflow | `cursor-cli-agent` | Cursor |
| [cursor-cli-impl-plan-completion-loop](packages/cursor-cli-impl-plan-completion-loop) | workflow | `cursor-cli-agent` | - |
| [cursor-cli-impl-plan-completion-review-loop](packages/cursor-cli-impl-plan-completion-review-loop) | workflow | `cursor-cli-agent` | - |
| [cursor-cli-recent-change-quality-loop](packages/cursor-cli-recent-change-quality-loop) | workflow | `cursor-cli-agent` | - |
| [cursor-cli-refactoring-divide-and-conquer](packages/cursor-cli-refactoring-divide-and-conquer) | workflow | `cursor-cli-agent` | Cursor |
| [cursor-cli-refactoring-slice-review](packages/cursor-cli-refactoring-slice-review) | workflow | `cursor-cli-agent` | - |
| [cursor-cli-simple-work-package](packages/cursor-cli-simple-work-package) | workflow | `cursor-cli-agent` | Cursor |
| [cursor-cli-source-security-check-loop](packages/cursor-cli-source-security-check-loop) | workflow | `cursor-cli-agent` | Cursor |
| [cursor-cli-task-watchdog](packages/cursor-cli-task-watchdog) | workflow | `cursor-cli-agent` | Cursor |
| [cursor-cli-website-builder](packages/cursor-cli-website-builder) | workflow | `cursor-cli-agent` | Cursor |
| [riela-package-installer-skill](packages/riela-package-installer-skill) | skill | - | Codex, Claude |
| [riela-package-manager-skill](packages/riela-package-manager-skill) | skill | - | Codex, Claude |
| [riela-package-release-skill](packages/riela-package-release-skill) | skill | - | Agents, Codex, Claude |
| [riela-project-workflow-skill](packages/riela-project-workflow-skill) | skill | - | Codex, Claude, Cursor |
| [riela-temporary-workflow-skill](packages/riela-temporary-workflow-skill) | skill | - | Codex, Claude |
| [riela-workflow-creator-skill](packages/riela-workflow-creator-skill) | skill | - | Codex, Claude |
| [riela-workflow-skill-creator-skill](packages/riela-workflow-skill-creator-skill) | skill | - | Agents, Codex, Claude |

## Package Layout

Each package directory can include:

- `riela-package.json` - package manifest consumed by the package manager.
- `workflows/<workflow-id>/workflow.json` - Riela workflow bundle.
- `skills/agents/AGENTS.md` - agent-generic project guidance projected to
  `AGENTS.md` for project-scope installs.
- `skills/codex/**/SKILL.md` - Codex skills projected by the package.
- `skills/claude/**/SKILL.md` - Claude skills projected by the package.
- `skills/cursor/*.mdc` - Cursor rules projected to `.cursor/rules/*.mdc`
  for project-scope installs.

Package directories should use filesystem-safe names under `packages/`.
Registry-visible package ids live in `riela-package.json.name` and may be
unscoped, such as `greeting-node-addon`, or scoped, such as
`@tacogips/youtube-mp4-download-addon`. Prefer scoped package ids for
third-party or personal registries. Node add-on package entries use a separate
add-on namespace in `addons[].name`, such as `tacogips/youtube-mp4-download`;
the `riela/` add-on namespace is reserved for built-ins.

Use backend-specific skill directories for workflow-specific usage skills:
Codex-only workflows use `skills/codex`, Claude Code-only workflows use
`skills/claude`, and Cursor-only workflows use `skills/cursor`. Invocable
agent-independent maintainer or package-management skills should include named
Codex and Claude skills; add `skills/agents/AGENTS.md` only when broad project
guidance should also be projected to root `AGENTS.md`.

Packages that call another workflow declare it in `dependencies` inside
`riela-package.json`; the package manager checks those out before validating
the caller workflow.
