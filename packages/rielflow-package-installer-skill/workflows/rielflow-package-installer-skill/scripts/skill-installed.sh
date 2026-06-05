#!/usr/bin/env sh
set -eu

mailbox_dir="${RIEL_MAILBOX_DIR:?RIEL_MAILBOX_DIR is required}"
output_path="${mailbox_dir}/outbox/output.json"

mkdir -p "$(dirname "$output_path")"

cat >"$output_path" <<'JSON'
{
  "payload": {
    "status": "ready",
    "message": "Install this package to add .codex and .claude bootstrap instructions for installing rielflow-package-manager-skill.",
    "targetPackage": "rielflow-package-manager-skill",
    "registry": "https://github.com/tacogips/rielflow-packages",
    "skills": [
      "codex:rielflow-package-installer",
      "claude:rielflow-package-installer"
    ]
  }
}
JSON
