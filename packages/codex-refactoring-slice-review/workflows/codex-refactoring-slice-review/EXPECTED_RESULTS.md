# Expected Results

Stable assertions for deterministic verification with the bundled duplicate-scavenge
mock scenario.
Ignore `sessionId`, timestamps, and artifact paths.

## Validate

Command:

```bash
bun run packages/riela/src/bin.ts workflow validate codex-refactoring-slice-review --workflow-definition-dir .riela/workflows
```

Expected result: the workflow is valid.

## Run

Command:

```bash
bun run packages/riela/src/bin.ts workflow run codex-refactoring-slice-review \
  --workflow-definition-dir .riela/workflows \
  --mock-scenario .riela/workflows/codex-refactoring-slice-review/mock-scenario.json \
  --output json
```

Expected stable run summary:

```json
{
  "status": "completed",
  "workflowName": "codex-refactoring-slice-review",
  "workflowId": "codex-refactoring-slice-review",
  "nodeExecutions": 1,
  "transitions": 0,
  "exitCode": 0
}
```

Expected final output node: `slice-review`

Expected final output payload highlights:

```json
{
  "sliceId": "package-source-boundary",
  "title": "Package source boundary",
  "findings": [
    {
      "severity": "mid",
      "file": "packages/riela/src/index.ts",
      "risk": "Package contracts can drift from the implementation they are intended to own.",
      "confidence": "high",
      "duplicateScavenge": {
        "repeatedConcept": "package/root export normalization",
        "counterpartPaths": [
          "packages/riela/src/lib.ts",
          "packages/riela-core/src/index.ts",
          "packages/riela-addons/src/index.ts"
        ],
        "behavioralDifferences": [
          "Root src remains the compatibility API while package entrypoints become ownership roots."
        ],
        "consolidationTarget": "Package-owned entrypoint contract with root src compatibility shims.",
        "verificationSuggestions": [
          "bun test packages/riela/src/package-boundaries.test.ts",
          "bun run build"
        ]
      }
    }
  ],
  "proposedTasks": [
    {
      "taskId": "REF-001",
      "title": "Establish package source boundary contracts"
    }
  ],
  "conflictNotes": [
    "Duplicate-scavenge counterpart paths are review context only; this child review does not assign cross-slice write ownership.",
    "Root src remains a temporary compatibility surface until package-owned entrypoints pass verification.",
    "No provisioning package should be created because no concrete provisioning source surface was identified."
  ],
  "verificationSuggestions": [
    "bun run packages/riela/src/bin.ts workflow validate codex-refactoring-slice-review --workflow-definition-dir .riela/workflows",
    "bun run build"
  ],
  "residualRisks": [
    "No provisioning package is created without a concrete provisioning source surface."
  ]
}
```
