#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add the rielflow-workflow skill for workflow bundle creation, validation, and execution. Install rielflow-workflow-skill-creator-skill when you need to author packaged usage skills for workflows.","skills":["codex:rielflow-workflow","claude:rielflow-workflow"]}}
JSON
