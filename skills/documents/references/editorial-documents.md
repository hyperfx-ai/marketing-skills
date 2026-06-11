---
name: Editorial Documents
description: Themable editorial book-style PDFs — 12 palettes, logo support, chapter divider graphics. Landscape, two-column, clean white content pages.
---

# Editorial Documents

Use `generate_editorial.py` for guide-style, presentation-quality PDFs. Landscape A4, color only on cover and chapter dividers, white content pages.

## Themes (12 distinct palettes)

Set `DATA["theme"]` to one of:

| Theme | Hue |
|-------|-----|
| `terracotta` | Clay orange (default) |
| `crimson` | Deep red |
| `saffron` | Warm gold / yellow |
| `coral` | Salmon pink-orange |
| `plum` | Wine purple |
| `olive` | Warm green |
| `rose` | Dusty pink |
| `espresso` | Rich dark brown |
| `navy` | Warm blue |
| `wine` | Dark burgundy |
| `teal` | Warm teal green |
| `aubergine` | Deep eggplant purple |

## DATA dict

```python
DATA = {
    "theme": "terracotta",
    "title": "The Hyper\nPlatform Guide",
    "subtitle": "Build intelligent agents...",
    "org_name": "Hyper",
    "logo_path": "/home/user/logo.png",  # or None for text logo
    "output_path": "/home/user/editorial.pdf",
}
```

## Logo

- **Path**: `logo_path` must be a sandbox path to an image (PNG, JPG). Rendered on cover, max 40pt height.
- **Generate**: Use `nano_banana_image_generation` with prompt: "Minimal logo for [org], clean geometric design, white on transparent, square."
- **Fallback**: If `logo_path` is None or file missing, a 4-square text logo is used.

## Chapter graphics

Chapter divider pages have concentric arcs in the top-right corner, tinted from the chapter color. No configuration — built into the design.

## PDF to images (preview)

Run `pdf_to_images.py` after generating to convert pages to PNGs:

```bash
pip install pdf2image
# In sandbox: apt-get install -y poppler-utils
python pdf_to_images.py /home/user/editorial.pdf -o /home/user/pdf_preview
```

Download the PNGs for full visibility of the generated document.
