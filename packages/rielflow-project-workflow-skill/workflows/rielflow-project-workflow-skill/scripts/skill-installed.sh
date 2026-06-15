#!/usr/bin/env sh
set -eu

mailbox_dir="${RIEL_MAILBOX_DIR:?RIEL_MAILBOX_DIR is required}"
output_path="${mailbox_dir}/outbox/output.json"

mkdir -p "$(dirname "$output_path")"

cat >"$output_path" <<'JSON'
{
  "payload": {
    "status": "ready",
    "message": "Install this package to add guidance for turning requested work into a project-scope Rielflow workflow and executing that workflow.",
    "skills": [
      "codex:rielflow-project-workflow",
      "claude:rielflow-project-workflow",
      "cursor:rielflow-project-workflow"
    ]
  }
}
JSON
