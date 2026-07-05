# Competitor Analysis

Step-by-step guide for identifying, analyzing, and benchmarking SEO competitors using the HyperSEO tools.

## When to Use

- The user asks "who are my competitors?".
- The user wants to understand why a competitor ranks and they don't.
- The user needs a competitive landscape overview before planning content.
- The user asks to compare two or more domains.

## Workflow

### Step 1: Identify competitors

Don't assume who the competitors are — discover them from data.

1. If you have the user's domain, run `hyperseo_competitor_domains_search` to find competitors based on shared organic keywords. This is the best starting point.
2. Alternatively, if you only have target keywords, run `hyperseo_competitors_search` to find domains that rank for similar terms.
3. The top 5 – 7 results are the real SEO competitors (these may differ from business competitors).

### Step 2: Domain comparison

For each competitor (and the user's own domain).

1. Run `hyperseo_bulk_traffic` with all domains at once to get a quick traffic comparison across all competitors in a single call.
2. Run `hyperseo_domain_overview_get` on each domain for detailed metrics (authority, backlinks, referring domains).
3. Present as a comparison matrix.

**Comparison matrix format:**

```
| Domain | Domain Rank | Organic Keywords | Est. Traffic | Backlinks | Referring Domains |
|--------|------------|-----------------|-------------|-----------|-------------------|
```

### Step 3: Keyword gap analysis

Find what competitors rank for that the user doesn't.

1. Run `hyperseo_domain_intersections_search` between the user's domain and each top competitor to find keywords where both appear in SERPs — this reveals direct keyword battlegrounds.
2. Run `hyperseo_domain_keywords_get` on the top 2 – 3 competitors (limit 50 each) to find keywords the user is missing entirely.
3. Compare: which high-value keywords do competitors have that the user is missing?
4. Cross-check the gaps with `hyperseo_keyword_difficulty` to find achievable targets.

### Step 4: Backlink comparison

Understand the link-building landscape.

1. Run `hyperseo_backlinks_history_get` on each competitor.
2. Compare link velocity: who is gaining or losing backlinks faster?
3. A competitor with strong backlink growth will be harder to overtake without a similar link strategy.

### Step 5: SERP position analysis

For the user's most important keywords.

1. Run `hyperseo_serp_results_get` to see exactly who holds the top positions.
2. Note the content types that rank (articles, product pages, videos, Reddit threads).
3. Identify patterns: do certain domains dominate across multiple keywords?

## Interpreting Results

**Domain rank**

- 0 – 20: very low authority, new or small site.
- 20 – 40: growing authority, can compete for low-difficulty keywords.
- 40 – 60: established site, can compete for medium-difficulty keywords.
- 60+: high authority, competitive for most keywords.

**Keyword gap opportunities**

Focus on gaps where:

- The competitor ranks in positions 5 – 20 (beatable).
- The keyword difficulty is under 50.
- Search volume is above 500.
- Your domain has some topical relevance.

**Backlink velocity**

If a competitor gains 100+ new referring domains per month and the user gains 5, content alone won't close the gap. Recommend link-building or pivot to less competitive terms.

## Output Format

Deliver a competitor analysis report with:

1. **Competitor overview table** — side-by-side domain metrics.
2. **Keyword gap list** — keywords competitors rank for that the user doesn't, sorted by opportunity (volume / difficulty).
3. **Backlink comparison** — link growth trends for each domain.
4. **SERP dominance** — which competitors appear most across target keywords.
5. **Actionable recommendations** — specific keywords to target, content to create, and where the user has a realistic chance of competing.

## Common Mistakes to Avoid

- **Comparing against impossible competitors**: a new blog should not benchmark against Wikipedia or Reddit. Focus on competitors of similar scale.
- **Ignoring content format**: a competitor may rank with video while you plan a blog post. Check the SERP format.
- **Treating all keyword gaps equally**: a gap is only valuable if the keyword has volume, is achievable at your authority level, and matches your business.
- **Skipping backlink context**: a domain with 10× more backlinks isn't beatable on the same keywords without a link strategy.
