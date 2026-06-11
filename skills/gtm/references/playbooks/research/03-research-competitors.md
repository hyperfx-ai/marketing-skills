# Competitor Research

Find real competitors through the canonical CMO brand store first, then multiple rounds of search from different sources only when the stored data is insufficient. One round of web_search is never enough — each round reveals names and terms that inform the next round.

## When to use

Read this in the `research/foundation` group, after `01-scrape-brand-profile.md`. Start with `cmo_get_brand_data().market_research.direct_competitors` and `cmo_get_brand_data().search_visibility.competitors`. Run the additional web/SEO research below only when current brand data has too few competitors, looks stale, or lacks enough detail for the specific playbook. The output (`competitors.md` artifact) is consumed by the gtm decision layer's offer-first gate, the channel-fit diagnostic, and several execution flows: `the `meta-ads-library` skill` (look up the actual competitor pages), `playbooks/organic-content/04-audit-seo-keywords.md` (gap keywords), and `playbooks/organic-content/08-research-serp.md` (top-ranking competitor URLs).

## Canonical Seed

```
brand = cmo_get_brand_data()
```

Use:

- `brand.market_research.direct_competitors` for rich competitor records
- `brand.search_visibility.competitors` for SERP-discovered competitor domains
- `brand.market_research.category_terms` and `brand.market_research.search_queries` as query seeds

If those fields are empty or stale, refresh with `cmo_collect_brand_data(url=brand.url)` before running extra search rounds.

## Round 1: ICP-Shaped Search (8-10 queries, parallel)

Generate queries the buyer would actually type. Use at least 5 of these angles:

1. **Pain language** — "how to automate ad reporting without hiring"
2. **Job-to-be-done** — "ai marketing agent for small teams"
3. **Category + modifier** — "ai marketing automation platform", "autonomous marketing tool"
4. **Comparison intent** — "best {category} 2026", "{category} comparison"
5. **Problem + solution shape** — "stop manually creating ad creatives", "one tool for all marketing channels"
6. **ICP-specific** — "marketing tool for solo founder", "agency campaign management platform"

```
web_search(queries=[all 8-10], num_results=5)
hyperseo_competitors_domain(domain=DOMAIN, limit=15)
hyperseo_competitors(keywords=[top 3-4 category terms], limit=15)
```

**Warning about SEO competitor tools:** For new or small domains (fewer than ~50 organic keywords), `hyperseo_competitors_domain` returns platforms like YouTube, LinkedIn, Instagram — not actual competitors. `hyperseo_competitors` (keyword-based) is slightly better but still noisy. For new brands, web search does the heavy lifting. Don't rely on SEO tools alone.

Collect every product name and domain from the results. Filter out platforms (YouTube, LinkedIn, Reddit, Google, Facebook, Instagram), review sites, listicles, blogs, educational sites, and the client's own domain.

## Round 2: Discovery Platforms (4-6 queries, parallel)

The first round finds who SEO knows about. This round finds what's emerging.

```
web_search(queries=[
  "{category} site:producthunt.com",
  "{category} site:news.ycombinator.com",
  "{category} launched 2025 OR 2026",
  "new {category} tools",
  "{category} alternatives site:reddit.com",
  "{ICP role} tools stack 2026"
], num_results=5)
```

Extract any new product names that didn't appear in Round 1.

## Round 3: Expand from Findings (3-5 queries)

Take the top 3-5 product names discovered in Rounds 1 and 2. Search for THEIR competitors and alternatives:

```
web_search(queries=[
  "{discovered_product_1} alternatives",
  "{discovered_product_2} vs",
  "{discovered_product_3} competitors",
  "tools like {discovered_product_4}",
  "{discovered_product_5} alternative"
], num_results=5)
```

This catches products that don't rank for the category term but compete head-to-head with the products that do. Each round expands the map.

## Round 4: Community Verification

If Reddit research (07) has been run, scan the thread titles and comments for product names that didn't surface in web search. People mention tools in discussions that never appear in SEO results — new tools, niche tools, frameworks, open-source projects.

If Reddit research hasn't been run yet, do a quick:

```
web_search(queries=[
  "{category} site:reddit.com",
  "what {category} do you use site:reddit.com"
], num_results=5)
```

## Classification

After all rounds, you should have 15-40 candidate products. Classify each:


| Classification       | Definition                                                               |
| -------------------- | ------------------------------------------------------------------------ |
| **Direct**           | Same problem, same ICP. The buyer evaluates these side by side.          |
| **Adjacent**         | Nearby job or slightly different buyer. Shows up in same conversations.  |
| **Aspirational**     | Market reference that shapes expectations but isn't a direct substitute. |
| **Not a competitor** | Platforms, listicles, blogs, marketplaces → discard.                     |


**Minimum bar:** At least 5 direct competitors identified. If fewer than 5 after 4 rounds of search, the category is genuinely emerging — say so and ask the user who they encounter in the market.

## Tiered Enrichment

**Direct competitors (top 5):** Full scrape.

```
firecrawl_batch_scrape(urls=[competitor homepages + pricing pages], formats=["markdown"], only_main_content=True)
```

For each, extract:

- Positioning statement (hero copy)
- Pricing model and price points
- Key features they lead with
- Who they target (read CTA patterns, case studies)
- Strengths vs the client
- Weaknesses
- Gap the client can exploit

**Adjacent (3-5):** One paragraph each from search snippets. What they do, how they differ, why the ICP encounters them.

**Aspirational (0-2):** One sentence. Who they are and what expectation they set.

## Trust Hierarchy

1. **User says "we lose deals to X"** → highest trust. Always include as direct.
2. **Multiple search rounds surface X** → high trust.
3. **Only one round found X** → moderate trust. Verify with a follow-up search.
4. **SEO overlap tools say X** → moderate trust. Often returns platforms.
5. **The website says "alternative to X"** → useful but could be aspirational.

## Cross-Pollination

- **→ Keyword research (04):** Competitor names become seeds ("{competitor} alternative", "{competitor} vs"). Competitor domains become inputs for keyword mining.
- **→ Ad library (06):** Direct competitor names become search queries.
- **→ AI visibility (05):** Competitor names go into brand tracking.
- **→ ICP expansion:** If competitors target audiences the client hasn't considered, flag it in the report.

## When Discovery Fails

Don't pad with loosely related tools. Instead:

1. Report what you found and how many rounds you ran
2. Ask: "Who do you actually encounter in deals or see mentioned by your target customers?"
3. The user's answer overrides all search results
