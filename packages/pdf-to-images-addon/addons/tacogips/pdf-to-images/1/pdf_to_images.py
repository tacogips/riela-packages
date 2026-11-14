#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

import fitz


def usage_error(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def optional_int(value: str | None, label: str) -> int | None:
    if value is None or value == "":
        return None
    try:
        parsed = int(value)
    except ValueError:
        usage_error(f"{label} must be an integer")
    if parsed < 1:
        usage_error(f"{label} must be >= 1")
    return parsed


def object_value(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def string_value(*values: object, default: str = "") -> str:
    for value in values:
        if isinstance(value, str) and value != "":
            return value
        if isinstance(value, (int, float)):
            return str(value)
    return default


def input_payload_from_stdin() -> dict:
    if sys.stdin.isatty():
        return {}
    line = sys.stdin.readline().strip()
    if not line:
        return {}
    try:
        envelope = json.loads(line)
    except json.JSONDecodeError as error:
        usage_error(f"stdin must contain one JSONL add-on invocation: {error}")
    node_payload = object_value(envelope.get("nodePayload"))
    inputs = object_value(node_payload.get("inputs"))
    config = object_value(node_payload.get("config"))
    upstream = object_value(node_payload.get("input"))
    return {
        "pdfPath": string_value(inputs.get("pdfPath"), config.get("pdfPath"), upstream.get("pdfPath")),
        "outputDirectory": string_value(inputs.get("outputDirectory"), config.get("outputDirectory"), default="pdf-pages"),
        "dpi": string_value(inputs.get("dpi"), config.get("dpi"), default="160"),
        "firstPage": string_value(inputs.get("firstPage"), config.get("firstPage")),
        "lastPage": string_value(inputs.get("lastPage"), config.get("lastPage")),
        "format": string_value(inputs.get("format"), config.get("format"), default="png"),
    }


def main(argv: list[str]) -> int:
    payload_input = input_payload_from_stdin()
    pdf_path = payload_input.get("pdfPath") or (argv[1] if len(argv) > 1 else "")
    output_directory = payload_input.get("outputDirectory") or (argv[2] if len(argv) > 2 and argv[2] else "pdf-pages")
    dpi_raw = payload_input.get("dpi") or (argv[3] if len(argv) > 3 and argv[3] else "160")
    first_page = optional_int(payload_input.get("firstPage") or (argv[4] if len(argv) > 4 else None), "firstPage")
    last_page = optional_int(payload_input.get("lastPage") or (argv[5] if len(argv) > 5 else None), "lastPage")
    image_format = payload_input.get("format") or (argv[6] if len(argv) > 6 and argv[6] else "png")

    if not pdf_path:
        usage_error("pdf-to-images requires a non-empty PDF path")
    source = Path(pdf_path)
    if not source.is_file():
        usage_error(f"PDF file not found: {pdf_path}")
    try:
        dpi = int(dpi_raw)
    except ValueError:
        usage_error("dpi must be an integer")
    if dpi < 36 or dpi > 600:
        usage_error("dpi must be between 36 and 600")
    if image_format == "jpg":
        image_format = "jpeg"
    if image_format not in {"png", "jpeg"}:
        usage_error(f"Unsupported image format: {image_format}")
    output_path = Path(output_directory)
    if output_path.is_absolute() or ".." in output_path.parts:
        usage_error("outputDirectory must be a relative path without '..' segments")

    artifact_root = Path(os.environ.get("RIELA_ARTIFACT_DIR", ".riela/artifacts"))
    files_dir = artifact_root / "addons" / "pdf-to-images" / output_path
    files_dir.mkdir(parents=True, exist_ok=True)

    document = fitz.open(source)
    try:
        total_pages = document.page_count
        start = first_page or 1
        end = last_page or total_pages
        if start > total_pages:
            usage_error(f"firstPage {start} exceeds PDF page count {total_pages}")
        if end < start:
            usage_error("lastPage must be >= firstPage")
        end = min(end, total_pages)
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        extension = "jpg" if image_format == "jpeg" else "png"
        images = []
        for page_number in range(start, end + 1):
            page = document.load_page(page_number - 1)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            image_path = files_dir / f"page-{page_number:04d}.{extension}"
            pixmap.save(image_path)
            images.append({
                "page": page_number,
                "path": str(image_path),
                "fileName": image_path.name,
                "fileSize": image_path.stat().st_size,
                "width": pixmap.width,
                "height": pixmap.height,
            })
    finally:
        document.close()

    payload = {
        "pdfToImages": {
            "status": "rendered",
            "pdfPath": str(source),
            "outputDirectory": output_directory,
            "dpi": dpi,
            "format": image_format,
            "sourcePageCount": total_pages,
            "pageCount": len(images),
            "images": images,
        }
    }
    payload.update({
        "pdfPath": payload["pdfToImages"]["pdfPath"],
        "pageCount": payload["pdfToImages"]["pageCount"],
        "images": images,
    })
    print(json.dumps(payload, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
