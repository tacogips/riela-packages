#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add AGENTS.md maintainer guidance for updating riela package manifests, validating package payloads, and preparing registry releases.","skills":["agents:agents","codex:riela-package-release","claude:riela-package-release"],"digestScript":".riela/workflows/riela-package-release-skill/scripts/update-package-digests.ts"}}
JSON
