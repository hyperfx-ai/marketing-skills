---
name: image-generation
description: Generate images through the Hyper MCP with the unified `images_generate` tool — text-to-image, image-to-image, and multi-placement paid-social creatives — with eval-routed model="auto" (gpt-image-2.6-sunburst, gpt-image-2.6-flare, nano-banana-2.1, nano-banana-pro, flux-3-image, seedream-4.5). Use when the user asks to generate an image, create ad creatives in 9:16/4:5/1:1, do an image-to-image edit, render text inside an image, or produce a print-quality poster.
metadata:
  version: 2.0.0
requires_toolkits:
  - image_gen
icon: image_gen
short_description: Generate and edit images with one tool and a model choice, from ad creatives to product shots.
---

# Image Generation

Generate images with the `images_generate` tool. It handles text-to-image,
image-to-image (pass `reference_images`), and multi-image composition. By default
(`model="auto"`) it picks the best model for the request; set `model` to choose one.

## Requirements

This skill assumes the [Hyper MCP](https://app.hyperfx.ai/mcp) is connected to your
agent so the `images_generate` tool is available. For brand-consistent ad creative
work, Firecrawl must also be configured under your Hyper integrations.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| Hyper chat | Call the tool by its name; `search_tools(queries=["<provider> <action>"])` shows its parameters | `<name>(...)` |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call_read("<name>", {...})`, `call_write` or `call_destructive`: the one that `describe` names in `call_with` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found: in Hyper chat, find its toolkit id with `discover_toolkits` and pass it to `enable_toolkit`. On an MCP client or the CLI, tell the user which integration to connect in Hyper.

## Call shape

```python
images_generate(
    requests=[{"id": "ad1", "prompt": "Editorial morning daylight product photo on stone counter"}],
    aspect_ratio="4:5",      # "1:1" (default), "9:16", "16:9", "4:5", "5:4", "2:3", "3:2", "3:4", "4:3", "21:9"
    ad_placements=["9:16", "4:5", "1:1"],  # optional: generate native paid-social sizes in one call
    ad_format="product_hero",              # optional: "ugc" | "product_hero" | "headline_offer" | "us_vs_them" | "testimonial"
    quality="standard",      # "draft" | "standard" | "high"
    n=1,                     # 1-4 images per request
    model="auto",            # see "Choosing a model" below
)
```

- **Image-to-image / brand references:** put files in the request:
  `requests=[{"prompt": "Compose into a gift basket", "reference_images": ["file1", "file2"]}]`.
- **Multi-placement paid social:** pass `ad_placements=["9:16", "4:5", "1:1"]` so every placement is framed natively and audited with the 7-check quality gate. For full ad packs with crisp HTML headlines and CTAs, use `ad_creatives_generate`.
- **Reproducible output:** pass `seed=...`.
- **Ground in real-world search:** pass `use_search=True`.
- Do not display image URLs — they render automatically in chat.

## Choosing a model

`model="auto"` is the right default. Under `"auto"`, Hyper selects the eval-verified winner per request:

| Task | `model` |
|------|---------|
| Production text-to-image and ad visuals (`standard` / `high` default) | `gpt-image-2.6-sunburst` |
| Fast concept drafts (`draft` default) | `gpt-image-2.6-flare` |
| Reference images, multi-reference edits, and extreme aspect ratios (1:4, 1:8, 4:1, 8:1) (`auto` default with refs) | `nano-banana-2.1` |
| Readable text inside the image or Google Search grounding (`use_search=True`) | `nano-banana-pro` |
| Candid photographic UGC scenes (text-to-image only) | `flux-3-image` |
| Reproducible text-to-image when `seed` is set (takes no references) | `seedream-4.5` |

Legacy IDs (`gpt-image-2.5-flare`, `gpt-image-2.5-sunburst`, `nano-banana`) remain accepted for explicit callers, but prefer `model="auto"` or the promoted models above. Never call retired `gpt-image-2`.

See [references/image-prompting.md](references/image-prompting.md) for per-model
prompt-writing tips.

## Branded / website ad creatives — extract branding first

If the user gives a website URL and wants on-brand creatives:

1. Call `firecrawl_branding_extract` with the URL → returns brand colors, fonts,
   personality/tone, and saved image files (logo, favicon, og_image).
2. Optionally `firecrawl_urls_scrape` with `formats=["screenshot"]` for visual context.
3. Write the prompt using the actual hex colors, font names, and tone, and pass the
   logo `file_id` in `reference_images`.

The branding result's `file` field is a JSON data file, NOT an image — never pass it
as a reference. Only `logo.file_id` and `images.*.file_id` are usable images.

## Higher-level workflows

For multi-shot product or marketplace work, prefer the workflow tools — they preserve
product identity and return structured results:

- `images_product_photoshoots_create` — multi-shot product photography (studio,
  lifestyle, hero, carousel, ad pack). See
  [references/product-photoshoot.md](references/product-photoshoot.md).
- `images_marketplace_cards_create` — marketplace listing image sets (Amazon main +
  secondary, A+ modules, Shopify). See
  [references/marketplace-cards.md](references/marketplace-cards.md).

## Reminders

- Do NOT display image URLs to the user — they show automatically in chat.
- Refine vague prompts unless the user wants verbatim generation.
- Match `aspect_ratio` to intent (social, print, web).
- Use `quality="high"` for production, `"draft"`/`"standard"` while iterating.
- Generated `file_id`s can be reused as `reference_images` in later calls.
- For website brand work, call `firecrawl_branding_extract` before generating.
