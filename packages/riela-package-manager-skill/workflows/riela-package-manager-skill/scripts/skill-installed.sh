#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add the riela-package skill for package search and project/user-scope installs.","skills":["codex:riela-package","claude:riela-package"]}}
JSON
