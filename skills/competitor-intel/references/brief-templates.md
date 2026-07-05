# Brief Templates

Four brief shapes, four jobs. Pick the shape that matches the job decided in Phase 1 of [`SKILL.md`](../SKILL.md), then fill it from the data pulled in Phase 3 with diffs from Phase 4. Source playbook for *what* to pull lives in [`source-by-source.md`](./source-by-source.md).

Output rules apply to every brief:

- Every claim has a **source URL + scrape timestamp**. Unsourced claims get cut.
- Use neutral language. The reader interprets; the brief reports.
- Mark interpretation explicitly when present: prefix with **Observation:** or **Interpretation:**.
- Lead with the 3 things that matter most. Bury the rest below.
- Keep aggregates over anecdotes — "averaged 8K likes/post over 30d" beats "one post got 12K."

## Template 1 — Battle card (sales)

**Goal:** Equip a salesperson to handle a competitive deal in real time. 1 page per competitor.

**Length:** Strict 1-page-per-competitor cap. If it doesn't fit, the salesperson won't read it.

```markdown
# Battle Card — [Competitor Name]
**As of:** YYYY-MM-DD
**Owner:** [internal owner of this card]

## At a glance
- **Category position:** [1-line summary, e.g. "Mid-market SaaS, US-focused, $15M ARR estimate"]
- **Last meaningful change:** [e.g. "Raised Series B Apr 2026, expanded to EU"]
- **Where they win:** [1-line]
- **Where we win:** [1-line]

## Their pitch (verbatim from their site)
- **Headline:** "[homepage h1]" — [pricing-page or homepage URL]
- **Top 3 value props:** [from features page or homepage subheads]
- **Pricing entry point:** $[X]/mo (Pro: $[Y]/mo) — [pricing URL]
- **Free trial / freemium:** [Yes — N days, with constraints / No]

## What they say about us (if anything)
- [Direct quotes from their comparison pages, blog posts, or sales calls if you have them]
- "" if none found — say so explicitly

## Common objection lines + counter
| They'll say | You say |
| --- | --- |
| "But [competitor] is cheaper" | "[concrete answer with a number/feature]" |
| "[competitor] integrates with X natively" | "[concrete answer]" |
| "[competitor] has been around longer" | "[concrete answer]" |

## Win patterns (if you have win-loss data, otherwise mark TODO)
- We win when: [scenario] — [evidence]
- We lose when: [scenario] — [evidence]

## Recent moves (90 days)
- [date] — [what changed, source URL]
- [date] — [what changed, source URL]
- [date] — [what changed, source URL]

## Don't say
- [Anything that's a lie]
- [Anything that's punching down]
- [Anything that triggers their lawyers]
```

**Worked example (excerpt):**

```markdown
# Battle Card — Convertly
**As of:** 2026-04-30

## At a glance
- **Category position:** Mid-market marketing automation, US/EU, ~$22M ARR (LinkedIn headcount × ARR-per-head benchmark)
- **Last meaningful change:** Pricing raised on Pro tier $79 → $99 (apr 2026 — pricing page diff vs Mar 2026 archive)
- **Where they win:** Native HubSpot sync, mature email editor
- **Where we win:** AI-driven segmentation, $30/mo cheaper at the entry tier

## Common objection lines + counter
| They'll say | You say |
| --- | --- |
| "Convertly is the established player" | "Established with a UI from 2019 — show them our editor side-by-side" |
| "Our HubSpot is already wired up" | "We do HubSpot natively too — here's the 5-min migration video" |
```

## Template 2 — Weekly digest

**Goal:** One scrollable summary the marketing/exec team reads every Monday. 1 page total, all competitors.

**Length:** ~1 page (<300 words). Read time under 90 seconds.

```markdown
# Competitor Digest — Week of [Mon date]

## Top 3 things that matter
1. **[Competitor A] [thing they did]** — [why it matters in <20 words]. [source URL]
2. **[Competitor B] [thing they did]** — [why it matters]. [source URL]
3. **[Competitor C] [thing they did]** — [why it matters]. [source URL]

## Per-competitor changes (this week vs last week)

### Competitor A
- Site: [diff or "no change"]
- Pricing: [diff or "no change"]
- Social: [follower/post deltas, biggest post]
- Search: [rank changes, new content surfacing]
- Mentions: [reddit/twitter activity delta]

### Competitor B
- Site: [...]
- Pricing: [...]
- Social: [...]
- Search: [...]
- Mentions: [...]

### Competitor C
[same shape]

## Watch list (next week)
- [Competitor X is rumored to be launching Y by [date] — verify]
- [Competitor Y's pricing-page A/B test is still running — capture before it ends]
```

**Critical:** sections with no change get an explicit "no change this week" line — don't omit them, or readers can't tell whether you forgot or there's nothing.

## Template 3 — Comparison-page input

**Goal:** Feed the marketing team objective, comparable data they can render into a comparison page (yourbrand.com/vs/competitor) without lying.

**Length:** As long as needed for the matrix to be complete. Optimized for accuracy + comparability, not brevity.

```markdown
# Comparison Data — [Competitor Name] vs Us
**Pulled:** YYYY-MM-DD
**Sources:** [list of URLs scraped]

## Pricing matrix

| Plan | Price (USD/mo, paid annually) | Price (USD/mo, paid monthly) | Seats | [Key limit 1] | [Key limit 2] | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Their Free | $0 | $0 | 1 | [N] | [N] | [URL] |
| Their Pro | $[X] | $[X+] | [N] | [N] | [N] | [URL] |
| Their Business | $[X] | $[X+] | [N] | [N] | [N] | [URL] |
| Our Free | $0 | $0 | [N] | [N] | [N] | yourbrand.com/pricing |
| Our Pro | $[X] | $[X+] | [N] | [N] | [N] | yourbrand.com/pricing |
| Our Business | $[X] | $[X+] | [N] | [N] | [N] | yourbrand.com/pricing |

## Feature matrix

| Feature | Them | Us | Notes |
| --- | --- | --- | --- |
| [Feature 1] | ✓ | ✓ | Both have it |
| [Feature 2] | ✓ | — | Their differentiation |
| [Feature 3] | — | ✓ | Our differentiation |
| [Feature 4] | Beta | ✓ GA | Note maturity |
| [Feature 5] | "Coming soon" (no date) | ✓ | Note vaporware risk |

## Integration coverage

- **Their integrations:** [list, with link to their integrations page]
- **Our integrations:** [list]
- **Overlap:** [N]
- **Their unique:** [N]
- **Our unique:** [N]

## Trial / freemium policy

| | Them | Us |
| --- | --- | --- |
| Free plan? | [Yes / No] | [Yes / No] |
| Free trial days | [N] | [N] |
| Credit card required? | [Yes / No] | [Yes / No] |
| Auto-converts to paid? | [Yes / No] | [Yes / No] |

## Verbatim positioning (their words, captured from site)

| Page | Quoted copy | URL |
| --- | --- | --- |
| Homepage hero | "[exact h1]" | [URL] |
| Pro tier subhead | "[exact text]" | [URL] |
| About page | "[exact mission text]" | [URL] |

## Disclosure
All data above pulled on [date]. Pricing and features can change — re-pull before publishing the comparison page if more than 7 days have passed.
```

**Why so structured:** comparison pages are legal-adjacent. The matrix forces apples-to-apples comparisons that are defensible. The "verbatim positioning" section is what lets you quote them on the comparison page without inventing.

## Template 4 — Board-prep update

**Goal:** Quarterly or board-meeting-prep slide content. Executives, not operators. Aggregates, not anecdotes.

**Length:** ~1 page across all competitors, with one chart per metric.

```markdown
# Competitive Position — [QN YYYY]

## Headline
[1 sentence the board chair could repeat from memory.] e.g. "We've closed the rank gap with [Top Competitor] from -47 to -12 over the last 90 days while sustaining 2x organic traffic growth."

## Share of voice (where this matters)
| Channel | Us | [Comp A] | [Comp B] | [Comp C] | Source / metric |
| --- | --- | --- | --- | --- | --- |
| Organic search (est. monthly traffic) | [N] | [N] | [N] | [N] | hyperseo_domain_overview_get |
| Backlinks (90d delta) | +[N] | +[N] | +[N] | +[N] | hyperseo_backlinks_history_get |
| AI Overview citations (count over [keywords]) | [N] | [N] | [N] | [N] | hyperseo_ai_overviews_get |
| Instagram followers (current / 90d delta) | [N] / +[N] | [N] / +[N] | [N] / +[N] | [N] / +[N] | scrape_instagram |
| TikTok median views/post (90d) | [N] | [N] | [N] | [N] | scrape_tiktok_videos |

## Rank position on the 10 keywords that matter most
| Keyword | Us | [Comp A] | [Comp B] | [Comp C] | 90d delta (us) |
| --- | --- | --- | --- | --- | --- |
| [keyword 1] | [N] | [N] | [N] | [N] | +/- [N] |
| [keyword 2] | [N] | [N] | [N] | [N] | +/- [N] |
| ... | | | | | |

## What changed this quarter
- **Our wins:** [3 bullets, sourced]
- **Their wins:** [3 bullets, sourced]
- **Misses (ours):** [2 bullets, sourced]

## Strategic read
[1 paragraph max — interpret the data above. What does the trend imply for next quarter's focus.]

## Risks to watch
- [Competitor X is doing [Y]. If it lands, it pressures our [Z].]
- [Category headwind: e.g., "Google AI Overview adoption shifts demand away from organic clicks."]
```

**Critical for board format:** every data point has a source attribution column or footnote. Boards ask "where does this number come from?" — pre-empt it.

## Worked example — diff section of a weekly digest

The hardest section of any brief is the *diff*. What does a useful diff look like?

**Bad (snapshot, not diff):**

> Convertly's homepage says "Marketing automation that grows with you."

**Good (diff with context):**

> **Convertly homepage diff vs last week:**  
> H1 changed from "The marketing automation platform" → "Marketing automation that grows with you."  
> CTA button changed from "Start free trial" → "See pricing."  
> **Interpretation:** moving from acquisition-led ("trial") to consideration-led ("pricing") messaging. Consistent with their pricing-page raise — likely shifting upmarket.  
> *Source: convertly.com/, scraped 2026-04-29 vs 2026-04-22 archive.*

The interpretation is short, marked, and non-essential — a reader can ignore it and still get the observation. That's the right shape.
