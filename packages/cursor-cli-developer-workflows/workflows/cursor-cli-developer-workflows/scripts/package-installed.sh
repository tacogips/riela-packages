#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add the standard Cursor CLI developer workflow packages.","skills":[],"packages":["cursor-cli-adversarial-implementation-review-loop","cursor-cli-deepdesign","cursor-cli-design-and-implement-review-loop","cursor-cli-fable-design-and-implement-review-loop","cursor-cli-impl-plan-completion-loop","cursor-cli-recent-change-quality-loop","cursor-cli-refactoring-divide-and-conquer","cursor-cli-refactoring-slice-review","cursor-cli-simple-work-package","cursor-cli-source-security-check-loop","cursor-cli-task-watchdog","cursor-cli-website-builder"]}}
JSON
