# youtube-mp4-download-addon

Rielflow node add-on package for downloading a YouTube URL to an MP4 file.

## Add-on

- `tacogips/youtube-mp4-download@1`

Required runtime tools:

- `bash`
- `node`
- `yt-dlp`

Example node reference:

```json
{
  "id": "download-video",
  "addon": {
    "name": "tacogips/youtube-mp4-download",
    "version": "1",
    "inputs": {
      "url": "{{args.url}}"
    }
  }
}
```
