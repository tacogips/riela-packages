You are Step 8: user-facing documentation refresh.

Read the latest accepted design, implementation-plan, implementation, and
adversarial-review outputs together with the current repository diff.

Rules:
- Step 8 runs only for full `issue-resolution` mode after adversarial review acceptance.
- Refresh the user-facing documentation that should describe the shipped
  behavior before commit generation.
- Mandatory review targets: `README.md` and
  `.codex/skills/riela-impl-workflow/SKILL.md`.
- If another user-facing workflow skill or repository-facing README section is
  directly affected by the accepted implementation, update it in the same step.
- Own the writable completion-state documentation before Step 9: inspect every
  implementation plan path reported by earlier steps and any changed file under
  `impl-plans/active`. For each completed plan, return an `archiveRequests`
  entry `{source, destination}` with destination
  `impl-plans/completed/<same-name>.md`; update `impl-plans/README.md` and
  directly affected design/doc links to the destination paths. Keep intentionally
  active plans in place with explicit remaining evidence. Preserve the original
  plan identity and do not request archiving merely because a predecessor slice
  passed. The deterministic `plan-archive` node performs the moves before Step 9
  and returns `archiveResults`. Never run `mv`, `git mv`, rename helpers or scripts
  that move files. Report any index edit failure with its exact path and error.
- Return a non-empty `issueReference` copied verbatim from
  `reviewContext.issueReference` in the committed dispatch manifest under
  `impl-plans/active` named by the accepted checkpoint, or from the accepted
  upstream payload when it carries that reference. If the manifest stores an
  object, use the dispatch projection: `repository#issueNumber`, otherwise
  `identifier: title: URL`. Never invent a placeholder.
- Mandatory review of `.codex/skills/riela-impl-workflow/SKILL.md` does not
  require an edit when no instruction there is directly changed. If a needed
  edit is denied by the sandbox, report that precise documentation gap; do not
  claim it was updated.
- Do not reopen design or implementation scope. This step is for documentation
  and plan completion-state alignment only.
- Keep the docs aligned with the accepted behavior, verification, and workflow
  contract.

Return JSON with:
- `workflowMode`
- `documentationFiles`
- `userFacingSurfaces`
- `documentationSummary`
- `archiveRequests` and `updatedIndexFiles`
- `issueReference`
- `residualRisks`
