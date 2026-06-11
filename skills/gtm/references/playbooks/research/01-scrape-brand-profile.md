# Scrape Brand Profile

Extract product identity, brand assets, and voice from the canonical CMO brand store or, when needed, from a website URL. This is the foundation — everything downstream depends on this being right.

## When to use

Read this when running the `research/foundation` group (first step of a Full Brand Audit, or any time the brand has changed positioning and the cached profile is stale). Always check `cmo_get_brand_data` first. If the brand data is missing/stale, run `cmo_collect_brand_data({"url": URL})` to refresh the canonical profile before using fallback one-off scrapers. This step feeds `02-audit-website-tracking.md` and `03-research-competitors.md`.

## What You Get

- **Product name, tagline, summary** — extracted from page copy
- **CTA patterns** — normalized labels (book_demo, start_free, contact_sales)
- **Voice** — tone, sentence style, vocabulary level, proof style, personality traits
- **Brand assets** — logo file_id, screenshot file_id, OG image file_id (if available)
- **Colors and typography** — from Firecrawl branding extraction

## Tool Calls

Preferred canonical flow:

```
cmo_get_brand_data()
```

If no current brand is attached, or if the user provided a new URL/explicit refresh request:

```
cmo_collect_brand_data(url=URL)
```

Use direct Firecrawl only as a fallback for one-off creative asset extraction when canonical CMO data does not include usable logo/screenshot references:

```
firecrawl_extract_branding(url=URL)
firecrawl_scrape_url(url=URL, formats=["markdown"], only_main_content=True)
```

From canonical CMO data or fallback scraped copy, extract product name, tagline, summary, CTA patterns, and voice. If fallback copy is too thin, scrape 2-3 sub-pages (pricing, features, about) if visible in the homepage to get richer copy for voice analysis.

## Voice Extraction

Do not guess voice from the company name or logo. Analyze actual copy:

- **Tone** — direct, casual, technical, aspirational, etc.
- **Sentence style** — short imperatives, long explanatory, mixed
- **Vocabulary** — technical jargon, plain language, operator-first
- **Proof style** — product demos, ROI claims, social proof, case studies
- **Energy** — low/measured vs high/urgent

Read the homepage hero, subheads, pricing page CTA text, and proof sections. Voice is how they actually write, not what their brand guidelines say.

## Failure Modes

- **Firecrawl returns empty markdown:** Page might block scraping or use heavy client-side rendering. Try `firecrawl_scrape_url` with `wait_for=5000` to wait for JS. If still empty, note it and move on with branding data only.
- **No OG image:** Common. Skip it, note "not available" in the brand file.
- **ai_function returns generic voice:** The input copy is probably too short. Scrape 2-3 sub-pages (pricing, features, about) and re-run with more text.
