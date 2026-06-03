# Project Codex Deepdesign

This package contains the `codex-deepdesign` rielflow workflow and Codex skill.

Keep package changes focused on the workflow bundle and skill guidance. Preserve the loop contract: Node 2 and Node 3 return to Node 1 for any `high` or `middle` finding, and final output occurs only after both reviewers accept the latest design.

When the workflow encounters a user confirmation point, it should continue with the generally preferable conservative specification and document the provisional decision for later review.

Update `rielflow-package.json` digests after edits.
