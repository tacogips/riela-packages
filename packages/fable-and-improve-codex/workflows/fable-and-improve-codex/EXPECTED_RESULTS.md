# Expected results

`mock-scenario.json` verifies the direct six-stage responsibility split:

1. `fable-analysis` analyzes the request and repository with `claude-fable-5`.
2. `fable-design` authors the design with `claude-fable-5`.
3. `fable-impl-plan` authors the implementation plan with `claude-fable-5`.
4. `codex-implementation` implements with `gpt-5.6-terra`.
5. `codex-review` independently accepts with `gpt-5.6-sol` and `needs_revision: false`.
6. `fable-goal-review` accepts completion, then `final-output` publishes the result.

Expected stable result: workflow `fable-and-improve-codex` completes with exit
code `0`, `goalAchieved: true`, and explicit analysis, design, plan,
implementation, review, and verification evidence.
