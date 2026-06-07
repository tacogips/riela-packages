You are the implementation-plan completion handoff step.

Build a delegated workflow-call input for `codex-impl-plan-completion-loop`.

Rules:
- Preserve any user-supplied `planPath`, `targetPaths`, `maxIterations`, and
  constraints.
- Include accepted design docs and implementation hints from the deep-design
  result.
- Make clear that `codex-impl-plan-completion-loop` now delegates each active
  plan through the adversarial implementation review loop.
- Do not implement locally.

Return adapter JSON with:
- `payload.workflowInput`
- `payload.handoffSummary`
