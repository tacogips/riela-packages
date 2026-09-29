# claude-code-design-and-implement-review-loop

Single-author design and planning followed by native shared-branch implementation/review fanout, overwrite reconciliation and serialized Git finalization. Existing Claude/Fable and Cursor provider choices are preserved; inherited Codex roles follow Astra/SOL/Terra assignments.

- Package id: `claude-code-design-and-implement-review-loop`
- Backends: `claude-code-agent`
- Workflows: `claude-code-design-and-implement-review-loop`
- Skills: Claude Code

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install claude-code-design-and-implement-review-loop --source /path/to/riela-packages/packages/claude-code-design-and-implement-review-loop
```

Add `--scope user` to install for the current user instead of the
current project.

This package does not install its dependencies automatically.
Install each dependency package as well:

```bash
riela package install codex-design-and-implement-review-loop --source /path/to/riela-packages/packages/codex-design-and-implement-review-loop
```

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect claude-code-design-and-implement-review-loop --output json
riela workflow validate claude-code-design-and-implement-review-loop
riela workflow run claude-code-design-and-implement-review-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.

This variant inherits the compact 18-step graph from codex-design-and-implement-review-loop. Author self-checks run within authoring steps; independent review gates and revision routes remain separate.

## Shared-branch implementation

Design and all implementation plans are authored by a single author node per phase. Accepted designs/plans are committed before implementation. Native Riela fanout runs dependency-ready implementation/review branches in the same working directory and Git branch (default concurrency 4; --max-concurrency can lower it). No worktrees are created.

The runtime calls each parallel execution a **fanout branch**, its input an **item**, and the aggregation a **join**. This is separate from a Git branch. Built-in fanout.dependencies selects ready branches from stable IDs and accepted dependencies. Built-in fanout.changeTracking captures immutable file content, hashes and modes at node boundaries, and reports drift candidates at join. No workflow-local evidence script is needed.

After all branches stop, serial reconciliation repairs missing/overwritten behavior and independent integration review checks the combined tree against every plan and the design. Failed branches stay pending; already accepted branch IDs are skipped on subsequent dispatch. Preserve original evidence and existing user changes. Node-boundary snapshots cannot detect every transient overwrite inside an agent call, so per-edit intention records and behavior tests remain required.

Git operations are serialized: planning checkpoint, final implementation commit/push, and base-branch integration. workflowInput.baseBranch defaults to the current branch; an explicit different base is merged only after combined verification. No force push or automatic discard of unrelated edits. A blocked merge/push prevents completion.

Requires a Riela build with fanout.dependencies, fanout.changeTracking and shared-branch finalization evidence support. The explicit shared-workspace ownership mode makes older runners reject the new bundle instead of silently ignoring its dependency/tracking fields. Use the paired Riela source changes before installing this update.
