#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
workflow_dir="$(cd "$script_dir/.." && pwd)"
context_dir="$workflow_dir/containers/youtube-shorts-to-text"
image="${YOUTUBE_SHORTS_TO_TEXT_IMAGE:-riela/youtube-shorts-to-text:0.1.0}"
docker_bin="${DOCKER_BIN:-docker}"

if [ -z "$image" ]; then
  image="riela/youtube-shorts-to-text:0.1.0"
fi

"$docker_bin" build -f "$context_dir/Containerfile" -t "$image" "$context_dir"
