# codex-design-and-implement-review-loop

Shared Codex workflow for issue resolution or planning-only design and implementation-plan handoff. The workflow owns both the sequential path and the bounded feature-local fanout path, then joins accepted plans before implementation or planning-only completion.

Design, design-review, implementation-plan, and implementation-plan-review nodes use Codex GPT-6 Astra. Design, planning, and implementation author self-checks are integrated into their authoring steps to reduce workflow calls without removing independent quality gates. The implementation node uses Codex GPT-5.6 Terra. Test-integrity review, independent implementation review, and adversarial implementation review use Codex GPT-5.6 SOL.

The executable graph contains 18 steps. Compared with the earlier 22-step graph, the three standalone author self-review steps are folded into their authoring steps and completion verification shares Step 9 with commit preparation. All six acceptance gates remain represented; independent review thresholds are unchanged. Prompt integration has not been proven equivalent in real-agent quality evaluations.

- Package id: `codex-design-and-implement-review-loop`
- Backends: `codex-agent`
- Workflows: `codex-design-and-implement-review-loop`
- Skills: Codex (`codex-design-and-implement-review-loop`)

## Install

From your project directory, with a local checkout of this registry:

```bash
riela package install codex-design-and-implement-review-loop --local-path /path/to/riela-packages
```

Add `--scope user` to install for the current user instead of the
current project.

## Run

Inspect the workflow inputs and structure, then run it:

```bash
riela workflow inspect codex-design-and-implement-review-loop --output json
riela workflow validate codex-design-and-implement-review-loop
riela workflow run codex-design-and-implement-review-loop --output jsonl
```

See the [registry README](../../README.md) for the full package index
and the recommended install flow.
