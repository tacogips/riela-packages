# Expected Results

`codex-website-builder` should:

- Normalize either direct workflow input or chat-event feedback into one website
  build request.
- Produce or revise a SolidJS/Bun website under the requested target directory.
- Pin the CSS framework and library allowlist during the design step before
  implementation.
- Generate or update local visual assets needed by the website.
- Run Bun install/build/server commands only through the packaged Docker image
  with the repository mounted at `/workspace`.
- Start a local Docker-hosted Bun server and return a review URL.
- Commit generated website source snapshots before Playwright review.
- Use Playwright in the review node and loop back to the correct node for high
  or middle findings.
- Finish only when the running site is accepted with no high or middle review
  findings.
- Work with event-source configs outside the workflow, allowing users to enable
  exactly one provider such as Telegram or Discord without editing
  `workflow.json`.
