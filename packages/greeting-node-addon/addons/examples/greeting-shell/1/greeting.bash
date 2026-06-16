#!/usr/bin/env bash
set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "greeting.bash requires jq to encode JSON output" >&2
  exit 127
fi

name="${1:-friend}"
timezone="${GREETING_TIMEZONE:-UTC}"
index="${GREETING_INDEX:-1}"
timestamp="$(TZ="$timezone" date '+%Y-%m-%dT%H:%M:%S%z')"

jq -nc \
  --arg greeting "Hello ${name}" \
  --arg greetingIndex "$index" \
  --arg timezone "$timezone" \
  --arg timestamp "$timestamp" \
  '{
    greeting: $greeting,
    greetingIndex: $greetingIndex,
    timezone: $timezone,
    timestamp: $timestamp
  }'
