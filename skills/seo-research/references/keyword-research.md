# Keyword Research

Step-by-step guide for finding and prioritizing keyword opportunities using the HyperSEO tools exposed by the Hyper MCP.

## When to Use

- The user wants to find keywords for a new page, product, or campaign.
- The user asks "what keywords should I target?".
- The user has seed terms and wants to expand them.
- The user needs to validate keyword ideas with real data.

## Workflow

### Step 1: Seed expansion

Start with the user's seed terms and expand them.

1. Run `hyperseo_keyword_ideas_generate` with their seed keywords (set `limit` to 30–50 for a broad view).
2. Review the ideas for relevance — discard anything off-topic.
3. If the user has a domain, also run `hyperseo_site_keywords_search` to discover terms their site naturally aligns with.

### Step 2: Volume and commercial value

Take the most promising candidates and check real demand.

1. Run `hyperseo_search_volume_get` once, with the whole shortlist in `keywords` (up to 1,000 keywords in one call).
2. Note search volume, CPC, and competition level.
3. High CPC often signals commercial intent — these keywords convert.

### Step 3: Difficulty and intent assessment

Filter by what's actually achievable and classify intent.

1. Run `hyperseo_keyword_difficulty_get` on the shortlist.
2. Run `hyperseo_intents_search` on the same keywords to classify intent (informational, navigational, commercial, transactional).
3. Score each keyword against the priority framework below.
4. Intent classification helps you decide the right content format before you start writing.

### Step 4: AI search demand (optional but recommended)

Check if these keywords are also being queried in AI assistants.

1. Run `hyperseo_ai_search_volume_get` on the top candidates.
2. Keywords with high AI volume may represent emerging demand not yet saturated in traditional search.

### Step 5: SERP validation

For top-priority keywords, check what currently ranks.

1. Run `hyperseo_serp_results_get(keyword=...)` once for each of your highest-priority keywords.
2. Look at who ranks, the format of each result (`result_type`), and any `featured_snippet` row. This tool does not return AI Overviews or People Also Ask.
3. This tells you what you need to create to compete.

## Priority Framework

Classify every keyword into a tier based on difficulty and volume:

| Tier | Difficulty | Volume | Action |
| --- | --- | --- | --- |
| Quick Win | 0 – 30 | 500+ | Target immediately. These are low-hanging fruit. |
| Medium Play | 30 – 50 | 1,000+ | Target with strong content. Requires effort but achievable. |
| Long-Term Bet | 50 – 70 | 5,000+ | Build toward over months. Needs topical authority first. |
| Aspirational | 70+ | Any | Don't target directly. Build surrounding content first. |
| Skip | Any | < 100 | Not worth the effort unless strategically important. |

## Keyword Clustering

Don't present keywords as a flat list. Group them into clusters by intent.

**Informational cluster** — "what is X", "how to X", "X guide".

- Content format: blog posts, guides, tutorials.
- Goal: build authority, earn backlinks.

**Commercial investigation** — "best X", "X vs Y", "X reviews".

- Content format: comparison pages, listicles, reviews.
- Goal: capture mid-funnel traffic.

**Transactional** — "buy X", "X pricing", "X free trial".

- Content format: landing pages, product pages.
- Goal: convert directly.

**Navigational** — "X login", "X website".

- Usually not targetable unless it's your brand.
- Note: see where the brand ranks for these with `hyperseo_domain_keywords_get(domain=...)`, or with Search Console `google_search_console_performance_get(dimensions=["query"])`.

## Output Format

Use `hyperseo_intents_search` to auto-fill the Intent column. Present the final keyword research as a prioritized table:

```
| Keyword | Volume | Difficulty | CPC | AI Volume | Intent | Cluster | Priority |
|---------|--------|-----------|-----|-----------|--------|---------|----------|
```

Include a summary with:

- Total addressable search volume across all recommended keywords.
- Number of quick wins vs long-term plays.
- Recommended first 3 – 5 keywords to target.
- Suggested topic clusters.

## Common Mistakes to Avoid

- **Chasing volume alone**: a 50,000-volume keyword at difficulty 90 is useless if the domain has no authority.
- **Ignoring intent**: ranking for informational keywords won't drive sales if the user needs conversions.
- **Flat keyword lists**: always cluster and prioritize. A list of 100 unranked keywords is not actionable.
- **Skipping SERP validation**: the actual SERP tells you what Google rewards. Don't recommend a blog post if the top 10 results are all product pages.
