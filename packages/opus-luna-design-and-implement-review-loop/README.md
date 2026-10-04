# opus-luna-design-and-implement-review-loop

Claude Code version of `codex-design-and-implement-review-loop`. Opus 5.5 owns
design, implementation planning, every review gate and the final integration
review. GPT-6 Luna implements the plans in parallel native fanout.

| Role | Node(s) | Backend / model |
| --- | --- | --- |
| Intake, design, implementation plans | `step1-issue-intake`, `step2-design-doc-update`, `step4-impl-plan-create` | `claude-code-agent` / `claude-opus-5-5` |
| Design and plan review | `step3-design-review`, `step5-impl-plan-review` | `claude-opus-5-5` (read-only) |
| Implementation (fanout) | `step6-implement` | `codex-agent` / `gpt-6-luna`, high effort, fast tier |
| Test-integrity and adversarial review | `step6-test-integrity-check`, `step7-adversarial-review` | `claude-opus-5-5` (read-only) |
| Integration review | `integration-review` | `claude-opus-5-5` (read-only) |
| Reconciliation, docs, completion, Git handoff | remaining agent nodes | `claude-opus-5-5` |

- Package id: `opus-luna-design-and-implement-review-loop`
- Backends: `claude-code-agent`, `codex-agent`, `command`
- Workflows: `opus-luna-design-and-implement-review-loop`
- Skills: Claude Code (`opus-luna-design-and-implement-review-loop`)

## Review revision routing

Opus review gates are read-only. Design and plan findings return immediately to
their Opus author. Test-integrity and adversarial findings return immediately to
the original GPT-6 Luna implementation step in the same native branch; the
progress gate and both independent reviews run again after the correction.
Integration findings selectively redispatch their owning Luna plans rather than
requesting serial in-place repairs. Reviewers do not edit or delegate repairs.

Each material finding carries a detailed `repairRequests` brief and actionable
`feedback`: owner, file/symbol, accepted intent, reproduction, root cause,
authorized paths, invariants, ordered changes, exact verification commands,
regression assertions and observable completion criteria. Luna reads both the
direct review inbox and redispatched `reviewFeedback`, and reports resolution
and current-source evidence per finding. Scope gaps remain explicit blockers.

## GPT-6 Luna fanout

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
riela package install opus-luna-design-and-implement-review-loop --source /path/to/riela-packages/packages/opus-luna-design-and-implement-review-loop
```

Add `--scope user` to install for the current user instead of the current
project. Both the Claude Code CLI and the Codex CLI must be available.

## Run

```bash
riela workflow inspect opus-luna-design-and-implement-review-loop --output json
riela workflow validate opus-luna-design-and-implement-review-loop
riela workflow run opus-luna-design-and-implement-review-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index.
