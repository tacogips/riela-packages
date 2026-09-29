# Expected results

Use installed Riela from the repository root:

```sh
riela workflow validate fable-and-improve-codex --workflow-definition-dir packages/fable-and-improve-codex/workflows --output json
bun packages/fable-and-improve-codex/tests/check-output-contract.ts --evidence-root "$PWD/tmp/fable-and-improve-codex-contracts"
```

The runner copies the authored bundle into separate evidence directories and runs mocked `riela workflow run` processes with isolated session and artifact stores. Expect ten passed cases, zero failures, a positive assertion count, complete command logs, and `summary.json`. It renews the full happy path because the earlier retry receipt does not prove an exact current-input source match. No live model, Git, or knowledge action runs.

| Case | Expected observed result |
| --- | --- |
| `happy` | Root completes with exit 0 and 18 executions; checkpoint and integration precede final Git, then knowledge create reaches final output. |
| `completion-revision` | Step 9 first accepts a revision without commit fields, returns to Fable goal review, then accepts completion and reaches final git-commit once. |
| `planning-only` | Accepted completion retains active plan status and bypasses archive cleanup. |
| `checkpoint-empty-message` | Output validation rejects empty `commitMessage` at plan-checkpoint before plan-git-commit. |
| `commit-missing-message` | Output validation rejects accepted Step 9 without `commitMessage` before step10-git-commit. |
| `commit-empty-message` | Output validation rejects accepted Step 9 with empty `commitMessage` before step10-git-commit. |
| `knowledge-create` | Creates knowledge and reaches final output. |
| `knowledge-merge-archive` | Merges, then archives the old note and reaches final output. |
| `knowledge-merge-no-archive` | Merges and bypasses the archive write. |
| `knowledge-skip` | Bypasses knowledge write add-ons and reaches final output. |

The runner asserts published payloads and execution records, explicit sandboxes on 16 agent nodes, required producer schemas and budgets, and the production graph/settings against checkpoint `b5cf797`. Mock verification cannot enforce live backend sandbox behavior or external side effects.
