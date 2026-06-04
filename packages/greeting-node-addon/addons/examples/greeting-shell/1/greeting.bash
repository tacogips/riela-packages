#!/usr/bin/env bash
set -euo pipefail

mailbox_dir="${RIEL_MAILBOX_DIR:?RIEL_MAILBOX_DIR is required}"
output_path="${mailbox_dir}/outbox/output.json"
mkdir -p "$(dirname "$output_path")"

if ! command -v jq >/dev/null 2>&1; then
  echo "greeting.bash requires jq to encode JSON output" >&2
  exit 127
fi

name="${1:-friend}"
timezone="${GREETING_TIMEZONE:-UTC}"
index="${GREETING_INDEX:-1}"
timestamp="$(TZ="$timezone" date '+%Y-%m-%dT%H:%M:%S%z')"
tmp_output="$(mktemp "${output_path}.XXXXXX")"
trap 'rm -f "$tmp_output"' EXIT

jq -n \
  --arg greeting "Hello ${name}" \
  --arg greetingIndex "$index" \
  --arg timezone "$timezone" \
  --arg timestamp "$timestamp" \
  '{
    greeting: $greeting,
    greetingIndex: $greetingIndex,
    timezone: $timezone,
    timestamp: $timestamp
  }' > "$tmp_output"

mv "$tmp_output" "$output_path"
trap - EXIT
