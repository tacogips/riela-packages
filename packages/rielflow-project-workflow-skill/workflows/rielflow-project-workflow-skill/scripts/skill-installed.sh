#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add guidance for turning requested work into a project-scope Rielflow workflow and executing that workflow.","skills":["codex:rielflow-project-workflow","claude:rielflow-project-workflow","cursor:rielflow-project-workflow"]}}
JSON
