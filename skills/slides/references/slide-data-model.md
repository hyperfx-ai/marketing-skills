---
name: Slide Data Model
description: Full JSON schema for src/slides.json — all slide types, fields, and examples.
---

## Overview

All presentation content lives in `src/slides.json`. This file is the single source of truth consumed by both the reveal.js renderer (live preview) and the PptxGenJS exporter (PPTX download).

## Top-Level Structure

```json
{
  "meta": { ... },
  "slides": [ ... ]
}
```

## Meta Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Presentation title (shown on title slide and browser tab) |
| `author` | string | Yes | Author name (embedded in PPTX metadata) |
| `theme` | string | Yes | One of: `minimal-swiss`, `neo-brutal`, `editorial-nature`, `pitch-dark` |
| `brandColor` | string | Yes | Hex color (e.g. `#3b82f6`) used for accents, bullets, stat values |
| `fontHeading` | string | No | Override heading font family |
| `fontBody` | string | No | Override body font family |

## Slide Types

Every slide object has a `type` field and an optional `notes` field (string, rendered as speaker notes).

### title

Opening slide with a large centered heading.

```json
{
  "type": "title",
  "title": "The Future of AI",
  "subtitle": "How artificial intelligence is reshaping every industry",
  "notes": "Welcome the audience."
}
```

| Field | Type | Required |
|-------|------|----------|
| `title` | string | Yes |
| `subtitle` | string | No |
| `notes` | string | No |

### section

Section divider — use to break the deck into logical parts.

```json
{
  "type": "section",
  "title": "The Landscape",
  "subtitle": "Where we are today"
}
```

| Field | Type | Required |
|-------|------|----------|
| `title` | string | Yes |
| `subtitle` | string | No |
| `notes` | string | No |

### content

Standard bullet-point slide.

```json
{
  "type": "content",
  "title": "Key Breakthroughs",
  "bullets": [
    "Foundation models with trillion-parameter scale",
    "Multimodal reasoning across text, image, and code",
    "Autonomous agents that plan, act, and reflect"
  ]
}
```

| Field | Type | Required |
|-------|------|----------|
| `title` | string | Yes |
| `bullets` | string[] | Yes |
| `notes` | string | No |

### two-column

Side-by-side comparison with independent headings and bullets.

```json
{
  "type": "two-column",
  "title": "Then vs Now",
  "left": {
    "heading": "2020",
    "bullets": ["Single-task models", "Text-only interfaces"]
  },
  "right": {
    "heading": "2026",
    "bullets": ["General-purpose agents", "Multimodal native"]
  }
}
```

| Field | Type | Required |
|-------|------|----------|
| `title` | string | Yes |
| `left.heading` | string | Yes |
| `left.bullets` | string[] | Yes |
| `right.heading` | string | Yes |
| `right.bullets` | string[] | Yes |
| `notes` | string | No |

### image

Full-width image with optional caption.

```json
{
  "type": "image",
  "title": "Agent Architecture",
  "imageUrl": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&q=80",
  "caption": "Modern AI systems combine reasoning, tools, and memory"
}
```

| Field | Type | Required |
|-------|------|----------|
| `title` | string | Yes |
| `imageUrl` | string | Yes |
| `caption` | string | No |
| `notes` | string | No |

Use full HTTPS URLs for images. Both the browser preview and PPTX export can fetch remote images directly.

### quote

Centered quotation with attribution.

```json
{
  "type": "quote",
  "quote": "The best way to predict the future is to invent it.",
  "attribution": "Alan Kay"
}
```

| Field | Type | Required |
|-------|------|----------|
| `quote` | string | Yes |
| `attribution` | string | No |
| `notes` | string | No |

### stat

Metric cards — works best with 2-4 stats.

```json
{
  "type": "stat",
  "title": "AI by the Numbers",
  "stats": [
    { "value": "$184B", "label": "Global AI market size (2025)" },
    { "value": "72%", "label": "Enterprises using AI in production" },
    { "value": "10x", "label": "Productivity gains in code generation" }
  ]
}
```

| Field | Type | Required |
|-------|------|----------|
| `title` | string | Yes |
| `stats` | array | Yes |
| `stats[].value` | string | Yes |
| `stats[].label` | string | Yes |
| `notes` | string | No |

### closing

Final slide with contact information.

```json
{
  "type": "closing",
  "title": "Thank You",
  "subtitle": "Let's build the future together",
  "contactInfo": ["hello@hyper.ai", "hyper.ai", "@hyperai"]
}
```

| Field | Type | Required |
|-------|------|----------|
| `title` | string | Yes |
| `subtitle` | string | No |
| `contactInfo` | string[] | No |
| `notes` | string | No |

## Writing the File

Use `sandbox_write_file` to create or overwrite the entire file:

```python
sandbox_write_file(
    file_path="src/slides.json",
    content='{ "meta": { ... }, "slides": [ ... ] }',
)
```

Or use `sandbox_edit_file` for targeted edits to an existing `slides.json`.

The Vite dev server picks up changes automatically via HMR — no restart needed.
