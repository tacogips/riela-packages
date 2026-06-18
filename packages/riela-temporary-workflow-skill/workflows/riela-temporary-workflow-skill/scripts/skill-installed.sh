#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add the riela-temporary-workflow skill for creating and running temporary workflows from inline JSON or JSON files.","skills":["codex:riela-temporary-workflow","claude:riela-temporary-workflow"]}}
JSON
