---
name: image-generation
description: Generate images through the Hyper MCP with the unified `images_generate` tool — text-to-image, image-to-image, and branded ad creatives — choosing the model (gpt-image-2, nano-banana, nano-banana-pro, seedream-4.5) per task. Use when the user asks to generate an image, create an ad creative, do an image-to-image edit, render text inside an image, or produce a print-quality poster.
metadata:
  version: 1.0.0
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

## Call shape

```python
images_generate(
    requests=[{"id": "ad1", "prompt": "A polished SaaS ad, clean composition"}],
    aspect_ratio="16:9",     # "1:1" (default), "9:16", "16:9", "4:5", "2:3", "3:2", "3:4", "4:3", "21:9", ...
    quality="standard",      # "draft" | "standard" | "high"
    n=1,                      # 1-4 images per request
    model="auto",            # see "Choosing a model" below
)
```

- **Image-to-image / brand references:** put files in the request:
  `requests=[{"prompt": "Compose into a gift basket", "reference_images": ["file1", "file2"]}]`.
- **Reproducible output:** pass `seed=...`.
- **Ground in real-world search:** pass `use_search=True`.
- Do not display image URLs — they render automatically in chat.

## Choosing a model

`model="auto"` is the right default. Override only when the task clearly calls for a
specific model:

| Task | `model` |
|------|---------|
| First-pass concepts / quick ad ideation | `gpt-image-2` |
| Image-to-image with references, high-resolution refinement, broad aspect ratios | `nano-banana` |
| Readable text inside the image (posters, labels, infographics) or search-grounded scenes | `nano-banana-pro` |
| Product photography, material/fabric fidelity, accurate spatial depth | `seedream-4.5` |

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
