# On-Page and Technical

Optimize any page (blog post, landing page, product page) for Google and AI search, ship the right structured data, make sure machines can actually read it, and prove the work moved the needle.

---

## 1. On-page checklist

**Title tag**
- Primary keyword near the front, in the user's query language.
- Under ~60 characters so it does not truncate.
- Earns the click: include a number or a concrete benefit where it fits. Google rewrites titles it finds weak, so make yours the obvious choice.

**Meta description**
- Not a ranking factor, but it drives click-through. State the benefit; do not just describe the page.
- ~150 to 160 characters; treat exact counts as soft. Include the primary keyword once, naturally.

**Headings**
- One H1, matching the page topic. Logical H2/H3 nesting; do not skip levels.
- Phrase H2s and H3s as the questions people ask.

**Internal linking and topic clusters**
- Link by usefulness, with descriptive anchor text (never "click here").
- Build pillar-and-cluster structures: a broad pillar page links to specific supporting pages, each linking back up and across. The strongest on-page authority signal you control.
- No orphan pages. Aim for roughly 5 to 10 contextual internal links per 1,000 words; anchor-text variety matters more than an exact count.

**Images**
- Descriptive alt text (~80 to 140 chars) that says what the image shows and why it matters.
- Compress; serve modern formats (WebP/AVIF).

**URLs**
- Short (under ~60 chars), lowercase, hyphen-separated, keyword-bearing, shallow (2 to 3 levels).
- No dates in the slug. Do not rewrite existing URLs just to optimize them.

**Freshness**
- Show a real, visible "Last updated" date and keep `dateModified` accurate.
- Freshness is a real lever on fast-moving topics, minor on evergreen ones. Update substantively; do not date-bump cosmetically.

**The answer is on the page**
- The thing you want cited must be visible text, not buried in a click-to-open accordion, not an image of text, not injected only after interaction.

---

## 2. Structured data (JSON-LD)

Schema does not earn AI citations by itself (a 2026 controlled test found no measurable non-Google lift), but it is cheap, helps Google understand and feature the page, and builds the clean entity data AI systems lean on. Ship it for those reasons; do not over-promise AI impact.

**Rules**
- **JSON-LD only** (Google's recommended format). Put it in `<head>` or at the end of `<body>`.
- **Match the visible content.** Never mark up anything not on the page. Wrong schema is worse than none.
- **Connect the graph.** Use `@graph` with `@id` cross-references so the Article points to its author `Person` and publisher `Organization`.

**The 2026 stack worth shipping for a blog**
- `Article` (or `BlogPosting`): `headline`, `image`, `datePublished`, `dateModified`, `author` (a `Person` with a `url`), `publisher` (an `Organization` with a `logo`). For `author.name`, use the name only; put titles in separate fields.
- `Organization` site-wide: name, `logo`, and `sameAs` links to the brand's real profiles.
- `Person` for the author, with `sameAs` to LinkedIn / X / professional profiles.
- `BreadcrumbList` for navigation context.

**Deprecations to know (do not promise these rich results):**
- **FAQ rich results** stopped showing for most sites in 2026. Still write FAQ sections (great for AI extraction and UX), but do not pitch a Google FAQ rich result.
- **HowTo rich results** are gone too. Keep step structure for readers and extraction; expect no special Google treatment.

**Validating**
- A plain fetch / curl cannot see JSON-LD injected by JavaScript. Validate with Google's Rich Results Test or a real browser.

---

## 3. Technical AEO: make sure machines can read it

Content the engines cannot reach cannot rank or be cited. These are gates.

**Crawlable and indexable (the eligibility gate)**
- To appear in Google's AI features at all, a page must be indexed and snippet-eligible. That is the whole technical requirement.
- Confirm it is not blocked by `robots.txt`, not `noindex`, has a clean canonical, and is in the sitemap.
- Keep one canonical version of every page. Duplicates split signals.

**AI crawler access**
- Allow the bots that put you in answers:
  - **Retrieval / search bots** (allow them): `OAI-SearchBot` (ChatGPT), `PerplexityBot`, `ClaudeBot`, `Google-Extended`, `Bingbot` (Copilot).
  - **Training bots** (optional): `GPTBot`, `CCBot`. OpenAI and Anthropic split their bots so you can allow retrieval while blocking training.
- Blocking the retrieval bots removes you from AI answers today. Default for visibility is to allow them.
- `robots.txt` is advisory; to actually block a bot, use a WAF / Cloudflare.

**Rendering (the quiet killer)**
- Most AI crawlers do **not** execute JavaScript. They fetch raw HTML and stop. Googlebot renders JS; the AI bots largely do not.
- Consequence: a client-side-only page can rank in Google yet be invisible to ChatGPT and Perplexity. **Server-render or statically render anything you want AI-cited.**

**Core Web Vitals**
- A constraint, not a lever. Severe slowness can stop a page from being crawled at all. Fix severe failures (LCP, INP, CLS), then move on.

---

## 4. Measure it and prove impact

Set the expectation up front: content changes show up in classic search in days to weeks, and in AI answers in weeks.

**Classic search signal**
- `google_search_console_query_insights`: track impressions, clicks, CTR, and average position by query and page. Watch for pages climbing positions, and high-impression / low-CTR pages that need a title or meta rewrite.

**AI search visibility**
- `hyperseo_mentions_track`: ask the questions a customer would ("best [category] for [use case]") with the brand and 2 to 3 competitors, and see which models name whom, and what they cite. Run before optimizing (baseline) and monthly after.
- `hyperseo_ai_search_volume_get`: how much query volume exists in AI channels for the target terms.
- `hyperseo_ai_overviews_get`: whether Google shows an AI Overview for the term and which sources it cites.
- Google Search Console now reports AI-feature visibility, but as impressions only, with AI Overviews and AI Mode blended. Useful for trend, not clean click attribution.
- In GA4, AI assistants increasingly show up as their own referral channel, but a large share of AI-referred visits arrive as Direct, so treat AI referral numbers as a floor.

**What good looks like**
- Movement in GSC position and CTR on the target query.
- The brand appearing in `hyperseo_mentions_track` for queries where it was absent, within roughly 90 days of shipping strong content.
- The page showing up among the cited sources in `hyperseo_ai_overviews_get`.

For full audits, competitor benchmarking, and keyword expansion, hand off to the `seo-research` skill.
