#!/usr/bin/env bash
set -euo pipefail

name="${1:-friend}"
if [[ -z "$name" ]]; then
  name="friend"
fi

timezone="${GREETING_TIMEZONE:-UTC}"
if [[ -z "$timezone" ]]; then
  timezone="UTC"
fi

greetings=("Hello" "Good morning" "Good afternoon" "Good evening" "Welcome back")
raw_index="${GREETING_INDEX:-0}"
if [[ ! "$raw_index" =~ ^-?[0-9]+$ ]]; then
  raw_index=0
fi
index=$(( raw_index < 0 ? -raw_index : raw_index ))
index=$(( index % ${#greetings[@]} ))
greeting="${greetings[$index]}"

iso="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
if local_time="$(TZ="$timezone" date +"%Y-%m-%d %H:%M:%S %Z" 2>/dev/null)"; then
  :
else
  timezone="UTC"
  local_time="$(TZ=UTC date +"%Y-%m-%d %H:%M:%S %Z")"
fi

python3 - "$greeting" "$name" "$iso" "$local_time" "$timezone" <<'PY'
import json
import sys

greeting, name, iso, local_time, timezone = sys.argv[1:]
payload = {
    "runtime": "local-bash",
    "greeting": greeting,
    "name": name,
    "message": f"{greeting}, {name}. The current time is {iso}.",
    "datetime": {
        "iso": iso,
        "local": local_time,
        "timezone": timezone,
    },
    "greetingsAvailable": [
        "Hello",
        "Good morning",
        "Good afternoon",
        "Good evening",
        "Welcome back",
    ],
}
json.dump(payload, sys.stdout, separators=(",", ":"))
sys.stdout.write("\n")
PY
