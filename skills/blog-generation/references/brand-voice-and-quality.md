# Brand Voice and Quality

The difference between content that builds a brand and content that quietly damages it. Off-brand, generic, AI-tell-ridden writing erodes the exact trust you are trying to earn, and AI engines are increasingly tuned against promotional, low-substance text. On-brand and human is a ranking and citation asset, not a finishing touch.

Do this **before** writing the first draft. The gate that every post passes before it ships is at the end of `blog-archetypes.md`.

---

## 1. Build a voice profile from the brand's own site

Read the customer's existing site with `firecrawl_urls_scrape` / `web_pages_fetch`: homepage, an about page, two or three of their best existing posts, and any product or pricing pages. From that, write a short profile that every draft must honor:

- **What they actually sell**, in one sentence, in their words.
- **Who it is for** (the specific customer, not "businesses").
- **Their category and positioning.** What box does the brand sit in, and what is its one-line claim?
- **Tone**: where they sit on formal vs casual, plain vs technical, bold vs measured. Name it concretely ("plain, confident, lightly wry"; "warm and reassuring"; "clinical and precise").
- **Reading level and sentence rhythm.** Short and punchy, or longer and considered.
- **Vocabulary**: the words and phrases they use, and the ones they clearly avoid. Industry terms they expect their reader to know.
- **Proof assets**: the real numbers, customers, credentials, certifications, and stories they can legitimately cite. (For a dentist: years in practice, procedures, real patient outcomes, credentials. For a jeweler: materials, craftsmanship, provenance, guarantees.)
- **Point of view**: what they believe about their space that a generic competitor would not say.

When in doubt about voice or a factual claim, ask the customer rather than inventing (in a scheduled run, skip the claim and send the question with `notify_user`). A wrong fact in their name is worse than a slow draft.

---

## 2. Positioning clarity: so LLMs file the brand correctly

A specific failure mode the customer cares about: getting recommended by AI **in the right context**. If the content describes the brand vaguely or inconsistently, models either ignore it or recommend it for the wrong thing. Fix that on the page:

- **State the category and the one-liner explicitly and consistently.** "[Brand] is a [category] for [audience] that [core value]." Use the same framing across every page and in the `Organization` schema.
- **Name the use cases the brand should be recommended for**, in plain language, as their own sections or FAQ entries ("Best for...", "When to use [Brand]"). Models pick these up as the contexts to surface the brand.
- **Be honest about the edges.** Saying what the brand is *not* for, or who should pick something else, increases trust and makes the right-context recommendation more likely, not less.
- **Keep naming consistent** everywhere (the exact brand name, product names, category words). Contradictory descriptions across pages confuse entity resolution and the brand gets mis-filed.

---

## 3. Substance rules (no fabrication, ever)

- **Never invent a statistic, quote, customer, credential, or outcome.** AI engines penalize unverifiable claims, humans lose trust when they catch one, and in regulated verticals (health, finance, legal) a fabricated claim is a real liability. Use the brand's real proof assets, or cite a real external source, or do not make the claim.
- **Attribute external facts.** A number without a source is a liability; a number with a credible source is a citation magnet.
- **Specific over generic, always.** The brand's real numbers and stories are both more persuasive to humans and more citable by AI than any amount of polished generality.
- **Match the reader's sophistication.** Do not over-explain to experts or under-explain to novices.

---

The AI tells and the pre-publish gate are at the end of `blog-archetypes.md`, the file of the writing step.
