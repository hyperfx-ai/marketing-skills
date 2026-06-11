---
name: slides
description: Create themed slide presentations in the sandbox using reveal.js with a JSON data model — preview in-browser, export to PPTX. Use when the user wants a slide deck, pitch deck, presentation, or PPTX export with consistent visual themes.
use_cases:
  - Create a slide deck or presentation
  - Generate pitch deck slides
  - Build a themed presentation from a brief
  - Export slides to PowerPoint (PPTX)
  - Preview a presentation in the browser
triggers:
  - slides
  - slide deck
  - presentation
  - pitch deck
  - reveal.js
  - pptx
  - powerpoint
  - keynote
  - slide generation
  - create slides
requires_toolkits:
  - sandbox
---

# Slide Generation

Create themed presentations in the sandbox using the reveal.js starter template. Define slides as structured JSON, preview live in the browser, and export to PPTX.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Sandbox toolkit** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## Core Principles

1. Always clone the reveal-slides-template starter — never scaffold from scratch.
2. All slide content is defined in `src/slides.json` — this is the single source of truth for both the web preview and PPTX export.
3. Choose a theme before writing content. Set `meta.theme` and `meta.brandColor` first.
4. Preview in the browser before declaring done. Take a screenshot to verify.
5. The PPTX export is available two ways: the Download button in the live preview toolbar, or `pnpm run export:pptx` from CLI.
6. When using `sandbox_write_file` for `src/slides.json`, serialize the slide data to JSON text first. Do not pass a structured object as the tool argument.

## Routing Table

Read the focused reference based on the task:

| Need | Reference |
|------|-----------|
| JSON schema for slides.json (all slide types and fields) | `references/slide-data-model.md` |
| Available themes, how to pick one, CSS variable overrides | `references/theming.md` |
| Exporting to PPTX (browser download or CLI) | `references/pptx-export.md` |

For sandbox runtime mechanics (starting sandbox, running commands, file boundaries, artifacts), follow the **sandbox** curated skill and its references.

## Workflow

```
1. Start sandbox
2. Clone starter:
   cd /home/user
   git clone https://github.com/multigen-ai/reveal-slides-template.git slides
   sandbox_set_active_directory(path="/home/user/slides")
   pnpm install
3. Edit src/slides.json — set meta (title, author, theme, brandColor) and slides array, then write the file as serialized JSON text
4. Start dev server:
   pnpm dev
5. Verify:
   sandbox_check_running_port(port=3000)
   sandbox_get_preview_url(port=3000)
6. Take screenshot to confirm visual output
7. For PPTX export, either:
   a. User clicks the Download PPTX button in the live preview toolbar
   b. Or run: pnpm run export:pptx
      The file is written to presentation.pptx in the project root
```

## Slide Types

| Type | Purpose | Key Fields |
|------|---------|------------|
| `title` | Opening slide with big heading | `title`, `subtitle` |
| `section` | Section divider | `title`, `subtitle` |
| `content` | Bullet-point slide | `title`, `bullets[]` |
| `two-column` | Side-by-side comparison | `title`, `left{heading, bullets[]}`, `right{heading, bullets[]}` |
| `image` | Full-width image | `title`, `imageUrl`, `caption` |
| `quote` | Centered quotation | `quote`, `attribution` |
| `stat` | Metric cards (1-4 stats) | `title`, `stats[{value, label}]` |
| `closing` | Final slide with contact info | `title`, `subtitle`, `contactInfo[]` |

## Quick Reference: Sandbox Tools Used

| Tool | Purpose |
|------|---------|
| `sandbox_start()` | Start sandbox |
| `shell(command)` | Run commands in the sandbox (clone, install, start dev server) |
| `sandbox_edit_file(path, old, new)` | Edit slides.json or styles |
| `sandbox_write_file(path, content)` | Create or overwrite slides.json with JSON text content |
| `sandbox_check_running_port(port)` | Verify dev server is up on port 3000 |
| `sandbox_get_preview_url(port)` | Get public preview URL |
| `sandbox_screenshot(url)` | Capture screenshot for verification |

## Downstream Composition

| Phase | Skill |
|-------|-------|
| Sandbox runtime, file boundaries, artifacts | `sandbox` curated skill |
| Marketing landing pages (different starter) | `marketing-website` curated skill |
| Deploy to Cloudflare | `cloudflare-app-deployment` curated skill |
