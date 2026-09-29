# Expected results

Run workflow validate/inspect, then run the repository compact-workflow
regression with the paired Riela source build. The full entry path requires a
resolved kaiba client for its memory add-ons; the deterministic regression
starts at `fable-design` to isolate the authored graph and uses the bundled
`mock-scenario.json`. Mock calls do not invoke models, commit or push.

Expect completed and exitCode 0. `fable-design` precedes independent design and
plan review gates, then plan checkpoint and commit. `dispatch-plans` starts
native branches that pass implementation progress, test-integrity and
adversarial gates before branch evidence. The parent wave-outcome gate
terminates blocked-only runs or continues successful evidence through
reconciliation and Fable integration review. Revisions return to the correct
author/worker; dependency waves repeat only after acceptance. Fable goal review
precedes E2E evidence, docs, completion and final Git steps.

From the repository root, use the installed `riela` CLI and a fresh absolute evidence directory under this worktree's `tmp/`:

```sh
riela workflow validate fable-and-improve-opus --workflow-definition-dir packages/fable-and-improve-opus/workflows --output json
bun packages/fable-and-improve-opus/tests/check-output-contract.ts --evidence-root "$PWD/tmp/opus-output-contract-regression"
```

The target validation reports `valid: true`. The Bun runner executes nine isolated mock cases, reports nine passed scenarios, a positive assertion count and zero failures, and writes each full CLI stdout/stderr, final exit, session result, fixture hash and source hash beneath the evidence root. All agent and add-on responses are mocked; no live model, Git or knowledge write is used. Focused probes use copies in the evidence root; the production bundle is never modified.

| Case | Expected result |
| --- | --- |
| `happy` | Completed root session; checkpoint and plan Git precede dispatch; reconciliation, integration and goal review precede final Git; knowledge create and final output follow. |
| `completion-revision` | First Step 9 response has no commit fields and routes back through docs refresh; the second is accepted; Step 10 executes once. |
| `planning-only` | Accepted planning-only payload completes without archive cleanup. |
| `commit-missing-message` | Step 9 schema rejects acceptance without a message before Step 10. |
| `commit-empty-message` | Step 9 schema rejects an empty acceptance message before Step 10. |
| `knowledge-create` | Create add-on executes; merge and archive do not. |
| `knowledge-merge-archive` | Merge, archive brief and archive execute in order with required fields. |
| `knowledge-merge-no-archive` | Merge executes; archive brief returns false without archive fields; archive add-on is bypassed. |
| `knowledge-skip` | Judge omits merge/archive fields; all write add-ons are bypassed. |

The runner also checks 22 explicit supported agent sandboxes, required producer schemas and retry budgets, the deterministic `dispatch-plans` command contract, and consumed mock payload fields in execution records. CLI mock execution validates output contracts, routing and relay behavior; it does not enforce real agent sandboxing or perform real Git or knowledge actions.
