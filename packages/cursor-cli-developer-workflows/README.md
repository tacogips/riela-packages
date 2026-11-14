# cursor-cli-developer-workflows

Meta package that pins the standard Cursor CLI developer workflow set in its dependencies and ships one Cursor dispatcher rule for choosing among them. Install the listed dependency packages together with this package.

- Package id: `cursor-cli-developer-workflows`
- Backends: `cursor-cli-agent`
- Workflows: `cursor-cli-developer-workflows`
- Skills: Cursor

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install cursor-cli-developer-workflows --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install cursor-cli-adversarial-implementation-review-loop --local-path /path/to/riela-packages
riela package install cursor-cli-deepdesign --local-path /path/to/riela-packages
riela package install cursor-cli-design-and-implement-review-loop --local-path /path/to/riela-packages
riela package install cursor-cli-fable-design-and-implement-review-loop --local-path /path/to/riela-packages
riela package install cursor-cli-impl-plan-completion-loop --local-path /path/to/riela-packages
riela package install cursor-cli-recent-change-quality-loop --local-path /path/to/riela-packages
riela package install cursor-cli-refactoring-divide-and-conquer --local-path /path/to/riela-packages
riela package install cursor-cli-refactoring-slice-review --local-path /path/to/riela-packages
riela package install cursor-cli-simple-work-package --local-path /path/to/riela-packages
riela package install cursor-cli-source-security-check-loop --local-path /path/to/riela-packages
riela package install cursor-cli-task-watchdog --local-path /path/to/riela-packages
riela package install cursor-cli-website-builder --local-path /path/to/riela-packages
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
