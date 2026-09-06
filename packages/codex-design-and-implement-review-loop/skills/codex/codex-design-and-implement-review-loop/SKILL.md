---
name: codex-design-and-implement-review-loop
description: Run the all-Codex Riela workflow for analysis, design, implementation planning, implementation, independent review, verification, documentation, and completion checks. Use for issue resolution or planning-only handoff when Codex should own every agent role; do not use when Claude or Fable should participate.
---

# Codex Design And Implement Review Loop

Run the installed `codex-design-and-implement-review-loop` workflow instead of
manually emulating its orchestration.

## Responsibility split

- Codex `gpt-6-astra`: design, design review, implementation-plan creation,
  implementation-plan review, and feature-local plan joining
- Codex `gpt-5.6-terra`: implementation, tests, verification, and revisions
- Codex `gpt-5.6-sol`: intake, implementation self-review, test-integrity
  review, independent and adversarial implementation review, documentation,
  and completion checks

The workflow supports ordinary issue resolution and planning-only handoff. It
can fan out independent feature plans, joins them before implementation, and
loops blocking design, plan, test-integrity, implementation, or adversarial
review findings back to the owning Codex step.

## Run

```bash
riela workflow validate codex-design-and-implement-review-loop
riela workflow inspect codex-design-and-implement-review-loop --output json
riela workflow run codex-design-and-implement-review-loop \
  --variables '{"workflowInput":{"requestedOutcome":"Implement and verify the requested change.","targetScope":"Describe the target scope.","constraints":["Do not modify unrelated files."],"acceptanceCriteria":["The requested behavior works."],"verificationHint":"Run the smallest relevant verification."}}' \
  --output jsonl
```

Use `--scope user` for a user-scope install. Preserve the operator's requested
mode, constraints, authorization boundaries, and acceptance criteria. The
workflow may prepare a commit and push near completion, so do not run it unless
those repository mutations are authorized; otherwise use inspection or
validation without starting the workflow.

Report the resulting artifacts, changed files, verification evidence, review
decisions, residual risks, and final workflow status.
