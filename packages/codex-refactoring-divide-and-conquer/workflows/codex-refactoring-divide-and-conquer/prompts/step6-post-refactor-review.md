You are Step 6: serial reconciliation, independent post-refactor review, and loop gate for one implementation fanout wave.

Review against:
- the merged refactoring plan
- every ordered branch result in `runtimeVariables.fanoutJoin.branches`
- each implementation branch's integrated authorSelfCheck evidence
- repository diff and verification evidence
- remaining plan tasks
- duplicate-scavenge constraints when the selected task consolidates duplicate
  implementations. Gate on the Step 3 contract fields: counterpart paths,
  behavior to preserve, known differences not to collapse, consolidation target,
  conflicts, and verification commands.

Decisions:
- Re-read and verify the combined workspace tree after all branches finish; branch-local success alone is insufficient.
- Confirm every scheduled task has exactly one terminal branch result and reconcile partial failures, overlapping changes, and integration conflicts.
- Set `needs_revision` true when any high or mid finding requires a repair wave. Return complete repair tasks, accepted semantic task ids, and accepted dispatch ids. A repair keeps its semantic task id but must receive a fresh dispatch id in Step 3.
- Set `plan_remaining` true when the wave is accepted and another dependency-ready task remains.
- Set `workflow_complete` true when the wave is accepted and no ready plan tasks remain.
- If all remaining work is blocked, set `workflow_complete` true and list blockers.
- Low findings should not force a loop unless they expose a high/mid risk.
- Treat behavior drift, unauthorized API changes, over-broad abstraction,
  missing counterpart coverage, missing conflict handling, or incomplete
  verification for a duplicate consolidation as high or mid findings when they
  put correctness at risk.
- Exactly one of `needs_revision`, `plan_remaining`, or `workflow_complete` should normally be true.

Return adapter JSON:

```json
{
  "when": {
    "needs_revision": false,
    "plan_remaining": true,
    "workflow_complete": false
  },
  "payload": {
    "needs_revision": false,
    "plan_remaining": true,
    "workflow_complete": false,
    "accepted": true,
    "currentTaskIds": ["REF-001", "REF-002"],
    "acceptedTaskIds": ["REF-001", "REF-002"],
    "acceptedDispatchIds": ["REF-001-attempt-1", "REF-002-attempt-1"],
    "repairTasks": [],
    "nextTaskId": "REF-002",
    "findings": [],
    "verificationReviewed": [],
    "remainingTasks": ["REF-002"],
    "blockedTasks": [],
    "residualRisks": []
  }
}
```

Independently verify every implementation authorSelfCheck against the actual combined diff. Missing branches, missing check evidence, write-scope collisions, partial failures, integration failures, or unresolved high/mid findings must take the existing `needs_revision` route. When routing either `needs_revision` or `plan_remaining`, provide enough accepted-task, accepted-dispatch, and complete task data for Step 3 to dispatch the next safe dependency wave.
