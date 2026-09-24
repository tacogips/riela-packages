# fable-astra-design-plan-review-loop

Fable 5 が design と implementation plan を作成し、GPT-6 Astra が両方を敵対的レビューします。
指摘への修正・根拠付き反論を Fable が返し、Astra が再判定する対話ループです。
設計と計画の完成までを扱い、実装は実行しません。

- Author: `claude-code-agent` / `claude-fable-5` / medium
- Reviewer: `codex-agent` / `gpt-6-astra` / medium / read-only
- Models: frozen (no automatic substitution)
- Skills: Codex and Claude Code (`fable-astra-design-plan-review-loop`)

## Install and run

```bash
riela package install fable-astra-design-plan-review-loop --source packages/fable-astra-design-plan-review-loop
riela workflow validate fable-astra-design-plan-review-loop
riela workflow run fable-astra-design-plan-review-loop \
  --variables '{"workflowInput":{"requestedOutcome":"Design the requested feature and its implementation plan.","targetScope":"Relevant components","constraints":[],"acceptanceCriteria":["Both documents agree and cover the requested behavior."]}}' \
  --output jsonl
```

Run from the target repository. Both authenticated backends and access to the
specified models are required. Use an absolute source path when installing from
another repository; `--scope user` installs user-wide.

Optional workflowInput.targetDesignDoc and targetImplPlan choose output paths.
Fable follows repository document conventions, falling back to design-docs/ and
impl-plans/. Outputs include both files, revision/digests, acceptance coverage,
finding IDs, responses, reviewer dispositions and discussion history.

High/middle findings block acceptance; low suggestions are reported as residual
risks. Fable may rebut with evidence, but only Astra closes review findings.
Both files are re-reviewed after revisions. Missing/stale artifacts and material
unknowns block approval. The runtime bounds loops (maxLoopIterations=8 plus its
convergence guard); exhaustion is unresolved, never automatic acceptance.
Only planning documents are edited. No implementation, commits or pushes.

See the workflow's EXPECTED_RESULTS.md for deterministic mock validation.
