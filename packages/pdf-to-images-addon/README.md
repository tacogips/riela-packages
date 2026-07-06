# pdf-to-images-addon

Riela node add-on package for rendering PDF pages to image files inside a
Python PyMuPDF container for visual analysis workflows.

## Add-on

- `tacogips/pdf-to-images@1`

Runtime:

- container execution
- Python 3.12 + PyMuPDF in the packaged `Containerfile`

Install and run directly:

```bash
riela node install tacogips/pdf-to-images
riela node run tacogips/pdf-to-images \
  --variables '{"pdfPath":"docs/report.pdf","outputDirectory":"report-pages","dpi":160,"format":"png"}'
```

Rendered images are written under
`$RIELA_ARTIFACT_DIR/addons/pdf-to-images/<outputDirectory>` when
`RIELA_ARTIFACT_DIR` is set, or `.riela/artifacts/addons/pdf-to-images/...`
inside the project otherwise.

Example node reference:

```json
{
  "id": "render-pdf-pages",
  "addon": {
    "name": "tacogips/pdf-to-images",
    "version": "1",
    "inputs": {
      "pdfPath": "{{inbox.latest.output.payload.pdfPath}}"
    },
    "config": {
      "dpi": 160,
      "firstPage": 1,
      "lastPage": 3,
      "format": "png"
    }
  }
}
```
