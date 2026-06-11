# SERP Research

Research what currently ranks for a keyword and where the content gaps are. Run this before writing any SEO content.

## When to use

Read this whenever the agent is about to write an SEO blog post (`11-write-blog-post.md`). Always runs after a target keyword has been picked from `04-audit-seo-keywords.md`. Output is a structured SERP brief (top URLs, content gaps, ranking patterns) that becomes the input to the blog writing step.

## Workflow

1. `hyperseo_serp_results(keyword=..., depth=10)` — get top 10 organic results
2. `hyperseo_ai_overview(keyword=...)` — see how AI summarizes this topic
3. `firecrawl_batch_scrape(urls=top_8, formats=["markdown"], only_main_content=True)` — read what ranks

Scraping only 3 results gives you a keyhole view. You need 8-10 to see the actual patterns — what angles are saturated, what's missing, who dominates, and where the real gap is.

## Gap Analysis

From the scraped content, identify:

- **What they all cover** — the commodity content every post includes. You need to cover this too, but it's not your angle.
- **What they all repeat** — the lazy sections that get copy-pasted across listicles. Don't add to the pile.
- **What's missing** — the specific question, use case, or depth that nobody addresses. This is your angle.
- **What the AI overview gets wrong or oversimplifies** — opportunity for nuance that gets cited.
- **Content format patterns** — are they all listicles? All how-tos? All comparisons? A different format is itself a gap.
- **Freshness** — when were the top results published? Stale content (2024 or older) is easy to outrank with current information.

## Output

A writing brief with:
- Target keyword + related terms
- Top 8-10 URLs with publish dates and their angles (one line each)
- AI overview summary and its gaps
- Saturated angles (what NOT to write)
- Missing angles and unanswered questions (at least 3)
- Recommended article angle (the gap to exploit)
- Suggested word count based on competitor lengths
