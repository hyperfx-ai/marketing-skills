---
name: customer-research
description: Mine online communities and analyze existing assets to understand what customers actually think, say, and struggle with. Use when the user wants to do customer research, ICP research, voice-of-customer (VOC), review mining, Reddit mining, YouTube comment analysis, G2/Capterra scraping, build customer personas, map jobs to be done, understand churn reasons, or find authentic customer language for copy. Also use when given transcripts, surveys, or support tickets to synthesize.
icon: apify
short_description: Mine Reddit, YouTube, G2, X, and TikTok for what customers say in their own words.
---

# Customer Research

Guide for gathering and synthesizing real customer intelligence — from online communities, review sites, video comments, and social platforms — using the Hyper MCP scraper toolkit.

The goal is always the same: surface what customers actually say (in their own words), not what you assume they say.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Researching competitor brands (site, ads, search rank) | [`competitor-intel`](../competitor-intel) |
| Writing copy *informed by* the research | `copywriting` |
| Optimizing a page using VOC insights | `page-cro` |
| Keyword research and SERP analysis | [`seo-research`](../seo-research) |

## Requirements

- **Hyper MCP installed.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Apify scrapers toolkit enabled** at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations) — provides Reddit, Twitter, YouTube, TikTok, and Instagram scrapers.

Not all scrapers need to be active for every run — enable the ones relevant to your ICP (Reddit and one review site is the minimum). If a scraper tool is missing from the tool list, skip that source and continue with the others.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `scrape_reddit` | Mine posts and comments from subreddits or by keyword |
| `search_tweets` | Search X/Twitter with advanced operators and engagement filters |
| `youtube_videos_search_top` | Find the top YouTube videos on a topic — use as input for comment mining |
| `youtube_comments_search` | Pull comments from specific YouTube video URLs |
| `youtube_video_transcripts_fetch` | Fetch the full transcript of a YouTube video for language/topic extraction |
| `scrape_tiktok_videos` | Search TikTok by keyword or hashtag — find trending conversations and comments |
| `web_scrape_page` | Scrape review pages (G2, Capterra, Trustpilot, app stores) |
| `firecrawl_urls_scrape` | Cleaner extraction for JS-heavy review pages |
| `search_google_results` | Find discussion threads, forum posts, and `site:` searches |
| `scrape_instagram_posts` | Pull recent posts from specific brand or community accounts |

## Critical rules

1. **Always capture verbatim language.** Don't paraphrase customer quotes — the exact words are what gets used in copy and messaging. Extract and preserve them.
2. **Scrape before summarizing.** Don't rely on your training data to describe what customers say about a product. Actually fetch the sources.
3. **Label confidence on every insight.** High = 3+ independent sources, unprompted. Medium = 2 sources or prompted only. Low = single source. Never present a Low-confidence finding as a conclusion.
4. **Mind the bias of each source.** Reddit skews technical and skeptical. Review sites skew toward power users and people with strong opinions. Support tickets skew toward problems. Factor this in before generalizing.
5. **Don't invent persona details.** If you don't have data for a persona field, leave it blank rather than filling it in with assumptions.
6. **`youtube_video_transcripts_fetch` is slow (~15–30s).** It spins up an isolated sandbox. Only use it for videos where the language in the spoken content (not comments) is what matters.

---

## Two modes

Most research combines both modes. Establish which applies before starting.

### Mode 1 — Analyze existing assets

The user provides raw material: interview transcripts, survey responses, NPS verbatims, support tickets, win/loss notes. No tool calls needed — the job is extraction and synthesis.

Read `references/synthesis-templates.md` for the extraction framework, persona template, and VOC quote bank format. Then produce the requested deliverable.

### Mode 2 — Go find research online

The user needs intel from online communities, review sites, and social platforms. This is where MCP tools do the heavy lifting.

See `references/source-playbooks.md` for per-source tool call examples and signal extraction tips.

---

## Mode 2 workflow

**Bias toward action.** If the user's message includes a product name (or URL) and a recognizable goal (research competitors, build a persona, understand churn, find VOC language), skip the questions, state your plan in one sentence, and start Step 1. Only ask when something essential is genuinely missing — product identity or target segment, for example. Don't ask all five questions before doing anything.

### Step 1 — Pick sources based on ICP type

Before calling anything, decide which sources are worth hitting for this specific audience:

| ICP | Required | Supplement if time allows |
| --- | --- | --- |
| B2B SaaS, technical buyers | Reddit (role subs) + G2/Capterra | YouTube tutorials, X/Twitter |
| SMB / founders | Reddit (r/entrepreneur, r/smallbusiness) + G2/Capterra | YouTube, X/Twitter |
| Developer / DevOps | Reddit (r/devops, r/programming) + G2/Capterra | YouTube, Hacker News |
| B2C / consumer | Reddit hobby subs + app store reviews (1–3 star) | YouTube comments, TikTok |
| Enterprise | G2 Enterprise filter + X/Twitter | LinkedIn, YouTube |

**Minimum viable run: Reddit + one review site.** Add supplementary sources only when the minimum doesn't produce enough signal, or when the ICP table above calls for them.

For platform-by-platform tool call examples, read `references/source-playbooks.md`.

### Step 2 — Run targeted scrapes

Pull from at least 2 sources. Single-source findings are low confidence by definition.

**Reddit — the highest-signal source for most ICPs:**

```python
scrape_reddit(
    searches=["[product category] frustrations", "[competitor name] problems"],
    sort="top",
    time="year",
    max_items=50,
    skip_comments=False,
    search_posts=True,
    search_comments=True
)
```

For specific subreddits, pair with `start_urls`:

```python
scrape_reddit(
    start_urls=["https://www.reddit.com/r/marketing/"],
    searches=["CRM"],
    sort="top",
    time="year",
    max_items=30
)
```

**YouTube comments — rich qualitative data:**

```python
# Step 1: find the relevant videos
youtube_videos_search_top(query="[product category] honest review", max_results=5, sort_by="views")

# Step 2: mine comments from the top results
youtube_comments_search(
    start_urls=["https://www.youtube.com/watch?v=VIDEO_ID_1", "https://www.youtube.com/watch?v=VIDEO_ID_2"],
    max_comments=100,
    comments_sort_by="0"   # "0" = top comments, "1" = newest
)
```

**X/Twitter — complaints, frustrations, and niche conversations:**

```python
search_tweets(
    search_terms='"[product name]" frustrating OR broken OR switched OR canceled',
    max_items=50,
    min_faves=5
)
```

**Review sites (G2, Capterra, Trustpilot):**

```python
# G2 reviews for a specific product
web_scrape_page(
    url="https://www.g2.com/products/[product-slug]/reviews",
    ai_query="Extract the top complaints and pain points from customer reviews. Include verbatim quotes.",
    use_proxy=True
)
```

**TikTok — consumer conversations and trending frustrations:**

```python
scrape_tiktok_videos(
    search_queries=["[product category] problems", "[competitor name] review"],
    results_per_page=30
)
```

**Google discovery — find threads and communities you haven't thought of:**

```python
search_google_results(
    query='site:reddit.com "[product category]" "I switched" OR "I quit" OR "stopped using"',
    num_results=20
)
```

### Step 3 — Extract signal from raw data

For each source, extract into this structure:

| Field | What to capture |
| --- | --- |
| Verbatim quote | Exact words — do not paraphrase |
| Source | Platform, URL, date |
| Sentiment | Positive / negative / neutral / frustrated |
| Theme | Pain / trigger / outcome / alternative / language |
| Profile signals | Role, company size, industry hints from context |

### Step 4 — Synthesize across sources

After pulling from 3+ sources, synthesize into the research report format in `references/synthesis-templates.md`. The report includes:

- Top themes ranked by frequency × intensity
- VOC quote bank organized by theme
- Confidence labels on every finding
- Source bias notes

### Step 5 — Build personas (optional)

Only build personas if you have ≥5 independent data points from a consistent segment. If not, say so and describe what additional research is needed first.

Persona template is in `references/synthesis-templates.md`.

---

## Questions to ask before starting

Only ask what's genuinely missing. If the product and goal are clear, go. If not, lead with these — one or two at a time, not all at once:

1. **What's the product?** (if not obvious from context — a URL works)
2. **What's the goal?** Improve messaging? Build personas? Understand churn? Find product gaps?
3. **Who is the target segment?** (all customers, a specific tier, churned users, prospects who didn't convert)
4. **What do you already have?** (transcripts, surveys, tickets, nothing)
5. **What deliverable do you need?** (synthesis report, quote bank, persona, competitive language comparison)

---

## Deliverables

Ask which one(s) the user needs before generating:

| Deliverable | When to use |
| --- | --- |
| **Research synthesis report** | General intelligence gathering — themes, quotes, implications |
| **VOC quote bank** | Copy projects — verbatim customer language organized by theme |
| **Persona document** | ICP definition work, onboarding, sales training |
| **Jobs-to-be-done map** | Product prioritization, messaging architecture |
| **Competitive language comparison** | Positioning work — how customers describe you vs. competitors |
| **Research gap analysis** | When the user has partial data and wants to know what's missing |
