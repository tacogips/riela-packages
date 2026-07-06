#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"This meta package ships the cursor-cli-developer-workflows dispatcher rule and pins the standard Cursor CLI developer workflow packages as dependencies; install each listed package explicitly.","skills":["cursor:cursor-cli-developer-workflows"],"packages":["cursor-cli-adversarial-implementation-review-loop","cursor-cli-deepdesign","cursor-cli-design-and-implement-review-loop","cursor-cli-fable-design-and-implement-review-loop","cursor-cli-impl-plan-completion-loop","cursor-cli-recent-change-quality-loop","cursor-cli-refactoring-divide-and-conquer","cursor-cli-refactoring-slice-review","cursor-cli-simple-work-package","cursor-cli-source-security-check-loop","cursor-cli-task-watchdog","cursor-cli-website-builder"]}}
JSON
