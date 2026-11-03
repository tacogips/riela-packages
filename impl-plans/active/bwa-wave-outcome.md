# bwa-wave-outcome

Status: active. Wave 1. Issue `local:tacogips/riela-packages#opus-terra-blocked-wave-amendment`.
Design: `design-docs/specs/design-opus-terra-blocked-wave-amendment.md` D1-D5, D7 (unit tests).

```json
{
  "planId": "bwa-wave-outcome",
  "planPath": "impl-plans/active/bwa-wave-outcome.md",
  "dependsOn": [],
  "writePaths": [
    "impl-plans/active/bwa-wave-outcome.md",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/implementation-wave-outcome.py",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/nodes/node-implementation-wave-outcome.json",
    "packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/workflow.json",
    "packages/opus-terra-design-and-implement-review-loop/tests/test_wave_outcome.py",
    "packages/opus-terra-design-and-implement-review-loop/tests/test_blocked_wave_amendment.py"
  ],
  "sharedPaths": [],
  "artifactRoots": [],
  "verification": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_wave_outcome.py packages/opus-terra-design-and-implement-review-loop/tests/test_blocked_wave_amendment.py -v",
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest packages/opus-terra-design-and-implement-review-loop/tests/test_dispatch_amendment.py packages/opus-terra-design-and-implement-review-loop/tests/test_workflow_routing.py -v",
    "cmp packages/codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/scripts/dispatch-plans.py packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/dispatch-plans.py",
    "git diff --exit-code -- packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/scripts/dispatch-wave.py",
    "python3 -c \"import json;json.load(open('packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop/workflow.json'))\"",
    "git diff --check"
  ],
  "acceptanceCriteria": [
    "An eligible fully blocked wave at round < 2 emits when {implementation_blocked:true, partial_success:false, amendment_required:true}, and its payload carries checkpointAmendment with reason 'blocked-wave-scope-or-contract', blockedPlanIds, verbatim blockers, manifestPath, previousCheckpointCommit (HEAD), amendmentRound, maxAmendmentRounds (2), summaryPath and rawJoinPath.",
    "Ineligible waves (any D1 rule 1-7 failure) and budget-exhausted waves emit amendment_required:false with no checkpointAmendment. The six verdict fields are unchanged from today. Partial-success and unblocked waves always emit amendment_required:false.",
    "workflow.json implementation-wave-outcome has exactly 3 transitions in the D4 order and labels. No other workflow.json change except that step's description.",
    "The node schema adds amendment_required (required boolean) and checkpointAmendment (optional object), and stays closed.",
    "wave-summary.json carries amendmentDecision. summary.verdict deep-equals the emitted payload.",
    "dispatch-plans.py and dispatch-wave.py are unchanged. MAX_CHECKPOINT_AMENDMENTS is imported, never redefined.",
    "All listed tests pass."
  ]
}
```

## Intent and context

Mode `issue-resolution`. Today a fully blocked wave always ends at
`implementation-blocked-output`. This plan adds the deterministic eligibility
check, the shared round counter, the output contract and the routing that send
amendment-eligible waves to `step4-impl-plan-create` (design D1-D5).

Abbreviations: `W` = `packages/opus-terra-design-and-implement-review-loop/workflows/opus-terra-design-and-implement-review-loop`;
`T` = `packages/opus-terra-design-and-implement-review-loop/tests`.

Patterns to imitate:
- `W/scripts/dispatch-wave.py:load_dispatch_module` (importlib loading of a sibling script).
- `W/scripts/dispatch-wave.py:amendment_result` (checkpointAmendment field names and 0-based round semantics).
- `W/scripts/dispatch-plans.py:git` (subprocess git with cwd=root, check=False).
- `W/scripts/implementation-progress-check.py:environment_blocked` (environment predicates; copy the predicate, do not import that script).
- `T/test_dispatch_amendment.py` and `T/test_wave_outcome.py:envelope/branch/run` (fixtures).

## Non-goals

- Do not edit `dispatch-plans.py` (byte identity with the Codex base is tested) or `dispatch-wave.py`.
- Do not edit prompts, mocks, README, EXPECTED_RESULTS, riela-package.json or registry-index.json. Other plans own them.
- Do not change the six verdict fields' values, the caps, the LEVELS, or the partial-success/reconcile route.
- No model calls and no network. Do not auto-amend tracking-contract or evidence-incomplete waves.

## File-level changes

1. `W/scripts/implementation-wave-outcome.py`
   - Load `dispatch-wave.py` with importlib, like `load_dispatch_module`. Bind
     `MAX_CHECKPOINT_AMENDMENTS = <dispatch_wave module>.MAX_CHECKPOINT_AMENDMENTS`
     and `dispatch = <dispatch_wave module>.dispatch` (the dispatch-plans helpers).
     The literal `MAX_CHECKPOINT_AMENDMENTS = 2` must not appear in this file.
   - Constants: `AMENDMENT_REASON = "blocked-wave-scope-or-contract"`,
     `AMENDMENT_BYTE_LIMIT = 16384`, `SCOPE_SIGNALS`, `EXCLUSION_MARKERS`
     (the exact D1 rule 4 and rule 5 lists, grouped by family as a dict
     `family -> tuple[str, ...]`), `BLOCKER_COPY_KEYS = ("paths","path","dependency","evidence","resumeCriterion","resumeCriteria","message")`.
   - `SCHEMA_KEYS` becomes the six existing keys plus `"amendment_required"`.
     Add `OPTIONAL_KEYS = ("checkpointAmendment",)`.
   - New `_checkpoint_lineage(root: Path) -> tuple[str, str, int]`, which returns
     `(manifestPath, headCommit, amendmentRound)` and raises ValueError on any failure:
     - HEAD comes from `git rev-parse HEAD`.
     - committedFiles comes from `git diff-tree --root --no-commit-id --name-only -r HEAD`.
     - Call `dispatch.checkpoint_source([{"fromStepId":"plan-git-commit","createdOrder":1,"payload":{"git":{"operation":"commit","commitHash":head,"committedFiles":files}}}], root)`.
     - Read `originalHead` from that manifest. It must be a non-empty string,
       `git cat-file -e <sha>^{commit}` must succeed, and
       `git merge-base --is-ancestor <sha> HEAD` must succeed.
     - `count = git rev-list --count --first-parent <originalHead>..HEAD`.
       A count below 1 raises. Otherwise round = count - 1.
   - New `_amendment_decision(join, plans, verdict, root, summary_path, raw_path) -> dict`.
     It returns `{eligible: bool, amendmentRequired: bool, amendmentRound: int|None, maxAmendmentRounds: int, ineligibleReasons: [str], checkpointAmendment: dict|None}`.
     - Return immediately with reason `not-fully-blocked` unless
       `verdict.implementation_blocked and not verdict.partial_success`.
     - Rule 1: every plan record's `classification` is in `{"blocked","pending"}`.
     - Rule 2: for every blocked plan, `blockerType == "implementation-dependency"`.
     - Rule 3: read the raw branch output via the plan's `rawPointer`
       (`/branches/<i>` into `join["branches"]`) and apply the environment predicates.
     - Rule 4: drop the gate marker, which is a dict containing `evidenceFingerprint`
       whose `type` equals the plan's blockerType. Require at least one remaining
       blocker, and require each remaining blocker to be a dict with a scope
       signal per D1 rule 4.
     - Rule 5: scan the listed keys plus every string in the blocker's
       `resumeCriteria`, plus the plan record's `resumeCriteria` strings. A
       non-string `resumeCriteria` entry is ineligible.
     - Rule 6: call `_checkpoint_lineage`. Any exception becomes reason
       `checkpoint-unresolved: <msg>`.
     - Rule 7: the amendment size must be within `AMENDMENT_BYTE_LIMIT` (compact JSON bytes).
     - Collect all failing reasons. Keep at most 10, each at most 160 chars.
       `amendmentRequired = eligible and round < MAX_CHECKPOINT_AMENDMENTS`.
       When eligible but exhausted, add reason
       `amendment-budget-exhausted: round N of M`.
   - checkpointAmendment shape is exactly design D3. Copy `blockers[]` entries
     with only the `BLOCKER_COPY_KEYS` that are present, plus `planId`, with
     values unchanged (no `_text` truncation). Order follows verdict
     `blockedPlanIds`, then raw blocker order.
   - `classify()`:
     - Compute the decision after `_classify_join`.
     - Build the payload as the capped verdict plus `amendment_required`, plus
       `checkpointAmendment` only when required.
     - Keep the `VERDICT_BYTE_LIMIT` check on the six-key verdict portion.
     - The 65536 summary+payload check uses the full payload. If no level fits
       while the amendment is present, drop the amendment, set
       amendment_required false, add reason `amendment-oversize`, and retry.
       Never raise solely because of the amendment.
     - Write `amendmentDecision` (without `checkpointAmendment`) into the
       summary at top level, and keep `"verdict": payload`.
     - Return `{"when":{"implementation_blocked":..,"partial_success":..,"amendment_required":..},"payload":payload}`.
2. `W/nodes/node-implementation-wave-outcome.json`: add the properties
   `amendment_required: {type: boolean}` and `checkpointAmendment: {type: object}`,
   add `amendment_required` to `required`, keep `additionalProperties: false`,
   and change nothing else.
3. `W/workflow.json`, step `implementation-wave-outcome` only:
   - `transitions` must be exactly
     `[{toStepId:"step4-impl-plan-create",label:"implementation_blocked && !(partial_success) && amendment_required"},{toStepId:"implementation-blocked-output",label:"implementation_blocked && !(partial_success || amendment_required)"},{toStepId:"reconcile-implementations",label:"!(implementation_blocked) || partial_success"}]`.
   - Description: "Aggregate preclassified native implementation branch outcomes; blocked-only waves amend within the shared checkpoint-amendment budget or terminate, while evidence-complete successful candidates continue to independent acceptance."
   - Preserve the file's 2-space JSON formatting and trailing newline.
4. `T/test_wave_outcome.py`: update only the assertions that the feature
   changes, keeping them exact.
   - `test_blocked_only_is_not_partial_success` expects
     `{'implementation_blocked':True,'partial_success':False,'amendment_required':False}`
     (the temp dir is not a git repo).
   - `test_node_schema_prompt_and_transitions` has `required` equal to `SCHEMA_KEYS`,
     properties equal to `SCHEMA_KEYS + OPTIONAL_KEYS`, and the 3-transition list.
   - `test_all_success_and_closed_payload_contract` compares against `set(SCHEMA_KEYS)`,
     which now includes amendment_required.
5. `T/test_blocked_wave_amendment.py` (new). Its helper builds a temp git repo:
   - `git init -q`, plus `-c user.name=t -c user.email=t@t` on commits.
   - An intake commit with any file, then checkpoint C0 adding
     `impl-plans/active/t-dispatch.json` = `{"taskId":"t","originalHead":<intake sha>,"plans":[{"planId":"a","writePaths":["src/a.py"]}]}`.
   - An optional `extra_checkpoints=n` that modifies the manifest and commits n times.
   - Envelopes are built with `T/test_wave_outcome.py`-style helpers, and the
     script is loaded via importlib.

## Pitfalls

- An existing temp-dir test (non-git) must still classify. A git failure is an
  ineligibility reason, never an exception or exit 1.
- Do not run git in the repository under test from tests. Always pass the
  temp root, and run `subprocess` with `cwd=root`.
- `checkpoint_source` reads files from the working tree and requires `.json`
  with a `plans` list. Keep the manifest file present.
- The progress-gate marker has `type` and not `blockerType`. Do not treat it
  as a substantive blocker, and do not let it supply a scope signal.
- The denylist must not include bare `test`, `review` or `fixture`.
- Do not truncate `checkpointAmendment` values. Do not add amendment keys to
  the `_cap_verdict` output.
- summary.verdict must equal the emitted payload, because
  `prompts/reconcile-implementations.md` requires deep equality.

## Test cases (`T/test_blocked_wave_amendment.py`)

- Eligible: one plan blocked with `blockerType implementation-dependency`
  and blockers `[{paths:['src/b.py'],dependency:'b.py outside writePaths',evidence:'e',resumeCriterion:'authorize src/b.py in writePaths'}, marker]`
  at C0 -> amendment_required true, round 0, max 2, previousCheckpointCommit == C0
  sha, manifestPath == 'impl-plans/active/t-dispatch.json', the blockers
  entry is verbatim with planId, and the marker is excluded.
- Each blocker type other than implementation-dependency
  (implementation-material-finding, implementation-materially-unverified,
  implementation-no-progress, implementation-incomplete,
  implementation-invalid-evidence) -> false.
- `environmentBlocked:true` on the output -> false. `status:'blocked-environment'` -> false.
- Each of the four denylist families in `message` -> false. Each family only in
  the blocker `resumeCriteria` -> false. The exact reproduction is
  `{paths:['tests/test_contract.py'],dependency:'missing additive field',resumeCriteria:['Resolve test-integrity failure: restore skipped test before continuing.']}`
  -> false. Marker only in the plan-level resumeCriteria -> false. A non-string
  resumeCriteria entry -> false.
- Positive control: the same blocker with
  `resumeCriteria:['Authorize tests/test_contract.py in writePaths via checkpoint amendment.']`
  -> true.
- A string-only blocker -> false. A plan with only the marker -> false.
- A tracking-rejected branch (failureReason `policy_blocked: fanout snapshot ...`)
  -> false. changeEvidence complete:false -> false. A blocked plan plus a
  failed branch -> false.
- A non-git root -> false, with an ineligibleReasons entry starting `checkpoint-unresolved`.
- extra_checkpoints=2 (round 2) -> false, with an `amendment-budget-exhausted` reason.
  The wave summary amendmentDecision has eligible true and amendmentRequired false.
- Shared counter: extra_checkpoints=1 (simulating one dispatch amendment) ->
  true with round 1. Then commit one more manifest change -> false.
  `wave.MAX_CHECKPOINT_AMENDMENTS == dispatch_wave.MAX_CHECKPOINT_AMENDMENTS`,
  and the script source has no `MAX_CHECKPOINT_AMENDMENTS = ` line.
- Partial success (eligible-looking blocked plan plus a successful plan with evidencePaths) -> false.
- Transition order and labels in workflow.json equal the D4 list. Write a small
  evaluator for the three labels over all 8 combinations of
  (implementation_blocked, partial_success, amendment_required): at most one
  label is true, and exactly one is true for every combination reachable
  from the script (amendment_required implies a full block).
- An oversize amendment (a blocker evidence string over 16384 bytes) -> false,
  with reason `amendment-oversize`, and the script does not raise.

## Done criteria

- The verification commands above all exit 0. `cmp` reports no difference,
  and `git diff --exit-code` on dispatch-wave.py exits 0.
- Progress log: append a dated `## Progress` section to this file listing
  changed files, the commands run, and their exit statuses.

## Progress 2026-11-03

- Implemented deterministic blocked-wave eligibility, shared checkpoint lineage budget, bounded amendment payload and summary decision in `scripts/implementation-wave-outcome.py`; updated the closed node schema and three workflow transitions.
- Added `tests/test_blocked_wave_amendment.py` and updated exact assertions in `tests/test_wave_outcome.py`. Scope signals, denylist families, gate and environment failures, incomplete evidence, partial success, non-git lineage, oversize amendments and shared budget are covered.
- Focused wave tests: exit 0, 23 tests; dispatch amendment and workflow routing tests: exit 0, 14 tests. `cmp` dispatch-plans, dispatch-wave diff, and workflow JSON parse: exit 0. Logs are under `tmp/blocked-wave-amendment/bwa-wave-outcome/attempt-1/`.
- Completion criteria: assigned source, routing, schema and behavioral tests implemented; formal review and downstream prompt, scenario, release and final integration work remain assigned to later workflow steps.
