#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add guidance for authoring packaged skills that teach agents how to use Riela workflows.","skills":["agents:agents","codex:riela-workflow-use-skill","claude:riela-workflow-use-skill"]}}
JSON
