---
name: riel-claude-code-impl-workflow
description: Use when implementation work in a rielflow project changes behavior, adds functionality, or fixes bugs and the user has not explicitly asked to avoid workflows. Routes the work through the packaged `claude-code-design-and-implement-review-loop` workflow, including design/plan alignment, implementation, review, user-facing documentation refresh, commit-message generation, and built-in git commit/push steps.
---

# Riel Claude Code Implementation Workflow

Use this skill as the default Claude Code path for implementation work in this repository.

## Apply This Skill When

- fixing a bug
- adding or changing runtime behavior
- implementing a feature from a design or implementation plan
- making a non-trivial refactor that changes implementation behavior
- reviewing or hardening dedicated `workflow self-improve` implementation
  behavior, including its CLI, server, library, GraphQL, report, backup, patch,
  and git-commit integration

## Do Not Apply This Skill When

- the user explicitly says not to use a workflow
- the task is documentation-only or planning-only with no implementation
- the task is specifically to debug or repair `rielflow` itself; use the current repository's fix workflow skill
- the task is to operate or troubleshoot live `workflow run --auto-improve`
  supervision rather than implement repository behavior; use
  an auto-improve operations skill

## Default Workflow

Use the packaged workflow bundle:

- Workflow id: `claude-code-design-and-implement-review-loop`
- Package id: `claude-code-design-and-implement-review-loop`

Preferred entry point from the repository root:

```bash
rielflow workflow package checkout claude-code-design-and-implement-review-loop
rielflow workflow run claude-code-design-and-implement-review-loop --output json
```

Equivalent direct command:

```bash
rielflow workflow package checkout claude-code-design-and-implement-review-loop
rielflow workflow run claude-code-design-and-implement-review-loop --output json
```

## Runtime Inputs

For normal implementation work, run the workflow in issue-resolution mode.

Pass structured workflow input through `--variables` when the task needs
explicit issue/reference context. Typical fields:

- `workflowInput.issueUrl`
- `workflowInput.issueNumber`
- `workflowInput.issueRepository`
- `workflowInput.issueTitle`
- `workflowInput.issueBody`
- `workflowInput.targetFeatureArea`
- `workflowInput.requestedBehavior`
- `workflowInput.claudeCodeAgentReferences`
- `workflowInput.referenceRepositoryRoot`
- `workflowInput.referenceRepositoryUrl`

Keep `workflowInput.claudeCodeAgentReferences` explicit when the issue depends on
Claude Code-specific behavior. `claude-code-agent` is an execution-backend identifier, not
Rielflow product branding, and should not be renamed or generalized during
product-name updates.

Planning-only mode is available via:

- `workflowInput.executionMode: "design-plan-only"`

## Expected Behavior

The workflow is responsible for:

1. issue or task intake
2. design-document updates
3. design self-review
4. design review
5. implementation-plan creation or revision
6. implementation-plan self-review
7. implementation-plan review
8. implementation work
9. implementation self-review
10. implementation review
11. user-facing documentation refresh (`README.md`, mandatory workflow skill
    docs, and any directly affected user-facing skills such as event-source
    runbooks)
12. staged secret scan with `gitleaks git --pre-commit --redact --staged --verbose`
13. commit-message generation
14. built-in git commit and git push add-on steps

Because the workflow ends with commit/push, do not use it when the user has
explicitly asked to avoid workflow-driven commits or wants manual local edits
only.

Rename-related issue-resolution runs should preserve `DIVEDRA_*` environment
variables as compatibility/runtime contracts unless a design explicitly
approves a migration. Product-owned package names, CLI examples, workflow
catalog paths, and human-facing documentation should use Rielflow/`rielflow`.

Telemetry-related issue-resolution runs should keep user-facing documentation
aligned with the runtime privacy contract. OpenTelemetry tracing is opt-in via
an OTLP endpoint or `RIELFLOW_OTEL_ENABLED=true`; workflow message payloads
stored in SQLite `workflow_messages.payload_json` must remain excluded unless
`RIELFLOW_OTEL_EXPORT_MESSAGES=true` is explicitly set for trusted fixtures.
Do not describe runtime communication payloads as inbox/outbox files; SQLite
`workflow_messages` is the source of truth. Jaeger smoke checks should use the
repository-owned
`compose.jaeger.yaml` file and `docker compose -f compose.jaeger.yaml`.

Workflow package checkout issue-resolution runs should refresh user-facing
docs for package manifests, direct `--workflow-definition-dir` destinations,
package status/update commands, and vendor-scoped skill layouts. Keep `Issue
#35` references explicit when that issue is present in workflow input but
unrelated, and preserve `claude-code-agent` as an execution-backend identifier while
documenting Claude Code skill projection as `.claude-code/skills/<name>/SKILL.md`.

SQLite message-store issue-resolution runs should refresh `README.md`, the
SQLite message-store design, the node communication design when communication
semantics change, and this workflow skill. User-facing docs must state that
`workflow_messages` is the canonical source for communication reads, replay,
retry, GraphQL inspection, and manager mutations; legacy per-message
communication files and session communication arrays are not fallback sources.
Also document that `RIEL_RUNTIME_DB`, `RIEL_ARTIFACT_DIR`, and
`RIEL_ATTACHMENT_ROOT` control the runtime database and file/binary handoff
roots, that SQLite stores only attachment-root-relative references for
file/binary handoffs, and that failed SQLite writes block message publication.
For payload attachment snapshot changes, user-facing docs must state that
`payload.attachments[]` is a mixed descriptor array: non-file descriptors
remain in `workflow_messages.payload_json`, only safely materialized
file-backed descriptors are rewritten to normalized `attachment-root` refs, and
`workflow_messages.artifact_refs_json` stays limited to materialized file refs.
Keep PR references such as `PR #54`, branch names such as
`feature/sqlite-message-store`, and `claude-code-agent` execution references
explicit in workflow outputs.

## Reporting

After the workflow finishes, report:

- workflow mode
- changed files
- verification commands
- commit message
- commit hash
- pushed remote and branch

If the workflow fails because `rielflow` appears incorrect, switch to the
current repository's fix workflow.
