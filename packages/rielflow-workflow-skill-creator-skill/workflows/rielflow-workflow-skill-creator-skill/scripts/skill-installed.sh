#!/usr/bin/env sh
set -eu

mailbox_dir="${RIEL_MAILBOX_DIR:?RIEL_MAILBOX_DIR is required}"
output_path="${mailbox_dir}/outbox/output.json"

mkdir -p "$(dirname "$output_path")"

cat >"$output_path" <<'JSON'
{
  "payload": {
    "status": "ready",
    "message": "Install this package to add guidance for authoring packaged skills that teach agents how to use Rielflow workflows.",
    "skills": [
      "agents:agents",
      "codex:rielflow-workflow-use-skill",
      "claude:rielflow-workflow-use-skill"
    ]
  }
}
JSON
