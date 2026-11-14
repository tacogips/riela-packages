# codex-website-builder

`codex-website-builder` is a Riela workflow package for building and
iterating SolidJS websites with Bun. It separates the work into Codex GPT-5.6 SOL
nodes for site design, asset generation, implementation, Docker-contained Bun
server operation, and Playwright-based review. Each generated source snapshot
is committed before review so the project can be restored through git history.

## Workflow

- `site-design` turns the user request or chat feedback into an implementation
  brief for a SolidJS/Bun website and fixes the CSS framework/library allowlist
  before implementation.
- `asset-generate` creates or updates local website assets and records how they
  are used.
- `server-node` creates or revises the SolidJS app source without running Bun on
  the host.
- `bun-container-server` builds the packaged Bun Docker image, bind-mounts the
  repository at `/workspace`, runs `bun install`/build inside Docker, and starts
  or refreshes the local review server from the container.
- `source-commit-message` prepares a snapshot commit for website sources.
- `review-node` uses Playwright against the running local server, reviews the
  site, and routes back to design, asset, or implementation when blocking
  feedback remains.

The default design stack is pinned in the design prompt:

- `solid-js@1.9.13`
- `@solidjs/router@0.16.1`
- `vite@8.0.16`
- `vite-plugin-solid@2.11.12`
- `typescript@6.0.3`
- `tailwindcss@4.3.0`
- `@tailwindcss/vite@4.3.0`
- `lucide-solid@1.17.0`

The design node may remove unnecessary entries, but it must not introduce
additional runtime libraries without recording the reason and exact pinned
version. The implementation node must use exact dependency versions, commit the
resulting Bun lockfile, and avoid package lifecycle scripts unless explicitly
justified.

## Bun Container

The workflow includes a lightweight image at
`workflows/codex-website-builder/containers/bun-site-runner/Containerfile`.
The command node builds it locally and runs Bun through Docker with:

- repository bind mount: `<repo>:/workspace`
- target app working directory: `/workspace/<targetDirectory>`
- containerized dependency install/build/dev server
- dropped Linux capabilities and `no-new-privileges`
- lifecycle scripts disabled during install through `bun install
  --ignore-scripts`

This keeps Bun and package-manager execution out of the host process while
still sharing design docs, generated assets, and source files through the
mounted workspace.

## Event Sources

The workflow does not hardcode Telegram, Discord, or other chat providers.
Riela event sources live outside the workflow under `.riela-events`.
Multiple source definitions can be installed together, and only the selected
one should have `"enabled": true`; the others should use `"enabled": false`.
`riela events serve` starts only enabled sources, so changing providers does
not require editing the workflow.

This package includes templates in
`workflows/codex-website-builder/event-templates/.riela-events`.
Copy one or more templates into the target project event root, enable exactly
one source/binding/destination set, then validate:

```bash
riela events validate \
  --workflow-definition-dir .riela/workflows \
  --event-root .riela-events
```

Start serving events:

```bash
riela events serve \
  --workflow-definition-dir .riela/workflows \
  --event-root .riela-events
```

## Direct Run Input

```json
{
  "projectName": "demo-site",
  "targetDirectory": "apps/demo-site",
  "siteRequest": "Build a product website for a small analytics tool.",
  "feedback": "Make the primary CTA clearer.",
  "reviewUrl": "http://127.0.0.1:4173",
  "constraints": [
    "Use SolidJS and Bun",
    "Keep generated sources committed after each implementation snapshot",
    "Run Bun only through the packaged Docker image"
  ]
}
```
