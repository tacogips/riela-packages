#!/usr/bin/env sh
set -eu

mailbox_dir="${RIEL_MAILBOX_DIR:?RIEL_MAILBOX_DIR is required}"
output_path="${mailbox_dir}/outbox/output.json"

mkdir -p "$(dirname "$output_path")"

cat >"$output_path" <<'JSON'
{
  "payload": {
    "status": "ready",
    "message": "Install this package to add the rielflow-temporary-workflow skill for creating and running temporary workflows from inline JSON or JSON files.",
    "skills": [
      "codex:rielflow-temporary-workflow",
      "claude:rielflow-temporary-workflow"
    ]
  }
}
JSON
