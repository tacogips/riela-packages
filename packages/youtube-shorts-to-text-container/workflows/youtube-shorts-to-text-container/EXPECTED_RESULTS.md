# Expected Results

Running `youtube-shorts-to-text-container` should produce a JSON payload with:

- `status` equal to `transcribed`
- `youtubeShortsToText.videoPath`
- `youtubeShortsToText.audioPath`
- `youtubeShortsToText.transcriptPath`
- `youtubeShortsToText.rawResponsePath`
- `youtubeShortsToText.transcriptPreview`
- `youtubeShortsToText.gcsObjectDeleted`

The downloaded MP4, extracted FLAC, transcript text, and raw Google Speech
response are written under the Riela artifact directory.
