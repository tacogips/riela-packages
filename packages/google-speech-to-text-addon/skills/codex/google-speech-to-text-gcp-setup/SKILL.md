---
name: google-speech-to-text-gcp-setup
description: Use when configuring or verifying Google Cloud permissions for the tacogips/google-speech-to-text Riela node add-on, including service account credentials, Cloud Storage bucket or prefix access, Speech-to-Text API enablement, and live smoke tests through the add-on.
---

# Google Speech-to-Text GCP Setup

Use this skill when a `tacogips/google-speech-to-text` node needs real Google
Cloud Speech-to-Text execution against a static audio file.

## Guardrails

- Do not print service account JSON, private keys, access tokens, or refresh
  tokens. Report only safe metadata such as project id and service account
  email.
- Prefer the add-on's real REST path for final verification. `gcloud storage`
  checks are useful, but they are not a substitute for running the add-on.
- Use Computer Use with Google Cloud Console when `gcloud` lacks owner/admin
  credentials for API enablement, bucket creation, or IAM edits.
- Keep permissions scoped to the target bucket/prefix use case. Avoid project
  `Storage Admin` unless the user explicitly asks for broad storage control.

## Inputs To Establish

Identify these before changing GCP state:

- `project_id` for the Google Cloud project.
- `service_account_email` used by the add-on.
- Credential source, usually `GOOGLE_APPLICATION_CREDENTIALS_JSON`,
  `GOOGLE_APPLICATION_CREDENTIALS`, or `GOOGLE_ACCESS_TOKEN`.
- Target `gcsUriPrefix`, for example `gs://bucket/prefix`.
- Local audio file for a live smoke test.

If credentials come from kinko in this repository, load them without displaying
values:

```bash
repo_root="${RIELA_PACKAGES_ROOT:-$PWD}"
eval "$(kinko export bash --force --path "$repo_root")"
node -e '
const c = JSON.parse(process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON);
console.log(JSON.stringify({
  project_id: c.project_id,
  client_email: c.client_email,
  type: c.type
}, null, 2));
'
```

## Required GCP State

1. APIs enabled on the target project:
   - Cloud Resource Manager API, when using project/bucket IAM tooling.
   - Cloud Storage API.
   - Cloud Speech-to-Text API.

2. A non-public Cloud Storage bucket for temporary uploaded audio:
   - Uniform bucket-level access is preferred.
   - Public access prevention should stay on.
   - Use a dedicated prefix for Riela temporary audio, for example
     `riela-smoke` or `riela/audio`.

3. Bucket IAM for the add-on service account:
   - Grant `roles/storage.objectAdmin` on the bucket to allow upload, read,
     list, and cleanup of temporary audio objects.
   - If the bucket must be prefix-limited, use a bucket IAM condition matching
     the object resource name prefix. Confirm the condition with an actual
     object upload/read/delete smoke test.

4. Speech API authorization:
   - First try the add-on after Cloud Speech-to-Text API is enabled.
   - If `speech:longrunningrecognize` returns HTTP 403, grant the service
     account the narrow Speech client role available in the project IAM UI, then
     retry. Do not add broad project roles just to satisfy Speech access.

## Setup Workflow

Use `gcloud` when an admin account is already authenticated:

```bash
gcloud services enable \
  cloudresourcemanager.googleapis.com \
  storage.googleapis.com \
  speech.googleapis.com \
  --project "$PROJECT_ID"

gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" \
  --member "serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role "roles/storage.objectAdmin"
```

If those commands fail due to admin permission or missing ADC, switch to Google
Cloud Console through Computer Use:

1. Select the target project.
2. Enable Cloud Resource Manager API, Cloud Storage API, and Cloud Speech-to-Text
   API if they are not enabled.
3. Create or select the target bucket.
4. Open the bucket's Permissions tab.
5. Use Grant access for the service account.
6. Select `Storage Object Admin`.
7. Save and wait for IAM propagation.

## Verify Storage Access

Run a small object smoke test with the service account. It is acceptable for
project metadata checks to warn or fail if the service account is not a project
viewer; the important checks are object create, read, and delete.

```bash
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
printf '%s' "$GOOGLE_APPLICATION_CREDENTIALS_JSON" > "$tmp/sa.json"
printf 'riela smoke\n' > "$tmp/test.txt"
export CLOUDSDK_CONFIG="$tmp/gcloud"

gcloud auth activate-service-account --key-file="$tmp/sa.json" >/dev/null
gcloud storage cp "$tmp/test.txt" "$GCS_URI_PREFIX/test.txt"
gcloud storage cat "$GCS_URI_PREFIX/test.txt"
gcloud storage rm "$GCS_URI_PREFIX/test.txt"
```

## Verify The Add-on Path

Run the add-on through riela's node add-on runner or a small temporary
workflow against a real local audio file and the configured `gcsUriPrefix`.
Inspect the workflow result through `session status --output json`,
`session export --output json`, or GraphQL/runtime database diagnostics.

Do not verify this add-on by reading `inbox` or `outbox` files. Workflow
communication payloads are stored in SQLite, and transcript previews should be
summarized from the structured runtime output without dumping long transcripts.

After a successful smoke test, delete the uploaded audio object unless the user
asks to keep it:

```bash
gcloud storage rm "$UPLOADED_GCS_URI"
```

Report the final `gcsUriPrefix`, service account email, API/IAM changes made,
and verification evidence.
