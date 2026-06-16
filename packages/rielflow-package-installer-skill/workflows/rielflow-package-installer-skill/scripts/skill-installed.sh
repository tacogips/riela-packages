#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add .codex and .claude bootstrap instructions for installing rielflow-package-manager-skill.","targetPackage":"rielflow-package-manager-skill","registry":"https://github.com/tacogips/rielflow-packages","skills":["codex:rielflow-package-installer","claude:rielflow-package-installer"]}}
JSON
