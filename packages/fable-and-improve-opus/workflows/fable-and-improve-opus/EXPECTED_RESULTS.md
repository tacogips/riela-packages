# Expected results

From the repository root, use the installed `riela` CLI and a fresh absolute evidence directory under this worktree's `tmp/`:

```sh
riela workflow validate fable-and-improve-opus --workflow-definition-dir packages/fable-and-improve-opus/workflows --output json
bun packages/fable-and-improve-opus/tests/check-output-contract.ts --evidence-root "$PWD/tmp/opus-output-contract-regression"
```

The target validation reports `valid: true`. The Bun runner executes ten isolated mock cases, reports ten passed scenarios, a positive assertion count and zero failures, and writes each full CLI stdout/stderr, final exit, session result, fixture hash and source hash beneath the evidence root. All agent and add-on responses are mocked; no live model, Git or knowledge write is used. The production workflow graph stays unchanged; focused probes use copies in the evidence root.

| Case | Expected result |
| --- | --- |
| `happy` | Completed root session; checkpoint and plan Git precede dispatch; reconciliation, integration and goal review precede final Git; knowledge create and final output follow. |
| `completion-revision` | First Step 9 response has no commit fields and routes through goal review; the second is accepted; Step 10 executes once. |
| `planning-only` | Accepted planning-only payload completes without archive cleanup. |
| `checkpoint-empty-message` | Producer schema rejects the empty message before plan Git commit. |
| `commit-missing-message` | Step 9 schema rejects acceptance without a message before Step 10. |
| `commit-empty-message` | Step 9 schema rejects an empty acceptance message before Step 10. |
| `knowledge-create` | Create add-on executes; merge and archive do not. |
| `knowledge-merge-archive` | Merge, archive brief and archive execute in order with required fields. |
| `knowledge-merge-no-archive` | Merge executes; archive brief returns false without archive fields; archive add-on is bypassed. |
| `knowledge-skip` | Judge omits merge/archive fields; all write add-ons are bypassed. |

The runner also checks 16 explicit supported agent sandboxes, required producer schemas and retry budgets, production graph/settings equality to checkpoint `b5cf79770a8c5c218057d470b0b1a68d16c52901`, and consumed mock payload fields in execution records. CLI mock execution validates output contracts, routing and relay behavior; it does not enforce real agent sandboxing or perform real Git or knowledge actions.
