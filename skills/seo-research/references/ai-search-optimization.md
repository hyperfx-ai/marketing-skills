# AI Search Optimization

Guide for understanding and optimizing visibility in AI search — Google AI Overviews, ChatGPT, Claude, Perplexity, and other AI assistants. This is sometimes called GEO (Generative Engine Optimization) or AEO (AI Engine Optimization).

## When to Use

- The user asks about AI search visibility or brand mentions in ChatGPT / Perplexity.
- The user wants to know if AI assistants recommend their product.
- The user wants to understand Google AI Overviews for their target keywords.
- The user asks about GEO or AEO strategy.

## Why AI Search Matters

AI assistants are becoming a significant discovery channel. Users ask ChatGPT, Perplexity, and Claude for product recommendations, how-to answers, and comparisons. Being mentioned (or missing) from these responses directly impacts brand visibility.

Key differences from traditional SEO:

- **No click-through**: AI responses answer directly. The goal is being cited, not ranking a blue link.
- **Source credibility matters**: AI models cite authoritative, well-structured content.
- **Different demand patterns**: some queries have high AI volume but low Google volume, and vice versa.
- **Multiple models, different results**: ChatGPT, Claude, and Perplexity may cite completely different sources for the same query.

## Workflow

### Step 1: Measure current AI visibility

Before optimizing, establish a baseline.

1. Run `hyperseo_mentions_track` with the user's brand name and 2 – 3 key competitor brands, using a query their customers would ask.
   - Example: `query="best project management tools"`, `brands=["Asana", "Monday.com", "ClickUp"]`.
2. This queries multiple LLMs (GPT, Claude, Perplexity) with web search enabled and checks which brands appear in responses.
3. Note: which models mention the brand, what context they provide, and which sources they cite.
4. **Note:** Perplexity results may intermittently return a routing error. If so, rely on the GPT and Claude results — brand mention data from two models is still actionable. Do not retry in a loop.

### Step 2: Check AI search demand

Understand how much query volume exists in AI channels.

1. Run `hyperseo_ai_search_volume_get` for the user's target keywords.
2. Compare with `hyperseo_search_volume_get` for the same keywords.
3. Look for keywords where AI volume is growing fast — these represent emerging opportunities.

**Interpreting AI volume:**

- AI search volume measures monthly queries to ChatGPT, Claude, Perplexity, and similar tools.
- Growing AI volume with stable Google volume suggests users are shifting to AI for that query type.
- Keywords with high AI volume and low Google difficulty are prime targets.

### Step 3: Analyze Google AI Overviews

Google's AI Overviews appear above traditional search results for many queries.

1. Run `hyperseo_ai_overviews_get` for the user's most important keywords.
2. Review: which sources does Google AI cite?
3. Note the domains and content types that get cited.
4. This reveals what kind of content earns AI citations.

### Step 4: Competitive AI visibility

Compare brand visibility across AI models.

1. Run `hyperseo_mentions_track` for multiple relevant queries with the user's brand and top competitors.
2. Build a visibility matrix: which brands are mentioned by which models for which queries.
3. Identify gaps: queries where competitors are mentioned but the user is not.

## Strategies for Earning AI Citations

Based on what sources AI models tend to cite:

**Structured, authoritative content**

- Clear headings that match question patterns.
- Definitive statements and data points (not vague qualifiers).
- Lists, comparisons, and structured data that AI can extract.

**Be the primary source**

- Original research, benchmarks, and proprietary data get cited more than aggregated content.
- First-party case studies and results are preferred over generic advice.

**Answer questions directly**

- AI models look for content that directly answers the query in the first 1 – 2 paragraphs.
- Use the question as a heading, then answer immediately.

**Build domain authority**

- AI models weight established, authoritative domains.
- Backlink profile and domain rank influence citation likelihood.
- This connects back to traditional SEO fundamentals.

## Output Format

**AI visibility report:**

1. **Brand mention status** — table showing which AI models mention the brand for key queries.
2. **AI vs traditional volume** — side-by-side comparison for target keywords.
3. **Google AI Overview sources** — which domains get cited for target keywords.
4. **Competitor comparison** — who has better AI visibility and why.
5. **Recommendations** — specific content improvements to earn AI citations.

```
| Query | GPT Mentions Brand? | Claude Mentions? | Perplexity Mentions? | Competitor Mentioned? |
|-------|---------------------|-----------------|---------------------|----------------------|
```

## Common Mistakes to Avoid

- **Treating AI search like Google SEO**: keyword stuffing and backlink tactics don't directly influence AI citations. Content quality and structure matter more.
- **Checking only one model**: different AI models cite different sources. Always check multiple.
- **Ignoring the gap**: if competitors are consistently mentioned and you're not, the content or authority gap needs addressing before any optimization.
- **Expecting quick changes**: AI model knowledge updates on different schedules. Improvements in content may take weeks to reflect in AI responses.
