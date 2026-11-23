# Brand Inputs & Extraction

How to collect a brand's visual identity for ad creative: extract it from a website with `firecrawl_branding_extract`, or gather it from the user directly, then save it as `brand-kit.json`.

## When to call `firecrawl_branding_extract`

Call it in Step 0 when the brand has a website and the workspace has no `brand-kit.json` for that brand. It is built into Hyper; there is nothing to set up. One call returns branding data, a saved logo, and a described website screenshot:

```python
brand = firecrawl_branding_extract(url="https://example.com")
```

Skip it when a confirmed `brand-kit.json` already exists, when the user supplies brand guidelines or assets, or when running outside Hyper (use the manual intake below).

## Return shape

```
brand.success                 -- false when extraction failed; read brand.error
brand.error                   -- failure reason, when success is false

brand.logo.file_id            -- file id of the saved logo (pass as a reference)
brand.logo.path               -- storage path of the saved logo
brand.logo.description        -- e.g. "Brand logo for Example"

brand.screenshot.file_id      -- file id of the saved website screenshot
brand.screenshot.path         -- storage path of the screenshot
brand.screenshot.description  -- AI description of what the page shows

brand.images                  -- other saved brand images (logo, favicon, og_image), when found

brand.branding                -- full brand data:
  .colors                     -- primary, accent, background, text (hex)
  .typography                 -- font families and sizes
  .spacing                    -- base units, border radius
  .components                 -- button and input styles
  .personality                -- tone and voice
  .designSystem               -- overall design system summary
  .confidence                 -- extraction confidence scores

brand.social_links            -- social profile links found on the site
brand.metadata                -- page metadata (title, description, and similar)
brand.file                    -- the saved branding JSON file (data, NOT an image)
```

Read `brand.screenshot.description` before writing any prompt or concept. It tells you what the product actually is; never guess from the company name.

**`brand.file` is JSON.** Never pass it as an image reference. Only the logo, screenshot, and `brand.images` entries are images.

## Caveats

- **Cached repeat calls.** Results are cached per domain. A repeat call for the same domain returns the cached branding data with `screenshot` set to `None` and `logo.file_id` set to `None`. Reuse the earlier run's `logo.path` / `screenshot.path` (or their file ids), or force a fresh extraction:

  ```python
  brand = firecrawl_branding_extract(url="https://example.com", refresh=True)
  ```

- **SVG logos.** The tool converts SVG logos to PNG, but conversion can occasionally fail and leave an SVG. Image and ad tools reject or skip SVG references, so confirm the logo is PNG or JPG before passing it. If it isn't, ask the user for a PNG/JPG logo.

## Reference roles

When passing assets to `ad_creatives_generate` (`references=[{"file_id": ..., "role": ...}]`), give each one the role that matches what it is:

| Asset | Role |
| --- | --- |
| Logo (PNG/JPG) | `"logo"` |
| Real product photos (packaging, device, physical product) | `"product"` |
| Website screenshot | `"style"` — use `"product"` only when the product is the software UI itself |
| Existing ads to iterate on | `"source_creative"` |

```python
references = [
    {"file_id": brand.logo.file_id, "role": "logo"},
    {"file_id": brand.screenshot.file_id, "role": "style"},
]
```

## Saving `brand-kit.json` (schema v1)

In a Hyper workspace, save the confirmed visual tokens to `/files/<brand-slug>/brand-kit.json`. `creative_concepts_generate` and `ad_creatives_generate` read it automatically (pass `brand_kit_path` when the workspace holds more than one kit). Save only after the user confirms the colors, fonts, and logo; extraction is a draft, not the truth.

| Field | Required | Source |
| --- | --- | --- |
| `version` | optional (defaults to `1`) | always `1` |
| `brand_name` | yes | site title or user |
| `website` | optional | the extracted URL |
| `logo.primary` | yes | `brand.logo.path` (returned under `/files/generated/branding_data/...` or a workspace PNG/JPG path/file ID) |
| `logo.on_dark` | optional | a light logo variant, if supplied |
| `colors.primary`, `colors.background`, `colors.text` | yes | `brand.branding.colors`, as `#RRGGBB` |
| `colors.secondary`, `colors.accent` | optional | `brand.branding.colors`, as `#RRGGBB` |
| `fonts.headline.family`, `fonts.body.family` | yes | `brand.branding.typography` |
| `fonts.headline.file`, `fonts.body.file` | optional | uploaded font files, if supplied |
| `product_photos` | optional | path to the user's product photos |
| `context` | optional | `/files/<brand-slug>/brand-context.md` when it exists |
| `confirmed_by_user` | optional (defaults to `false`) | set `true` only after the user confirms |
| `updated_at` | yes | ISO timestamp |

Minimal valid file:

```json
{
  "version": 1,
  "brand_name": "Acme",
  "website": "https://example.com",
  "logo": { "primary": "/files/acme/logo.png" },
  "colors": { "primary": "#1A4DFF", "background": "#FFFFFF", "text": "#111111" },
  "fonts": { "headline": { "family": "Inter" }, "body": { "family": "Inter" } },
  "context": "/files/acme/brand-context.md",
  "confirmed_by_user": true,
  "updated_at": "2026-11-23T10:00:00Z"
}
```

Never create or overwrite `brand-context.md` from this skill; the narrative brand doc belongs to `brand-context`.

## Manual intake (no URL, failed extraction, or outside Hyper)

When there is no website, `brand.success` is false, or no extraction tool is available, ask for:

1. Logo as PNG or JPG (not SVG).
2. 2–3 brand colors as hex codes (primary, background, text).
3. Headline and body font names.
4. Product photos, if the product is physical.
5. A one-sentence description of what the product is and who it is for.

In a Hyper workspace, map the answers into `brand-kit.json` as above. Outside Hyper, keep them in the conversation or the user's own brand doc and use them in every brief. If the user prefers to skip brand setup, proceed unbranded and say so.

## Copy tone from brand personality

Use `brand.branding.personality` (or the voice section of `brand-context.md`) to set the copy voice:

- Professional → authoritative, data-driven, clear value props
- Playful → conversational, informal CTAs
- Technical → precise language, feature-focused, specs matter
- Luxury → aspirational, exclusive language, understated claims

Brand colors inform context (a fintech brand versus a kids' toy brand), but don't paste hex codes into image prompts; the references and `brand-kit.json` already carry the colors.
