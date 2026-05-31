#!/usr/bin/env sh
set -eu

mailbox_dir="${RIEL_MAILBOX_DIR:?RIEL_MAILBOX_DIR is required}"
output_path="${mailbox_dir}/outbox/output.json"

mkdir -p "$(dirname "$output_path")"

cat >"$output_path" <<'JSON'
{
  "payload": {
    "status": "ready",
    "message": "Install this package to add the rielflow-package skill for package search and project/user-scope installs.",
    "skills": [
      "codex:rielflow-package",
      "claude:rielflow-package"
    ]
  }
}
JSON
