---
name: ad-creative-generation
description: Generate on-brand ad creatives — visuals + copy — for Google, Meta (Facebook / Instagram), and other paid platforms via the Hyper MCP. Extracts brand identity from a website, writes ad copy variants, and produces brand-consistent images using reference-based image generation. Use when the user asks for ad creative, ad copy variants, RSA headlines, Meta ad creative, display ads, carousel ads, or A/B test variants.
metadata:
  version: 2.0.0
requires_toolkits:
  - ad_creatives
  - image_gen
icon: image_gen
short_description: Concept generation, multi-placement ad packs (9:16, 4:5, 1:1), quality checks, and Save to Creatives.
---

# Ad Creative Generation

Generate ad creatives — both visuals and copy — that match a brand's identity. This skill orchestrates brand extraction, copywriting, and image generation into a single workflow.

## Requirements

This skill assumes the [Hyper MCP](https://app.hyperfx.ai/mcp) is connected to your agent so the tools below are available. Brand extraction also requires Firecrawl to be configured under your Hyper integrations.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| Hyper chat | Call the tool by its name; `search_tools(queries=["<provider> <action>"])` shows its parameters | `<name>(...)` |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call_read("<name>", {...})`, `call_write` or `call_destructive`: the one that `describe` names in `call_with` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found: in Hyper chat, find its toolkit id with `discover_toolkits` and pass it to `enable_toolkit`. On an MCP client or the CLI, tell the user which integration to connect in Hyper.

## Tool surface

| Group | Tools |
|-------|-------|
| Brand extraction | `firecrawl_branding_extract` |
| Competitor ads | `marketing_queries_start`, `marketing_queries_continue` (stream `ads.meta_library`) |
| Concept generation | `creative_concepts_generate` |
| Full multi-placement ad packs (image or video) | `ad_creatives_generate` |
| Direct image generation (eval-routed default) | `images_generate` (`model="auto"`, supports `ad_placements=["9:16", "4:5", "1:1"]`) |
| Direct video generation | `videos_generate` (`model="gemini-omni-1.2-flash"`, supports `aspect_ratio` `"9:16" | "4:5" | "1:1" | "16:9"`) |

For deeper image-tool selection guidance see the `image-generation` skill. For video post-production see `video-generation`. To turn finished creatives into running campaigns see `google-ads` and `meta-ads`.

## Out of scope

- Picking the right image model when the task isn't ad creative — use `image-generation`.
- Creating, launching, or budgeting actual ad campaigns — use `google-ads`, `meta-ads`, `tiktok-ads`, `pinterest-ads`, or `amazon-ads`.
- Searching live competitor ads — use `meta-ads-library`. To read the Meta ads of a known competitor by its domain or Meta page in one query, use `marketing_queries_start` with the `ads.meta_library` stream; a repeated query within a day reads the stored run at no cost.

## Critical rules

- **Read `brand-kit.json` and `brand-context.md` first** under `/files/<brand-slug>/` before asking brand questions. If neither exists, call `firecrawl_branding_extract` once and save `/files/<brand-slug>/brand-kit.json`.
- **Use the two-step ad workflow for full creative sets:** call `creative_concepts_generate` first so the user picks concepts, then call `ad_creatives_generate` with the chosen concept and `placements` (`["9:16", "4:5", "1:1"]`).
- **Use `model="auto"` on `images_generate`** when generating single visuals or direct placement sets (`ad_placements=["9:16", "4:5", "1:1"]`). Under `"auto"`, Hyper routes standard/high text-to-image to `gpt-image-2.6-sunburst`, drafts to `gpt-image-2.6-flare`, and reference-image compositions to `nano-banana-2.1`. Never call retired `gpt-image-2`, `veo-3.1-generate-preview`, or `sora-2`.
- **Every ad creative runs through the 7-check quality audit.** Never present an asset with `quality.passed == false` as ready to ship or save it to Creatives — offer a targeted retry or explain which check failed.
- **Pass real product references with explicit roles** (`role="product"` or `role="logo"`) so packaging, labels, and logo stay faithful. SVG logos are auto-converted to PNG.
- **DO NOT display image or video URLs** — the chat card renders every placement at its true aspect ratio automatically.
- **Respect character limits** — Google RSA headlines are 30 chars, descriptions 90 chars; Meta primary text is 125 chars visible.
- **Change one variable per variant** so test results are attributable.
- **Always generate native ad placements** — `9:16` (`1080x1920`, Stories/Reels with 250px top and 340px bottom safe zones), `4:5` (`1080x1350`, Feed portrait), `1:1` (`1080x1080`, Feed square), or `1.91:1` (`1200x628`, Display/Link).

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

**Read `references/brand-extraction.md` only when the site gives no logo, colors or screenshot.**

### Phase 2: Ad Copy Generation

Using the brand personality, tone, and value proposition from the extraction, write ad copy variants. Structure copy by what's being tested:

1. **Hook variants** — different opening angles (number-led, question, pain-point, benefit-first)
2. **Body variants** — different messaging (social proof, feature highlight, urgency)
3. **CTA variants** — different calls to action (Learn More, Shop Now, Get Started, Try Free)

Change only one element per variant so results can be attributed to specific changes.

**The platform file of Phase 4 holds the copy rules of its placements. Read `references/ad-copy-frameworks.md` only for copy with no placement.**

### Phase 3: Concept & Multi-Placement Ad Pack Generation

Prefer `creative_concepts_generate` + `ad_creatives_generate` for full branded ad sets (the compositor applies crisp HTML typography, safe zones, and the 7-check quality audit automatically):

```python
concepts = creative_concepts_generate(
    brief="Launch summer hydration campaign for athletes",
    count=4,
    formats=["image"],
)

pack = ad_creatives_generate(
    concept=concepts.concepts[0],
    placements=["9:16", "4:5", "1:1"],
    variants=2,
    quality="standard",
    references=[{"file_id": brand.logo.file_id, "role": "logo"}],
    save_to="generated",
)
```

For direct single-pass image generation without HTML text composition, call `images_generate` with `model="auto"` and `ad_placements`:

```python
images_generate(
    requests=[{
        "prompt": "Natural morning daylight lifestyle shot of the product on stone counter, clean headroom for copy.",
        "reference_images": [brand.logo.file_id, brand.screenshot.file_id],
    }],
    model="auto",
    ad_placements=["9:16", "4:5", "1:1"],
    ad_format="product_hero",
    quality="standard",
)
```

#### Following user direction

If the user asks for a specific creative style (UGC, lifestyle imagery, comparison, testimonial, video), follow their direction. Pass `kind="video"` to `ad_creatives_generate` when producing paid-social video packs with an opening headline and branded end card.

#### Things to avoid (unless the user specifically asks)

- Made-up visual elements (robot mascots, invented packaging, random platform logos)
- UI chrome (buttons, nav bars, form inputs) — ad platforms add their own CTAs
- Guessing what the product does from the company name
- Generic marketing clip art or banned brand claims

## Visual Tool Selection

| Scenario | Tool | Why |
|----------|------|-----|
| Full branded ad set (9:16, 4:5, 1:1 + crisp headline/CTA + quality audit) | `creative_concepts_generate` -> `ad_creatives_generate` | Deterministic typography, safe zones, auto-retry, Save to Creatives |
| Direct image ad / concept pass | `images_generate` (`model="auto"`, optional `ad_placements`) | Eval-routed (`gpt-image-2.6-sunburst` standard, `gpt-image-2.6-flare` draft, `nano-banana-2.1` references) |
| Search-grounded or text-in-image poster | `images_generate` (`model="nano-banana-pro"`) | Grounded search and dense in-image copy |
| Seeded reproducible product shot | `images_generate` (`model="seedream-4.5"`, `seed=...`) | Reproducible text-to-image |
| Video ad creative pack | `ad_creatives_generate(kind="video")` or `videos_generate` (`model="gemini-omni-1.2-flash"`) | Native 9:16 + deterministic 4:5 / 1:1 crop and branded end card |

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
