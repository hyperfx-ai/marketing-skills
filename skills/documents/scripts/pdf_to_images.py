"""Convert a PDF to PNG images (one per page) for preview/visibility.

Renders each page as a PNG. Use after generating a PDF to get full visibility
of the output before sharing. Requires pdf2image (and poppler in the sandbox).

Usage:
    python pdf_to_images.py

Customization:
    Edit the DATA dict at the bottom. Set pdf_path to the PDF file path
    (e.g. /home/user/editorial.pdf) and output_dir for where to save images.

Sandbox:
    If you see "Unable to get page count" or poppler errors, install:
    apt-get update && apt-get install -y poppler-utils
"""

import os
import sys

DATA = {
    "pdf_path": "/home/user/editorial.pdf",
    "output_dir": "/home/user/pdf_preview",
    "dpi": 150,
}


def convert(pdf_path: str, output_dir: str, dpi: int = 150) -> list[str]:
    """Convert PDF pages to PNG images. Returns list of output paths."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print("pip install pdf2image", file=sys.stderr)
        raise

    if not os.path.isfile(pdf_path):
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(pdf_path))[0]

    try:
        images = convert_from_path(pdf_path, dpi=dpi)
    except Exception as e:
        if "poppler" in str(e).lower() or "Unable to get" in str(e):
            print(
                "poppler-utils required. In sandbox run: apt-get update && apt-get install -y poppler-utils",
                file=sys.stderr,
            )
        raise

    paths = []
    for i, img in enumerate(images):
        path = os.path.join(output_dir, f"{base}_page_{i + 1:03d}.png")
        img.save(path, "PNG")
        paths.append(path)

    print(f"Saved {len(paths)} images to {output_dir}")
    return paths


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Convert PDF pages to PNG images")
    p.add_argument("pdf_path", nargs="?", default=DATA["pdf_path"], help="Path to PDF")
    p.add_argument(
        "-o", "--output", default=DATA["output_dir"], help="Output directory"
    )
    p.add_argument(
        "--dpi", type=int, default=DATA.get("dpi", 150), help="DPI for rendering"
    )
    args = p.parse_args()
    convert(args.pdf_path, args.output, args.dpi)
