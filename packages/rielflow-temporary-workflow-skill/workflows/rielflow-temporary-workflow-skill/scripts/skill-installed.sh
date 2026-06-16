#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add the rielflow-temporary-workflow skill for creating and running temporary workflows from inline JSON or JSON files.","skills":["codex:rielflow-temporary-workflow","claude:rielflow-temporary-workflow"]}}
JSON
