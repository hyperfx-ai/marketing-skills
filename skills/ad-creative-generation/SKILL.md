---
name: ad-creative-generation
description: Generate on-brand ad creative for Meta, Google, and other paid platforms - copy variants, creative concepts, and placement-sized image or video packs. Works through the Hyper MCP, and still delivers copy, concepts, and visual briefs without Hyper. Use when the user asks for ad creative, ad copy variants, RSA headlines, Meta ad creative, display ads, carousel ads, or A/B test variants.
metadata:
  version: 2.0.0
requires_toolkits:
  - ad_creatives
  - image_gen
  - video_generation_toolkit
  - firecrawl_toolkit
icon: image_gen
short_description: Ad copy variants, creative concepts, and placement-sized image or video packs (9:16, 4:5, 1:1, 1.91:1).
---

# Ad Creative Generation

Write ad copy variants, pitch creative concepts, and produce placement-sized image or video ads that match a brand. The workflow is the same everywhere: gather brand context, write copy, pick a concept, generate creatives, review before delivery.

> **Brand files.** In a Hyper workspace, brand files live under `/files/<brand-slug>/`:
> - `brand-context.md` — positioning, audience, voice, and verified proof. Owned by the `brand-context` skill; this skill only reads it.
> - `brand-kit.json` (optional) — visual tokens: logo, colors, fonts, product photos. See `references/brand-extraction.md`.
>
> `creative_concepts_generate` reads `brand-kit.json`, and only when a kit exists does it also read `brand-context.md` (through the kit's `context` field or the sibling path). `ad_creatives_generate` reads `brand-kit.json` only, never `brand-context.md`. Outside Hyper, use whatever brand doc or details the user provides.

## Requirements

- **[Hyper MCP](https://app.hyperfx.ai/mcp)** for brand extraction (`firecrawl_branding_extract`), concepts and ad packs (`creative_concepts_generate`, `ad_creatives_generate`), and image/video generation. All are built into Hyper; there is no separate integration to connect.
- **Optional:** the Hyper Ads app (https://app.hyperfx.ai/apps) to save passed assets straight into Hyper Ads Creatives (`save_to="creatives"`).
- Some directory MCP connectors do not expose `images_generate` / `videos_generate` directly. If they are missing, use `ad_creatives_generate`, or deliver copy plus placement visual briefs.
- **Without Hyper:** Steps 0–2 work fully as text, and Step 3 produces placement-ready creative briefs for the user's own design or image tool.

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
| --- | --- |
| Brand files (Hyper workspace) | `files_list`, `files_read`, `files_create` |
| Brand extraction | `firecrawl_branding_extract` |
| Competitor ads (optional) | `marketing_queries_start`, `marketing_queries_continue` (stream `ads.meta_library`) |
| Concepts and multi-placement ad packs | `creative_concepts_generate`, `ad_creatives_generate` (background; poll `tool_job_read` if a `background_job.job_id` returns) |
| Direct image / video generation | `images_generate`, `videos_generate`, `ugc_videos_create` |

For image model choice see `image-generation`; for video models and post-production see `video-generation`. To launch finished creatives see `google-ads` and `meta-ads`.

## Out of scope

- Image work that isn't ad creative — use `image-generation`.
- Creating, launching, or budgeting campaigns — use `google-ads`, `meta-ads`, `tiktok-ads`, `pinterest-ads`, or `amazon-ads`.
- Broad competitor ad research — use `meta-ads-library` or `competitor-intel`.
- Writing or rebuilding `brand-context.md` — use `brand-context`.

## Workflow

### Step 0 — Gather brand context (never skip)

**With Hyper workspace file tools (`files_list` / `files_read`):**

1. List `/files/` and check for `/files/<brand-slug>/brand-kit.json` and `brand-context.md` for the requested brand.
2. **Both exist for this brand:** read them, then ask only for campaign details (offer, goal, target placements).
3. **Several folders contain `brand-kit.json`:** always pass `brand_kit_path="/files/<brand-slug>/brand-kit.json"` to `creative_concepts_generate` and `ad_creatives_generate`. Omitting it returns an error that lists the kits.
4. **The only `brand-kit.json` belongs to a different brand:** do not let the tools auto-apply it. Gather the new brand's details and save and pass its own `brand_kit_path`, or ask the user.
5. **Only `brand-context.md` exists:** the ad tools do not read it without a kit, so put the positioning, audience, voice rules and banned words, and verified proof directly in `brief`.
6. **Only `brand-kit.json` exists:** ask for audience, offer, proof points, and words to avoid, or suggest running `brand-context`.
7. **Neither exists:** ask for the website URL or brand assets. For physical products, also ask for real product photos so generation does not invent packaging.
   - With a URL, call `firecrawl_branding_extract(url=...)` and read `brand.screenshot.description` to learn what the product really is. Never guess from the company name.
   - If extraction fails (`success` is false) or there is no URL, ask for a PNG/JPG logo, 2–3 hex colors, headline and body fonts, product photos, and a one-sentence product description.
   - If the user wants to skip brand setup, proceed unbranded and say so.
   - Save `/files/<brand-slug>/brand-kit.json` only after the user confirms the extracted or supplied visual tokens (schema v1 in `references/brand-extraction.md`). Never create or overwrite `brand-context.md` here; suggest running `brand-context` if the user wants a persistent narrative brand doc.

**Outside Hyper (no workspace file tools):** ask the user for their brand doc, website URL, or a quick 5-point intake: product one-liner, target audience, offer, visual colors and fonts, proof points and words to avoid. Do not mention `/files/` paths.

### Step 1 — Write ad copy variants

1. **Hook variants** — number-led, question, pain-point, benefit-first, social proof.
2. **Body variants** — problem-agitate-solve, feature-benefit, before-after.
3. **CTA variants** — matched to funnel stage (Learn More, Get Started, Shop Now, Book a Demo).

Change one variable per variant so results are attributable. Ground every claim in verified proof from the brand context; if the proof isn't there, the copy doesn't make the claim. Platform limits and copy rules: `references/google-ads-creatives.md` and `references/meta-ads-creatives.md`. Frameworks, variant grouping, and A/B pairing: `references/ad-copy-frameworks.md`.

### Step 2 — Generate concepts

```json
{
  "brief": "Summer hydration launch for amateur runners; offer: 20% off first order",
  "count": 4,
  "formats": ["image"],
  "brand_kit_path": "/files/acme/brand-kit.json"
}
```

Call `creative_concepts_generate` with at least one of `brief`, `source_creative_ids`, or `source_file_ids` (`count` `1`–`10`, default `5`; `formats` defaults to `["image"]`). Put any copy direction, offer, voice bans, and verified proof into `brief`. Show the returned concepts and let the user pick before generating full packs. Without Hyper, present each concept as text: `title`, `angle`, `hook`, `visual_direction`, `headline`, `primary_text`, `call_to_action`.

### Step 3 — Generate creatives

**Matched multi-placement sets (primary path):** pass the chosen concept (either returned by Step 2 or written directly with `title`, `angle`, `hook`, `visual_direction`, `headline`, `call_to_action`, optional `primary_text`, `format`) to `ad_creatives_generate`:

```json
{
  "concept": {
    "title": "Morning Stride",
    "angle": "Fast hydration after summer runs",
    "hook": "Still dragging after mile 5?",
    "visual_direction": "Runner pouring cold citrus drink into bottle on sunlit patio, clean headroom",
    "headline": "Hydrate faster after every run",
    "primary_text": "Zero-sugar electrolytes made for summer miles.",
    "call_to_action": "Shop Now",
    "format": "image"
  },
  "kind": "image",
  "placements": ["1:1", "4:5", "9:16"],
  "variants": 2,
  "quality": "standard",
  "references": [{ "file_id": "<product photo file ID>", "role": "product" }],
  "brand_kit_path": "/files/acme/brand-kit.json",
  "save_to": "generated"
}
```

Defaults: `kind` follows `concept.format`, `placements` defaults to `["1:1", "4:5", "9:16"]`, `variants` defaults to `1` (`1`–`4` visual variants of the concept), `quality` defaults to `"standard"` (`"draft" | "standard" | "high"`), and `save_to` defaults to `"generated"`.

| Placement | Size | Use |
| --- | --- | --- |
| `"9:16"` | 1080x1920 | Stories and Reels; top 250px and bottom 340px kept clear |
| `"4:5"` | 1080x1350 | Feed portrait |
| `"1:1"` | 1080x1080 | Feed square (also accepted for Google Display alongside 1200x1200) |
| `"1.91:1"` | 1200x628 | Display and link ads; images only, rejected for video |

Drop `"1.91:1"` for video.

**Reference roles:** logo → `"logo"`; real product photos → `"product"`; website screenshot → `"style"` (use `"product"` only when the product is the software UI itself); existing ads → `"source_creative"`. Logos must be raster PNG/JPG, not SVG. When `brand-kit.json` already sets `logo.primary`, `ad_creatives_generate` loads it automatically — pass a `"logo"` reference only to override it or when running without a kit.

**Direct single-pass tools** (direct generation without concept and overlay packaging):

- `images_generate(..., ad_placements=["9:16", "4:5", "1:1"])` generates each placement independently instead of adapting one base image, and supports only `9:16`, `4:5`, and `1:1`. See `image-generation` for model choice.
- `videos_generate` / `ugc_videos_create` with `ad_placements=["9:16"]` (or `"4:5"`, `"1:1"`) produce one clip framed for the first placement when `aspect_ratio` is omitted. See `video-generation` for models and post-production.

**Without Hyper:** write one creative brief per placement: dimensions, visual layout, copy placement, safe zones, and reference notes, ready for the user's design or image tool.

### Step 4 — Review and deliver

Each `ad_creatives_generate` asset returns a quality result: pass/fail, a score, and 7 checks (product fidelity, no invented products, realism, artifacts, text legibility, brand match, safe zones). Static image packs retry failed checks automatically. Video packs are checked once on the opening frame; the CTA appears on the closing end card. Present any unpassed asset as a draft, name the failed check, and offer a targeted retry (re-call `ad_creatives_generate` for only the failed placement with a tighter `concept` or clearer `references`). Never present an unpassed asset as ready to launch.

**Delivery by surface:**

- **Hyper Chat:** assets render in the ad creative card; do not repeat raw image or video URLs in prose. Save to Hyper Ads Creatives with the card button or `save_to="creatives"` (requires the Hyper Ads app). Only passed assets are saved to Creatives; failed assets stay in generated drafts.
- **MCP / CLI:** list each asset's placement, variant, pass/fail status, and returned `url` (or `path`) so the user can view or download it.

## Quality gate

- No invented products, packaging, labels, mascots, or claims; never guess the product from the company name.
- No UI chrome (fake buttons, nav bars, form fields); ad platforms add their own CTA.
- Proof points only from `brand-context.md` or facts the user confirmed.
- Character limits respected for every platform and field.
- One variable per variant, with variants grouped by what they test.
- Follow the user's style direction (UGC, lifestyle, illustration, testimonial); references still carry brand consistency.

## Platform quick reference

| Platform | Format | Size | Key limits |
| --- | --- | --- | --- |
| Meta Feed | 1:1 or 4:5 | 1080x1080 / 1080x1350 | Primary text ~125 chars visible; headline ~40 chars |
| Meta Stories / Reels | 9:16 | 1080x1920 | Vertical full screen; keep top 250px and bottom 340px clear |
| Meta Carousel | 1:1 or 4:5 | 1080x1080 / 1080x1350 | 2–10 cards |
| Google RSA | Text only | — | Up to 15 headlines (30 chars), 4 descriptions (90 chars) |
| Google Display | 1.91:1 and 1:1 | 1200x628 / 1200x1200 | Short headline 30, long headline 90, description 90 chars |

## Routing table

| User need | Reference |
| --- | --- |
| Brand colors, logo, extraction, `brand-kit.json` | `references/brand-extraction.md` |
| Ad copy, headlines, hooks, variants, A/B pairs | `references/ad-copy-frameworks.md` |
| Google RSAs, Display, Performance Max assets | `references/google-ads-creatives.md` |
| Meta Feed, Stories, Reels, carousel | `references/meta-ads-creatives.md` |

When the request spans several areas (for example "make ads for this website"), run the full workflow above.
