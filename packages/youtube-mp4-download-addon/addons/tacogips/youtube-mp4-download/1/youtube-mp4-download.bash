#!/usr/bin/env bash
set -euo pipefail

url="${1:-}"
yt_dlp_path="${2:-}"
output_directory="${3:-}"
file_name_template="${4:-}"
format_selector="${5:-}"
node_path="${6:-}"

if [ -z "$url" ]; then
  echo "youtube-mp4-download requires a non-empty URL" >&2
  exit 2
fi
if [ -z "${RIEL_MAILBOX_DIR:-}" ]; then
  echo "RIEL_MAILBOX_DIR is not set" >&2
  exit 2
fi

yt_dlp_path="${yt_dlp_path:-yt-dlp}"
output_directory="${output_directory:-video}"
file_name_template="${file_name_template:-%(title).200B-%(id)s.%(ext)s}"
format_selector="${format_selector:-bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best}"
node_path="${node_path:-node}"

outbox_dir="$RIEL_MAILBOX_DIR/outbox"
files_dir="$outbox_dir/files/$output_directory"
mkdir -p "$files_dir"

"$yt_dlp_path" \
  --no-playlist \
  --restrict-filenames \
  --merge-output-format mp4 \
  --format "$format_selector" \
  --output "$files_dir/$file_name_template" \
  "$url"

mp4_path="$(find "$files_dir" -type f -name '*.mp4' -print | sort | tail -n 1)"
if [ -z "$mp4_path" ] || [ ! -f "$mp4_path" ]; then
  echo "yt-dlp completed but no MP4 file was produced in $files_dir" >&2
  exit 1
fi

file_name="$(basename "$mp4_path")"
file_size="$(wc -c < "$mp4_path" | tr -d ' ')"
mkdir -p "$outbox_dir"

URL="$url" \
MP4_PATH="$mp4_path" \
FILE_NAME="$file_name" \
FILE_SIZE="$file_size" \
"$node_path" <<'NODE' > "$outbox_dir/output.json"
const payload = {
  youtubeMp4Download: {
    status: "downloaded",
    url: process.env.URL,
    outputPath: process.env.MP4_PATH,
    fileName: process.env.FILE_NAME,
    fileSize: Number(process.env.FILE_SIZE ?? "0")
  }
};
Object.assign(payload, {
  downloadStatus: payload.youtubeMp4Download.status,
  url: payload.youtubeMp4Download.url,
  outputPath: payload.youtubeMp4Download.outputPath,
  fileName: payload.youtubeMp4Download.fileName,
  fileSize: payload.youtubeMp4Download.fileSize
});
process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
NODE
