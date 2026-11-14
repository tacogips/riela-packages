# youtube-mp4-to-text-workflow

Example Riela workflow package that composes three standalone node add-on
packages:

1. `tacogips/youtube-mp4-download`
2. `tacogips/mp4-audio-extract`
3. `tacogips/google-speech-to-text`

Inputs:

- `url`: YouTube URL to download.
- `languageCode`: Google Speech language code, for example `ja-JP`.
- `gcsUriPrefix`: Google Cloud Storage prefix for the temporary audio upload,
  for example `gs://my-transcription-bucket/riela/audio`.

The workflow deliberately keeps each operation as its own node. The downloaded
MP4 path is passed to the audio extraction node, and the extracted FLAC path is
passed to the transcription node through Riela node outputs. The transcription
node uploads that static FLAC file to Cloud Storage and uses Google
Speech-to-Text long-running recognition, so hour-long files are handled without
streaming.
