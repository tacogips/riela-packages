#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add the riela-workflow skill for workflow bundle creation, validation, and execution. Install riela-workflow-skill-creator-skill when you need to author packaged usage skills for workflows.","skills":["codex:riela-workflow","claude:riela-workflow"]}}
JSON
