---
name: PPTX Export
description: How to export presentations to PowerPoint format — browser download and CLI paths.
---

## Two Export Paths

### 1. Browser Download (Live Preview)

The live preview includes a floating toolbar at the bottom of the screen with a **Download PPTX** button. Clicking it generates the PPTX client-side using PptxGenJS and triggers a browser download.

This requires the Vite dev server to be running (`pnpm dev`). The user clicks the button in the sandbox preview — no CLI step needed.

### 2. CLI Export

Run from the project root:

```bash
pnpm run export:pptx
```

This executes `scripts/export-pptx.ts` via `tsx`. It reads `src/slides.json`, generates the PPTX, and writes it to `presentation.pptx` in the project root.

Custom output path:

```bash
pnpm run export:pptx -- --output=/home/user/slides/my-deck.pptx
```

## How It Works

Both export paths use PptxGenJS with `LAYOUT_WIDE` (13.33" x 7.5" — standard widescreen).

For each slide in `slides.json`:

1. A slide is added to the PptxGenJS presentation
2. The theme's color palette determines background, text, and accent colors
3. Layout is handled per slide type (title centered, content left-aligned, stats in card grid, etc.)
4. Images are fetched from their URLs and embedded directly

### Theme-to-Color Mapping

The PPTX exporter maps each theme to a fixed color palette:

| Theme | Background | Foreground | Heading | Surface | Muted |
|-------|------------|------------|---------|---------|-------|
| `pitch-dark` | `050505` | `E5E5E5` | `FFFFFF` | `141414` | `888888` |
| `minimal-swiss` | `F4F4F5` | `27272A` | `09090B` | `FFFFFF` | `71717A` |
| `neo-brutal` | `FFDF00` | `000000` | `000000` | `FFFFFF` | `333333` |
| `editorial-nature` | `E8ECE7` | `3A4038` | `1E241C` | `F4F6F3` | `6B7368` |

The `brandColor` from `meta` is used for accent elements (bullets, stat values, accent bars, column headings).

## Image Handling

Image slides use `imageUrl` (an HTTPS URL). PptxGenJS fetches the image at export time and embeds it in the .pptx file.

- Both browser and CLI exports support remote URLs
- No pre-download step is needed
- If the URL is unreachable, the slide will have a blank image area

## Output File

- **Browser export**: Downloaded by the browser as `<title-slug>.pptx`
- **CLI export**: Written to `presentation.pptx` (or custom `--output` path)

To make the CLI output accessible for download from the sandbox:

```python
shell("pnpm run export:pptx")
display_file(path="/home/user/slides/presentation.pptx")
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `PptxGenJS is not a constructor` | Import compatibility issue — the template handles this with `(Module as any).default ?? Module` |
| Images show as blank in PPTX | Verify the `imageUrl` is a publicly accessible HTTPS URL |
| Content not centered | The exporter uses `LAYOUT_WIDE` (13.33" x 7.5") — coordinates are pre-calculated for this layout |
| CLI export hangs | Image fetch may be slow for large images — use smaller/compressed URLs |
