# opus-terra-design-and-implement-review-loop

Claude Code version of `codex-design-and-implement-review-loop`. Opus 5.5 owns
design, implementation planning, every review gate and the final integration
review. GPT-6.1 Terra implements the plans in parallel native fanout.

| Role | Node(s) | Backend / model |
| --- | --- | --- |
| Intake, design, implementation plans | `step1-issue-intake`, `step2-design-doc-update`, `step4-impl-plan-create` | `claude-code-agent` / `claude-opus-5-5` |
| Design and plan review | `step3-design-review`, `step5-impl-plan-review` | `claude-opus-5-5` (read-only) |
| Implementation (fanout) | `step6-implement` | `codex-agent` / `gpt-6.1-terra`, medium effort |
| Deterministic gates | `plan-contract-validate`, `dispatch-plans`, `plan-archive` | `command` |
| Wave aggregation (fanout join) | `implementation-wave-outcome` | `command` / `scripts/implementation-wave-outcome.py` |
| Test-integrity and adversarial review | `step6-test-integrity-check`, `step7-adversarial-review` | `claude-opus-5-5` (read-only) |
| Integration review | `integration-review` | `claude-opus-5-5` (read-only) |
| Reconciliation, docs, completion, Git handoff | remaining agent nodes | `claude-opus-5-5` |

- Package id: `opus-terra-design-and-implement-review-loop`
- Backends: `claude-code-agent`, `codex-agent`, `command`
- Workflows: `opus-terra-design-and-implement-review-loop`
- Skills: Claude Code (`opus-terra-design-and-implement-review-loop`)

## Compact wave summary

The `implementation-wave-outcome` command stores `fanout-join.json` and a bounded `wave-summary.json` at `tmp/opus-terra-waves/<workflowExecutionId>/wave-NNN/`. The summary is at most 49152 bytes and the verdict is at most 16384 bytes, for a combined bound of 64 KiB. Reconciliation and integration review locate the highest wave and require verdict equality before using the summary. Mock scenarios do not execute the command. Riela 0.2.34 still renders the persistent `fanoutJoin` request variable into later agent prompts; this is the open Q1 limitation tracked in `design-docs/user-qa/opus-terra-wave-input-compaction.md`.

## Review revision routing

Opus review gates are read-only. Design and plan findings return immediately to
their Opus author. Test-integrity and adversarial findings return immediately to
the original GPT-6.1 Terra implementation step in the same native branch; the
progress gate and both independent reviews run again after the correction.
Integration findings selectively redispatch their owning Terra plans rather than
requesting serial in-place repairs. Reviewers do not edit or delegate repairs.

The pre-commit `plan-contract-validate` gate routes invalid tracking contracts
back to Step 4. `dispatch-plans` routes bounded checkpoint amendments to Step 4
and sends exhausted amendments to the blocked output after two attempts. Step 8
returns archive requests for the deterministic `plan-archive` command, which
performs moves without git and bounds the Step 8/Step 9 loop at three rounds.

Each material finding carries a detailed `repairRequests` brief and actionable
`feedback`: owner, file/symbol, accepted intent, reproduction, root cause,
authorized paths, invariants, ordered changes, exact verification commands,
regression assertions and observable completion criteria. Terra reads both the
direct review inbox and redispatched `reviewFeedback`, and reports resolution
and current-source evidence per finding. Scope gaps remain explicit blockers.

## GPT-6.1 Terra fanout

The plan author decomposes work into as many independent plans as the design
allows, with disjoint `writePaths`, shared files owned by a small first-wave
contract plan, and a shallow dependency DAG. Plans spell out the key points a
lower-precision model would miss: target symbols and contracts, the code
pattern to imitate, edge cases and pitfalls, test cases and exact verification
commands. They do not contain the implementation itself. The fanout transition
declares no concurrency limit, so every dependency-ready plan of a wave runs at
once; pass `--max-concurrency` to `riela workflow run` to cap it.

## Install

```bash
riela package install opus-terra-design-and-implement-review-loop --source /path/to/riela-packages/packages/opus-terra-design-and-implement-review-loop
```

Add `--scope user` to install for the current user instead of the current
project. Both the Claude Code CLI and the Codex CLI must be available.

## Run

```bash
riela workflow inspect opus-terra-design-and-implement-review-loop --output json
riela workflow validate opus-terra-design-and-implement-review-loop
riela workflow run opus-terra-design-and-implement-review-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index.
