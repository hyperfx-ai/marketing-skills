# SEO Site Audit

Step-by-step guide for auditing a domain's organic search health using the HyperSEO tools. Covers domain authority, current rankings, keyword opportunities, backlink health, page speed, and AI visibility.

## When to Use

- The user asks "how is my site doing in search?".
- The user wants a health check on their domain's SEO performance.
- The user is evaluating a domain before acquisition or investment.
- The user wants to understand their current organic position before planning improvements.

## Workflow

### Step 1: Domain overview

Get a high-level snapshot of domain health.

1. Ask for the exact domain (e.g., `example.com` — don't guess).
2. Run `hyperseo_domain_overview_get` on the domain.
3. Review: organic keywords count, estimated traffic, backlinks, referring domains, domain rank.

**Quick health indicators:**

| Metric | Weak | Developing | Established | Strong |
| --- | --- | --- | --- | --- |
| Domain Rank | 0 – 10 | 10 – 30 | 30 – 50 | 50+ |
| Organic Keywords | < 100 | 100 – 1,000 | 1,000 – 10,000 | 10,000+ |
| Referring Domains | < 50 | 50 – 500 | 500 – 5,000 | 5,000+ |

### Step 1b: Real performance data (conditional — requires Google Search Console integration)

If the user has Google Search Console connected in Hyper:

1. Call `google_search_console_list_sites()` to confirm the domain is verified and get the exact `site_url` as registered in GSC.
2. Call `google_search_console_query_insights` — this is a **SQL query tool**. Read the tool description for the example table name and column list, then pass a SQL string:
   ```
   google_search_console_query_insights(
       query="SELECT query, SUM(clicks) AS clicks, SUM(impressions) AS impressions,
              AVG(position) AS avg_pos FROM [table name from tool description]
              WHERE date >= CURRENT_DATE - 30 GROUP BY query ORDER BY clicks DESC LIMIT 20"
   )
   ```
   **If the tool returns a "No data cached" error:** check the `suggestion` field in the response — it contains the workspace-specific table name (workspace-specific, e.g. `hyper_cache_google_search_console_<workspace>__daily_insights`). Retry the query using that exact table name. If no data exists at all, call `google_search_console_sync()` first to trigger an initial sync, wait for it to complete, then re-query.

   Returns actual clicks, impressions, CTR, and average position from GSC — ground-truth data vs. DataForSEO estimates.
3. Use this alongside `hyperseo_domain_overview_get`. Real GSC clicks will differ from ETV estimates — present both where available.

If GSC is not connected, skip this step and rely on DataForSEO estimates throughout.

### Step 2: Current rankings and trends

Understand what the domain already ranks for and how it's trending.

1. Run `hyperseo_domain_keywords_get` with `limit=50` to see top-ranked keywords.
2. Run `hyperseo_rank_history_get` to see organic traffic and keyword count trends over time — is the domain growing or declining?
3. Sort current keywords by traffic to find the pages driving the most organic visits.
4. Identify:
   - **Strengths**: keywords in positions 1 – 5 (defend these).
   - **Low-hanging fruit**: keywords in positions 6 – 20 (improve these with content updates).
   - **Declining**: keywords losing position (investigate and fix).
   - **Trend**: compare recent months to past months — a declining trend requires urgent action.

### Step 3: Keyword opportunities

Find untapped potential.

1. Run `hyperseo_site_keywords_search` to discover keywords the domain could target but isn't.
2. Cross-check the best opportunities with `hyperseo_keyword_difficulty`.
3. Focus on keywords where:
   - The domain has topical relevance.
   - Difficulty is achievable for the domain's authority level.
   - Volume justifies the effort.

### Step 4: Backlink health

Assess the domain's link profile.

1. Run `hyperseo_backlinks_history_get` for the domain.
2. Look for:
   - **Growth trend**: are backlinks growing, stable, or declining?
   - **Referring domain ratio**: healthy profiles have a diverse set of referring domains, not just many links from few domains.
   - **Recent losses**: a sudden drop in referring domains can signal lost partnerships or content removal.

### Step 5: Competitive context

No audit is complete without context.

1. Run `hyperseo_competitor_domains_search` to find competitors based on shared organic keywords.
2. Run `hyperseo_bulk_traffic` on the user's domain + top 3 – 5 competitors to compare traffic levels quickly.
3. Run `hyperseo_domain_overview_get` on the top 3 competitors for detailed metrics.
4. Compare: how does the domain stack up on authority, traffic, and backlinks?
5. This frames the audit findings — "you rank for 500 keywords" means different things if competitors rank for 500 vs 50,000.

### Step 6: Page speed check

Assess Core Web Vitals.

1. Run `hyperseo_pagespeed` on the domain's homepage and 2 – 3 key pages (both mobile and desktop).
2. Key metrics to evaluate:
   - **Performance score**: 90+ is good, 50 – 89 needs improvement, below 50 is poor.
   - **LCP (Largest Contentful Paint)**: should be under 2.5 s.
   - **TBT (Total Blocking Time)**: should be under 200 ms.
   - **CLS (Cumulative Layout Shift)**: should be under 0.1.
3. Poor page speed directly hurts rankings, especially on mobile.

### Step 7: AI visibility check

Evaluate presence in AI search channels.

1. Run `hyperseo_ai_search_volume_get` for the domain's top keywords to understand AI channel demand.
2. Run `hyperseo_mentions_track` with the brand name on 2 – 3 relevant queries.
3. Note whether AI assistants mention the brand, and how they describe it.

## Audit Report Structure

Present findings as a structured report.

**1. Executive summary**

- Overall health assessment (one paragraph).
- Top 3 strengths.
- Top 3 areas for improvement.

**2. Domain metrics**

```
| Metric | Value | Assessment |
|--------|-------|-----------|
| Domain Rank | [X] | [Weak/Developing/Established/Strong] |
| Organic Keywords | [X] | ... |
| Estimated Traffic | [X] | ... |
| Backlinks | [X] | ... |
| Referring Domains | [X] | ... |
```

**3. Top performing keywords**

```
| Keyword | Position | Volume | Traffic | URL |
|---------|---------|--------|---------|-----|
```

**4. Quick win opportunities**

Keywords in positions 6 – 20 that could move to page 1 with content improvements.

**5. Untapped keyword opportunities**

Keywords the domain should target but currently doesn't rank for.

**6. Historical trends**

Monthly organic traffic and keyword counts from `hyperseo_rank_history_get`. Is the domain growing or declining?

**7. Backlink health**

Trend chart summary, growth / decline assessment, referring domain diversity.

**8. Page speed**

Core Web Vitals for key pages (mobile and desktop). Flag any metrics outside acceptable ranges.

**9. Competitive benchmark**

Side-by-side comparison with top 3 competitors using `hyperseo_bulk_traffic` and `hyperseo_domain_overview_get`.

**10. AI visibility status**

Whether the brand appears in AI assistant responses for key queries.

**11. Prioritized recommendations**

Ordered list of specific actions, starting with highest-impact, lowest-effort items.

## Common Mistakes to Avoid

- **Auditing without context**: raw numbers mean nothing without competitive benchmarks. Always compare against competitors.
- **Focusing only on what's broken**: highlight strengths too. The user needs to know what to protect, not just what to fix.
- **Presenting data without interpretation**: don't dump raw tool output. Every metric needs a "so what" explanation.
- **Ignoring content quality**: metrics tell you what's happening, not why. If rankings are low despite good authority, the content itself may be the issue — note this for the user to investigate.
- **One-time mindset**: an audit is a snapshot. Recommend re-auditing quarterly to track progress.
