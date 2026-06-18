---
name: riel-codex-website-builder
description: Use when running, configuring, or troubleshooting the codex-website-builder Riela package for SolidJS/Bun website generation, Docker-contained Bun execution, Playwright review, git snapshot commits, pinned website dependencies, and Telegram/Discord/webhook feedback events.
---

# Codex Website Builder

Use this skill after installing `codex-website-builder`.

## Run Directly

```bash
riela workflow run codex-website-builder --input-json '{
  "projectName": "demo-site",
  "targetDirectory": "apps/demo-site",
  "siteRequest": "Build a SolidJS website for the requested product.",
  "constraints": [
    "Use SolidJS and Bun",
    "Run Bun only through the packaged Docker image",
    "Pin the CSS framework and website dependencies during design"
  ]
}'
```

## Bun Runs In Docker

The workflow's `server-node` writes source but must not run Bun on the host.
`bun-container-server` builds the packaged image from
`.riela/workflows/codex-website-builder/containers/bun-site-runner/Containerfile`,
mounts the repository at `/workspace`, and runs `bun install`, build, and the
review server inside Docker.

The default design stack is:

- `solid-js@1.9.13`
- `@solidjs/router@0.16.1`
- `vite@8.0.16`
- `vite-plugin-solid@2.11.12`
- `typescript@6.0.3`
- `tailwindcss@4.3.0`
- `@tailwindcss/vite@4.3.0`
- `lucide-solid@1.17.0`

If a request needs another library, require an exact pinned version and a
design-node reason before implementation.

## Configure One Event Source

Event config is separate from the workflow. Copy templates from the installed
workflow bundle:

```bash
mkdir -p .riela-events
cp -R .riela/workflows/codex-website-builder/event-templates/.riela-events/* .riela-events/
```

Enable exactly one provider by setting `enabled` to `true` in its source,
binding, and destination JSON files. Leave every other provider disabled.

Validate:

```bash
riela events validate \
  --workflow-definition-dir .riela/workflows \
  --event-root .riela-events
```

Serve:

```bash
riela events serve \
  --workflow-definition-dir .riela/workflows \
  --event-root .riela-events
```

## Notes

- The workflow snapshots generated website source through git after each
  Dockerized Bun server pass and before Playwright review.
- The review node is responsible for operating the running site with Playwright
  and routing feedback to design, asset, or implementation.
- Event source selection does not require editing `workflow.json`; only the
  `.riela-events` provider files change.
