# Expected results

`mock-scenario.json` verifies the responsibility split plus the knowledge-base
loop:

1. `fable-analysis` analyzes the request and repository with `claude-fable-5`
   and names a `knowledgeQuery` keyword.
2. `kb-recall-prior` recalls durable prior knowledge from the kaiba knowledge
   base (`kaiba/memory-recall`; `resultCount: 0` against an empty note root).
3. `fable-design` authors the design with `claude-fable-5`, applying the
   recalled knowledge.
4. `fable-impl-plan` authors the implementation plan with `claude-fable-5`.
5. `opus-implementation` implements with `claude-opus-5`.
6. `opus-review` independently accepts with `claude-opus-5` and
   `needs_revision: false`.
7. `fable-goal-review` accepts completion.
8. `kb-self-review` extracts one durable lesson, `kb-recall-related` recalls
   related notes, and `kb-merge-judge` decides `create`
   (`create_knowledge: true`), so `kb-create` (`kaiba/memory-consolidate`)
   writes one knowledge note (`entriesWritten: 1`, non-empty `noteIds`).
9. `final-output` publishes the result.

Run the mock against disposable roots so the real knowledge base is untouched:

```bash
riela workflow run fable-and-improve-opus \
  --workflow-definition-dir <riela-packages-checkout>/packages/fable-and-improve-opus/workflows \
  --mock-scenario <riela-packages-checkout>/packages/fable-and-improve-opus/workflows/fable-and-improve-opus/mock-scenario.json \
  --variables '{"memoryRoot":"./tmp/fable-and-improve-opus/memory","noteRoot":"./tmp/fable-and-improve-opus/notes","workflowInput":{"requestedOutcome":"Add and verify the requested documentation note."}}' \
  --output json
```

Expected stable result: workflow `fable-and-improve-opus` completes with exit
code `0`, `goalAchieved: true`, explicit analysis, design, plan,
implementation, review, and verification evidence, and one knowledge-base note
written by `kb-create`.
