---
name: meta-ads-library
description: Research competitor Facebook and Instagram ads from the Meta Ads Library via the Hyper MCP — search by keyword, pull full ad creative and metadata, enrich with page contact info for lead generation, and surface structured ad-intelligence summaries in chat. Use when the user wants to scrape the Meta Ads Library, spy on competitor ads, monitor new ads in a category, build a lead list from advertisers, or surface creative trends across an industry.
icon: meta_ads_library
short_description: Search the Meta Ads Library for competitor ads and surface structured ad intelligence.
---

# Meta Ads Library

Guide for searching the Meta Ads Library and producing structured competitor ad intelligence.

The skill's job is to turn raw scraped ads into useful summaries: top advertisers, common CTAs, recurring hooks, recently launched creatives, and (optionally) enriched lead lists. All output is presented inline in chat — there is no database or persistence layer.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Multi-source competitor research (site, social, search rank, etc., not just ads) | [`competitor-intel`](../competitor-intel) |
| Generating *new* ad creative based on what you found | [`ad-creative-generation`](../ad-creative-generation) |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Apify integration connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps) — the Meta Ads Library tools run via Apify under the hood.

If `search_facebook_ads` is not in the tool list, stop and tell the user to enable Hyper MCP and connect Apify.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `search_facebook_ads` | Search the Meta Ads Library by keyword. Returns compact results (title, body, CTA, link, page name, dates, platforms). Max 40 per call. |
| `get_facebook_ad_details` | Get full details for a specific ad. Requires both `ad_archive_id` **and** `page_id` — both come from `search_facebook_ads` results. |
| `search_facebook_ads_enriched` | Search + enrich each result with page contact info (email, phone, website). Slower (multiple API calls per result). Max 20 per call. |
| `search_facebook_pages` | Search Facebook pages by category + location (not by keyword). Useful for building a lead list from a vertical. |
| `scrape_facebook_pages` | Scrape detailed data from specific Facebook page URLs. |

## Critical rules

1. **Public-only data.** The Meta Ads Library is public. Don't attempt to bypass any access control or scrape private content.
2. **Count limits differ between tools.** `search_facebook_ads` allows `count` up to 40. `search_facebook_ads_enriched` caps at 20 — exceeding this returns an error.
3. **`get_facebook_ad_details` needs two IDs.** Both `ad_archive_id` and `page_id` are required. Both are returned in every `search_facebook_ads` result row — pass them through together.
4. **Enriched search is slow.** It makes a Facebook page scrape per ad and optionally a website scrape. Only use it when contact info matters (lead-gen workflows). For pure ad intelligence, use the regular `search_facebook_ads`.
5. **Apify-backed tools fail intermittently.** Expect occasional `"fetch failed"` responses. Retry once after a short delay before reporting the source as missing.
6. **Don't over-interpret a single ad.** "Brand X is running a discount" is noise. "5 of the top 10 advertisers in this query are running discounts" is signal. Always aggregate before drawing conclusions.

## Workflow

### Phase 1 — Define the query

Before running anything, agree on:

1. **The search query** — keyword(s) competitors would target. Examples: `"meal kit delivery"`, `"AI marketing tools"`, `"skincare for sensitive skin"`.
2. **Country** — ISO code (e.g. `"US"`, `"GB"`, `"AU"`). Default to `"ALL"` only if the user explicitly wants global.
3. **Active vs all** — `active_status="active"` is usually what you want. Inactive ads are historical and noisier.
4. **Time window** — `period` accepts `"last24h"`, `"last7d"`, `"last14d"`, `"last30d"`, or `"all_time"`. Match the window to the user's intent (weekly digest → `"last7d"`, trend research → `"last30d"`).
5. **The job** — what is this for?
   - **Creative trend report** → use `search_facebook_ads`, summarize patterns across hooks, CTAs, formats.
   - **Top advertiser snapshot** → use `search_facebook_ads`, group by `page_name`.
   - **Lead list** → use `search_facebook_ads_enriched`, filter for rows with `contact_email` or `contact_website`.

### Phase 2 — Pull the ads

```
search_facebook_ads(
    query="meal kit delivery",
    country="US",
    active_status="active",
    count=40,                # max for this tool
    period="last30d"
)
```

Each result row includes: `ad_archive_id`, `page_id`, `page_name`, `is_active`, `start_date_formatted`, `end_date_formatted`, `title`, `body`, `cta_text`, `link_url`, `caption`, `ad_library_url`, `page_categories`, `publisher_platform`.

For more than 40 ads, paginate by re-calling with `offset=40`, `offset=80`, etc.

For lead-gen with contact info:

```
search_facebook_ads_enriched(
    query="meal kit delivery",
    country="US",
    active_status="active",
    count=20,                # max for the enriched tool
    scrape_websites=True,
    filter_spam=False
)
```

Enriched rows add: `contact_email`, `contact_phone`, `contact_website`, `page_followers`, `page_rating`, address, business hours.

### Phase 3 — Get full creative for the most interesting ads (optional)

`search_facebook_ads` returns truncated bodies for some ads. To get the complete creative — including video URLs and images — call `get_facebook_ad_details` on the specific ads worth a deeper look:

```
get_facebook_ad_details(
    ad_archive_id="559220927273823",      # from search results
    page_id="328127803978438"             # from search results
)
```

Both args come from the same row in `search_facebook_ads`. Do this for the top 3–5 ads, not all 40 — each detail call is a separate Apify run.

### Phase 4 — Surface the intelligence

Present the findings inline in chat. Pick the format that matches the user's job from Phase 1.

**Top advertisers (group by page):**

| Page | Active ads | Categories | Notable angle |
| --- | --- | --- | --- |
| Brand A | 12 | Restaurant, Meal Kit | "Skip the grocery store" hook in 8/12 ads |
| Brand B | 7 | Software, Subscription | Heavy on UGC video, "$1 first week" offer |

**Common CTAs and hooks:**

| Pattern | Count | Examples |
| --- | --- | --- |
| `Sign up` CTA | 18 | … |
| `Shop now` CTA | 12 | … |
| Price-anchor opener ("From $X/week") | 9 | … |
| Founder-story opener | 4 | … |

**Recently launched ads (last 7 days):**

| Page | Started | CTA | Hook | Library URL |
| --- | --- | --- | --- | --- |
| Brand A | 2026-04-28 | Sign up | "Skip the grocery run this week" | <ad_library_url> |

**Lead list (enriched only):**

| Page | Email | Website | Followers | Active ads |
| --- | --- | --- | --- | --- |
| Brand A | hello@a.com | a.com | 12K | 7 |

### Phase 5 — Recurring monitoring (optional)

If the user wants ongoing tracking:

1. Save the query, country, and `active_status` settings.
2. Re-run weekly with `period="last7d"`.
3. Brief becomes a delta report — *new* ads since the last run, advertisers that changed posting cadence, CTA / offer shifts.

This is when [`competitor-intel`](../competitor-intel) becomes the better skill — it handles multi-source diffing across many surfaces, not just Meta ads.

## Output standards

- **Always cite the `ad_library_url`** for any specific ad referenced in the brief — the user can click through to verify.
- **Aggregate before quoting.** Don't paste raw ad bodies; extract the pattern and quote 1–2 representative examples.
- **Mark interpretation explicitly.** "Observation: 8 of 10 top advertisers use a 'first week free' offer. Possible interpretation: …".
- **Note the time window.** Every brief should state the search query, country, and date range it was generated from.
