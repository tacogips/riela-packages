#!/usr/bin/env python3
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


def fail(message, code=1):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def run(command):
    print("+ " + " ".join(command), file=sys.stderr)
    subprocess.run(command, check=True, stdout=sys.stderr, stderr=sys.stderr)


def json_request(url, method="GET", token=None, body=None, content_type="application/json"):
    data = None
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        raw = response.read()
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def bytes_request(url, method="GET", token=None, data=None, content_type="application/octet-stream"):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=300) as response:
        raw = response.read()
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def b64url(data):
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def access_token_from_credentials(credentials):
    token_uri = credentials.get("token_uri", "https://oauth2.googleapis.com/token")
    if credentials.get("type") == "authorized_user":
        form = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "refresh_token": credentials["refresh_token"],
        }).encode("utf-8")
        request = urllib.request.Request(token_uri, data=form, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))["access_token"]

    if credentials.get("type") != "service_account":
        fail("Unsupported Google credential type", 2)

    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claim = {
        "iss": credentials["client_email"],
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "aud": token_uri,
        "iat": now,
        "exp": now + 3600,
    }
    unsigned = f"{b64url(json.dumps(header, separators=(',', ':')).encode())}.{b64url(json.dumps(claim, separators=(',', ':')).encode())}"
    with tempfile.NamedTemporaryFile("w", delete=False) as key_file:
        key_file.write(credentials["private_key"])
        key_path = key_file.name
    try:
        signature = subprocess.check_output(["openssl", "dgst", "-sha256", "-sign", key_path], input=unsigned.encode("ascii"))
    finally:
        try:
            os.unlink(key_path)
        except OSError:
            pass
    assertion = f"{unsigned}.{b64url(signature)}"
    form = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion,
    }).encode("utf-8")
    request = urllib.request.Request(token_uri, data=form, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))["access_token"]


def google_access_token():
    token = os.environ.get("GOOGLE_ACCESS_TOKEN")
    if token:
        return token
    raw = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not raw and os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        raw = Path(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]).read_text(encoding="utf-8")
    if not raw:
        fail("Google credentials unavailable. Set GOOGLE_ACCESS_TOKEN, GOOGLE_APPLICATION_CREDENTIALS_JSON, or GOOGLE_APPLICATION_CREDENTIALS.", 2)
    return access_token_from_credentials(json.loads(raw))


def parse_gcs_prefix(prefix):
    if not prefix.startswith("gs://"):
        fail(f"gcsUriPrefix must start with gs://: {prefix}", 2)
    without_scheme = prefix[5:].rstrip("/")
    bucket, _, path_prefix = without_scheme.partition("/")
    if not bucket:
        fail("gcsUriPrefix is missing a bucket", 2)
    return bucket, path_prefix


def upload_to_gcs(audio_path, prefix, token):
    bucket, path_prefix = parse_gcs_prefix(prefix)
    object_name = "/".join(part for part in [path_prefix, f"{int(time.time())}-{uuid.uuid4().hex}-{audio_path.name}"] if part)
    upload_url = (
        "https://storage.googleapis.com/upload/storage/v1/b/"
        + urllib.parse.quote(bucket, safe="")
        + "/o?uploadType=media&name="
        + urllib.parse.quote(object_name, safe="")
    )
    response = bytes_request(upload_url, method="POST", token=token, data=audio_path.read_bytes())
    return bucket, object_name, f"gs://{bucket}/{object_name}", response


def delete_gcs_object(bucket, object_name, token):
    url = (
        "https://storage.googleapis.com/storage/v1/b/"
        + urllib.parse.quote(bucket, safe="")
        + "/o/"
        + urllib.parse.quote(object_name, safe="")
    )
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"}, method="DELETE")
    with urllib.request.urlopen(request, timeout=120):
        return True


def transcript_from_response(operation):
    if operation.get("error"):
        fail(f"Google Speech operation failed: {json.dumps(operation['error'], separators=(',', ':'))}")
    response = operation.get("response", operation)
    segments = []
    for result in response.get("results", []):
        alternatives = result.get("alternatives") or []
        if alternatives:
            text = alternatives[0].get("transcript", "").strip()
            if text:
                segments.append(text)
    return "\n".join(segments).strip()


def recognize_sync(audio_path, language_code, token):
    content = audio_path.read_bytes()
    max_sync_bytes = 9 * 1024 * 1024
    if len(content) > max_sync_bytes:
        fail("Extracted audio is too large for synchronous Speech recognition; provide workflowInput.gcsUriPrefix for long-running recognition.", 2)
    request_body = {
        "config": {
            "languageCode": language_code,
            "encoding": "FLAC",
            "sampleRateHertz": 16000,
            "audioChannelCount": 1,
            "enableAutomaticPunctuation": True,
            "enableWordTimeOffsets": True,
        },
        "audio": {"content": base64.b64encode(content).decode("ascii")},
    }
    response = json_request(
        "https://speech.googleapis.com/v1/speech:recognize",
        method="POST",
        token=token,
        body=request_body,
    )
    return response


def recognize_long_running(audio_path, language_code, gcs_uri_prefix, token, transcript_dir):
    bucket, object_name, gcs_uri, upload_response = upload_to_gcs(audio_path, gcs_uri_prefix, token)
    (transcript_dir / "gcs-upload.json").write_text(json.dumps(upload_response, indent=2, sort_keys=True), encoding="utf-8")

    request_body = {
        "config": {
            "languageCode": language_code,
            "encoding": "FLAC",
            "sampleRateHertz": 16000,
            "audioChannelCount": 1,
            "enableAutomaticPunctuation": True,
            "enableWordTimeOffsets": True,
        },
        "audio": {"uri": gcs_uri},
    }
    operation_start = json_request(
        "https://speech.googleapis.com/v1/speech:longrunningrecognize",
        method="POST",
        token=token,
        body=request_body,
    )
    (transcript_dir / "operation-start.json").write_text(json.dumps(operation_start, indent=2, sort_keys=True), encoding="utf-8")
    operation_name = operation_start.get("name")
    if not operation_name:
        fail("Google Speech did not return an operation name")

    poll_interval = int(os.environ.get("GOOGLE_SPEECH_POLL_INTERVAL_SECONDS") or "15")
    timeout_seconds = int(os.environ.get("GOOGLE_SPEECH_OPERATION_TIMEOUT_SECONDS") or "14400")
    deadline = time.time() + timeout_seconds
    operation = {}
    while time.time() <= deadline:
        operation = json_request(
            "https://speech.googleapis.com/v1/operations/" + urllib.parse.quote(operation_name, safe="/"),
            method="GET",
            token=token,
        )
        (transcript_dir / "google-response.json").write_text(json.dumps(operation, indent=2, sort_keys=True), encoding="utf-8")
        if operation.get("done") is True:
            break
        time.sleep(max(1, poll_interval))
    else:
        fail(f"Google Speech operation timed out after {timeout_seconds}s: {operation_name}")

    gcs_deleted = False
    if os.environ.get("YOUTUBE_SHORTS_TO_TEXT_KEEP_GCS_OBJECT") != "1":
        try:
            gcs_deleted = delete_gcs_object(bucket, object_name, token)
        except urllib.error.HTTPError as error:
            print(f"GCS cleanup failed with HTTP {error.code}", file=sys.stderr)
    return operation, {
        "recognitionMode": "longrunning",
        "gcsUri": gcs_uri,
        "gcsObjectDeleted": gcs_deleted,
        "operationStartPath": str(transcript_dir / "operation-start.json"),
    }


def main():
    if len(sys.argv) < 3:
        fail("usage: worker.py <youtube-url> <language-code> [gcs-uri-prefix]", 2)
    url = sys.argv[1]
    language_code = sys.argv[2]
    gcs_uri_prefix = sys.argv[3] if len(sys.argv) > 3 else ""
    language_code = language_code or "ja-JP"
    output_root = Path("/work/out")
    host_output_root = os.environ.get("HOST_OUTPUT_DIR", str(output_root))
    video_dir = output_root / "video"
    audio_dir = output_root / "audio"
    transcript_dir = output_root / "transcripts"
    for directory in [video_dir, audio_dir, transcript_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    output_template = str(video_dir / "%(title).160B-%(id)s.%(ext)s")
    run([
        "yt-dlp",
        "--no-playlist",
        "--restrict-filenames",
        "--merge-output-format",
        "mp4",
        "--format",
        "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--output",
        output_template,
        url,
    ])
    mp4_files = sorted(video_dir.glob("*.mp4"), key=lambda path: path.stat().st_mtime)
    if not mp4_files:
        fail("yt-dlp completed but no MP4 file was produced")
    video_path = mp4_files[-1]
    audio_path = audio_dir / "extracted.flac"
    run([
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "flac",
        str(audio_path),
    ])

    token = google_access_token()
    if gcs_uri_prefix:
        operation, recognition_metadata = recognize_long_running(audio_path, language_code, gcs_uri_prefix, token, transcript_dir)
        raw_response_path = transcript_dir / "google-response.json"
    else:
        operation = recognize_sync(audio_path, language_code, token)
        raw_response_path = transcript_dir / "google-response.json"
        raw_response_path.write_text(json.dumps(operation, indent=2, sort_keys=True), encoding="utf-8")
        recognition_metadata = {
            "recognitionMode": "sync",
            "gcsUri": None,
            "gcsObjectDeleted": None,
            "operationStartPath": None,
        }

    transcript = transcript_from_response(operation)
    transcript_path = transcript_dir / "transcript.txt"
    transcript_path.write_text(transcript + ("\n" if transcript else ""), encoding="utf-8")

    def host_path(path):
        if path is None:
            return None
        path = Path(path)
        return str(Path(host_output_root) / path.relative_to(output_root))

    payload = {
        "status": "transcribed",
        "youtubeShortsToText": {
            "status": "transcribed",
            "url": url,
            "languageCode": language_code,
            "videoPath": host_path(video_path),
            "videoFileSize": video_path.stat().st_size,
            "audioPath": host_path(audio_path),
            "audioFileSize": audio_path.stat().st_size,
            "transcriptPath": host_path(transcript_path),
            "rawResponsePath": host_path(raw_response_path),
            "operationStartPath": host_path(recognition_metadata["operationStartPath"]),
            "recognitionMode": recognition_metadata["recognitionMode"],
            "gcsUri": recognition_metadata["gcsUri"],
            "gcsObjectDeleted": recognition_metadata["gcsObjectDeleted"],
            "transcriptPreview": transcript[:600],
            "transcriptLength": len(transcript),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
