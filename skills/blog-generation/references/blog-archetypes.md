# Blog Archetypes (authoritative per-type specs)

The full playbook for each blog type. Pick one with the table below, then build to that type's exact spec. Every type still obeys the universal rules in `blog-playbook.md` (answer-first lead, question-shaped H2s, self-contained sections, no fabrication) and the voice and quality gate in `brand-voice-and-quality.md`. The schema notes assume the JSON-LD rules in `on-page-and-technical.md`.

## Pick the type

| Archetype | Query / intent it serves | Length | Schema | AI-citation lever |
| --- | --- | ---: | --- | --- |
| What-is / definition | "what is X", "X meaning" (informational) | 800-1,500 | Article | Clean definition block; the canonical "X is..." sentence |
| How-to / step-by-step | "how to X", "X steps" (task) | 1,000-2,000 | Article (ordered steps) | Numbered, self-contained steps |
| Comparison (X vs Y) | "X vs Y" (commercial) | 1,500-3,000 | Article | The comparison table + clear verdict |
| Listicle / best-of | "best X", "top X for Y" (commercial) | 1,500-2,500 | Article + ItemList | Ranked table + consistent per-entry blocks |
| Alternatives | "X alternatives" (commercial) | 1,500-2,500 | Article + ItemList | Per-alternative "best for" framing |
| Pillar / hub guide | broad head term (authority) | 2,500-4,000 | Article | Topical completeness + internal links |
| Pain / diagnostic | "why is my X doing Y", "X not working" | 1,000-1,800 | Article | Direct cause-and-fix answer up top |
| Original research / data | a claim only your data can prove | 1,200-3,000 | Article (+ Dataset if apt) | First-party stats others will cite |
| Case study | "X results", proof for buyers | 800-1,500 | Article | Named, numeric, attributable outcome |
| Glossary / definition page | many small "what is X" terms at scale | 300-800 each | DefinedTerm / Article | One crisp definition per term |

Choosing rule: classify the query intent (`hyperseo_intents_search`), then confirm the format against what already ranks (`hyperseo_serp_results_get`). If the SERP is all listicles, do not publish an essay.

---

## What-is / definition guide

**Use for** informational "what is / what does X mean" queries. The workhorse for topical authority and AI definitions.

**Structure**
1. Lead: "**[Term]** is [one self-contained sentence]." Then 1 to 2 sentences of expansion. This is the block AI quotes for the definition.
2. "How does [X] work?" (mechanism, plain language).
3. "Why does [X] matter?" or "What is [X] used for?" (concrete examples, ideally first-hand).
4. Types / variations, or key components, if the term has them.
5. "[X] vs [related term]" mini-section if people confuse the two.
6. FAQ (4 to 8 real questions).

**Pitfalls:** burying the definition; staying abstract with no examples; padding to hit a word count.

---

## How-to / step-by-step guide

**Use for** task intent. People who want to *do* the thing.

**Structure**
1. Lead: state the outcome and roughly how long / hard it is. "You can [outcome] in [N] steps. Here is how."
2. Prerequisites or what you need (short).
3. Numbered steps. Each step: a bolded action-verb name, what to do, and the result. Each step self-contained.
4. Common mistakes / troubleshooting (this section earns "why is my X failing" citations too).
5. FAQ.

**AI angle:** numbered, atomic steps are extracted cleanly. Keep each step understandable on its own.

**Pitfalls:** vague steps ("configure your settings"); missing the result of each step; no troubleshooting.

---

## Comparison (X vs Y)

**Use for** commercial "X vs Y" queries where the reader is choosing between two options.

**Structure**
1. Lead with the verdict: one sentence on who should pick X and who should pick Y. Do not make them scroll for it.
2. A comparison table near the top (dimensions down the side, X and Y across).
3. A short section per option: what it is, what it is best at, honest limitation.
4. "Which should you choose?" tied to reader profiles ("If you [situation], pick X").
5. FAQ.

**Honesty rules:** compare like to like (product vs product, or company vs company, never mixed). Give each side a real "best for". Never trash the other option; a fair comparison is more persuasive and more citable. If you publish this on your own brand's site, your product can win, but the concession has to be real and the other tools' strengths stated like you mean them.

**Linking:** internal links to your own cluster; no outbound links to a direct competitor's site from a page you want to rank for the shared query (it leaks equity and signals endorsement). Mention them in text; do not link them.

---

## Listicle / best-of (the format AI cites most)

**Use for** "best X", "top X for [use case]", "best X for [vertical]". Listicles and comparisons are the single most-cited content format in AI answers, so this type gets the fullest spec.

**Structure**
1. **Lead** (40 to 60 words): state what the list covers and who it is for. Name the top pick in the first sentence so AI can extract it.
2. **Quick-comparison table at the top** (the highest-ROI block): one row per item, consistent columns. Keep the column order fixed, prices in a consistent short form, and "best for" cells concrete. If you score, make the scores vary honestly (not 9.5 for everything) and order the table by rank.
3. **One section per entry, identical structure** (consistency is what makes the list scannable and extractable):
   - `### N. [Name]`
   - One image of the item right after the heading (optional but strong; never caption it as "screenshot of X", let the alt text carry it).
   - Two or three short paragraphs: what it is and its lane; one concrete capability with a number; pricing transparency plus the best-fit buyer and an honest limitation.
   - A 4-bullet summary: **Pricing**, **Pros** (3 specifics), **Cons** (3 honest gaps), **Verdict** (one sentence on who it is for).
4. **"How we chose"** methodology section near the end. An E-E-A-T and trust signal: state the criteria, that you actually evaluated them, and any first-hand testing. It also makes the list more citable.
5. FAQ.

**Honesty and ranking:** if it is your brand's own list, your product can rank #1, but its Cons bullet must concede something real and its claims must be verifiable. On someone else's list, a brand should sit mid-pack with a sharp "best for" hook; being #1 in a third-party list reads as paid.

**Pitfalls:** inconsistent entry structure; vague "great, easy to use" filler instead of specifics; fabricated scores or fake pros/cons; identical scores; linking out to every listed competitor.

---

## Alternatives page (X alternatives)

**Use for** "X alternatives", "alternatives to X" (a buyer who knows X but is shopping).

**Structure**
1. Lead: one sentence on why someone looks for alternatives to X (price, missing feature, fit), then name the strongest alternative.
2. Quick table of alternatives with a "best for" per row.
3. Per-alternative sections (like a listicle entry, lighter).
4. "How to choose" by reader situation.
5. FAQ.

**Scope discipline:** keep the alternatives in the same product class. Someone searching "[CRM] alternatives" wants another CRM, not an adjacent tool. An off-class alternative will not convert and the page reads as bait. Only build this for direct, in-lane peers.

---

## Pillar / hub guide

**Use for** the broad head term that anchors a topic cluster.

**Structure**
1. Lead: define the topic and tell the reader what the guide covers.
2. Comprehensive sections covering every major subtopic, each a question-shaped H2 that summarizes and then links out to a dedicated supporting post.
3. A "chapters" or table-of-contents block near the top for navigation.
4. FAQ spanning the whole topic.

**Role:** the pillar is the internal-linking hub. Publish the supporting posts first, interlink them, then ship the pillar so it inherits a web of links. See clusters in `blog-playbook.md`.

---

## Pain / diagnostic ("why is my X doing Y")

**Use for** problem-aware queries ("why is my [thing] [bad outcome]", "[thing] not working"). These earn AI Overview citations because the model wants a direct cause-and-fix.

**Structure**
1. Lead: the most common cause and the one-line fix, immediately. "[Outcome] is usually caused by [cause]. Fix it by [action]."
2. A ranked list of likely causes, each with how to confirm it and how to fix it.
3. How to prevent it recurring. (If the brand's product prevents this, the natural, non-salesy place to name it.)
4. When to get help / escalate.
5. FAQ.

**AI angle:** the answer-first cause-and-fix is exactly what gets pulled into an AI Overview. Lead with it.

---

## Original research / data study (the best long-term citation asset)

**Use for** a claim only the brand's own data can prove. The most citable thing you can publish, because no model can generate it from training.

**Structure**
1. Lead: the single headline finding, as one quotable stat. "We analyzed [N] [things]. [Headline number]."
2. Key findings as a scannable list, each a stat with its number.
3. Methodology (what you measured, sample size, dates, limitations). Non-negotiable for trust and citation.
4. Charts/tables of the data (with the numbers in text too, since AI bots may not read the chart image).
5. What it means / what to do about it.

**Rules:** real data only, never fabricated or "illustrative" numbers presented as real. State the sample and date. This is the asset competitors and journalists cite back to you, which compounds your entity authority.

---

## Case study (first-party proof)

**Use for** buyer-stage proof, and as the page you link every outcome claim back to.

**Structure**
1. Lead: the named customer and the headline result in one sentence. "[Customer] [did X] and [got Y result]."
2. The situation / problem.
3. What they did (the brand's role, specifically).
4. Results with real numbers and, ideally, a named quote from the customer.
5. A short "could this work for you" close.

**Rules:** real customer, real numbers, real (approved) quote. The highest-trust, most-citable proof a brand owns. Get permission before naming anyone.

---

## Glossary / definition page (at scale)

**Use for** building many small definition pages for an industry's terms (a programmatic-style cluster).

**Structure (per term):** one clean "**[Term]** is [definition]" lead, a short expansion, a "related terms" set of internal links, and one example. Keep each page genuinely useful and distinct. Do not mass-produce thin, near-identical pages with no added value; that triggers scaled-content spam treatment. Each page needs a real reason to exist.

---

## Cross-references

- Universal structure, content blocks, GEO writing rules, clusters: `blog-playbook.md`
- Schema per type, on-page, technical: `on-page-and-technical.md`
- Getting cited, authority, off-page: `ai-citation-playbook.md`
- Voice, anti-cringe, pre-publish gate: `brand-voice-and-quality.md`
