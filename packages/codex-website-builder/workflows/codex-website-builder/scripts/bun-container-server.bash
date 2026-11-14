#!/usr/bin/env bash
set -euo pipefail

workflow_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_dir="$(pwd)"
runtime_dir="${repo_dir}/.riela/website-builder"
mkdir -p "$runtime_dir"
invocation_input="$(cat || true)"

if ! command -v docker >/dev/null 2>&1; then
  python3 - <<'PY'
import json
import sys

payload = {
    "dockerAvailable": False,
    "needs_implementation_revision": True,
    "error": "docker command is required for containerized Bun execution",
}
json.dump(payload, sys.stdout, separators=(",", ":"))
sys.stdout.write("\n")
PY
  exit 0
fi

config_shell="$(INVOCATION_INPUT="$invocation_input" python3 - <<'PY'
import json
import os
import re
import shlex
import sys
from pathlib import PurePosixPath

raw = os.environ.get("INVOCATION_INPUT", "").strip()
if raw:
    envelope = json.loads(raw.splitlines()[0])
else:
    envelope = {}
data = envelope.get("input") if isinstance(envelope, dict) else None
if not isinstance(data, dict):
    data = envelope if isinstance(envelope, dict) else {}

payloads = []
for entry in data.get("upstream", []):
    output = entry.get("output") if isinstance(entry, dict) else None
    payload = output.get("payload") if isinstance(output, dict) else None
    if isinstance(payload, dict):
        payloads.append(payload)

latest_outputs = data.get("latestOutputs")
if isinstance(latest_outputs, dict):
    for value in latest_outputs.values():
        if isinstance(value, dict):
            payload = value.get("payload")
            if isinstance(payload, dict):
                payloads.append(payload)

workflow_input = data.get("workflowInput")
if not isinstance(workflow_input, dict):
    workflow_input = {}

def first_string(keys, default=""):
    for payload in reversed(payloads + [workflow_input]):
        if not isinstance(payload, dict):
            continue
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return default

def first_int(keys, default):
    for payload in reversed(payloads + [workflow_input]):
        if not isinstance(payload, dict):
            continue
        for key in keys:
            value = payload.get(key)
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.isdigit():
                return int(value)
    return default

target = first_string(["targetDirectory"], "apps/codex-website")
target = target.replace("\\", "/").strip("/")
parts = PurePosixPath(target).parts
if not parts or any(part in ("", ".", "..") for part in parts):
    raise SystemExit(f"invalid targetDirectory: {target!r}")

review_url = first_string(["reviewUrl"], "")
port = first_int(["reviewPort", "port"], 4173)
match = re.search(r":([0-9]{2,5})(?:/|$)", review_url)
if match:
    port = int(match.group(1))
if not 1024 <= port <= 65535:
    port = 4173

start_command = first_string(["containerStartCommand", "startCommand"], "")
if not start_command:
    start_command = f"bun run dev -- --host 0.0.0.0 --port {port}"

build_command = first_string(["containerBuildCommand", "buildCommand"], "bun run build")

for name, value in {
    "TARGET_DIRECTORY": target,
    "REVIEW_PORT": str(port),
    "CONTAINER_START_COMMAND": start_command,
    "CONTAINER_BUILD_COMMAND": build_command,
}.items():
    print(f"{name}={shlex.quote(value)}")
PY
)"
eval "$config_shell"

target_host_dir="${repo_dir}/${TARGET_DIRECTORY}"
if [[ ! -d "$target_host_dir" ]]; then
  python3 - "$TARGET_DIRECTORY" <<'PY'
import json
import sys

payload = {
    "targetDirectory": sys.argv[1],
    "dockerAvailable": True,
    "needs_implementation_revision": True,
    "error": "targetDirectory does not exist; server-node must create the SolidJS app before Bun runs",
}
json.dump(payload, sys.stdout, separators=(",", ":"))
sys.stdout.write("\n")
PY
  exit 0
fi

if [[ ! -f "${target_host_dir}/package.json" ]]; then
  python3 - "$TARGET_DIRECTORY" <<'PY'
import json
import sys

payload = {
    "targetDirectory": sys.argv[1],
    "dockerAvailable": True,
    "needs_implementation_revision": True,
    "error": "package.json is missing; server-node must create a Bun/SolidJS package before Bun runs",
}
json.dump(payload, sys.stdout, separators=(",", ":"))
sys.stdout.write("\n")
PY
  exit 0
fi

image_tag="${WEBSITE_BUILDER_IMAGE_TAG:-}"
if [[ -z "$image_tag" || "$image_tag" == "{{workflowInput.bunImageTag}}" ]]; then
  image_tag="riela/codex-website-builder-bun:0.1.0"
fi
containerfile="${workflow_dir}/containers/bun-site-runner/Containerfile"
container_context="${workflow_dir}/containers/bun-site-runner"
container_name_source="$(printf '%s-%s' "$RIEL_WORKFLOW_EXECUTION_ID" "$TARGET_DIRECTORY" | tr '/:_ .' '-----')"
container_name="riela-website-${container_name_source:0:80}"
log_file="${runtime_dir}/${container_name}.log"
container_id_file="${runtime_dir}/${container_name}.cid"

docker build -t "$image_tag" -f "$containerfile" "$container_context" >"${runtime_dir}/${container_name}.build.log" 2>&1

docker rm -f "$container_name" >/dev/null 2>&1 || true

common_docker_args=(
  --cap-drop ALL
  --security-opt no-new-privileges
  --pids-limit 256
  --memory 1536m
  --cpus 2
  -v "${repo_dir}:/workspace"
  -w "/workspace/${TARGET_DIRECTORY}"
)

install_args=(install --ignore-scripts)
if [[ -f "${target_host_dir}/bun.lock" || -f "${target_host_dir}/bun.lockb" ]]; then
  install_args=(install --frozen-lockfile --ignore-scripts)
fi

docker run --rm "${common_docker_args[@]}" "$image_tag" bun "${install_args[@]}" >>"${runtime_dir}/${container_name}.build.log" 2>&1
docker run --rm "${common_docker_args[@]}" "$image_tag" sh -lc "$CONTAINER_BUILD_COMMAND" >>"${runtime_dir}/${container_name}.build.log" 2>&1

container_id="$(
  docker run -d \
    --name "$container_name" \
    "${common_docker_args[@]}" \
    -p "127.0.0.1:${REVIEW_PORT}:${REVIEW_PORT}" \
    "$image_tag" sh -lc "$CONTAINER_START_COMMAND" \
)"
printf '%s\n' "$container_id" > "$container_id_file"

health_url="http://127.0.0.1:${REVIEW_PORT}"
python3 - "$health_url" <<'PY'
import sys
import time
import urllib.request

url = sys.argv[1]
last = None
for _ in range(60):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if 200 <= response.status < 500:
                raise SystemExit(0)
    except Exception as exc:  # noqa: BLE001
        last = exc
    time.sleep(1)
raise SystemExit(f"server did not respond at {url}: {last}")
PY

docker logs "$container_name" > "$log_file" 2>&1 || true

python3 - \
  "$TARGET_DIRECTORY" \
  "$image_tag" \
  "$container_name" \
  "$container_id" \
  "$REVIEW_PORT" \
  "$health_url" \
  "$container_id_file" \
  "$log_file" \
  "$CONTAINER_BUILD_COMMAND" \
  "$CONTAINER_START_COMMAND" \
  "${install_args[*]}" <<'PY'
import json
import sys

(
    target_directory,
    image_tag,
    container_name,
    container_id,
    review_port,
    review_url,
    container_id_file,
    log_file,
    build_command,
    start_command,
    install_command,
) = sys.argv[1:]

payload = {
    "dockerAvailable": True,
    "targetDirectory": target_directory,
    "containerImage": image_tag,
    "containerName": container_name,
    "containerId": container_id,
    "reviewPort": int(review_port),
    "reviewUrl": review_url,
    "containerIdFile": container_id_file,
    "serverLogFile": log_file,
    "installCommand": f"bun {install_command}",
    "buildCommand": build_command,
    "serverCommand": start_command,
    "workspaceMount": "<repo>:/workspace",
    "bunRunsOnHost": False,
    "hasSourceChanges": True,
}
json.dump(payload, sys.stdout, separators=(",", ":"))
sys.stdout.write("\n")
PY
