# youtube-shorts-to-text-container

Riela workflow package for downloading a YouTube Shorts URL and transcribing
its audio through a Docker-contained worker.

The workflow keeps media tooling out of the host environment. The host only
needs:

- `bash`
- Docker
- Riela

The container image includes `yt-dlp`, `ffmpeg`, Python, and the worker script.
At runtime the wrapper passes Google credentials from the host environment into
Docker without writing them to package files.

## Build The Image

```bash
packages/youtube-shorts-to-text-container/workflows/youtube-shorts-to-text-container/scripts/build-image.sh
```

The default image tag is:

```text
riela/youtube-shorts-to-text:0.1.0
```

The workflow wrapper auto-builds that image when it is missing. Set
`YOUTUBE_SHORTS_TO_TEXT_SKIP_BUILD=1` to require a prebuilt image.

## Inputs

- `url`: YouTube Shorts or regular YouTube URL.
- `languageCode`: Google Speech language code. Defaults to `ja-JP`.
- `gcsUriPrefix`: optional Cloud Storage prefix for temporary FLAC upload, for
  example `gs://my-bucket/riela/audio`. Omit it for short audio that fits
  Google Speech synchronous recognition.

Google authentication is read from one of:

- `GOOGLE_ACCESS_TOKEN`
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`
- `GOOGLE_APPLICATION_CREDENTIALS`

`GOOGLE_APPLICATION_CREDENTIALS_JSON` is preferred because the wrapper can pass
it directly to the container. If `GOOGLE_APPLICATION_CREDENTIALS` points to a
local file, the wrapper mounts that file read-only into the container.

## Run

```bash
riela workflow run youtube-shorts-to-text-container \
  --workflow-definition-dir packages/youtube-shorts-to-text-container/workflows \
  --variables '{"url":"https://www.youtube.com/shorts/oA5tFm9ybqI","languageCode":"ja-JP"}'
```

The output JSON includes host artifact paths for:

- downloaded MP4
- extracted FLAC
- transcript text
- raw Google Speech response

When `gcsUriPrefix` is provided, temporary uploaded GCS audio is deleted after
successful transcription unless `YOUTUBE_SHORTS_TO_TEXT_KEEP_GCS_OBJECT=1` is
set.
