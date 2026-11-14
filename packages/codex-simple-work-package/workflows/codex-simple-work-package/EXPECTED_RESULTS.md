# Expected Results

The mock scenario should run the simple-work flow once:

- `implement` makes a focused code or documentation change.
- `review` accepts the change when no `high` or `middle` findings remain.
- `workflow-output` publishes the accepted summary.

If `review` returns `when.needs_revision: true`, the workflow must route back to
`implement` and only address `high` or `middle` findings before reviewing again.
