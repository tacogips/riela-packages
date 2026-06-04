#!/usr/bin/env bash
set -euo pipefail

mailbox_dir="${RIEL_MAILBOX_DIR:?RIEL_MAILBOX_DIR is required}"
output_path="${mailbox_dir}/outbox/output.json"
mkdir -p "$(dirname "$output_path")"

name="${1:-friend}"
timezone="${GREETING_TIMEZONE:-UTC}"
index="${GREETING_INDEX:-1}"
timestamp="$(TZ="$timezone" date '+%Y-%m-%dT%H:%M:%S%z')"

printf '{"greeting":"Hello %s","greetingIndex":"%s","timezone":"%s","timestamp":"%s"}\n' "$name" "$index" "$timezone" "$timestamp" > "$output_path"
