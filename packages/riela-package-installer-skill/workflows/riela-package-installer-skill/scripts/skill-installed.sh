#!/usr/bin/env sh
set -eu

cat <<'JSON'
{"payload":{"status":"ready","message":"Install this package to add .codex and .claude bootstrap instructions for installing riela-package-manager-skill.","targetPackage":"riela-package-manager-skill","registry":"https://github.com/tacogips/riela-packages","skills":["codex:riela-package-installer","claude:riela-package-installer"]}}
JSON
