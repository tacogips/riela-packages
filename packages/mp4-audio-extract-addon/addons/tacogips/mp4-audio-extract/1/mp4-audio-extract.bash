#!/usr/bin/env bash
set -euo pipefail

mp4_path="${1:-}"
ffmpeg_path="${2:-}"
sample_rate_hertz="${3:-}"
audio_channel_count="${4:-}"
node_path="${5:-}"
output_directory="${6:-}"

if [ -z "$mp4_path" ]; then
  echo "mp4-audio-extract requires a non-empty MP4 path" >&2
  exit 2
fi
if [ ! -f "$mp4_path" ]; then
  echo "MP4 file not found: $mp4_path" >&2
  exit 2
fi
if [ -z "${RIEL_MAILBOX_DIR:-}" ]; then
  echo "RIEL_MAILBOX_DIR is not set" >&2
  exit 2
fi

ffmpeg_path="${ffmpeg_path:-ffmpeg}"
sample_rate_hertz="${sample_rate_hertz:-16000}"
audio_channel_count="${audio_channel_count:-1}"
node_path="${node_path:-node}"
output_directory="${output_directory:-audio}"

outbox_dir="$RIEL_MAILBOX_DIR/outbox"
files_dir="$outbox_dir/files/$output_directory"
audio_path="$files_dir/extracted.flac"
mkdir -p "$files_dir"

"$ffmpeg_path" \
  -hide_banner \
  -loglevel error \
  -y \
  -i "$mp4_path" \
  -vn \
  -ac "$audio_channel_count" \
  -ar "$sample_rate_hertz" \
  -c:a flac \
  "$audio_path"

audio_size="$(wc -c < "$audio_path" | tr -d ' ')"
source_file_name="$(basename "$mp4_path")"
artifact_path="$output_directory/extracted.flac"
mkdir -p "$outbox_dir"

AUDIO_PATH="$audio_path" \
AUDIO_SIZE="$audio_size" \
SOURCE_FILE_NAME="$source_file_name" \
ARTIFACT_PATH="$artifact_path" \
SAMPLE_RATE_HERTZ="$sample_rate_hertz" \
AUDIO_CHANNEL_COUNT="$audio_channel_count" \
"$node_path" <<'NODE' > "$outbox_dir/output.json"
const payload = {
  audioExtract: {
    audioPath: process.env.AUDIO_PATH,
    fileSize: Number(process.env.AUDIO_SIZE ?? "0"),
    metadata: {
      provider: "ffmpeg",
      sourceFileName: process.env.SOURCE_FILE_NAME,
      audioArtifactPath: process.env.ARTIFACT_PATH,
      sampleRateHertz: Number(process.env.SAMPLE_RATE_HERTZ ?? "16000"),
      audioChannelCount: Number(process.env.AUDIO_CHANNEL_COUNT ?? "1")
    }
  }
};
process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
NODE
