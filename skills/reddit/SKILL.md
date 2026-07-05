---
name: reddit
description: Research Reddit discussions with high signal using scrape_reddit_leads and scrape_reddit — pain points, intent discovery, and trend tracking. Use when the user wants to mine subreddits for leads, find threads worth replying to, or track what a community says about a topic.
use_cases:
  - Find customer pain points from Reddit conversations
  - Monitor keyword mentions in specific subreddits
  - Discover high-intent discussions for outreach
  - Compare themes across Reddit communities
  - Build a Reddit-based insight summary with sources
triggers:
  - reddit research
  - reddit leads
  - scrape reddit
  - subreddit research
  - reddit pain points
  - reddit mentions
requires_toolkits:
  - reddit_scraper
suggested_toolkits: []
icon: reddit
short_description: Research subreddits, threads, and sentiment to mine questions and voice-of-customer.
---

# Reddit Research

Use these tools in this order for research quality:

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Reddit scraper toolkit** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

1. `scrape_reddit_leads` (precision first)
2. `scrape_reddit` (expand recall second)

## Default Workflow

### Step 1: Precision pass with `scrape_reddit_leads`

Start with focused keyword + subreddit pairs:

- `searches`: list of `{ "keyword": "...", "subreddit": "..." }`
- `hours_back`: set a clear recency window
- `search_posts=true`
- `search_comments=true` only when comment evidence is needed
- `sort="new"` for monitoring or `sort="top"` for stable discussions
- `negative_keywords` to suppress spam/noise

Use 1-3 specific keywords first. Avoid broad single words.

### Step 2: Expand with `scrape_reddit`

If precision results are too narrow:

- run `scrape_reddit` with subreddit `start_urls`
- add adjacent keyword variants in `searches`
- tune `sort` and `time` for recency vs quality
- keep `skip_comments=true` when only post-level signal is needed

## Query Quality Rules

- Prefer scoped subreddits before global search.
- Include negative filters (e.g. `onlyfans`, `porn`, `nsfw`, `promo`, `buy now`) when results are noisy.
- Increase specificity before increasing `max_items`.
- If results are sparse, widen subreddits and add semantically related keywords.

## Output Requirements

Return:

- top findings with short rationale
- source URLs
- subreddit distribution
- repeated themes/pain points
- recommended follow-up keywords

Do not return unfiltered dumps. Prioritize relevance and evidence.

