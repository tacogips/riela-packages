# google-speech-to-text-addon

Rielflow node add-on package for transcribing a local static audio file with
Google Cloud Speech-to-Text v1 long-running recognition.

The add-on uploads the extracted audio file to Google Cloud Storage, calls
`speech:longrunningrecognize`, polls the operation, and writes transcript,
caption, and raw response files to the Rielflow mailbox.

## Add-on

- `tacogips/google-speech-to-text@1`

## Skill

This package also includes the Codex skill
`google-speech-to-text-gcp-setup` for configuring and verifying the Google Cloud
project, service account, Cloud Storage bucket/prefix permissions, and live
Speech-to-Text smoke test required by this add-on.

Required runtime tools:

- `bash`
- `node`
- `curl`

`gcloud` is only used as a fallback token source when no access token or
application credential JSON is supplied.

Authentication is explicit through `addon.env`. Supported target variables:

- `GOOGLE_ACCESS_TOKEN`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`

Example node reference:

```json
{
  "id": "transcribe-audio",
  "addon": {
    "name": "tacogips/google-speech-to-text",
    "version": "1",
    "inputs": {
      "audioPath": "{{mailbox.latest.output.payload.audioExtract.audioPath}}",
      "languageCode": "ja-JP",
      "gcsUriPrefix": "gs://my-transcription-bucket/rielflow/audio"
    },
    "env": {
      "GOOGLE_APPLICATION_CREDENTIALS_JSON": {
        "fromEnv": "GOOGLE_APPLICATION_CREDENTIALS_JSON",
        "required": false
      }
    }
  }
}
```

Notes:

- `gcsUriPrefix` is required because static files longer than 60 seconds must be
  recognized from Cloud Storage with long-running recognition.
- The configured Google credential must be able to upload to the target bucket
  and read the uploaded audio object for Speech-to-Text recognition.
- Google Cloud Speech-to-Text v1 asynchronous recognition supports audio up to
  roughly 480 minutes; this package is intended for static files such as
  one-hour videos after audio extraction.
