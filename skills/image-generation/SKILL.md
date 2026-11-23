---
name: image-generation
description: Generate images from text, edit or compose with reference images, and adapt images for paid social. Use when the user asks to generate an image, create an ad creative, do an image-to-image edit, render text inside an image, or produce a print-quality poster.
metadata:
  version: 2.0.0
requires_toolkits:
  - image_gen
icon: image_gen
short_description: Generate and edit images with one tool and a model choice, from ad creatives to product shots.
---

# Image Generation

Use `images_generate` to generate images from text, edit or compose images from references, and adapt a creative brief for paid-social placements (`9:16`, `4:5`, `1:1`).

## Requirements

Connect to the [Hyper MCP](https://app.hyperfx.ai/mcp) to use these tools from an MCP client. Image generation (`images_generate`, `images_product_photoshoots_create`, `images_marketplace_cards_create`) and `firecrawl_branding_extract` are built into Hyper and require no separate integration.

Hyper Chat, Hyper CLI, and the full Hyper MCP endpoint expose image tools. Some official directory MCP connectors exclude `image_gen`. Check the active surface with `describe("images_generate")` or the equivalent lookup below. If image tools are unavailable or the user works without Hyper, deliver ready-to-use prompts and asset briefs for their image tool.

| Surface | Find a tool | Run it |
| --- | --- | --- |
| Hyper Chat | `search_tools(queries=["<tool or action>"])` | `<name>(...)` |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | Use the `call_with` entry from `describe` to choose `call_read("<name>", {...})`, `call_write`, or `call_destructive` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

## Call shape

Pass these JSON arguments to `images_generate`.

```json
{
  "requests": [
    {
      "id": "mug-hero",
      "prompt": "Create a morning daylight product photo on a stone counter. Keep the mug's silhouette, finish, and logo from the reference.",
      "reference_images": ["<stored image file ID>"]
    }
  ],
  "ad_placements": ["9:16", "4:5", "1:1"],
  "ad_format": "product_hero",
  "quality": "standard",
  "n": 1,
  "model": "auto"
}
```

| Argument | Values |
| --- | --- |
| `requests` | Array of objects with `prompt`, optional `id`, and optional `reference_images` containing stored image file IDs or `/files/...` paths. |
| `aspect_ratio` | `"1:1"` (default), `"9:16"`, `"16:9"`, `"4:5"`, `"5:4"`, `"2:3"`, `"3:2"`, `"3:4"`, `"4:3"`, or `"21:9"`. For `"1:4"`, `"1:8"`, `"4:1"`, or `"8:1"`, use `nano-banana-2.1` or `nano-banana`. Nano Banana Pro substitutes `"9:16"` for the tall ratios and `"21:9"` for the wide ratios. |
| `ad_placements` | Optional list from `["9:16", "4:5", "1:1"]`. When supplied, the placement list determines the output ratios. |
| `ad_format` | Optional creative style. Choose `"ugc"`, `"product_hero"`, `"headline_offer"`, `"us_vs_them"`, or `"testimonial"`. |
| `quality` | `"draft"`, `"standard"` (default), or `"high"`. |
| `n` | 1–4 images per request, default 1. GPT Image edits yield one image per request. |
| `seed` | Optional integer for reproducible runs with `seedream-4.5` only. |
| `use_search` | Optional boolean, default false. Search grounding works with `nano-banana-pro` only. |
| `model` | `"auto"` by default, or an explicit model below. |

With the default `n=1`, `ad_placements=["9:16", "4:5", "1:1"]` generates one image per placement per request, resized to `1080x1920`, `1080x1350`, and `1080x1080` respectively. For matched multi-placement packs with crisp HTML headlines, safe zones, and quality checks, use `ad_creatives_generate`. [Ad creative generation](../ad-creative-generation/SKILL.md)

## Choosing a model

Start with `model="auto"`. It chooses one model for the batch. In priority order, `use_search=true` selects `nano-banana-pro`, references on any request select `nano-banana`, and plain text-to-image with or without a `seed` selects `seedream-4.5`. An explicit model always takes precedence.

| Model | Choose it for |
| --- | --- |
| `gpt-image-2.6-sunburst` | Complex compositions, precise edits, and production visuals |
| `gpt-image-2.6-flare` | Fast drafts and concept iteration |
| `nano-banana-2.1` | Reference fidelity, multi-reference edits, and extreme aspect ratios |
| `nano-banana` | Edits and compositions from one or more references |
| `nano-banana-pro` | Readable text in posters, labels, or infographics, or search-grounded scenes |
| `flux-3-image` | Candid lifestyle and UGC-style photography from text |
| `seedream-4.5` | Product photography from text, detailed materials, and seeded runs |

`flux-3-image` and `seedream-4.5` accept text-only requests. `flux-3-image` ignores `quality`. For GPT Image edits (`gpt-image-2.6-*` and `gpt-image-2.5-*`), include `reference_images` on every request. Use separate requests for edit variants since `n` does not control edit output. [Image prompting](references/image-prompting.md)

## Branded / website ad creatives

1. Use the user's logo, colors, fonts, and screenshots first. If you need brand assets from a website, call `firecrawl_branding_extract(url=...)` for colors, typography, and any available `logo.file_id`, `logo.path`, or `screenshot`.
2. A cached result or failed asset save can leave you with a source URL and no stored file ID. If needed, store a usable raster copy first. For additional visual context, call `firecrawl_urls_scrape(url=..., formats=["screenshot"])`.
3. Use the actual hex colors, fonts, and visual direction in the prompt. Pass only raster images (`png`, `jpg`, `gif`, `webp`) as stored file IDs or `/files/...` paths. Convert SVGs to raster first. The branding response's `file` field contains JSON data.

## Higher-level workflows

- For studio, lifestyle, hero, or carousel shots from the same product, use `images_product_photoshoots_create`. [Product photoshoot](references/product-photoshoot.md)
- For listing image sets and A+ modules, use `images_marketplace_cards_create`. [Marketplace cards](references/marketplace-cards.md)

## Delivery & reminders

- Match the aspect ratio to the placement and refine vague prompts unless the user asks for verbatim generation.
- Use `"draft"` or `"standard"` for iteration and `"high"` for production when the model honors `quality`. Reuse generated image file IDs in later edits.
- In Hyper Chat, generated images render automatically. On MCP or CLI, share the returned image URL or workspace path for viewing or download. Without image tools, return structured prompts and aspect-ratio specs.
