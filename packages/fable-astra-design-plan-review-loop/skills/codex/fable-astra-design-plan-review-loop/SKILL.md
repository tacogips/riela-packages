---
name: fable-astra-design-plan-review-loop
description: Use Riela to have Fable 5 author design and implementation plans, debate GPT-6 Astra adversarial findings, and revise both documents until reviewed or blocked. Use for planning with these two models, not implementation execution.
---

# Fable–Astra Design and Plan Review

Run the packaged Riela workflow rather than emulating the two model roles.
Fable `claude-fable-5` authors both documents; GPT-6 Astra `gpt-6-astra`
independently reviews them. Both are frozen to the specified model, medium effort.

From the target repository, validate and inspect the installed workflow:

```bash
riela workflow validate fable-astra-design-plan-review-loop
riela workflow inspect fable-astra-design-plan-review-loop --output json
```

If missing, install `fable-astra-design-plan-review-loop` from the configured
registry, or use `--source <registry-checkout>/packages/fable-astra-design-plan-review-loop`
for an unpublished local package. Both Claude Code and Codex backends must be
configured with access to the pinned models. Do not silently substitute models.

Pass the user's request faithfully as workflowInput.requestedOutcome, plus
available targetScope, constraints and acceptanceCriteria. Optional targetDesignDoc
and targetImplPlan select repository-relative output paths.

```bash
riela workflow run fable-astra-design-plan-review-loop \
  --variables '{"workflowInput":{"requestedOutcome":"Design the requested feature and its implementation plan.","targetScope":"Relevant components","constraints":[],"acceptanceCriteria":["Both documents agree and cover the requested behavior."]}}' \
  --output jsonl
```

Fable writes only planning documents. Astra reviews both current artifacts and
adjudicates each fix or rebuttal by finding ID. High/middle findings block;
low findings remain visible. Runtime convergence guards and maxLoopIterations
bound the discussion. Do not automatically disable guards or restart an exhausted
loop to force success. Resume only with new evidence or a revised request.

Report accepted/blocked status, both document paths, reviewed revision, discussion
summary, unresolved findings and residual risks. A completed CLI session alone is
not acceptance: check final payload.accepted and status. Failed/exhausted sessions
remain unresolved. Planned verification is not executed verification; this workflow
does not implement, commit or push. Do not add an implementation phase unless requested.
