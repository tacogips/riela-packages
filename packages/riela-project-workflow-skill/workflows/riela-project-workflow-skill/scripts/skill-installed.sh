#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add guidance for turning requested work into a project-scope Riela workflow and executing that workflow.","skills":["codex:riela-project-workflow","claude:riela-project-workflow","cursor:riela-project-workflow"]}}
JSON
