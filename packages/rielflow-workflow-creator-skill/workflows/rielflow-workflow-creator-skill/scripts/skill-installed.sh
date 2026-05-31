#!/usr/bin/env sh
set -eu

mailbox_dir="${RIEL_MAILBOX_DIR:?RIEL_MAILBOX_DIR is required}"
output_path="${mailbox_dir}/outbox/output.json"

mkdir -p "$(dirname "$output_path")"

cat >"$output_path" <<'JSON'
{
  "payload": {
    "status": "ready",
    "message": "Install this package to add the rielflow-workflow skill for workflow creation, validation, and execution.",
    "skills": [
      "codex:rielflow-workflow",
      "claude:rielflow-workflow"
    ]
  }
}
JSON
