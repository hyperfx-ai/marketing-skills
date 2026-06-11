# Audit SEO Keywords

Build a keyword set of **at least 50 keywords** from multiple sources. SEO tools are the baseline — not the ceiling. The best keywords come from how real people talk about the problem right now.

## When to use

Read this when the gtm decision layer routes to `organic-content/seo-blog`, `organic-content/ai-visibility`, or `paid-ads/google`. Output (the keyword set) feeds `08-research-serp.md`, `11-write-blog-post.md`, and `the `google-ads` skill`. Skip if the user hands you a confirmed keyword list — accept it as the current truth and move on.

## Round 1: SEO Tool Baseline (parallel)

Start with 10-15 seeds from the confirmed brief:
- Category terms
- ICP job-to-be-done phrases
- Top competitor names + "alternative"
- Problem language from the confirmed brief

```
hyperseo_keyword_ideas(keywords=seeds, limit=30)
hyperseo_ai_search_volume(keywords=seeds)
hyperseo_domain_keywords(domain=DOMAIN, limit=20)
hyperseo_backlinks_history(target=DOMAIN)
hyperseo_domain_overview(domain=DOMAIN)
```

**Warning:** `hyperseo_keyword_ideas` often returns irrelevant results for niche or emerging categories (e.g., seeds about "ai marketing agent" returning "digital marketing agency nj"). Treat its output as a starting pool to filter, not a reliable list. The real value in Round 1 comes from `hyperseo_ai_search_volume` (shows which seeds have AI chatbot traffic) and `hyperseo_domain_keywords` (what the client already ranks for). For new/small domains, `hyperseo_domain_keywords` may return very few results — that's expected.

## Round 2: Competitor Keyword Mining (parallel)

Use the top 3-5 direct competitor domains from competitor research (03). **Only mine competitors with significant organic presence** — check the competitor research output for keyword counts. Domains with fewer than ~100 organic keywords will return nothing useful.

```
hyperseo_domain_keywords(domain="{established_competitor_1}", limit=20)
hyperseo_domain_keywords(domain="{established_competitor_2}", limit=20)
hyperseo_domain_keywords(domain="{established_competitor_3}", limit=20)
```

If all direct competitors are new/small domains (common in emerging categories), skip this round — the data won't be there. Web search (Round 3) and community mining (Round 4) become your primary sources instead.

Extract keywords competitors rank for that the client doesn't. These are proven — someone is already getting traffic from them.

## Round 3: Current Language from Web Search (6-8 queries)

SEO tools have stale data. Find what people are searching for RIGHT NOW:

```
web_search(queries=[
  "best {category} 2026",
  "how to {ICP job-to-be-done}",
  "{category} comparison",
  "{category} for {ICP role}",
  "new {category} tools",
  "{category} workflow",
  "{ICP problem} solution",
  "{category} site:producthunt.com"
], num_results=5)
```

Read the titles and descriptions of ranking pages. Extract:
- Exact phrases used in titles (these are validated — they rank)
- Category terms you didn't think of
- New product names being mentioned alongside the category
- Long-tail variants of your seeds

## Round 4: Community Language Mining

If Reddit research (07) has been run, go through the thread titles and top comments. Extract:
- The exact words the ICP uses when describing their problem
- Tool names and framework names being discussed
- Emerging jargon ("MCP", "agent skills", "tool calling" — whatever the space calls things now)
- Questions people ask (these become content keyword targets)

If Reddit research hasn't been run yet:
```
web_search(queries=[
  "{category} site:reddit.com",
  "{ICP problem} site:reddit.com",
  "what tools for {ICP job} site:reddit.com"
], num_results=5)
```

Community language matters because people don't search the way SEO tools think they do. Someone doesn't search "marketing operations automation platform" — they search "how do I stop doing this manually" or "best Claude setup for marketing."

## Round 5: Emerging and Adjacent Terms

Search for what's new in the space. These keywords won't show volume in SEO tools yet but they're what the ICP is starting to search:

```
web_search(queries=[
  "{category} site:news.ycombinator.com",
  "{category} launched 2025 OR 2026",
  "ai agents {industry} 2026",
  "{adjacent_category} vs {category}"
], num_results=5)
```

Extract product names, framework names, protocol names, and terminology that didn't appear in Rounds 1-4. These are your `trend` keywords.

## Round 6: Search Intent Classification

Take the top 15 keywords by volume:
```
hyperseo_search_intent(keywords=top_15)
```

## Compile and Tag

Merge all keywords from Rounds 1-5. Deduplicate. You should have **at least 50 unique keywords**. If fewer, you haven't mined enough sources — go back to whichever rounds returned thin results and expand with more queries.

Tag each keyword:

| Tag | Criteria | Action |
|-----|----------|--------|
| `quick_win` | difficulty < 30, volume > 200 | Target immediately with content |
| `big_bet` | difficulty >= 30, volume > 1000 | Long-term SEO investment |
| `trend` | from Rounds 4-5, low/no SEO volume but discussed in communities | Get in early |
| `competitor` | contains competitor name | Create comparison/alternative pages |
| `brand` | contains brand/product terms | Monitor, don't target |
| `supporting` | everything else | Use in content clusters |

Group into clusters by intent:
- **Problem-aware** — searcher knows the pain, not the solution
- **Solution-aware** — searcher knows the category
- **Comparison** — evaluating options
- **Emerging** — new terms, frameworks, protocols with no established volume yet
- **Brand** — product name searches

## Quality Gates

- **Minimum 50 keywords** after deduplication
- **At least 4 clusters** represented
- **At least 10 keywords from community/web sources** (Rounds 3-5) — not just SEO tool output
- **At least 5 competitor-derived keywords** from Round 2
- **At least 5 trend/emerging keywords** from Rounds 4-5

If any gate fails, go back to the thin round and run more queries.

## Cross-Pollination

- **← From competitor research (03):** Competitor domains for mining, competitor names for comparison terms
- **← From Reddit threads (07):** Exact language the ICP uses — these become seeds and trend keywords
- **→ To blog post (11):** Quick-win keywords become blog topic candidates
- **→ To ad copy (09):** High-CPC keywords show what competitors bid on
- **→ To AI visibility (05):** Keywords with AI search volume go into visibility checks
