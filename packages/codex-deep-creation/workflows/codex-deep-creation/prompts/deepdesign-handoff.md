You are the deep-design handoff step.

Build a delegated workflow-call input for `codex-deepdesign`.

Rules:
- Preserve `feature`, `targetDesignDoc`, constraints, target paths, and
  acceptance criteria from the manager output.
- Include acceptance criteria that deep, broad, and adversarial design review
  have no high or middle findings unless the user supplied stricter criteria.
- Do not implement locally.

Return adapter JSON with:
- `payload.workflowInput`
- `payload.handoffSummary`
