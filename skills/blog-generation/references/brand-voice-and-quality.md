# Brand Voice and Quality

The difference between content that builds a brand and content that quietly damages it. Off-brand, generic, AI-tell-ridden writing erodes the exact trust you are trying to earn, and AI engines are increasingly tuned against promotional, low-substance text. On-brand and human is a ranking and citation asset, not a finishing touch.

Do this **before** writing the first draft, and enforce the gate at the end before anything ships.

---

## 1. Build a voice profile from the brand's own site

Read the customer's existing site with `firecrawl_urls_scrape` / `web_scrape_page`: homepage, an about page, two or three of their best existing posts, and any product or pricing pages. From that, write a short profile that every draft must honor:

- **What they actually sell**, in one sentence, in their words.
- **Who it is for** (the specific customer, not "businesses").
- **Their category and positioning.** What box does the brand sit in, and what is its one-line claim?
- **Tone**: where they sit on formal vs casual, plain vs technical, bold vs measured. Name it concretely ("plain, confident, lightly wry"; "warm and reassuring"; "clinical and precise").
- **Reading level and sentence rhythm.** Short and punchy, or longer and considered.
- **Vocabulary**: the words and phrases they use, and the ones they clearly avoid. Industry terms they expect their reader to know.
- **Proof assets**: the real numbers, customers, credentials, certifications, and stories they can legitimately cite. (For a dentist: years in practice, procedures, real patient outcomes, credentials. For a jeweler: materials, craftsmanship, provenance, guarantees.)
- **Point of view**: what they believe about their space that a generic competitor would not say.

When in doubt about voice or a factual claim, ask the customer rather than inventing. A wrong fact in their name is worse than a slow draft.

---

## 2. Positioning clarity: so LLMs file the brand correctly

A specific failure mode the customer cares about: getting recommended by AI **in the right context**. If the content describes the brand vaguely or inconsistently, models either ignore it or recommend it for the wrong thing. Fix that on the page:

- **State the category and the one-liner explicitly and consistently.** "[Brand] is a [category] for [audience] that [core value]." Use the same framing across every page and in the `Organization` schema.
- **Name the use cases the brand should be recommended for**, in plain language, as their own sections or FAQ entries ("Best for...", "When to use [Brand]"). Models pick these up as the contexts to surface the brand.
- **Be honest about the edges.** Saying what the brand is *not* for, or who should pick something else, increases trust and makes the right-context recommendation more likely, not less.
- **Keep naming consistent** everywhere (the exact brand name, product names, category words). Contradictory descriptions across pages confuse entity resolution and the brand gets mis-filed.

---

## 3. Kill the AI tells (the anti-cringe rules)

The fastest way to make good content look like cheap content. Strip all of these:

- **Throat-clearing intros.** "In today's fast-paced / ever-evolving / digital landscape...", "In the world of...", "As we all know...". Delete and start with the answer.
- **The AI-essay vocabulary.** delve, unlock, elevate, harness, leverage (as filler), realm, tapestry, landscape, navigate the complexities, testament to, game-changer, supercharge, seamless, robust, cutting-edge, when it comes to. If a word smells like a model's default, cut it.
- **Empty hedging.** "may help", "can potentially", "might be able to". Make the claim or drop it.
- **The rule of three on autopilot.** Endless "X, Y, and Z" triads in every sentence. Vary the rhythm.
- **"It's important to note that...", "It's worth mentioning...", "Needless to say...".** Filler. Cut to the point.
- **Fake-balanced "conclusion" paragraphs** that restate the intro and say nothing new. End with a real takeaway and one action.
- **Overuse of em-dashes and emoji-bulleted lists** as a default texture. They are a tell when they appear everywhere. Use normal punctuation and plain bullets unless the brand's real voice does otherwise.
- **Generic openers and stock phrasing** that could appear on any competitor's site. If you could paste the sentence onto a rival's page unchanged, rewrite it with the brand's specifics.

The test: read it aloud as the founder. If they would be slightly embarrassed to publish it, it is not done.

---

## 4. Substance rules (no fabrication, ever)

- **Never invent a statistic, quote, customer, credential, or outcome.** AI engines penalize unverifiable claims, humans lose trust when they catch one, and in regulated verticals (health, finance, legal) a fabricated claim is a real liability. Use the brand's real proof assets, or cite a real external source, or do not make the claim.
- **Attribute external facts.** A number without a source is a liability; a number with a credible source is a citation magnet.
- **Specific over generic, always.** The brand's real numbers and stories are both more persuasive to humans and more citable by AI than any amount of polished generality.
- **Match the reader's sophistication.** Do not over-explain to experts or under-explain to novices.

---

## 5. The pre-publish quality gate

The post is not done until every box is checked.

**Voice and brand**
- [ ] Reads in the brand's actual voice (tone, vocabulary, reading level from the profile).
- [ ] No AI tells from section 3.
- [ ] The category and positioning one-liner are stated clearly and match every other page.
- [ ] Nothing in it would embarrass the founder.

**Substance**
- [ ] Every stat, quote, and claim is real and either first-party or sourced. Zero fabrication.
- [ ] The page says enough specific, verifiable things about the subject to be recommended for the right thing.
- [ ] It says something a generic competitor or a raw model could not have written.

**Structure**
- [ ] Answer-first lead; key term defined in the first ~150 words.
- [ ] Question-shaped H2s; each section self-contained and answer-first.
- [ ] At least one comparison table or structured block where the topic warrants it.
- [ ] FAQ block of real questions, each answered in 30 to 50 words.

**On-page and technical**
- [ ] Title (< ~60 chars, keyword front, click-worthy) and benefit-driven meta.
- [ ] Internal links into the cluster (siblings + pillar); descriptive anchors; no orphan.
- [ ] JSON-LD: Article + author Person + Organization, matching visible content.
- [ ] Visible "Last updated" date and accurate `dateModified`.
- [ ] The content you want cited is real server-rendered text, on a crawlable, indexable page.

**Measurement**
- [ ] Baseline captured (GSC position/CTR, `hyperseo_mentions_track`) so impact is provable later.

If any box fails, fix it before publishing.
