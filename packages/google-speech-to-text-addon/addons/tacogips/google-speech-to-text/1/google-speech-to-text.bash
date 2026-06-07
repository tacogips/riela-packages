#!/usr/bin/env bash
set -euo pipefail

audio_path="${1:-}"
language_code="${2:-}"
gcs_uri_prefix="${3:-}"

if [ -z "$audio_path" ]; then
  echo "google-speech-to-text requires a non-empty audio path" >&2
  exit 2
fi
if [ ! -f "$audio_path" ]; then
  echo "Audio file not found: $audio_path" >&2
  exit 2
fi
if [ -z "$gcs_uri_prefix" ]; then
  echo "google-speech-to-text requires gcsUriPrefix, for example gs://bucket/path-prefix" >&2
  exit 2
fi
case "$gcs_uri_prefix" in
  gs://*) ;;
  *)
    echo "gcsUriPrefix must start with gs://: $gcs_uri_prefix" >&2
    exit 2
    ;;
esac
if [ -z "${RIEL_MAILBOX_DIR:-}" ]; then
  echo "RIEL_MAILBOX_DIR is not set" >&2
  exit 2
fi

language_code="${language_code:-ja-JP}"
encoding="FLAC"
sample_rate_hertz="16000"
audio_channel_count="1"
output_formats="json,txt,srt,vtt"
output_base_name="transcript"
node_bin="${NODE_BIN:-node}"
curl_path="${CURL_PATH:-curl}"
gcloud_path="${GCLOUD_PATH:-gcloud}"
poll_interval_seconds="${GOOGLE_SPEECH_POLL_INTERVAL_SECONDS:-15}"
operation_timeout_seconds="${GOOGLE_SPEECH_OPERATION_TIMEOUT_SECONDS:-14400}"

outbox_dir="$RIEL_MAILBOX_DIR/outbox"
files_dir="$outbox_dir/files/transcripts"
tmp_dir="$outbox_dir/tmp"
mkdir -p "$files_dir" "$tmp_dir"

access_token="$("$node_bin" <<'NODE'
const crypto = require("node:crypto");
const fs = require("node:fs");
const https = require("node:https");

function postForm(url, fields) {
  const body = new URLSearchParams(fields).toString();
  return new Promise((resolve, reject) => {
    const request = https.request(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": Buffer.byteLength(body)
      }
    }, (response) => {
      let data = "";
      response.setEncoding("utf8");
      response.on("data", (chunk) => {
        data += chunk;
      });
      response.on("end", () => {
        if (response.statusCode < 200 || response.statusCode >= 300) {
          reject(new Error(`token endpoint returned HTTP ${response.statusCode}`));
          return;
        }
        resolve(JSON.parse(data));
      });
    });
    request.on("error", reject);
    request.end(body);
  });
}

function base64url(input) {
  return Buffer.from(input)
    .toString("base64")
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replace(/=+$/u, "");
}

async function tokenFromServiceAccount(credentials) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: "RS256", typ: "JWT" };
  const claim = {
    iss: credentials.client_email,
    scope: "https://www.googleapis.com/auth/cloud-platform",
    aud: "https://oauth2.googleapis.com/token",
    iat: now,
    exp: now + 3600
  };
  const unsigned = `${base64url(JSON.stringify(header))}.${base64url(JSON.stringify(claim))}`;
  const signature = crypto
    .createSign("RSA-SHA256")
    .update(unsigned)
    .sign(credentials.private_key);
  const assertion = `${unsigned}.${base64url(signature)}`;
  const response = await postForm("https://oauth2.googleapis.com/token", {
    grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
    assertion
  });
  return response.access_token;
}

async function tokenFromAuthorizedUser(credentials) {
  const response = await postForm("https://oauth2.googleapis.com/token", {
    grant_type: "refresh_token",
    client_id: credentials.client_id,
    client_secret: credentials.client_secret,
    refresh_token: credentials.refresh_token
  });
  return response.access_token;
}

async function main() {
  if (process.env.GOOGLE_ACCESS_TOKEN) {
    process.stdout.write(process.env.GOOGLE_ACCESS_TOKEN);
    return;
  }
  let raw = process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON;
  if (!raw && process.env.GOOGLE_APPLICATION_CREDENTIALS) {
    raw = fs.readFileSync(process.env.GOOGLE_APPLICATION_CREDENTIALS, "utf8");
  }
  if (!raw) {
    return;
  }
  const credentials = JSON.parse(raw);
  let token;
  if (credentials.type === "service_account") {
    token = await tokenFromServiceAccount(credentials);
  } else if (credentials.type === "authorized_user") {
    token = await tokenFromAuthorizedUser(credentials);
  }
  if (token) {
    process.stdout.write(token);
  }
}

main().catch(() => {
  process.exit(0);
});
NODE
)"

if [ -z "$access_token" ]; then
  if command -v "$gcloud_path" >/dev/null 2>&1; then
    access_token="$("$gcloud_path" auth application-default print-access-token 2>/dev/null || true)"
  fi
fi
if [ -z "$access_token" ]; then
  if command -v "$gcloud_path" >/dev/null 2>&1; then
    access_token="$("$gcloud_path" auth print-access-token 2>/dev/null || true)"
  fi
fi
if [ -z "$access_token" ]; then
  echo "Google access token is unavailable. Set GOOGLE_ACCESS_TOKEN, GOOGLE_APPLICATION_CREDENTIALS_JSON, GOOGLE_APPLICATION_CREDENTIALS, or configure gcloud credentials." >&2
  exit 2
fi

gcs_plan_json="$tmp_dir/google-speech-gcs-plan.json"
"$node_bin" - "$audio_path" "$gcs_uri_prefix" > "$gcs_plan_json" <<'NODE'
const path = require("node:path");
const [audioPath, gcsUriPrefix] = process.argv.slice(2);
const withoutScheme = gcsUriPrefix.replace(/^gs:\/\//u, "").replace(/\/+$/u, "");
const slash = withoutScheme.indexOf("/");
const bucket = slash === -1 ? withoutScheme : withoutScheme.slice(0, slash);
const prefix = slash === -1 ? "" : withoutScheme.slice(slash + 1);
if (!bucket) {
  throw new Error("missing GCS bucket");
}
const baseName = path.basename(audioPath).replace(/[^A-Za-z0-9._-]/g, "_");
const objectName = [prefix, `${Date.now()}-${baseName}`].filter(Boolean).join("/");
const uploadUrl = `https://storage.googleapis.com/upload/storage/v1/b/${encodeURIComponent(bucket)}/o?uploadType=media&name=${encodeURIComponent(objectName)}`;
process.stdout.write(JSON.stringify({
  bucket,
  objectName,
  gcsUri: `gs://${bucket}/${objectName}`,
  uploadUrl
}));
NODE

gcs_uri="$("$node_bin" - "$gcs_plan_json" <<'NODE'
const fs = require("node:fs");
const plan = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
process.stdout.write(plan.gcsUri);
NODE
)"
upload_url="$("$node_bin" - "$gcs_plan_json" <<'NODE'
const fs = require("node:fs");
const plan = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
process.stdout.write(plan.uploadUrl);
NODE
)"

upload_response_json="$files_dir/${output_base_name}.gcs-upload.json"
upload_status="$("$curl_path" \
  --silent \
  --show-error \
  --write-out '%{http_code}' \
  --output "$upload_response_json" \
  --request POST \
  --header "Authorization: Bearer $access_token" \
  --header "Content-Type: application/octet-stream" \
  --data-binary "@$audio_path" \
  "$upload_url")"

case "$upload_status" in
  2*) ;;
  *)
    echo "Google Cloud Storage upload failed with HTTP $upload_status" >&2
    cat "$upload_response_json" >&2
    exit 1
    ;;
esac

request_json="$tmp_dir/google-speech-longrunning-request.json"
operation_start_json="$files_dir/${output_base_name}.operation-start.json"
response_json="$files_dir/${output_base_name}.google-response.json"
transcript_txt="$files_dir/${output_base_name}.txt"
transcript_srt="$files_dir/${output_base_name}.srt"
transcript_vtt="$files_dir/${output_base_name}.vtt"

"$node_bin" - "$gcs_uri" "$language_code" "$encoding" "$sample_rate_hertz" "$audio_channel_count" > "$request_json" <<'NODE'
const [gcsUri, languageCode, encoding, sampleRateHertz, audioChannelCount] = process.argv.slice(2);
const config = {
  languageCode,
  encoding,
  sampleRateHertz: Number(sampleRateHertz),
  audioChannelCount: Number(audioChannelCount),
  enableAutomaticPunctuation: true,
  enableWordTimeOffsets: true
};
const audio = { uri: gcsUri };
process.stdout.write(JSON.stringify({ config, audio }));
NODE

start_status="$("$curl_path" \
  --silent \
  --show-error \
  --write-out '%{http_code}' \
  --output "$operation_start_json" \
  --request POST \
  --header "Authorization: Bearer $access_token" \
  --header "Content-Type: application/json" \
  --data-binary "@$request_json" \
  "https://speech.googleapis.com/v1/speech:longrunningrecognize")"

case "$start_status" in
  2*) ;;
  *)
    echo "Google Speech-to-Text longrunning request failed with HTTP $start_status" >&2
    cat "$operation_start_json" >&2
    exit 1
    ;;
esac

operation_name="$("$node_bin" - "$operation_start_json" <<'NODE'
const fs = require("node:fs");
const response = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
if (!response.name) {
  process.exit(1);
}
process.stdout.write(response.name);
NODE
)"

deadline=$(( $(date +%s) + operation_timeout_seconds ))
while true; do
  now="$(date +%s)"
  if [ "$now" -gt "$deadline" ]; then
    echo "Google Speech-to-Text operation timed out after ${operation_timeout_seconds}s: $operation_name" >&2
    exit 1
  fi

  poll_status="$("$curl_path" \
    --silent \
    --show-error \
    --write-out '%{http_code}' \
    --output "$response_json" \
    --request GET \
    --header "Authorization: Bearer $access_token" \
    "https://speech.googleapis.com/v1/operations/$operation_name")"
  case "$poll_status" in
    2*) ;;
    *)
      echo "Google Speech-to-Text operation poll failed with HTTP $poll_status" >&2
      cat "$response_json" >&2
      exit 1
      ;;
  esac

  done_value="$("$node_bin" - "$response_json" <<'NODE'
const fs = require("node:fs");
const response = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
process.stdout.write(response.done === true ? "true" : "false");
NODE
)"
  if [ "$done_value" = "true" ]; then
    break
  fi
  sleep "$poll_interval_seconds"
done

"$node_bin" - "$response_json" "$output_formats" "$transcript_txt" "$transcript_srt" "$transcript_vtt" "$language_code" "$audio_path" "$gcs_uri" "$operation_name" > "$outbox_dir/output.json" <<'NODE'
const fs = require("node:fs");
const [responseJsonPath, outputFormatsRaw, txtPath, srtPath, vttPath, languageCode, audioPath, gcsUri, operationName] = process.argv.slice(2);
const operation = JSON.parse(fs.readFileSync(responseJsonPath, "utf8"));
if (operation.error !== undefined) {
  throw new Error(`Google Speech-to-Text operation failed: ${JSON.stringify(operation.error)}`);
}
const response = operation.response ?? operation;
const formats = new Set(outputFormatsRaw.split(",").map((entry) => entry.trim()).filter(Boolean));

function parseGoogleTime(value) {
  if (typeof value !== "string" || !value.endsWith("s")) {
    return 0;
  }
  return Number(value.slice(0, -1)) || 0;
}

function srtTime(seconds) {
  const totalMs = Math.max(0, Math.round(seconds * 1000));
  const ms = totalMs % 1000;
  const totalSeconds = Math.floor(totalMs / 1000);
  const sec = totalSeconds % 60;
  const totalMinutes = Math.floor(totalSeconds / 60);
  const min = totalMinutes % 60;
  const hour = Math.floor(totalMinutes / 60);
  return `${String(hour).padStart(2, "0")}:${String(min).padStart(2, "0")}:${String(sec).padStart(2, "0")},${String(ms).padStart(3, "0")}`;
}

function vttTime(seconds) {
  return srtTime(seconds).replace(",", ".");
}

const segments = [];
for (const result of response.results ?? []) {
  const alternative = result.alternatives?.[0];
  if (alternative === undefined) {
    continue;
  }
  const words = alternative.words ?? [];
  const start = words.length > 0 ? parseGoogleTime(words[0].startTime) : 0;
  let end = words.length > 0 ? parseGoogleTime(words[words.length - 1].endTime) : start + 1;
  if (end <= start) {
    end = start + 1;
  }
  segments.push({
    transcript: alternative.transcript ?? "",
    confidence: alternative.confidence,
    start,
    end
  });
}
const transcript = segments
  .map((segment) => segment.transcript)
  .filter(Boolean)
  .join("\n")
  .trim();

const outputFiles = { json: responseJsonPath };
const captions = {};
if (formats.has("txt")) {
  fs.writeFileSync(txtPath, `${transcript}\n`, "utf8");
  outputFiles.txt = txtPath;
}
if (formats.has("srt")) {
  const srt = segments
    .map((segment, index) => `${index + 1}\n${srtTime(segment.start)} --> ${srtTime(segment.end)}\n${segment.transcript}\n`)
    .join("\n");
  fs.writeFileSync(srtPath, `${srt}\n`, "utf8");
  outputFiles.srt = srtPath;
  captions.srt = srt;
}
if (formats.has("vtt")) {
  const vttBody = segments
    .map((segment) => `${vttTime(segment.start)} --> ${vttTime(segment.end)}\n${segment.transcript}\n`)
    .join("\n");
  const vtt = `WEBVTT\n\n${vttBody}`;
  fs.writeFileSync(vttPath, `${vtt}\n`, "utf8");
  outputFiles.vtt = vttPath;
  captions.vtt = vtt;
}

const payload = {
  googleSpeechToText: {
    transcript,
    languageCode,
    audioPath,
    gcsUri,
    operationName,
    responsePath: responseJsonPath,
    outputFiles,
    captions,
    segments,
    resultCount: Array.isArray(response.results) ? response.results.length : 0,
    provider: "google-cloud-speech-to-text-v1",
    method: "longrunningrecognize"
  },
  transcript,
  transcriptPath: outputFiles.txt ?? null
};
process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
NODE
