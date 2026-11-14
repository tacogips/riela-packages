# mp4-audio-extract-addon

Riela node add-on package for extracting speech-ready FLAC audio from MP4.

## Add-on

- `tacogips/mp4-audio-extract@1`

Required runtime tools:

- `bash`
- `node`
- `ffmpeg`

Example node reference:

```json
{
  "id": "extract-audio",
  "addon": {
    "name": "tacogips/mp4-audio-extract",
    "version": "1",
    "inputs": {
      "mp4Path": "{{inbox.latest.output.payload.youtubeMp4Download.outputPath}}"
    },
    "config": {
      "sampleRateHertz": 16000,
      "audioChannelCount": 1
    }
  }
}
```
