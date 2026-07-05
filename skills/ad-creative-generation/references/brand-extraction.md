# Brand Extraction

Extract brand identity from a website for use in ad creative generation.

## Single-Call Workflow

`firecrawl_branding_extract` extracts branding data, downloads the logo, and captures a screenshot in one call:

```python
brand = firecrawl_branding_extract(url="https://example.com")
```

## Return Shape

```
brand.logo.file_id        -- File ID of the saved logo (pass to image gen)
brand.logo.path           -- Storage path of the saved logo
brand.logo.description    -- "Brand logo for Example"

brand.screenshot.file_id  -- File ID of the saved screenshot (pass to image gen)
brand.screenshot.path     -- Storage path of the saved screenshot
brand.screenshot.description -- AI description of the page

brand.branding            -- Dict with full brand data:
  .colors                 -- primary, accent, background, text (hex codes)
  .typography             -- fonts, font families, sizes
  .spacing                -- base units, border radius
  .components             -- button styles, input styles
  .personality            -- brand tone and voice
  .designSystem           -- overall design system summary
  .confidence             -- extraction confidence scores

brand.file                -- Saved branding JSON file (NOT an image)
```

**Critical:** `brand.file` is the JSON data file. Never pass it to image gen tools. Only `brand.logo.file_id` and `brand.screenshot.file_id` are images.

## Using Brand Assets in Image Generation

Always pass **both logo and screenshot** as reference images. SVG logos are automatically converted to PNG by the extraction tool, so always include the logo regardless of the original format.

```python
reference_images = [brand.logo.file_id, brand.screenshot.file_id]
```

The logo provides brand mark consistency. The screenshot shows the actual product UI so the model can derive both the visual style and generate realistic product shots.

### Default creative pattern (SaaS / product ads)

By default, compose: **logo + headline + realistic product screenshot**. Describe the product screenshot based on `brand.screenshot.description`, not guessed.

```python
images_generate(
    requests=[{
        "prompt": (
            "Social media ad creative for [company name]. "
            "Top: the [company] logo. "
            "Headline: '[headline]'. "
            "Below: a clean, realistic product screenshot of [describe actual UI from brand.screenshot.description]. "
            "Match the brand style from the references."
        ),
        "reference_images": reference_images
    }],
    quality="high"
)
```

This is the recommended default. If the user asks for a different creative direction (lifestyle, illustration, abstract, etc.), follow their lead — the references still provide brand consistency.

## Using Brand Data for Ad Copy

The extracted brand data is primarily useful for **copy**, not image prompts.

### Copy Tone from Brand Personality

Use `brand.branding["personality"]` to set the voice for ad copy:

- Professional → authoritative, data-driven, clear value props
- Playful → conversational, emoji-friendly, informal CTAs
- Technical → precise language, feature-focused, specs matter
- Luxury → aspirational, exclusive language, understated claims

### Colors in Copy (not image prompts)

Brand colors inform copy context (e.g., knowing the brand is a fintech vs. a kids' toy brand), but do NOT paste hex codes into image prompts — the reference images already contain the actual colors.

## Cached Results

`firecrawl_branding_extract` caches results by domain. Subsequent calls for the same domain return cached data without re-fetching. Use `refresh=True` to force a fresh extraction:

```python
brand = firecrawl_branding_extract(url="https://example.com", refresh=True)
```
