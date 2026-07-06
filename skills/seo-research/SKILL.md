---
name: seo-research
description: Data-driven SEO research and analysis through the Hyper MCP — keyword research, competitor analysis, content planning, AI search visibility (ChatGPT, Claude, Perplexity, Google AI Overviews), backlink trends, search intent classification, page speed / Core Web Vitals, and full site audits. Use when the user asks for an SEO audit, keyword research, content strategy, competitor benchmarks, brand visibility in AI search, ranking history, or any organic search analysis.
icon: hyperseo
short_description: Keyword research, SERP and AI-visibility analysis, competitor benchmarking, and site audits.
---

# SEO Research

Data-driven SEO research and analysis. Every recommendation must be backed by real data from the HyperSEO tools exposed by the Hyper MCP. Never guess metrics, never assume rankings, never recommend without evidence.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Google Ads campaign creation | `google-ads` |
| Meta (Facebook / Instagram) ads | `meta-ads` |
| Competitor *ad* research from the Meta Ads Library | `meta-ads-library` |
| Pinterest Ads campaign | `pinterest-ads` |
| Organic Instagram / TikTok / LinkedIn publishing | `instagram`, `tiktok`, `linkedin` |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **HyperSEO toolkit enabled** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps) — provides the `hyperseo_*` tool surface that wraps DataForSEO and AI search query data.

If `hyperseo_search_volume_get` is not in the tool list, stop and tell the user to enable the Hyper MCP and turn on the HyperSEO toolkit.

## Tool surface

| Tool group | Tools |
| --- | --- |
| Keyword research | `hyperseo_search_volume_get`, `hyperseo_keyword_difficulty`, `hyperseo_keyword_ideas`, `hyperseo_site_keywords_search`, `hyperseo_intents_search` |
| SERP & AI Overviews | `hyperseo_serp_results_get`, `hyperseo_ai_overviews_get` |
| Competitor analysis | `hyperseo_competitors_search`, `hyperseo_competitor_domains_search`, `hyperseo_domain_intersections_search`, `hyperseo_bulk_traffic` |
| Domain & rankings | `hyperseo_domain_overview_get`, `hyperseo_domain_keywords_get`, `hyperseo_rank_history_get` |
| Backlinks | `hyperseo_backlinks_history_get` |
| AI search visibility | `hyperseo_ai_search_volume_get`, `hyperseo_mentions_track` |
| Technical health | `hyperseo_pagespeed` |

## Initial Assessment

Before running any tools, understand what the user actually needs:

1. **What is the goal?** Are they researching keywords, auditing a site, planning content, analyzing competitors, or checking AI visibility?
2. **What is the domain / business?** Get the actual domain. Don't infer it.
3. **What is the target market?** Default to US (location code `2840`) unless told otherwise.
4. **What is the current state?** Are they starting from scratch or optimizing existing content?

Based on the answers, read the appropriate reference file:

| User need | Reference |
| --- | --- |
| "Find keywords for…" / "What should I target?" | [`references/keyword-research.md`](./references/keyword-research.md) |
| "Who are my competitors?" / "Analyze [domain]" | [`references/competitor-analysis.md`](./references/competitor-analysis.md) |
| "What should I write about?" / "Content plan" | [`references/content-seo-planning.md`](./references/content-seo-planning.md) |
| "Am I visible in AI search?" / "Track my brand in ChatGPT" | [`references/ai-search-optimization.md`](./references/ai-search-optimization.md) |
| "Audit my site" / "How is my domain doing?" | [`references/site-audit.md`](./references/site-audit.md) |

When the task spans multiple areas (e.g., "help me with SEO for my new site"), start with a site audit, then move to keyword research, then content planning.

## Core SEO Principles

Apply these throughout all analysis.

**Search intent comes first.** Every keyword has an intent. Use `hyperseo_intents_search` to classify at scale, then match content format to intent:

- Informational ("what is X") → guides, explainers.
- Commercial ("best X", "X vs Y") → comparison pages, reviews.
- Transactional ("buy X", "X pricing") → product / landing pages.
- Navigational ("X login") → not targetable by others.

**E-E-A-T matters.** Experience, Expertise, Authoritativeness, Trustworthiness. Google evaluates content quality. Recommend content strategies that demonstrate genuine expertise, not keyword-stuffed filler.

**Topic authority over individual keywords.** Ranking for one keyword in isolation is hard. Recommend topic clusters: a pillar page supported by related content that builds topical authority.

**AI search is a separate channel.** Traditional Google search volume and AI-chatbot query volume are different metrics measuring different behavior. Always check both when relevant. A keyword with low Google volume may have high AI query volume, and vice versa.

**Prioritize by ROI.** Low difficulty + decent volume = do first. High difficulty + high volume = long-term investment. Low volume + high difficulty = skip unless strategically important.

## Tool Quick Reference

| Task | Tool | Key output |
| --- | --- | --- |
| Check search volume and CPC | `hyperseo_search_volume_get` | Monthly volume, CPC, competition. |
| Assess ranking difficulty | `hyperseo_keyword_difficulty` | Difficulty score 0–100. |
| Generate keyword ideas | `hyperseo_keyword_ideas` | Related keywords with metrics. |
| Find keywords for a site | `hyperseo_site_keywords_search` | Keywords a domain could target. |
| See who ranks on Google | `hyperseo_serp_results_get` | Top positions, URLs, domains. |
| Check Google AI Overview | `hyperseo_ai_overviews_get` | AI-generated summary and cited sources. |
| See what a domain ranks for | `hyperseo_domain_keywords_get` | Current rankings and traffic. |
| Find competing domains (by keywords) | `hyperseo_competitors_search` | Domains ranking for similar keywords. |
| Find competing domains (by domain) | `hyperseo_competitor_domains_search` | Competitors based on shared organic keywords. |
| Get domain health metrics | `hyperseo_domain_overview_get` | Authority, traffic, backlinks. |
| Track backlink trends | `hyperseo_backlinks_history_get` | New / lost backlinks over time. |
| Check AI chatbot query volume | `hyperseo_ai_search_volume_get` | Monthly queries to ChatGPT, Claude, etc. |
| Track brand mentions in LLMs | `hyperseo_mentions_track` | Brand citations across AI models. |
| Compare traffic across domains | `hyperseo_bulk_traffic` | Organic / paid ETV and keyword counts per domain. |
| Track ranking history over time | `hyperseo_rank_history_get` | Monthly organic traffic and keyword trends. |
| Classify keyword search intent | `hyperseo_intents_search` | Intent type with confidence scores. |
| Find keyword overlaps between domains | `hyperseo_domain_intersections_search` | Shared SERP keywords with positions. |
| Check page speed / Core Web Vitals | `hyperseo_pagespeed` | Performance score, FCP, LCP, TBT, CLS. |

### Location codes

Default is US (`2840`). Common alternatives: UK `2826`, Canada `2124`, Australia `2036`, Germany `2276`.

## Output Standards

**Always present keyword data as tables:**

```
| Keyword | Volume | Difficulty | CPC | Priority |
|---------|--------|-----------|-----|----------|
```

**Always include the raw numbers** alongside interpretation. Don't say "high volume" without showing the number.

**Sort recommendations by priority.** Quick wins first, long-term bets last.

**When comparing domains**, use side-by-side tables showing organic keywords, traffic, backlinks, and domain rank.

**For content plans**, include: target keyword, search volume, difficulty, recommended content format, and priority tier.

## Critical Rules

1. **Never guess metrics.** If you don't have data, run the tool first.
2. **Research before recommending.** Don't suggest keywords without checking volume and difficulty.
3. **Ask for the domain.** Don't infer URLs from business names.
4. **Check both channels.** When relevant, compare Google search volume with AI search volume.
5. **Be honest about difficulty.** If a keyword is realistically unwinnable for the user's domain authority, say so and suggest alternatives.
6. **Think in clusters, not isolated keywords.** Group related keywords into topic clusters.
7. **Validate against SERPs.** Before recommending a content format, check what actually ranks with `hyperseo_serp_results_get`.
