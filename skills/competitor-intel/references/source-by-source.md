# Source-by-Source Playbook

Per-source operator guide for competitor intel. For each source: what it reveals, when to use it, the right tool call, common pitfalls. Read the section that matches the source you're pulling from. The cross-source workflow lives in [`SKILL.md`](../SKILL.md); brief output structure lives in [`brief-templates.md`](./brief-templates.md).

## Firecrawl — site, blog, pricing, landing pages

Firecrawl is the backbone for any web-content slice. Use it whenever the question is "what does the competitor's *site itself* say."

### What it reveals

- Pricing tiers, plan limits, add-ons, free-trial terms
- Hero copy, positioning, value props, primary CTAs
- Customer logos, testimonials, social proof
- Feature pages — what they emphasize and what they hide
- Brand assets — logo, color palette, fonts (`firecrawl_branding_extract`)
- Visual snapshot for evidence (`firecrawl_screenshots_create`)
- Full blog archive for content-strategy analysis (`firecrawl_websites_crawl`)

### Tool calls

| Need | Tool |
| --- | --- |
| One specific URL (homepage, pricing, a single blog post) | `firecrawl_urls_scrape(url=...)` |
| 5–50 known URLs at once | `firecrawl_urls_scrape_batch(urls=[...])` then `firecrawl_batches_status_check(...)` |
| Whole-site crawl (every blog post, every doc page) | `firecrawl_websites_crawl(url=..., max_pages=...)` then `firecrawl_crawls_status_check(...)` |
| Branding (logo + palette + voice) | `firecrawl_branding_extract(url=...)` |
| Visual snapshot for the brief | `firecrawl_screenshots_create(url=...)` |

### Pitfalls

- **JS-heavy SPAs may not render fully.** If the page comes back near-empty, fall back to `web_scrape_page` (stealth-proxy + JS render). Bonus: `web_scrape_page` accepts an `ai_query` argument that extracts targeted info from the page in one call (e.g. `ai_query="extract the pricing tier names and monthly prices"`).
- **`firecrawl_websites_crawl` can be slow + credit-heavy.** Cap with `max_pages` for first run. A 200-post blog archive easily becomes a 10-minute job.
- **Pricing pages with toggles (monthly / annual).** A single scrape captures the default state. Run twice — once for monthly, once for annual — by including the URL parameter or hash in the URL.
- **Geo-fenced pages.** Firecrawl scrapes from a default region; pricing in EUR vs USD vs GBP varies. Note the apparent locale of the result in the brief.

## HyperSEO — rankings, backlinks, domain overlap, AI search

The credit-metered SEO surface (DataForSEO under the hood). Use intentionally — every call has cost. For full HyperSEO depth on keyword research, see the [`seo-research`](../../seo-research) skill.

### What's most useful for competitor intel (vs general SEO)

| Tool | What it answers |
| --- | --- |
| `hyperseo_competitors_search(keywords=[...], location_code=2840, limit=10)` | Who ranks for the same keywords as us? Pass the *category keywords you want to win*, not a domain. Use when the user can't name the competitor set. |
| `hyperseo_competitor_domains_search(domain=..., location_code=2840)` | Per-competitor overlap and rank profile against a target domain. |
| `hyperseo_domain_overview_get(domain=..., location_code=2840)` | One-shot snapshot — keyword count, estimated monthly organic clicks (ETV), traffic value, backlinks. The "first call to make per competitor." |
| `hyperseo_domain_keywords_get(domain=..., limit=50, location_code=2840)` | What keywords does this competitor rank for? |
| `hyperseo_domain_intersections_search(domain1=ours, domain2=theirs, limit=50)` | Keywords *both* domains rank for in the same SERPs — and at what positions. Highest-leverage call for "what do we compete on" analysis. |
| `hyperseo_site_keywords_search(domain=..., limit=...)` | Keyword opportunities a domain targets or could target. |
| `hyperseo_backlinks_history_get(target=..., date_from="YYYY-MM-DD", date_to="YYYY-MM-DD")` | Are they building links? Losing them? Note: arg is `target`, not `domain`. |
| `hyperseo_rank_history_get(domain=..., date_from=..., date_to=...)` | Monthly ETV, keyword count, and rank trend over time for a domain. Does *not* take a per-keyword filter — it returns the domain-wide trend. |
| `hyperseo_mentions_track(query=..., brands=[...])` | Runs the `query` against OpenAI / Claude / Perplexity (with web search) and returns citations + which `brands` were mentioned. The right tool for "who shows up when LLMs answer this question." |
| `hyperseo_ai_overviews_get(keyword=..., location_code=2840)` | Google AI Overview / AI Mode summary + cited sources for one keyword. Singular keyword, integer location code. |
| `hyperseo_ai_search_volume_get(...)` | Search volume specifically for AI-search queries — different from web-search volume. |

### Pitfalls

- **Looping over competitors burns credits fast.** Always batch — pull `hyperseo_domain_overview_get` for all 5 competitors in succession, then move to next call. Don't interleave.
- **`hyperseo_competitors_search` returns 100s — cap your set early.** Take the top 5 organic competitors, then validate with the user before going deeper. A 12-competitor brief is unreadable.
- **Backlink and rank data lags by days/weeks** depending on the underlying provider. Don't use this for "what happened yesterday" — use it for trends.
- **AI Overview citations are volatile.** A single AI Overview pull is noise. Track over time; the trend is what matters.
- **Country/locale matters.** A US-default `hyperseo_serp_results_get` is meaningless for a competitor whose primary market is the UK. Always set `location_code` explicitly (integer — e.g. `2826` for UK, `2840` for US, `2124` for CA, `2036` for AU).

## Apify scrapers — organic social

The Apify-backed scrapers each handle one platform. Use the right one for each platform; don't try to make Firecrawl scrape Instagram (it can't handle the auth/render).

### Instagram

| Tool | What it pulls |
| --- | --- |
| `scrape_instagram(direct_urls=["https://www.instagram.com/<user>/"], results_type="posts", results_limit=50)` | General-purpose: pull posts, comments, details, or reels from a profile/hashtag/place URL. Set `results_type` to switch what you get. |
| `scrape_instagram_posts(usernames=["<user>"], results_limit=24)` | Targeted post pull — recent posts from known accounts with engagement data. Takes an array of usernames. |
| `scrape_instagram_followers_count(usernames=["<user1>", "<user2>"])` | Just the follower count — cheap and batchable. Track over time for growth-rate signal. Takes an array. |

**Useful for:** organic engagement trend, content cadence, hashtag patterns, what creative is working for them. Don't mistake total followers for engagement health — a 200K-follower account averaging 800 likes/post is in trouble; a 30K averaging 4K is winning.

**Pitfalls:** private accounts are unscrapable (don't try). Some posts return without all metadata if Instagram has changed its DOM — re-run later usually fixes it.

### TikTok

| Tool | What it pulls |
| --- | --- |
| `scrape_tiktok_videos(profiles=["<user>"], results_per_page=30)` | Recent videos — caption, view count, like count, comment count, share count, posted-at, video URL. Also accepts `hashtags`, `search_queries`, or `post_urls` instead of `profiles`. |
| `scrape_tiktok_comments(post_urls=["https://..."], comments_per_post=50)` | Comments on a specific video — useful for sentiment / customer-language mining. |

**Useful for:** posting cadence, viral moments, content format trends (which videos hit 100K vs 5K). TikTok's algorithm is hit-driven, so look at the *distribution* of view counts across the last 30 videos, not the average.

**Pitfalls:** TikTok aggressively rate-limits. Don't run more than ~3 username scrapes per minute — pace.

### LinkedIn *(conditional — integration must be enabled)*

| Tool | What it pulls |
| --- | --- |
| `scrape_linkedin_profiles(urls=[...])` | Profile-level data for personal *or* company URLs — title, headline, company info, recent posts |

**Useful for:** company-page positioning shifts, exec hires (a new VP of Marketing usually signals strategy change), thought-leadership content from execs. Pulled per-URL, so for a competitor org grab the company URL plus 2–3 key exec URLs.

**Important:** this tool is only present in the agent's tool list when the LinkedIn-scraper integration is enabled in the workspace. If you don't see `scrape_linkedin_profiles` in the tool inventory, skip the LinkedIn slice entirely — don't fail the whole brief.

**Pitfalls:** LinkedIn aggressively detects + blocks scraping. Even with the integration enabled, expect occasional empty results. Don't pull more than a handful at a time.

### Twitter / X

| Tool | What it pulls |
| --- | --- |
| `search_tweets(from_user=..., max_items=...)` | Tweets from a specific account. Also supports `search_terms`, `to_user`, `mention`, `since` / `until` (YYYY-MM-DD_HH:MM:SS_UTC), `min_faves`, `filter_replies`, `lang`, etc. — rich filter surface, prefer the typed args over a freeform query string. |

**Useful for:** real-time signals, launch announcements, exec / founder voice, where in the funnel a customer is when they tweet about the competitor.

**Pitfalls:** Twitter / X search is increasingly limited; some tweets are missing. Don't expect comprehensive coverage. Use for signal, not census.

### Reddit

| Tool | What it pulls |
| --- | --- |
| `scrape_reddit(searches=["<term>"], max_items=50, sort="new", time="month")` | Posts and threads matching the search terms — title, body, upvotes, comments, subreddit. Also accepts `start_urls=["https://www.reddit.com/r/<sub>/"]` to scrape a specific subreddit. `time` filter: "all" / "day" / "week" / "month" / "year". |
| `scrape_reddit_leads(searches=[{"keyword": ..., "subreddit": ...}], hours_back=24, max_items=100)` | Lead-flavored variant: structured keyword + optional subreddit search, with `negative_keywords` filter and `hours_back` lookback. Use for "find people complaining about [competitor]" or "find buying-intent posts." |

**Useful for:** unfiltered customer sentiment, competitive comparisons users do themselves, complaints / praise. The single best source for "what do real people say about this competitor."

**Pitfalls:** Reddit threads can be old — sort by `new` and filter by date. A post from 2021 doesn't reflect today's product. Self-promotion is rampant — discount any thread that looks astroturfed.

## Google search & trends

| Tool | What it pulls |
| --- | --- |
| `search_google_results(query=..., num_results=10, country="us", language="en", max_age_days=...)` | Google SERPs — organic results, People Also Ask, related queries, paid results. Returns titles, URLs, descriptions, positions. |
| `web_search(...)` | Generic web search — fallback if `search_google_results` returns empty or is rate-limited |
| `scrape_google_trends(search_terms=[...], time_range="today 3-m", geo="US")` | Trend interest over time. `time_range` options: `now 1-H`, `now 4-H`, `now 1-d`, `now 7-d`, `today 1-m`, `today 3-m`, `today 5-y`, `all`. Empty `geo` = worldwide. |

**Useful for:**

- `search_google_results(query="<competitor> reviews", num_results=20)` — what review sites surface, what's on page 1 (positive / negative).
- `search_google_results(query="<competitor> alternative", num_results=20)` — who Google considers their competition.
- `search_google_results(query="<competitor> vs <us>", num_results=20)` — existing comparison content (gold for understanding the conversation already happening).
- `scrape_google_trends(search_terms=["<competitor>", "<us>"], time_range="today 3-m", geo="US")` — relative interest delta. The single chart that always lands in a board update.

**Pitfalls:** SERPs are personalized. Results vary by location and history. Always set `geo=` explicitly when using trends, and assume search results are roughly directional, not exact.

## Web scraping fallbacks

For sites Firecrawl can't render (heavy SPA, JS-locked, anti-bot):

```
web_scrape_page(url=..., use_proxy=true, stealth_proxy=true, ai_query="extract the pricing tier names and monthly prices")
```

The `ai_query` argument turns one scrape call into a one-shot extraction — no follow-up parsing needed for well-defined fields. Use it whenever you know in advance what slice of the page matters.

Lighter-weight alternatives:
- `web_fetch_page(url=...)` — straight HTTP fetch, no JS render
- `web_loader(url=...)` — quick text extraction, less overhead than `web_scrape_page`

Order of fallback when Firecrawl is empty: `web_scrape_page` (with `ai_query`) → `web_fetch_page` → `web_loader`.

## Ecommerce competitor specifics

When the competitor is a DTC / ecommerce brand:

| Tool | What it pulls |
| --- | --- |
| `scrape_ecommerce_products(...)` | Product listings — title, price, availability, variants. Useful for catalog deltas. |
| `scrape_ecommerce_reviews(...)` | Product reviews — useful for sentiment + product-feedback mining at scale. |

These are stronger than `firecrawl_urls_scrape` on a PDP because they normalize the product fields across platforms (Shopify / WooCommerce / etc.) instead of returning raw HTML.

## Choosing the right source for the job

| The user wants… | Source priority |
| --- | --- |
| "What changed on [competitor]'s pricing page?" | Firecrawl on the pricing URL — diff against last scrape |
| "Are they ranking for X?" | `hyperseo_domain_keywords_get` (filter the result) — `hyperseo_rank_history_get` returns *domain-wide* trend, not per-keyword |
| "What keywords do they have that we don't?" | `hyperseo_domain_intersections_search` (returns keywords *both* rank for at what positions; gap = ours zero / theirs non-zero) |
| "How fast are they growing on Instagram?" | `scrape_instagram_followers_count(usernames=[...])` (trend over multiple runs) |
| "What's the conversation about them online?" | Reddit + Twitter + Google reviews search |
| "Who shows up in AI Overviews for our category?" | `hyperseo_ai_overviews_get(keyword=..., location_code=...)` per keyword |
| "Who do LLMs cite when asked about our category?" | `hyperseo_mentions_track(query="best [category] tools", brands=[...])` |
| "Are they hiring?" | LinkedIn (`scrape_linkedin_profiles` on the company URL) — check team size + recent posts about hiring |
| "Did they just raise / launch / pivot?" | Twitter (`search_tweets(from_user=...)`) + News via `search_google_results` |

## Cost & rate-limit discipline

Every source has cost (HyperSEO credits, Apify compute, Firecrawl quota). Operating principles:

1. **Cheapest call first.** A `hyperseo_domain_overview_get` is cheaper than a `firecrawl_websites_crawl` of their whole blog. Pull the cheap stuff to scope the expensive stuff.
2. **Per-competitor budget.** Decide before pulling: "for each competitor I'll spend ~5 calls." Stick to it. Drift kills credit budgets.
3. **Sequence, don't parallelize.** 8 parallel scrapes = 8 timeouts. 8 sequential scrapes = 8 results, with the option to bail early if the early ones don't reveal anything.
4. **Cache + re-use within the session.** A `hyperseo_domain_overview_get` result is stable for a day or two — don't re-pull within the same brief.
5. **Tell the user the budget upfront.** "This will hit ~25 HyperSEO calls and ~12 Firecrawl scrapes for the 4-competitor brief. OK to proceed?" Avoids a $50 surprise on the bill.
