# Deterministic routing check

Run from the registry checkout with a temporary working directory/session store:

```bash
riela workflow run fable-astra-design-plan-review-loop \
  --workflow-definition-dir packages/fable-astra-design-plan-review-loop/workflows \
  --mock-scenario packages/fable-astra-design-plan-review-loop/workflows/fable-astra-design-plan-review-loop/mock-scenario.json \
  --working-dir <temporary-directory> --session-store <temporary-directory>/sessions \
  --artifact-root <temporary-directory>/artifacts --output json
```

Expected node order: fable-author, astra-review, fable-author, astra-review,
workflow-output. The first review rejects A1, the second accepts revision 2.
Final payload is accepted and refers to revision 2.

Also test a rejecting reviewer on every visit with --max-loop-iterations 2:
the session must stop without running workflow-output or reporting acceptance.
Mocks test orchestration only, not model access, document writing, digest checks,
or review quality. Live backend execution is a separate integration check.
