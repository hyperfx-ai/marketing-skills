# Blog Playbook: structure that ranks and gets cited

How to write a blog post that wins Google rankings and gets pulled into AI answers. The core of the skill. Read it fully before drafting.

The mechanism to keep in mind: classic search ranks a *page*; AI search extracts a *passage*. A great post is built so that any section can be lifted out and stand on its own as the answer to one question. Write for the passage, and the page wins too.

---

## 1. Pick the archetype first

Match the content type to search intent (from `hyperseo_intents_search`) and to what already ranks (from `hyperseo_serp_results_get`). Do not write a 3,000-word essay where the SERP rewards a listicle. The full per-type specs live in `blog-archetypes.md`; read the one for your chosen type before drafting.

**Length rule:** match the intent and the SERP, then stop. Word count is not a ranking factor. Thin content loses; padded content also loses. The average AI-Overview-cited page in 2026 is roughly 1,300 words, and over half are under 1,000. Long-form earns more links, but only when every paragraph carries weight.

---

## 2. The non-negotiable structure

Every post, regardless of archetype, follows this shape.

1. **Title** in the user's own query language (not a clever hook). Primary keyword near the front, under ~60 characters.
2. **Answer-first lead (the most important 60 words on the page).** The first one or two sentences directly answer the primary query. No "in today's fast-paced world." This is the block AI extracts and the snippet Google pulls.
3. **A self-contained definition** of the key term inside the first ~150 words: "**[Term]** is [one clear sentence]." AI uses this as the canonical definition for "what is X" queries.
4. **A short key-takeaways / TL;DR block** for anything over ~1,200 words, stating the main answer and 3 to 5 bullets.
5. **Question-shaped H2s and H3s.** Phrase each heading the way a person asks it: "How does X work?", "How much does X cost?", "Is X worth it?" AI does section-level extraction, so a heading that matches the user's question gets the section cited even when the page is not ranked #1.
6. **Self-contained sections.** Each section answers its own heading in its first sentence, then expands. No orphan pronouns, no "as mentioned above." A reader (or model) dropped into the middle should understand it.
7. **An FAQ block** of 4 to 8 real questions (mine "People Also Ask" and `hyperseo_serp_results_get`), each answered in 30 to 50 words, answer first.
8. **One clear call to action** at the end. Exactly one primary next step.

---

## 3. The copy-paste content blocks

These are the extractable units AI search cites most. Use them liberally and fill them with real specifics.

**Definition block** (lead a "what is X" post or section with this):
```
[Term] is [one-sentence, self-contained definition: what it is + what it does].
[One or two sentences of expansion.] [One sentence on why it matters / when it is used].
```

**Step-by-step block** (how-to):
```
To [outcome], [one-sentence overview]. Here is the process:

1. **[Action verb + step name].** [What to do and the result.]
2. **[Step name].** [What to do.]
```

**Comparison table** (the single highest-ROI block for commercial and AI queries; AI surfaces tables heavily):
```
| Option | Best for | Price | [Key dimension] |
| --- | --- | --- | --- |
| [A] | [concrete use case, 4-7 words] | [short form] | [value] |

**Bottom line:** [one-sentence recommendation tied to who the reader is].
```

**FAQ block:**
```
### [Question phrased exactly as users ask it]
[Direct answer in the first sentence, 30-50 words. No preamble.]
```

**Statistic-citation block** (a top-three GEO lever; cite the source inline):
```
According to [Source, Year], [specific stat with a number and timeframe]. [What it means for the reader.]
```

**Expert-quote block** (another top GEO lever; attribute fully):
```
"[Direct quote]," says [Full Name], [Title] at [Organization].
```

**Evidence sandwich** (the most citable pattern for a claim that matters):
```
[Clear claim stated as a fact.]
- [Sourced data point 1]
- [Sourced data point 2]
[One-sentence actionable conclusion.]
```

---

## 4. The proven GEO writing rules

Validated by what actually moved rankings and citations, and by the Princeton GEO research (see `ai-citation-playbook.md` for the factor order).

1. **Answer first, explain second.**
   - Bad: "In today's rapidly evolving digital landscape, businesses are increasingly turning to..."
   - Good: "AI search optimization means structuring content so ChatGPT, Perplexity, and Google's AI Overviews quote it directly. The three levers that matter most are clear answers, cited statistics, and named-source quotes."
2. **Named entities and verifiable claims.** Specific, nameable facts get cited; vague claims get skipped.
   - Bad: "This saves a lot of time."
   - Good: "This cut setup from four hours to three minutes, documented in [Customer]'s case study."
3. **Define the key term explicitly** in the first ~200 words, as one clean sentence.
4. **Use a comparison table** in any post that weighs options. Highest single-tactic ROI for commercial and AI queries.
5. **Question-shaped sub-headings** that match how people prompt an AI.
6. **Cite sources, add statistics, add quotations.** The three strongest citation levers. One supporting stat or named source roughly every 150 to 250 words is a good density. Never invent them.
7. **Be specific to the subject where the goal is recommendation.** When the aim is for AI to recommend a particular product or company, the page must say enough concrete, verifiable things about it (capabilities, numbers, real outcomes, who it is for) for a model to associate it with the topic. A page that is 90% generic advice and 10% product will not get the product recommended.
8. **On-page keyword placement** (helps Google classify, without stuffing): exact primary keyword in the title, the first paragraph, at least one H2, the meta description, and the URL slug. Once each, naturally. Then stop.

---

## 5. Topic clusters, not orphan posts

A single post rarely builds authority. Plan in clusters.

- **Pillar page:** the broad head term, comprehensive, links out to every supporting post.
- **Supporting posts:** specific long-tail subtopics, each linking back up to the pillar and across to siblings.
- **Publish order:** ship 3 to 5 supporting posts and interlink them first, then publish the pillar so it inherits a web of internal links on day one.
- Every post links to at least two siblings in its cluster and up to the pillar. No orphans.

---

## 6. Improving an existing post (often higher ROI than a new one)

Before writing something new, check `google_search_console_query_insights` for pages that already get impressions:

- **Position 4 to 15, decent impressions, low CTR:** do not write a new post. Rewrite the title and meta to earn the click, and tighten the answer-first lead.
- **Position 10 to 20 on a relevant query with no dedicated page:** that query is a signal. Write a focused post targeting it, and link to it from related posts.
- **A long-tail query (5+ words) ranking that you never targeted:** gold. Build the post it is asking for.
- **Refreshing:** make substantive changes (new data, new sections, corrected claims), then update the visible date and `dateModified`. Do not bump the date with no real change.
