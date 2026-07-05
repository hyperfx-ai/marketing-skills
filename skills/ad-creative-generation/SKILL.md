---
name: ad-creative-generation
description: Generate on-brand ad creatives — visuals + copy — for Google, Meta (Facebook / Instagram), and other paid platforms via the Hyper MCP. Extracts brand identity from a website, writes ad copy variants, and produces brand-consistent images using reference-based image generation. Use when the user asks for ad creative, ad copy variants, RSA headlines, Meta ad creative, display ads, carousel ads, or A/B test variants.
metadata:
  version: 1.0.0
icon: image_gen
short_description: Brand extraction, ad copy variants, and on-brand images for Google and Meta placements.
---

# Ad Creative Generation

Generate ad creatives — both visuals and copy — that match a brand's identity. This skill orchestrates brand extraction, copywriting, and image generation into a single workflow.

## Requirements

This skill assumes the [Hyper MCP](https://app.hyperfx.ai/mcp) is connected to your agent so the tools below are available. Brand extraction also requires Firecrawl to be configured under your Hyper integrations.

## Tool surface

| Group | Tools |
|-------|-------|
| Brand extraction | `firecrawl_branding_extract` |
| Image generation (default) | `images_generate` (`model="gpt-image-2"`) |
| Image generation (text-heavy) | `images_generate` (`model="nano-banana-pro"`) |
| Image generation (photoreal product shots) | `images_generate` (`model="seedream-4.5"`) |

For deeper image-tool selection guidance see the `image-generation` skill. To turn finished creatives into running campaigns see `google-ads` and `meta-ads`.

## Out of scope

- Picking the right image model when the task isn't ad creative — use `image-generation`.
- Creating, launching, or budgeting actual ad campaigns — use `google-ads`, `meta-ads`, `tiktok-ads`, `pinterest-ads`, or `amazon-ads`.
- Searching live competitor ads — use `meta-ads-library`.

## Critical rules

- **Always extract branding first** before generating visuals for a website/brand.
- **Always pass both logo and screenshot** as reference images — SVG logos are auto-converted to PNG.
- **DO NOT display image URLs** — they are automatically shown in chat.
- **Read `brand.screenshot.description`** to understand the product — never guess from the company name.
- **Default to logo + headline + product screenshot** for SaaS / product ads unless the user requests a different style.
- **Use `model="gpt-image-2"` for the initial ad creative by default** — with reference images for branded work, or without for loose first-pass concepts.
- **Do not default to `model="nano-banana-pro"` for the first creative pass** — use it when the user explicitly asks or when readable text inside the image is the main requirement.
- **Set `aspect_ratio` to the placement** — `1:1` (feed), `9:16` (story), `16:9` (banner) — and `quality` (`"draft" | "standard" | "high"`); `images_generate` takes those, not raw pixel sizes.
- **Respect character limits** — Google RSA headlines are 30 chars, descriptions 90 chars; Meta primary text is 125 chars visible.
- **Change one variable per variant** so test results are attributable.
- **Match aspect ratio to placement** — feed is 1:1, story is 9:16 (use `1024x1536`), banner is 16:9 (use `1536x1024`).

## Routing Table

Based on what the user needs, read the appropriate reference file:

| User Need | Reference |
|-----------|-----------|
| "Extract branding from this site" / brand colors, logo | `references/brand-extraction.md` |
| "Write ad copy" / headlines / variants / hooks | `references/ad-copy-frameworks.md` |
| Google RSAs / display ads / Performance Max assets | `references/google-ads-creatives.md` |
| Meta / Facebook / Instagram ads / carousel / stories | `references/meta-ads-creatives.md` |

When the task spans multiple areas (e.g., "create ad creatives for this website"), follow the full workflow below.

## Core Workflow

### Phase 1: Brand Extraction

Call `firecrawl_branding_extract` with the website URL. This single call returns branding data, a saved logo, and a website screenshot:

```python
brand = firecrawl_branding_extract(url="https://example.com")
```

The result contains:
- `brand.logo.file_id` — logo image to use as reference
- `brand.screenshot.file_id` — website screenshot to use as reference
- `brand.branding` — colors, typography, spacing, personality

Both `logo` and `screenshot` are saved images ready to pass as `reference_images` to image generation tools. SVG logos are automatically converted to PNG, so always include the logo — no need to filter by format.

**For deeper guidance on brand extraction, read `references/brand-extraction.md`.**

### Phase 2: Ad Copy Generation

Using the brand personality, tone, and value proposition from the extraction, write ad copy variants. Structure copy by what's being tested:

1. **Hook variants** — different opening angles (number-led, question, pain-point, benefit-first)
2. **Body variants** — different messaging (social proof, feature highlight, urgency)
3. **CTA variants** — different calls to action (Learn More, Shop Now, Get Started, Try Free)

Change only one element per variant so results can be attributed to specific changes.

**For copy frameworks, hook patterns, and variant strategy, read `references/ad-copy-frameworks.md`.**

### Phase 3: Visual Creative Generation

Generate ad images using brand assets as references. Always pass **both logo and screenshot** as reference images — SVG logos are automatically converted to PNG by the branding tool.

**Read `brand.screenshot.description`** to understand what the product actually does and what the UI looks like. Do not guess from the company name.

**Preferred first pass: `images_generate` with `model="gpt-image-2"`**

#### Default approach (best practice for SaaS / product ads)

By default, a strong ad creative has three layers: **brand** (logo), **copy** (headline), and **product** (realistic screenshot showing the core value prop). This is the recommended starting point when the user hasn't specified a creative direction. Use `model="gpt-image-2"` for this initial composition unless the user explicitly asks for another model or the image is primarily a text-rendering task.

```python
images_generate(
    requests=[{
        "prompt": (
            "Social media ad creative for [company name]. "
            "Top: the [company] logo. "
            "Headline: '[headline from ad copy phase or site hero text]'. "
            "Below the headline: a clean, realistic product screenshot of [describe the actual UI "
            "based on brand.screenshot.description]. "
            "Match the brand style from the references."
        ),
        "reference_images": [brand.logo.file_id, brand.screenshot.file_id]
    }],
    model="gpt-image-2",
    aspect_ratio="1:1",
    quality="high"
)
```

#### Following user direction

If the user asks for a specific creative style (lifestyle imagery, abstract, illustration, people using the product, etc.), follow their direction. The defaults above are a starting point, not a constraint. The reference images still supply brand consistency regardless of creative direction.

#### Things to avoid (unless the user specifically asks)

- Made-up visual elements (robot mascots, random platform logos, abstract graphics)
- UI chrome (buttons, nav bars, form inputs) — ad platforms add their own CTAs
- Guessing what the product does from the company name
- Generic marketing clip art

## Visual Tool Selection

| Scenario | Tool | Why |
|----------|------|-----|
| On-brand creative (default) | `images_generate` (`model="gpt-image-2"`) with logo + screenshot refs | Best default for the first branded concept |
| Text-heavy creative (headlines in image) | `images_generate` (`model="nano-banana-pro"`) | Use only when text rendering inside the image is the main requirement |
| Quick ideation / concept exploration | `images_generate` (`model="gpt-image-2"`) | Fast first-pass concepting with no references needed |
| Iterative refinement of existing image | `images_generate` (`model="nano-banana"`) with the image as a reference | Edit a specific generated image |
| Photoreal product shots / material detail | `images_generate` (`model="seedream-4.5"`) | Strong fabric/texture/spatial depth |

## Platform Quick Reference

| Platform | Format | Image Size | Key Limits |
|----------|--------|-----------|------------|
| Meta Feed | 1:1 | 1080x1080 | Primary text: 125 chars visible |
| Meta Story | 9:16 | 1080x1920 | Full screen, 15s max |
| Meta Carousel | 1:1 | 1080x1080 | Up to 10 cards |
| Google RSA | N/A (text only) | N/A | 15 headlines (30 chars), 4 descriptions (90 chars) |
| Google Display | Various | 1200x628 | Responsive display ads |

**For full platform specs, read `references/google-ads-creatives.md` or `references/meta-ads-creatives.md`.**

## Ad Copy Variant Quick Reference

When generating variants from existing top performers:

1. Identify the winning elements: hook type, CTA, messaging angle, format
2. Generate variants that preserve winning elements while changing one variable
3. Group variants by what's being tested (hook, body, CTA)
4. Pair variants for A/B testing — each pair should isolate one variable

**For detailed frameworks, read `references/ad-copy-frameworks.md`.**

- **Follow user direction** — if the user wants lifestyle, illustration, abstract, or any other style, follow their lead. The reference images still supply brand consistency regardless of creative direction.
