---
name: blog-generation
description: "Generate one excellent, on-brand blog post per run for any business, built to rank on Google and get cited by AI search (ChatGPT, Claude, Perplexity, AI Overviews). A stateful engine: reads a brand strategy doc, picks a fresh topic (never repeats), researches, writes in the brand's voice, and logs the post back. Use when the user wants to write a blog post, run a daily or recurring blog task, or generate SEO / AEO / blog content. For keyword data and audits, defer to seo-research."
icon: hyperseo
short_description: Generate one on-brand blog post per run, built to rank and get cited by AI search.
---
# Blog Generation

One job, done well: produce a single excellent, on-brand blog post per run, optimized to rank on Google and get cited by AI search, and never repeat what you have already written. Built to run as a recurring task (for example, one post a day) or on demand for any business in any vertical: a dentist, a jeweler, a B2B SaaS, a DTC brand.

The whole game is captured in two ideas. First, AI search visibility is SEO done well: unique, genuinely useful, people-first content with a clear point of view, structured so a machine can extract a clean answer. There is no secret AEO hack. Second, the engine has **memory**: a single `blog-strategy.md` file, saved in persistent storage, holds the brand's context plus a running log of every post. That log is what stops it from ever repeating itself.

> **The memory contract (the most important rule in this skill).** The log lives in a real file that survives between runs. On the FIRST run it does not exist, so you create it. On EVERY run after that it already exists, so you read it into context before doing anything, then append the new post to it before you finish. Same brand, same file path, every time. If you ever write a post without first reading the log, or finish a run without appending to it, the engine is broken: it will loop and repeat topics. Read-the-log-first and append-the-log-last are non-skippable.

## Requirements

- **Hyper MCP connected.** https://app.hyperfx.ai/mcp
- **A brand strategy doc** (`blog-strategy.md`) in persistent files. If it does not exist yet, the engine builds one on the first run (Step 0). This is what lets it write in the brand's real voice and avoid repeats.
- **Recommended toolkits**, enabled at https://app.hyperfx.ai/integrations: **Firecrawl** (read the brand's site), **HyperSEO** (validate topics, see what ranks and what AI cites), **Google Search Console** (mine real signals and measure). Without them you can still draft, but flag that topic and ranking calls are unvalidated.

## Tool surface

| Job | Tools |
| --- | --- |
| Read and write `blog-strategy.md` and the post draft | your file tools (`read_file`, `create_file`, `edit_file`) |
| Learn the brand from their site (Step 0) | `firecrawl_urls_scrape`, `web_scrape_page` |
| Validate a topic and study the SERP / AI answer | `hyperseo_search_volume_get`, `hyperseo_keyword_difficulty`, `hyperseo_intents_search`, `hyperseo_ai_search_volume_get`, `hyperseo_serp_results_get`, `hyperseo_ai_overviews_get` |
| Mine real-world signal and measure impact | `google_search_console_query_insights` |
| Check whether AI recommends the brand | `hyperseo_mentions_track` |

## Out of scope: defer to other skills

| Request | Send them to |
| --- | --- |
| Keyword research, SERP / AI-Overview analysis, competitor benchmarks, site audits, AI-visibility tracking | `seo-research` |
| Turn a YouTube video into a post | `youtube` |
| What real customers say (Reddit, reviews) to ground a post | `customer-research` |
| Publish to a social channel | `linkedin`, `instagram`, `tiktok` |

## The run (do this every time the task fires)

**Step 0 (first run only): build the strategy doc.** If `blog-strategy.md` does not exist, create it before writing anything. Read the brand's site (`firecrawl_urls_scrape` on homepage, about, best existing posts, product/pricing) and fill the **Brand brief** using the method in `references/brand-voice-and-quality.md`. Seed the **Topic backlog** with 8 to 15 candidate topics (validate with HyperSEO where available). Then continue to Step 1. If anything critical is unknown (real proof assets, the brand's actual positioning), ask the user rather than inventing.

**Step 1: load your memory (read the log).** Open the brand's `blog-strategy.md` from its saved file path and read ALL of it into context: the Brand brief (the contract every draft honors) and the entire Published log (everything already written). This happens on every run after the first, with no exceptions. You cannot pick a fresh topic without it.

**Step 2: plan today's post.** Pick ONE topic that is not in the Published log and is genuinely distinct from it (see "Picking a fresh topic" below). Write a one-line plan capturing exactly these four things, and record it in the strategy doc:
- **Title / topic**: the working title and the primary query it targets.
- **Where it is coming from**: the source or trigger (a backlog item, a GSC gap, a customer question, a keyword gap, a news hook, a piece of the brand's own expertise or data).
- **What it is going to do**: the archetype (listicle, comparison, how-to, what-is, alternatives, pillar, pain/diagnostic, original research, case study, glossary) from `references/blog-archetypes.md`.
- **The research it is going to do**: the specific checks for this post (SERP read, AI-Overview check, sources to pull, the brand proof to feature).

**Step 3: research.** Run the plan. Validate the target (`hyperseo_search_volume_get`, `_keyword_difficulty`, `_search_intent`, `_ai_search_volume`). Study what wins (`hyperseo_serp_results_get`) and what AI already cites (`hyperseo_ai_overviews_get`). Read the top pages and find the angle they all miss. Pull the real facts, stats, and named sources you will cite. Never fabricate.

**Step 4: write the post.** Build to the archetype spec in `references/blog-archetypes.md`, using the answer-first structure and copy-paste blocks in `references/blog-playbook.md`, in the brand's voice per `references/brand-voice-and-quality.md`, with the citation tactics in `references/ai-citation-playbook.md`. On-page and schema per `references/on-page-and-technical.md`.

**Step 5: run the quality gate.** Pass every item in the pre-publish gate in `references/brand-voice-and-quality.md` before the post is done: on-brand voice, no AI tells, no fabrication, answer-first structure, on-page and schema, baseline captured. If anything fails, fix it.

**Step 6: update your memory (append to the log).** Append the finished post as a new row in the **Published log** in `blog-strategy.md` (date, title, slug, archetype, target query, source, link), and save the file back to the same path. Remove the topic from the backlog and add any new ideas the research surfaced. This append is exactly what the next run reads to avoid repeating you. Never finish a run without it.

**Step 7: deliver.** Output the post (and publish it if a publishing path is wired for this brand). Set the expectation that ranking moves in days to weeks and AI citations in weeks.

## Picking a fresh topic (so it never loops)

Each run must produce something new. To choose:

1. **Exclude everything in the Published log** and anything that merely rewords it (same intent under a different title is a repeat).
2. **Prefer the highest-priority unblocked backlog item** that fits the brand and has real demand.
3. **Vary the shape.** If the last few posts were listicles, write a how-to, a pain/diagnostic, or an original-data piece. A healthy blog mixes archetypes.
4. **Pull from live signal where available**: GSC queries the brand ranks for on page two (`google_search_console_query_insights`), keyword gaps (defer to `seo-research`), recurring customer questions, or a timely news hook in the brand's space.
5. **Lean on the brand's own substance.** The most citable, least repeatable posts use the brand's proprietary data, real customer outcomes, or first-hand expertise. Reach for these often.

## The strategy doc (`blog-strategy.md`) — the engine's memory

One Markdown file per brand, saved at a stable path in persistent storage (for example `/files/<brand-slug>/blog-strategy.md`) and reused at that SAME path on every run. Create it in Step 0, read it in Step 1, append to it in Step 6. The **Published log** section is the part that prevents repeats; it only ever grows. Template:

```markdown
# Blog Strategy: [Business name]

## Brand brief
- Business: [what they do, one sentence]
- Sells: [products / services]
- Audience / ICP: [the specific customer]
- Category + one-liner: "[Brand] is a [category] for [audience] that [core value]."
- Voice: [tone, reading level, point of view]
- Words we use / words we avoid: [...]
- Proof assets: [real numbers, customers, credentials, data, stories]
- Primary site: [url]
- Target topics / seed keywords: [themes]
- Publishing: [where posts go, cadence]

## Topic backlog (planned, prioritized)
| Priority | Working title | Archetype | Target query | Source / angle | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | ... | ... | ... | ... | planned |

## Published log (do NOT repeat anything here)
| Date | Title | Slug | Archetype | Target query | Source | Link |
| --- | --- | --- | --- | --- | --- | --- |
```

## Non-negotiables (true on every run)

- **Unique and people-first beats every hack.** If a model could already write the post from common knowledge, or ten pages already say it, do not publish it. Lead with the brand's real angle.
- **Answer first, then explain.** Open the post and every section with the direct answer. AI extracts it; Google rewards it.
- **On-brand and human, or it backfires.** Off-brand, AI-tell-ridden, salesy content erodes trust and AI engines deprioritize it. The brand's real voice is the asset. See `references/brand-voice-and-quality.md`.
- **Specific and verifiable, never vague or invented.** Numbers, names, dates, real sources. Never fabricate a stat, quote, customer, or credential.
- **One new post per run, always logged.** The log is what makes the engine an engine instead of a loop.

## Also handles: optimizing an existing post

The same references cover improving a page that already exists (rewrite a weak title and lead for a high-impression, low-CTR page, add structure and schema, sharpen the brand's recommendation context). Use `references/on-page-and-technical.md` and `references/brand-voice-and-quality.md`, and log the change in the strategy doc.

## References

- `references/blog-archetypes.md`: authoritative per-type specs for 10 blog types, each with structure, length, schema, AI-citation lever, and pitfalls. Listicles get the fullest treatment.
- `references/blog-playbook.md`: answer-first structure; copy-paste content-block templates; the proven GEO writing rules; topic clusters; improving an existing post.
- `references/brand-voice-and-quality.md`: extract a voice profile from the brand's site; positioning clarity; the anti-AI-tell and anti-cringe rules; the pre-publish quality gate.
- `references/ai-citation-playbook.md`: the Princeton GEO factor order; E-E-A-T and author/entity signals; off-page mentions; per-engine notes; the honest Google stance.
- `references/on-page-and-technical.md`: on-page checklist; JSON-LD schema and deprecations; crawlability / AI-bot / server-rendering gates; how to measure impact.
