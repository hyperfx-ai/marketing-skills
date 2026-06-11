---
name: image-generation
description: Choose the right image generation tool through the Hyper MCP — OpenAI (gpt-image-2), Nano Banana (Gemini), Seedream (ByteDance via fal.ai) — for ad creatives, branded compositions, text-heavy assets, photorealistic product shots, image-to-image edits, and high-resolution output. Use when the user asks to generate an image, create an ad creative, do an image-to-image edit, render text inside an image, or produce a print-quality poster.
use_cases:
  - Generate images with AI
  - Create ad creatives with text
  - Image-to-image generation
  - Style transfer
  - High-resolution image production
triggers:
  - image
  - generate image
  - create image
  - ad creative
  - image with text
requires_toolkits:
  - image_gen
suggested_toolkits:
  - file_manager
  - firecrawl
---

# Image Generation

Guide for selecting the right image generation tool through the Hyper MCP based on what the user is trying to make.

## Requirements

This skill assumes the [Hyper MCP](https://app.hyperfx.ai/mcp) is connected to your agent so the tools below are available. For brand-consistent ad creative work, Firecrawl must also be configured under your Hyper integrations.

## Tool surface

| Group | Tools |
|-------|-------|
| OpenAI (`gpt-image-2`) | `openai_image_generation`, `openai_image_edit` |
| Nano Banana (Gemini) | `nano_banana_image_generation`, `nano_banana_image_edit`, `nano_banana_multi_turn` |
| Seedream (ByteDance via fal.ai) | `seedream_image_generation` |
| Brand extraction (companion) | `firecrawl_extract_branding` |

## Out of scope

- Full ad creative workflows (brand extraction → copy → image) — use `ad-creative-generation`.
- Video generation, transcription, captions, voiceover — use `video-generation`.

## Tool Selection Framework

### Rule 0: Website / brand ad creative requests → extract branding first (Firecrawl)
If the user provides a website URL and asks for ad creatives, brand-consistent visuals, or marketing assets, **always extract branding before generating images**.

1. Call `firecrawl_extract_branding` with the URL. The result returns brand colors, fonts, personality / tone, and saved image files (logo, favicon, og_image).
2. Optionally call `firecrawl_scrape_url` with `formats=["screenshot"]` to capture the landing page for visual context.
3. Compose your image generation prompt using the extracted colors (hex codes), font names, and personality tone. Pass the logo `file_id` from the result as a `reference_image_file_id`.

**Critical:** The result includes a `file` field — this is a JSON data file, NOT an image. Never pass it to image gen tools. Only `logo.file_id` and `images.*.file_id` are actual images you can use as references.

### Rule 1: Explicit text-heavy assets → Nano Banana Pro (Gemini)
If the primary requirement is readable embedded text inside the image itself, such as headlines, labels, UI text, or poster copy:

```python
nano_banana_image_generation(
    model="pro",
    requests=[{"id": "ad1", "prompt": "Create an ad with readable text '50% OFF'"}],
    aspect_ratio="16:9",
    image_size="2K"
)
```

### Rule 2: Reference images or brand assets → OpenAI Edit by default
If the user provides images, branding assets, screenshots, or wants an initial branded composition, prefer `openai_image_edit`.

```python
openai_image_edit(
    requests=[{"prompt": "Compose into gift basket", "reference_images": ["file1", "file2"]}]
)
```

Use Nano Banana only when the user explicitly wants Nano Banana or the image is text-heavy enough that text rendering is the main concern.

### Rule 3: Initial ad creative or first-pass concepts → OpenAI
For initial creative exploration, first-pass ad concepts, or early branded directions, prefer OpenAI tools:

```python
openai_image_generation(
    requests=[{"prompt": "A polished SaaS ad concept with clean composition"}],
    size="1024x1024"
)
```

For reference-based branded ads, prefer:

```python
openai_image_edit(
    requests=[{"prompt": "Create a polished branded ad concept", "reference_images": ["file1", "file2"]}]
)
```

### Rule 4: Nano Banana Pro for production text rendering
Use `nano_banana_image_generation(model="pro")` when the user explicitly wants Nano Banana or when the output needs strong text rendering inside the image. Do not default to Nano Banana for the first creative pass when OpenAI tools can handle the concept.

## Available Tools

### OpenAI Image Generation
**Best for:** Quick ideation, first-pass concepts, general creative requests without reference images.

- Model: `gpt-image-2`
- Standard sizes: 1024x1024, 1024x1536, 1536x1024
- Quality: `low`, `medium`, `high`
- Fast results for general creative requests

### OpenAI Image Edit
**Best for:** Initial branded compositions, website-based ad creatives, image-to-image generation with OpenAI quality.

- Editing or composing images using references
- Multi-image composition

### Nano Banana Image Generation (Gemini)
**Best for:** Text-heavy production assets, explicit Nano Banana requests, and high-resolution refinements.

**Models:**
- `model="pro"` (default): Gemini 3 Pro — best quality, supports Google Search grounding
- `model="flash"`: Gemini 2.5 Flash — faster and cheaper

**Key Capabilities:**
- Text in images (headlines, labels, UI elements)
- High-resolution output (1K, 2K, 4K)
- Various aspect ratios (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)
- Image-to-image with `reference_images`
- Real-world grounding via `use_google_search=True`

### Seedream 4.5 Image Generation (ByteDance via fal.ai)
**Best for:** Product photography, marketing assets, text rendering in images, material / fabric preservation, scenes with accurate spatial depth.

**Key Capabilities:**
- Fast generation (~2-3 seconds)
- Resolutions up to 4K (`auto_2K`, `auto_4K`, or preset sizes)
- Photorealistic quality with strong material / texture detail
- Size presets: `square_hd`, `square`, `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9`, `auto_2K`, `auto_4K`

```python
seedream_image_generation(
    requests=[{"prompt": "Product shot of leather handbag on marble surface"}],
    image_size="auto_2K"
)
```

### Nano Banana Image Edit
**Best for:** Modifying single existing images.

- Targeted changes to uploaded images
- Same quality options as generation

### Nano Banana Multi-Turn
**ONLY use when the user explicitly says "use multi turn image editing".**

- `mode="sync"`: Chain mode — output from turn N becomes input for turn N+1
- `mode="parallel"`: Independent mode — all turns processed independently

## Request Format

All tools use the `requests` parameter:

```python
requests=[
    {"id": "optional_id", "prompt": "Description", "reference_images": ["optional"]}
]
```

## Common Patterns

| Pattern | Tool | Notes |
|---------|------|-------|
| Website-based ad creative | `firecrawl_extract_branding` → `openai_image_edit` | Extract branding first, then create the first branded concept |
| Ad with text | `nano_banana_image_generation(model="pro")` | Use when readable text inside the image is a core requirement |
| Quick concept | `openai_image_generation` | Simple, no constraints |
| Style transfer | Nano Banana + references | Image-to-image |
| Print-quality poster | Nano Banana + 4K | High resolution |
| Product photography | `seedream_image_generation` | Photorealistic, material detail |
| Edit existing image | `nano_banana_image_edit` | Single image modification |
| Batch generation | Multiple requests | Parallel generation |

### Pattern H: Brand-Consistent Ad Creative

1. Call `firecrawl_extract_branding` with the website URL
2. Read the returned colors, fonts, personality, and logo `file_id`
3. Write a prompt that includes the actual hex colors, font names, and tone from the result
4. Pass the logo `file_id` as a reference image
5. Generate the first pass with `openai_image_edit` when using brand references, or `openai_image_generation` for loose ideation
6. Use `nano_banana_image_generation(model="pro")` only if the image itself needs strong readable text rendering

## Important Reminders

- **DO NOT display image URLs to the user** — they are automatically shown in chat
- **Refine vague prompts** — unless the user explicitly wants verbatim generation
- **Match aspect ratio to intent** — social media, print, web, etc.
- **Use appropriate resolution** — 4K for production, 1K / 2K for iteration
- **Remember `file_id`s** — generated images can be reused in subsequent operations
- **For website-based brand work** — call `firecrawl_extract_branding` before generating ad creatives
- **For initial ad creatives** — prefer OpenAI tools first; reserve Nano Banana Pro for explicit text-heavy assets or explicit user preference
