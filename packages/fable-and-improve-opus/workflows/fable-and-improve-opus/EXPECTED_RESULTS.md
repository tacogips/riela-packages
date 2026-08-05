# Expected Results

Run the deterministic scenario from the `riela-packages` checkout:

```bash
riela workflow validate fable-and-improve-opus \
  --workflow-definition-dir packages/fable-and-improve-opus/workflows
riela workflow inspect fable-and-improve-opus \
  --workflow-definition-dir packages/fable-and-improve-opus/workflows \
  --output json
riela workflow run fable-and-improve-opus \
  --workflow-definition-dir packages/fable-and-improve-opus/workflows \
  --mock-scenario packages/fable-and-improve-opus/workflows/fable-and-improve-opus/mock-scenario.json \
  --output json
```

The stable path is:

1. `fable-goal-plan`
2. `opus-implementation`
3. `opus-review` with `needs_revision: false`
4. `fable-goal-review` with both routing flags false
5. `final-output`

Stable assertions:

```json
{
  "workflowId": "fable-and-improve-opus",
  "status": "completed",
  "rootOutput": {
    "status": "completed",
    "goalAchieved": true,
    "changedFiles": [
      "docs/example.md"
    ]
  }
}
```

Ignore session ids, timestamps, absolute artifact paths, and durations.
