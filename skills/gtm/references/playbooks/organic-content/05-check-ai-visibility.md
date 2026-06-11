# Check AI Visibility

Determine whether the brand appears in AI-generated answers (ChatGPT, Perplexity, Claude, Gemini) for category-relevant queries. GEO = Generative Engine Optimization.

## When to use

Read this when the gtm decision layer routes to `organic-content/ai-visibility`, or when running a Full Brand Audit (always run alongside `04-audit-seo-keywords.md` so the keyword set has both classical-SEO and AI-search signal). Output feeds the AI-visibility section of `seo-geo-audit.md`, which the decision layer reads to recommend `organic_content` with the AI-visibility workflow.

## What You Get

- **Per-query mention status** — is the brand mentioned in AI answers for each query?
- **Top sources cited** — which URLs do AI models cite instead?
- **Visibility level** — high (4+ mentions), medium (2-3), low (0-1)
- **Biggest gap** — the highest-volume query where the brand is NOT mentioned
- **Who wins instead** — which competitors show up in AI answers

## Step 1: Build Query Set (minimum 8 queries)

Don't just use the seed keywords. Build queries from **at least 4 of these angles:**

1. **Category "best of"** — "best {category}", "top {category} tools 2026"
2. **Problem-solution** — "how to {solve the ICP's problem}", "what tool can {do the job}"
3. **Comparison** — "{client} vs {competitor}", "is {client} worth it"
4. **Recommendation** — "what {category} should I use", "recommend a {category}"
5. **ICP-specific** — "best {category} for {ICP}", "{category} for agencies"
6. **Use-case** — "tool for automating {specific task}", "how to {specific workflow}"

## Step 2: Check AI Search Volume

```
hyperseo_ai_search_volume(keywords=all_queries)
```

Sort by AI search volume. Take the top 8 (or all of them if fewer than 8 have volume).

## Step 3: Track Mentions (parallel)

Run all in parallel:
```
hyperseo_track_mentions(query="{query_1}", brands=[brand_name, competitor_1, competitor_2, competitor_3])
hyperseo_track_mentions(query="{query_2}", brands=[brand_name, competitor_1, competitor_2, competitor_3])
...
```

Include the top 3 direct competitors from competitor research (03) in the `brands` array. This shows not just "are we mentioned" but "who gets mentioned instead."

## Step 4: AI Overview

```
hyperseo_ai_overview(keyword="{top_category_keyword}")
```

Read what the AI overview says about the category. This is the narrative the AI models are telling searchers.

## Quality Gates

- **Minimum 8 queries checked.** Fewer means you're only testing one angle.
- **Include competitor names in brand tracking.** "Are we mentioned?" is half the story. "Who IS mentioned?" is the other half.
- **At least one "best of" query and one problem-solution query.** These are the two highest-value AI answer types.

## Cross-Pollination

- **← From keyword research (04):** Use the keywords with highest AI search volume as inputs
- **← From competitor research (03):** Include competitor names in brand tracking
- **→ To content strategy:** Queries where the brand is NOT mentioned but competitors ARE = content gaps to fill
- **→ To positioning:** What the AI overview says about the category shapes how the brand should position

## Failure Modes

- **All queries return "not mentioned":** Normal for new brands. Map who IS mentioned — those are the AI visibility leaders to study and outperform with content.
- **AI search volume is zero for everything:** Category doesn't have AI search traffic yet. Report honestly. This is an opportunity to be first.
- **Track mentions returns partial model failures:** The tool queries multiple LLMs (GPT, Claude, Perplexity). Individual models may return errors (e.g., Perplexity 404). Report results from the models that succeeded and note which ones failed. Two out of three models responding is still useful data.
- **`hyperseo_ai_overview` returns a service error:** This endpoint can be intermittent. If it fails, note it and move on — the `track_mentions` data is more valuable anyway.
- **Track mentions returns errors for all models:** Tool may have rate limits or connectivity issues. Reduce to top 5 queries and retry with a short delay between calls.
