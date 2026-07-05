# Content SEO Planning

Step-by-step guide for building a data-informed content strategy using the HyperSEO tools. Focus on creating content that ranks by targeting validated keywords with the right content format.

## When to Use

- The user asks "what content should I create?".
- The user wants a content calendar with keyword targets.
- The user needs to plan blog posts, landing pages, or pillar content.
- The user wants to build topical authority in a specific area.

## Workflow

### Step 1: Define the topic territory

Understand what the user's content should cover.

1. Ask for their core topics or business areas (2 – 5 seed themes).
2. Run `hyperseo_keyword_ideas` for each seed theme (limit 30 – 50).
3. This gives a broad view of the keyword landscape around their topics.

### Step 2: Validate demand and intent

Not every idea has search demand. Validate.

1. Run `hyperseo_search_volume_get` on the most relevant keyword candidates.
2. Run `hyperseo_keyword_difficulty` on the same set.
3. Run `hyperseo_intents_search` to classify intent at scale — this determines the right content format for each keyword.
4. Also run `hyperseo_ai_search_volume_get` to check AI channel demand.
5. Discard keywords with no meaningful volume (< 100 / month) unless strategically important.

### Step 3: Analyze the SERP

For each high-priority keyword, understand what Google rewards.

1. Run `hyperseo_serp_results_get` for the top 10 – 15 keyword targets.
2. Note the content format that ranks:
   - Long-form guides (2000+ words)?
   - Listicles ("10 best…")?
   - Product pages?
   - Video results?
   - Reddit / forum threads?
3. Match your content format recommendation to what actually wins.

### Step 4: Check AI Overviews

For informational keywords, check if Google generates an AI Overview.

1. Run `hyperseo_ai_overviews_get` for key terms.
2. Review which sources get cited in the AI overview.
3. Content that earns AI citations gets visibility even above traditional position 1.

### Step 5: Build topic clusters

Organize keywords into topic clusters, not flat lists.

**Pillar page**: broad topic with high volume and higher difficulty.

- Targets the main keyword.
- Comprehensive, long-form content.
- Links to all supporting content.

**Supporting pages**: specific subtopics with lower difficulty.

- Target long-tail variations.
- Each links back to the pillar page.
- Builds topical authority that helps the pillar rank.

**Example cluster:**

```
Pillar: "email marketing guide" (vol: 8,100, diff: 65)
  ├── "email marketing best practices" (vol: 1,900, diff: 35)
  ├── "email subject line tips"        (vol: 2,400, diff: 28)
  ├── "email marketing automation"     (vol: 3,600, diff: 42)
  └── "email list building strategies" (vol: 1,200, diff: 30)
```

Start by publishing the supporting pages. Once 3 – 5 are live and interlinked, publish the pillar.

### Step 6: Prioritize and schedule

Create a content calendar ordered by priority.

**Priority factors:**

1. Quick wins first (difficulty < 30, volume > 500).
2. Supporting content before pillar content.
3. Commercial-intent pages before purely informational ones (if conversions matter).
4. Topics where you already have some authority or existing content.

## Content Brief Template

For each piece of content, provide:

```
Target Keyword: [primary keyword]
Secondary Keywords: [2-3 related terms to include naturally]
Search Volume: [monthly]
Difficulty: [0-100]
Search Intent: [from hyperseo_intents_search: informational / commercial / transactional / navigational]
Recommended Format: [guide / listicle / comparison / landing page]
SERP Insight: [what currently ranks - based on hyperseo_serp_results_get]
Cluster Role: [pillar / supporting]
Links To: [pillar page or related supporting pages]
```

## Output Format

Deliver the content plan as:

1. **Topic cluster map** — visual grouping of pillar + supporting content.
2. **Content calendar table:**

```
| Priority | Keyword | Volume | Difficulty | Format | Cluster Role | Notes |
|----------|---------|--------|-----------|--------|-------------|-------|
```

3. **Content briefs** — one per piece, using the template above.
4. **Quick wins highlighted** — top 3 – 5 pieces to publish first.

## Common Mistakes to Avoid

- **Writing without keyword data**: every content piece should target a validated keyword with real search demand.
- **Starting with the hardest keyword**: build authority with easier supporting content first, then tackle the pillar.
- **Ignoring SERP format**: if the SERP rewards listicles, don't write a 3,000-word essay.
- **Creating orphan content**: every page must link to and from related content. Isolated pages struggle to rank.
- **Focusing only on Google**: check AI search volume too. A keyword with moderate Google volume but high AI volume may be worth targeting for emerging visibility.
