#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add the rielflow-package skill for package search and project/user-scope installs.","skills":["codex:rielflow-package","claude:rielflow-package"]}}
JSON
