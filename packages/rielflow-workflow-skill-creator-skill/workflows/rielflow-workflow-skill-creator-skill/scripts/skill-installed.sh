#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add guidance for authoring packaged skills that teach agents how to use Rielflow workflows.","skills":["agents:agents","codex:rielflow-workflow-use-skill","claude:rielflow-workflow-use-skill"]}}
JSON
