# Source Playbooks

Per-source tool call patterns, search strategies, and signal extraction tips for customer research.

---

## Reddit

Reddit is typically the highest-signal source for most B2B and B2C ICPs. People write long, unfiltered explanations of their problems, alternatives they considered, and why they switched away from products.

**What to look for:**
- "I've been using X for Y months and..." → reveals trigger, tenure, and accumulated friction
- "We just switched from X to Y because..." → reveals switching triggers and decision criteria
- "Does anyone else struggle with..." → reveals shared pain points
- Threads with 50+ upvotes where people are explaining their situation in detail

**Search strategies:**

```python
# Broad pain/frustration sweep
scrape_reddit(
    searches=["[product category] frustrating", "[product category] problems", "[product name] vs"],
    sort="top",
    time="year",
    max_items=50,
    skip_comments=False,
    search_posts=True,
    search_comments=True
)

# Competitor switching conversations
scrape_reddit(
    searches=["switched from [competitor]", "moved away from [competitor]", "[competitor] alternative"],
    sort="top",
    time="year",
    max_items=30
)

# Subreddit-specific (when you know where your ICP hangs out)
scrape_reddit(
    start_urls=[
        "https://www.reddit.com/r/marketing/",
        "https://www.reddit.com/r/entrepreneur/"
    ],
    searches=["[product category]"],
    sort="top",
    time="year",
    max_items=40
)
```

**Bias note:** Reddit skews technical, skeptical, and vocal. Mainstream buyers who are satisfied don't usually post. Weight complaints appropriately.

**Subreddits by ICP:**

| ICP | Subreddits |
| --- | --- |
| Marketing / growth | r/marketing, r/PPC, r/SEO, r/digital_marketing |
| Founders / SMB | r/entrepreneur, r/smallbusiness, r/startups |
| SaaS / product | r/SaaS, r/ProductManagement, r/startups |
| DevOps / developer | r/devops, r/programming, r/webdev, r/sysadmin |
| E-commerce | r/ecommerce, r/shopify, r/Entrepreneur |
| Finance / accounting | r/personalfinance, r/accounting, r/bookkeeping |

---

## YouTube Comments

YouTube comments are rich with authentic customer language — especially on tutorial videos, comparison videos, and "honest review" videos. People ask questions, share frustrations, and describe their context in the comments.

**What to look for:**
- Questions that start with "How do I..." → reveals gaps in the product or onboarding
- Comments comparing alternatives: "I tried X and Y, ended up with Z because..."
- Frustrated reactions to features: "why can't it just..."
- "This changed everything for me" type comments → reveals the aha moment

**Step 1 — Find relevant videos:**

```python
# Find high-view comparison and review videos
youtube_videos_search_top(
    query="[product name] review 2026",
    max_results=10,
    sort_by="views"
)

# Find tutorial videos (comments reveal confusion and gaps)
youtube_videos_search_top(
    query="[product category] tutorial for beginners",
    max_results=10,
    sort_by="views"
)

# Find competitor videos
youtube_videos_search_top(
    query="[competitor name] vs [product name]",
    max_results=5,
    sort_by="views"
)
```

**Step 2 — Mine comments from the top 3–5 results:**

```python
youtube_comments_search(
    start_urls=[
        "https://www.youtube.com/watch?v=VIDEO_ID_1",
        "https://www.youtube.com/watch?v=VIDEO_ID_2",
        "https://www.youtube.com/watch?v=VIDEO_ID_3"
    ],
    max_comments=150,
    comments_sort_by="0"    # "0" = top (highest voted), "1" = newest
)
```

**Optional — mine the transcript for language:**

```python
# Only when the spoken content (not comments) matters — e.g., a customer story video
youtube_video_transcripts_fetch(video_id_or_url="https://www.youtube.com/watch?v=VIDEO_ID")
```

Note: `youtube_video_transcripts_fetch` takes 15–30s. Use sparingly.

---

## X / Twitter

Twitter is best for complaints (they're short and sharp), product comparisons, and finding people mid-decision. The advanced search syntax in `search_terms` is powerful.

**What to look for:**
- Complaints with engagement (faves ≥ 5 filters out noise)
- "Just switched from..." and "Can't believe X doesn't..." patterns
- Threads where people are asking for recommendations → reveals decision criteria

**Search strategies:**

```python
# Frustrated customers
search_tweets(
    search_terms='"[product name]" (frustrating OR broken OR terrible OR "doesn\'t work" OR canceled)',
    max_items=50,
    min_faves=5
)

# Switching conversations
search_tweets(
    search_terms='"switched from [product name]" OR "moved from [product name]" OR "[product name] alternative"',
    max_items=40,
    min_faves=3
)

# Request threads — people mid-decision
search_tweets(
    search_terms='"looking for" "[product category]" (recommend OR suggestions OR alternatives)',
    max_items=30,
    min_replies=2
)

# Competitor comparisons
search_tweets(
    search_terms='"[competitor] vs [product]" OR "[product] vs [competitor]"',
    max_items=30,
    min_faves=3
)
```

**Bias note:** Twitter skews toward people with opinions strong enough to post publicly. Use to find emotional language and extreme positions — validate frequency against Reddit and review sites.

---

## Review Sites (G2, Capterra, Trustpilot)

Review sites are goldmines for structured pain/benefit language. 1–3 star reviews reveal why customers churn. 4 star reviews often contain the most nuanced insight ("love it but wish it could..."). 5 star reviews reveal the aha moment in customers' own words.

**G2:**

```python
# Product reviews
web_scrape_page(
    url="https://www.g2.com/products/[product-slug]/reviews",
    ai_query="Extract verbatim customer quotes about: (1) biggest pain points, (2) what they wish the product did differently, (3) what convinced them to buy. Include the star rating context.",
    use_proxy=True
)

# Competitor reviews (what do their customers complain about?)
web_scrape_page(
    url="https://www.g2.com/products/[competitor-slug]/reviews?filters%5Bnps_score%5D%5B%5D=3&filters%5Bnps_score%5D%5B%5D=2&filters%5Bnps_score%5D%5B%5D=1",
    ai_query="What are the most common complaints about this product? Extract verbatim quotes.",
    use_proxy=True
)
```

**Capterra:**

```python
web_scrape_page(
    url="https://www.capterra.com/p/[id]/[product-name]/",
    ai_query="Extract the top pros and cons in customers' own words. Pull verbatim quotes from negative reviews.",
    use_proxy=True
)
```

**Trustpilot (B2C products):**

```python
web_scrape_page(
    url="https://www.trustpilot.com/review/[domain.com]",
    ai_query="Extract the most common complaint themes from low-rated reviews. Include verbatim quotes.",
    use_proxy=True
)
```

**App store reviews (mobile products):**

```python
# iOS
web_scrape_page(
    url="https://apps.apple.com/us/app/[app-name]/id[app-id]",
    ai_query="Extract the most common pain points from 1-3 star reviews. Include exact customer quotes.",
    use_proxy=True
)
```

**Tip:** If `web_scrape_page` returns JavaScript-blocked content, try `firecrawl_urls_scrape` instead:

```python
firecrawl_urls_scrape(
    url="https://www.g2.com/products/[product-slug]/reviews",
    only_main_content=True
)
```

---

## TikTok

Best for B2C and consumer-facing products. The comment sections on product review and comparison videos contain short but high-density emotional language.

```python
# Search for product/category conversations
scrape_tiktok_videos(
    search_queries=["[product category] honest review", "[product name] worth it"],
    results_per_page=30
)

# Hashtag mining (when you know the community hashtag)
scrape_tiktok_videos(
    hashtags=["[producthashtag]", "[categoryhashtag]"],
    results_per_page=30
)
```

Note: `scrape_tiktok_videos` returns video metadata and engagement stats, not the comments themselves. Use the video titles and captions as research signal. For comment text, note the video URLs and scrape comments via the Hyper browser tools if needed.

**Bias note:** TikTok skews younger and consumer-oriented. Strong for CPG, lifestyle, and consumer SaaS. Less useful for enterprise B2B.

---

## Google — Finding discussion threads

Google is useful for discovering discussion sources you haven't thought of, not for reading the content itself.

```python
# Find Reddit threads about a specific pain
search_google_results(
    query='site:reddit.com "[product category]" "I switched" OR "I quit" OR "stopped using"',
    num_results=20
)

# Find competitor complaints across the web
search_google_results(
    query='"[competitor name]" problems OR complaints OR "doesn\'t work" -site:[competitor.com]',
    num_results=20,
    max_age_days=365
)

# Find community discussions (forums, Slack archives, Hacker News)
search_google_results(
    query='"[product category]" ("tell me" OR "recommend" OR "alternatives") site:news.ycombinator.com',
    num_results=10
)

# Find review roundups
search_google_results(
    query='"best [product category]" OR "[product category] alternatives" 2026',
    num_results=15,
    max_age_days=180
)
```

Then use `firecrawl_urls_scrape` or `web_scrape_page` to read the most relevant URLs.

---

## Instagram

Best for pulling content from brand or community accounts — useful when researching how a competitor presents themselves and what language they use in captions.

```python
# Competitor brand posts
scrape_instagram_posts(
    usernames=["competitor_handle"],
    results_limit=30,
    data_detail_level="detailedData"
)

# Community / niche accounts
scrape_instagram_posts(
    usernames=["niche_community_account"],
    results_limit=20
)
```

Note: `scrape_instagram_posts` returns post captions, engagement, and metadata — not comment text. It's most useful for researching competitor messaging and content angles, not direct customer voice.

---

## What to do when a source fails

Some scraper tools are Apify-backed and occasionally return `fetch failed` or timeout:

1. Retry once after a short pause.
2. If it fails again, try an alternative tool (e.g., `firecrawl_urls_scrape` instead of `web_scrape_page`).
3. If still failing, note the source as unavailable and continue with remaining sources. Don't block the entire research on one failed scrape.
4. Never invent data to fill a gap — mark it as "source not available."
