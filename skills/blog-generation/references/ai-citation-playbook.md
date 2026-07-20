# AI Citation Playbook

How to get a brand cited and recommended by AI assistants (ChatGPT, Claude, Perplexity, Google AI Overviews and AI Mode, Gemini, Copilot). On-page structure (in `blog-playbook.md`) is necessary but not sufficient. This file covers the levers that decide whether a model trusts and surfaces the brand.

---

## 1. The factor order (what to edit first)

The Princeton GEO study tested optimization tactics on thousands of queries and measured the lift in AI visibility. Edit in this priority order. These are causal, not vibes:

1. **Cite sources** inline. Biggest lever. Add a credible source next to claims.
2. **Add statistics.** Specific numbers with timeframes.
3. **Add quotations** from named people or named sources.
4. **Authoritative, fluent tone.** Clear, confident, well-written prose.
5. **Improve clarity.** Plain, easy-to-extract sentences.

And the one that hurts: **keyword stuffing scored below the do-nothing baseline.** Density tricks actively reduce AI visibility.

Two findings that change strategy:
- **The lift is largest for pages not already ranked #1.** A challenger page can gain dramatically from citations and statistics; the incumbent gains little. If the brand is not winning, these tactics are the highest-leverage move available.
- **Combining tactics beats any single one.** Stat + named quote + source citation in the same section compounds.

A 2026 study of hundreds of thousands of AI-cited URLs adds the correlations: clarity and summarization, E-E-A-T signals, a Q&A format, and clean section structure all track with getting cited, while a **promotional, salesy tone tracks negatively.** Read-out: write like a credible expert explaining something, not like a brochure.

---

## 2. Be the primary source

AI models preferentially cite original, first-hand material over aggregated rehashing. The most citable content a brand can publish:

- **Original data and research.** A survey, a benchmark, an analysis of the brand's own anonymized usage. This is the single best long-term citation asset.
- **First-party case studies with real numbers.** "[Customer] went from X to Y in Z." Specific, attributable, impossible for a model to generate from training.
- **Genuine expertise and experience.** First-hand detail, opinions, edge cases, and lessons that only someone who actually did the work would know.

If the page only restates what is already on the web, there is no reason for a model to cite it over the original. Find the brand's proprietary angle and lead with it.

---

## 3. E-E-A-T and author signals (now an eligibility gate)

For queries where sourcing matters, a page with no verifiable author entity is structurally excluded from citation. Treat author identity as infrastructure, not decoration.

- **Named, credentialed authors.** Real person, real bio, real credentials, photo. "Admin" or "Staff" bylines give engines nothing to verify.
- **Experience layered on expertise.** The bio and the content should show first-hand experience, not just topical knowledge.
- **Author `Person` schema with `sameAs`.** Link the author to their LinkedIn, X, and any professional or scholarly profile. AI systems traverse these chains to resolve "is this a real, trustworthy person."

---

## 4. Brand entity and off-page presence (the part most people skip)

The biggest blind spot, and for AI recommendation it is decisive. In 2026 analyses, **unlinked brand mentions across the web correlated with AI citations more strongly than backlinks did.** Models recommend brands they have seen described, consistently, in many credible places.

- **Make the brand a clean entity.** Consistent name and description everywhere. An `Organization` schema with `sameAs`. Where the brand qualifies, a Wikidata entry gives it a persistent identifier. Claim the Google Knowledge Panel.
- **Get mentioned where AI reads.** The engines lean heavily on encyclopedic references, large community sites (Reddit shows up disproportionately, especially in Perplexity), YouTube, and the credible publications of the niche. A mention there is worth more than another link on a low-authority blog.
- **Get into the "best X" roundups.** Listicle and comparison content is the most-cited format in AI answers. Being honestly included in third-party "best [category]" lists puts the brand into the exact pages models quote for recommendations.
- **Be consistent.** The same positioning, category, and one-liner across the site, profiles, and third-party mentions.

This is why content alone is necessary but not sufficient: the page makes the brand citable; the off-page footprint makes the model confident enough to actually recommend it.

---

## 5. Per-engine notes

They barely overlap. The same brand can be cited very differently across engines. Cover the topic well and broadly rather than overfitting one engine.

- **ChatGPT search:** leans on Bing's index and on content-to-answer fit; fresher content tends to do better.
- **Perplexity:** heavy on community sources (notably Reddit), rewards clean atomic answers and clear structure, surfaces PDFs.
- **Google AI Overviews and AI Mode:** run on core Search ranking plus retrieval and query fan-out. The model decomposes a question into many sub-queries, so cover the whole topic cluster. Recognized entities (Knowledge Graph) get surfaced more.
- **Copilot:** Bing-based; page speed and indexability matter.
- **Claude:** selective; favors factual density and authoritative, well-structured sources.

The unifying move is to be the clearest, best-sourced, most-mentioned answer to the question.

---

## 6. The honest Google stance (say this to clients)

Google's own 2026 guidance is the credibility anchor, and worth stating plainly to a customer who has been sold "AEO secrets":

- Optimizing for AI search "is still SEO." AI Overviews and AI Mode use the same core ranking and quality systems, plus retrieval (grounding) and query fan-out.
- The single biggest lever is unique, people-first, non-commodity content. Do not publish what others already said or what a model could generate on its own.
- There is no required special markup, no required file, no need to chunk content, and no separate "AI writing style." Eligibility is ordinary: indexed and snippet-eligible.
- Authentic mentions help; inauthentic mention-farming does not.

The pitch to a customer is honest and durable: there is no trick. There is doing the fundamentals unusually well, in their real voice, with their real proof, structured so a machine can quote it.
