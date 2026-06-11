# Find Reddit Threads

Discover high-signal Reddit threads where the ICP discusses problems the brand solves. These are engagement opportunities — not spam targets.

## When to use

Read this when the gtm decision layer routes to `community/reddit`, or during a Full Brand Audit to populate `social-intel.md`. Inputs: ICP and product summary from `01-scrape-brand-profile.md`, plus any keyword cluster from `04-audit-seo-keywords.md`. Output is a ranked list of threads that becomes the input to `13-draft-reddit-replies.md`.

## What You Get

- **Filtered thread list** — title, URL, subreddit, upvotes, match reason
- **Sorted by engagement** — highest upvotes first
- **Capped at 20** — quality over quantity, but enough to see patterns

## Choosing Keywords and Subreddits

Keywords from the confirmed brief:
- ICP pain points ("how to automate ad reporting")
- Category terms ("ai marketing agent")
- Problem language ("managing multiple ad platforms")

Subreddits based on the ICP:
- SaaS/tech: r/SaaS, r/startups, r/entrepreneur
- Marketing: r/marketing, r/PPC, r/digital_marketing
- Industry-specific: whatever subreddit the ICP frequents

## Tool Calls

```
scrape_reddit_leads(
  searches=[
    {"keyword": "{ICP pain point}", "subreddit": "{target_sub}"},
    {"keyword": "{category term}", "subreddit": "{target_sub}"},
    {"keyword": "{category term}"}
  ],
  hours_back=720,
  search_posts=True,
  search_comments=False,
  sort="relevance",
  max_items=15
)
```

Use 720 hours (30 days) as default — 168 (1 week) is too narrow for most categories. Include at least one search without a subreddit filter for global discovery. Use `"relevance"` sort to find the most topical threads, not just the newest.

**Response shape:** Results come back in an `items` array. Each item has `matched_keyword`, `matched_subreddit`, `type` ("post" or "comment"), `title`, `text`, `url`, `community`, `upvotes`, `comments_count`, `created_at`. Filter on `type == "post"`.

## Filtering

- Posts only (`type == "post"`) — comments show `title` as "Comment on: N/A" and are harder to engage with
- Upvotes >= 3 — signal that the community cares (5 is too high for niche subs)
- Deduplicate by URL
- Sort by upvotes descending

## Failure Modes

- **Reddit returns nothing:** The category might not have Reddit presence, or the keywords are too specific. Broaden the keywords or try adjacent subreddits.
- **All results are old:** Increase `hours_back` from 168 (1 week) to 720 (1 month). If still nothing, the category doesn't have active Reddit discussion. Note this honestly.
- **Results are off-topic:** The keywords are too generic. Use more specific ICP language from the confirmed brief.
