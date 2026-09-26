# cursor-cli-developer-workflows

Meta package that pins the standard Cursor CLI developer workflow set in its dependencies and ships one Cursor dispatcher rule for choosing among them. Install the listed dependency packages together with this package.

- Package id: `cursor-cli-developer-workflows`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-developer-workflows`
- Skills: Cursor

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-developer-workflows --source /path/to/riela-packages/packages/cursor-cli-developer-workflows
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install cursor-cli-adversarial-implementation-review-loop --source /path/to/riela-packages/packages/cursor-cli-adversarial-implementation-review-loop
riela package install cursor-cli-deepdesign --source /path/to/riela-packages/packages/cursor-cli-deepdesign
riela package install cursor-cli-design-and-implement-review-loop --source /path/to/riela-packages/packages/cursor-cli-design-and-implement-review-loop
riela package install cursor-cli-fable-design-and-implement-review-loop --source /path/to/riela-packages/packages/cursor-cli-fable-design-and-implement-review-loop
riela package install cursor-cli-impl-plan-completion-loop --source /path/to/riela-packages/packages/cursor-cli-impl-plan-completion-loop
riela package install cursor-cli-recent-change-quality-loop --source /path/to/riela-packages/packages/cursor-cli-recent-change-quality-loop
riela package install cursor-cli-refactoring-divide-and-conquer --source /path/to/riela-packages/packages/cursor-cli-refactoring-divide-and-conquer
riela package install cursor-cli-refactoring-slice-review --source /path/to/riela-packages/packages/cursor-cli-refactoring-slice-review
riela package install cursor-cli-simple-work-package --source /path/to/riela-packages/packages/cursor-cli-simple-work-package
riela package install cursor-cli-source-security-check-loop --source /path/to/riela-packages/packages/cursor-cli-source-security-check-loop
riela package install cursor-cli-task-watchdog --source /path/to/riela-packages/packages/cursor-cli-task-watchdog
riela package install cursor-cli-website-builder --source /path/to/riela-packages/packages/cursor-cli-website-builder
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect cursor-cli-developer-workflows --output json
riela workflow validate cursor-cli-developer-workflows
riela workflow run cursor-cli-developer-workflows --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
