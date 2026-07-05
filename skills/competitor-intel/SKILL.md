---
name: competitor-intel
description: Run end-to-end competitor research and monitoring through the Hyper MCP — pick the set, scrape every public surface (site, blog, pricing, organic social, search rank, mentions, demand) via Firecrawl + HyperSEO + the Apify scrapers, diff against last run, and synthesize a brief. Use when the user wants to research competitors, build a battle card or comparison page, run a weekly digest, or asks "what's [competitor] doing?" or "how do we compare?".
metadata:
  version: 1.0.0
icon: firecrawl
short_description: Scrape and monitor competitors across web, SEO, and social, then synthesize battle cards.
---

# Competitor Intel

End-to-end competitor research and monitoring. Define the set, pull from every public surface that matters, diff against last run (or your own), and produce a brief that's actually useful — battle card, weekly digest, board update, or comparison-page input.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Competitor *paid ads* (Facebook / Instagram active ads) | [`meta-ads-library`](../meta-ads-library) |
| Pure SEO / keyword research with HyperSEO as the primary surface | [`seo-research`](../seo-research) — uses the same HyperSEO toolkit but goes much deeper on keyword work |
| Generating *creative* (images / copy) for a comparison campaign once the intel is in | [`ad-creative-generation`](../ad-creative-generation) |
| Pulling data from competitor *email programs* | Not feasible — opt-in only. Use `firecrawl_urls_scrape` on their landing pages instead. |

`competitor-intel` is the *integration layer* — it pulls from every source and synthesizes. It uses HyperSEO for the rank/backlink/intersection slice but isn't the SEO research skill itself.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **At least one of these toolkits** connected at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations):
  - **Firecrawl** *(highly recommended — backbone for any site/blog/pricing-page work)*
  - **HyperSEO** *(needed for rank, backlink, domain-overlap analysis)*
  - **Apify scrapers** — Instagram, TikTok, LinkedIn, Twitter, Reddit, Google search, Google Trends
  - **Image generation** *(optional — only if the brief feeds a comparison-page or battle-card asset downstream)*

If none of those tool prefixes appear in the agent's tool list (`firecrawl_*`, `hyperseo_*`, `scrape_instagram*`, `scrape_tiktok*`, `search_tweets`, `scrape_reddit*`, `search_google_results`, `scrape_google_trends`, `web_scrape_page`), stop and tell the user to enable the Hyper MCP and connect at least Firecrawl + one social scraper. The LinkedIn scraper (`scrape_linkedin_profiles`) is only present when that specific integration is enabled — gracefully skip the LinkedIn slice if it's missing rather than failing the whole brief.

## Tool surface

| Phase | Tools |
| --- | --- |
| Site & web content | `firecrawl_urls_scrape`, `firecrawl_urls_scrape_batch`, `firecrawl_websites_crawl`, `firecrawl_screenshots_create`, `firecrawl_branding_extract`, `web_scrape_page` (JS-rendering fallback, supports `ai_query` for targeted extraction), `web_fetch_page`, `web_loader` |
| Search rankings & backlinks | `hyperseo_competitors_search`, `hyperseo_competitor_domains_search`, `hyperseo_domain_overview_get`, `hyperseo_domain_keywords_get`, `hyperseo_domain_intersections_search`, `hyperseo_site_keywords_search`, `hyperseo_backlinks_history_get`, `hyperseo_rank_history_get`, `hyperseo_mentions_track` |
| Brand mentions in AI search & SERPs | `hyperseo_ai_overviews_get`, `hyperseo_ai_search_volume_get`, `hyperseo_mentions_track`, `search_google_results`, `web_search` |
| Organic social — Instagram | `scrape_instagram`, `scrape_instagram_posts`, `scrape_instagram_followers_count` |
| Organic social — TikTok | `scrape_tiktok_videos`, `scrape_tiktok_comments` |
| Organic social — LinkedIn | `scrape_linkedin_profiles` *(conditional — only available when the LinkedIn-scraper integration is enabled in your Hyper workspace)* |
| Organic social — Twitter / X | `search_tweets` |
| Community / sentiment — Reddit | `scrape_reddit`, `scrape_reddit_leads` |
| Ecommerce competitor specifics | `scrape_ecommerce_products`, `scrape_ecommerce_reviews` |
| Demand / trend signals | `scrape_google_trends`, `hyperseo_search_volume_get`, `hyperseo_intents_search` |
| Optional: comparison-page assets | `images_generate` |

## Critical rules

1. **Public-only data.** Never scrape behind login walls or paywalls. If a target is gated, stop and surface that — don't try to bypass.
2. **Pick the competitor set before scraping.** 3–5 competitors is the sweet spot. 10+ produces an unreadable brief and burns scraper credits. If the user doesn't have a list, run `hyperseo_competitors_search(domain=<their_domain>)` first to surface the top organic competitors, then confirm the set with them.
3. **Snapshot, then diff.** First run is just a baseline — there's nothing to compare against. The value compounds on the second and third runs (what changed in pricing, what new posts went up, who lost rank). Make this expectation clear when the user runs it for the first time.
4. **HyperSEO is credit-metered.** Be intentional. Don't loop `hyperseo_domain_overview_get` over 12 competitors when you only need 4. Each call has cost — batch and cache.
5. **Apify scrapers can be slow and rate-limited.** Don't kick off 8 scrapes in parallel. Sequence them, and surface partial results to the user as they arrive instead of waiting for the full run.
6. **Snapshot what you scraped, not just the analysis.** Always include the source URL, scrape timestamp, and a short excerpt for any claim in the brief — otherwise next week's diff has nothing to compare against and the brief becomes unfalsifiable.
7. **Don't over-interpret single data points.** "Competitor X dropped a Reel that got 12K likes" is noise. "Competitor X has averaged 8K likes/post for the last 30 days, up from 2K" is signal. Build comparisons on aggregates, not anecdotes.
8. **Stay clearly factual.** Use neutral language ("Competitor X published Y on date Z, copy reads as…") not value judgments ("Competitor X's strategy is broken…"). The brief is intel, not opinion.
9. **Disambiguate brand-name SERPs.** A search for `<competitor>` alone often returns unrelated results that share the brand name (e.g. a search for "hyperfx" returns mostly HyperX headphones, not hyperfx.ai). Always pair the brand with a category modifier — `<competitor> alternative`, `<competitor> reviews`, `<competitor> pricing`, `<competitor> vs <us>` — to get clean SERPs.
10. **Apify-backed scrapers fail intermittently.** Expect occasional `"fetch failed"` or empty-result responses from `scrape_instagram*`, `scrape_tiktok*`, `scrape_reddit*`, `scrape_google_trends`, `search_tweets`, and `search_google_results`. Retry once after a short delay before reporting the source as missing — and surface partial results to the user rather than failing the whole brief if a scraper stays down.

## Workflow

### Phase 1 — Define the competitor set

Ask the user (or infer):

1. **Their domain** — needed to ground all relative comparisons.
2. **Their competitor set** — 3–5 names + domains. If unclear, surface the top organic competitors. `hyperseo_competitors_search` takes the *keywords the user wants to win*, not their domain — so first agree on 3–5 high-intent keywords for the user's category, then run:

```
hyperseo_competitors_search(
  keywords=["<category keyword 1>", "<category keyword 2>", "<category keyword 3>"],
  location_code=2840,  # 2840=US, 2826=UK, 2124=CA, 2036=AU
  limit=10
)
```

Then confirm the surfaced set with the user before continuing — never guess and proceed.

3. **The job** — what is this brief *for*? The shape changes by job:
   - **Battle card for sales** → focus on positioning, pricing, "what to say when…" objection lines.
   - **Weekly digest for marketing/exec team** → focus on what *changed* this week.
   - **Comparison-page input for marketing** → focus on objective, comparable feature/pricing data.
   - **Board / board-prep update** → focus on aggregate position (share of voice, rank deltas, growth).
4. **The cadence** — one-shot or recurring? Recurring scopes the source matrix tighter so each run completes in reasonable time.

If the user can't answer #3, stop and ask. Building intel without knowing the artifact is a guaranteed waste.

### Phase 2 — Build the source matrix

Not every source matters for every competitor or every job. Per-competitor, decide which surfaces to pull from.

| Competitor type | Sources that matter most |
| --- | --- |
| **Direct SaaS / B2B** | Site, blog, pricing page, LinkedIn company posts (if available), AI-search citations (`hyperseo_ai_overviews_get`), domain rank delta |
| **Ecommerce / DTC brand** | Site, product catalog (`scrape_ecommerce_products`), product reviews (`scrape_ecommerce_reviews`), Instagram, TikTok, Reddit threads, Google Trends interest |
| **Consumer / creator brand** | Instagram, TikTok, Twitter, YouTube *(via the YouTube toolkit if connected)*, Reddit |
| **Content-led / publication** | Site, blog (full crawl), backlinks history, AI-search citations, search rank trend |
| **Local / multi-location** | Site, Google search results for "[brand] near me", Reddit / Twitter sentiment, Google Trends regional |

The full per-source playbook (when to use, what it reveals, quirks) lives in [`references/source-by-source.md`](./references/source-by-source.md).

### Phase 3 — Pull the data

Sequence the pulls; don't fire everything in parallel. Order matters for cost and for letting partial results inform the next call.

**Order to use:**

1. **Cheapest first — HyperSEO baselines** (one call per competitor, reuse data across the brief):

```
hyperseo_domain_overview_get(domain="<competitor>.com", location_code=2840)
hyperseo_domain_keywords_get(domain="<competitor>.com", limit=50, location_code=2840)
hyperseo_domain_intersections_search(
  domain1="yourbrand.com",
  domain2="<competitor>.com",
  limit=50,
  location_code=2840
)
```

2. **Site content via Firecrawl:**

```
firecrawl_urls_scrape(url="https://<competitor>.com/pricing")
firecrawl_urls_scrape(url="https://<competitor>.com/")
firecrawl_branding_extract(url="https://<competitor>.com")  # logo, colors, voice
```

For a full-blog-archive deep dive use `firecrawl_websites_crawl` once and check status with `firecrawl_crawls_status_check`. If Firecrawl returns near-empty for a JS-heavy SPA, fall back to `web_scrape_page(url=..., use_proxy=true, ai_query="extract pricing tiers and prices")`.

3. **Social — sequenced per platform** (note: most scrapers take *arrays* of identifiers, not a single username):

```
scrape_instagram(direct_urls=["https://www.instagram.com/<competitor>/"], results_type="posts", results_limit=30)
scrape_instagram_followers_count(usernames=["<competitor>"])  # cheap, do it weekly
scrape_tiktok_videos(profiles=["<competitor>"], results_per_page=30)
search_tweets(from_user="<competitor_handle>", max_items=50)

# Only if scrape_linkedin_profiles is in your MCP tool list:
scrape_linkedin_profiles(urls=["https://www.linkedin.com/company/<competitor>"])
```

4. **Sentiment & demand:**

```
scrape_reddit(searches=["<competitor>"], max_items=50, sort="new", time="month")
scrape_google_trends(
  search_terms=["<competitor>", "yourbrand"],
  time_range="today 3-m",  # options: now 7-d, today 1-m, today 3-m, today 5-y, all
  geo="US"
)
search_google_results(query="<competitor> reviews", num_results=20, country="us")
```

5. **AI search visibility (only for SaaS/B2B usually):**

```
# AI Overview takes ONE keyword at a time + integer location_code
hyperseo_ai_overviews_get(keyword="<your category keyword>", location_code=2840)

# track_mentions runs the query against OpenAI / Claude / Perplexity and returns citations
hyperseo_mentions_track(
  query="best <your category> tools",
  brands=["<competitor>", "yourbrand"]
)
```

Surface partial results as each phase completes — don't wait for the whole pull to finish before showing the user something.

### Phase 4 — Diff

The point of the skill is *delta*, not snapshot. For each competitor, compare:

| Source | Compare against |
| --- | --- |
| Pricing page | Last scrape (changes in tier names, prices, plan limits, new add-ons) |
| Homepage hero | Last scrape (new positioning copy, new CTA, new logos) |
| Domain rank | `hyperseo_rank_history_get(domain=..., date_from=..., date_to=...)` vs last 30/90 days |
| Domain keywords | Net-new keywords ranking, lost keywords |
| Domain intersection (theirs ∩ yours) | Keywords *they* rank for and *you don't* — content gaps |
| Instagram / TikTok | Posts since last run, follower delta, engagement-rate delta |
| Twitter / Reddit | Volume of mentions vs prior period |
| AI-search citations | New AI Overview citations vs last run |

For a first run, there's no "last" — the diff section in the brief becomes "baseline established, will diff against this on next run." Tell the user this explicitly so they don't expect insight on day 1.

### Phase 5 — Brief

Synthesize into the artifact. Brief shapes by job (full templates in [`references/brief-templates.md`](./references/brief-templates.md)):

- **Battle card** — 1 page, per-competitor: positioning summary, 3 strongest competitor claims, 3 counter-claims for our side, common objections + responses, win-loss patterns.
- **Weekly digest** — 1 page total, all competitors: bullet list of what changed this week per competitor, ranked by significance.
- **Comparison-page input** — feature matrix table, pricing table, plan limits table — all sourced with URLs and timestamps.
- **Board-prep update** — share-of-voice, rank deltas, content velocity, sentiment trend over the period.

Output standards (apply to every brief):

- **Always cite source + timestamp** for every claim. "Competitor X raised the Pro tier from $79 → $99 (pricing page, 2026-04-29)" beats "X raised prices."
- **Use neutral language.** Brief is for the reader to draw their own conclusion.
- **Distinguish observation from interpretation.** Mark interpretation explicitly: "Observation: rank dropped 12 positions on 'invoice automation' over 30d. Possible interpretation: …".
- **Keep one ranked list of "things that matter"** at the top of the brief. Bury everything else below it. Most readers stop after the first 3 bullets.

### Phase 6 — Monitor on cadence (optional)

If the user wants ongoing monitoring rather than a one-shot:

1. Save the source matrix and competitor set somewhere durable (`bigquery_*`, Notion, a Sheets tab, or just inline in the user's prompt template).
2. Schedule the agent to re-run the pull on a cadence — weekly is the sweet spot. Daily produces too much noise; monthly misses fast moves.
3. The brief shape becomes the *weekly digest* by default, with the option to escalate to a deep brief when something significant changes.

## Reference workflows

| Reference | When to read |
| --- | --- |
| [`references/source-by-source.md`](./references/source-by-source.md) | Per-source playbook — what each scraper / HyperSEO call reveals, when to use it, and the quirks (rate limits, JS-rendering issues, cache windows, credit cost) |
| [`references/brief-templates.md`](./references/brief-templates.md) | Battle card, weekly digest, comparison-page, and board-prep templates with worked examples and output structure |
