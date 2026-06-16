#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add AGENTS.md maintainer guidance for updating rielflow package manifests, validating package payloads, and preparing registry releases.","skills":["agents:agents","codex:rielflow-package-release","claude:rielflow-package-release"],"digestScript":".rielflow/workflows/rielflow-package-release-skill/scripts/update-package-digests.ts"}}
JSON
