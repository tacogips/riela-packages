#!/usr/bin/env bash
set -euo pipefail

url="${1:-}"
language_code="${2:-}"
gcs_uri_prefix="${3:-}"

if [ -z "$url" ]; then
  echo "youtube-shorts-to-text-container requires workflowInput.url" >&2
  exit 2
fi

language_code="${language_code:-ja-JP}"
image="${YOUTUBE_SHORTS_TO_TEXT_IMAGE:-riela/youtube-shorts-to-text:0.1.0}"
if [ -z "$image" ]; then
  image="riela/youtube-shorts-to-text:0.1.0"
fi
docker_bin="${DOCKER_BIN:-docker}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
workflow_dir="$(cd "$script_dir/.." && pwd)"
context_dir="$workflow_dir/containers/youtube-shorts-to-text"
artifact_root="${RIELA_ARTIFACT_DIR:-${RIEL_ARTIFACT_DIR:-.riela/artifacts}}"
run_id="${RIELA_NODE_EXEC_ID:-manual-$(date +%Y%m%dT%H%M%S)}"
safe_run_id="$(printf '%s' "$run_id" | tr -c 'A-Za-z0-9._-' '_')"
output_dir="$artifact_root/youtube-shorts-to-text-container/$safe_run_id"
mkdir -p "$output_dir"

if ! command -v "$docker_bin" >/dev/null 2>&1; then
  echo "Docker executable not found: $docker_bin" >&2
  exit 2
fi

if ! "$docker_bin" image inspect "$image" >/dev/null 2>&1; then
  if [ "${YOUTUBE_SHORTS_TO_TEXT_SKIP_BUILD:-}" = "1" ]; then
    echo "Docker image not found and auto-build is disabled: $image" >&2
    exit 2
  fi
  "$docker_bin" build -f "$context_dir/Containerfile" -t "$image" "$context_dir" >&2
fi

docker_args=(
  run
  --rm
  -i
  --network
  bridge
  -v
  "$output_dir:/work/out"
  -e
  "HOST_OUTPUT_DIR=$output_dir"
  -e
  "GOOGLE_SPEECH_POLL_INTERVAL_SECONDS=${GOOGLE_SPEECH_POLL_INTERVAL_SECONDS:-15}"
  -e
  "GOOGLE_SPEECH_OPERATION_TIMEOUT_SECONDS=${GOOGLE_SPEECH_OPERATION_TIMEOUT_SECONDS:-14400}"
)

for env_name in GOOGLE_ACCESS_TOKEN GOOGLE_APPLICATION_CREDENTIALS_JSON YOUTUBE_SHORTS_TO_TEXT_KEEP_GCS_OBJECT; do
  if [ -n "${!env_name:-}" ]; then
    docker_args+=(-e "$env_name")
  fi
done

if [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]; then
  if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "GOOGLE_APPLICATION_CREDENTIALS points to a missing file" >&2
    exit 2
  fi
  docker_args+=(
    -v
    "$GOOGLE_APPLICATION_CREDENTIALS:/work/credentials/google-credentials.json:ro"
    -e
    "GOOGLE_APPLICATION_CREDENTIALS=/work/credentials/google-credentials.json"
  )
fi

docker_args+=(
  "$image"
  "$url"
  "$language_code"
  "$gcs_uri_prefix"
)

"$docker_bin" "${docker_args[@]}"
