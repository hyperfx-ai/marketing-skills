# The lint pass

The mandatory final pass for every draft, in any system — and the entry point when the user brings existing text ("tighten this," "make it sound human"). Two parts: the universal rules, then the AI-tell ban list. For deeper editing work, run the sweeps at the end of this file.

Fix violations before showing the draft. When editing a user's text, preserve their meaning and voice; you are removing failure, not imposing taste.

## The ten universal rules

Each rule with the failure and the fix:

**1. The point appears in the first two sentences.**
- Fail: "Reporting has changed a lot over the last decade. Teams have more data than ever, and expectations keep rising. That's why we built..."
- Fix: "Your Friday KPI deck can build itself. Here's how we do it."

**2. No sentence over 25 words unless it earns it; never two in a row.**
- A long sentence earns its length by carrying a genuinely compound thought. Two in a row means one of them is hiding two sentences.

**3. Active voice unless the actor is unknown or irrelevant.**
- Fail: "The migration was completed and improvements were observed."
- Fix: "We finished the migration; load times dropped 40%."
- Legitimate passive: "The account was accessed from three countries in one hour" (actor unknown — that's the point).

**4. Every claim is concrete: a number, a name, an example — or it goes.**
- Fail: "Trusted by leading companies to deliver significant results."
- Fix: "4,200 finance teams, including Loop Returns, cut reporting time by an average of 3 hours a week." (Only if true. A cut claim is fine; an invented number never is.)

**5. Cut hedges unless the hedge is the point.**
- "quite," "fairly," "somewhat," "arguably," "in many cases," "to some extent" — delete and reread; the sentence almost always improves. Keep a hedge only when precision requires it ("early data suggests" before real data).

**6. Verbs over nominalizations.**
- "made a decision" → "decided" · "conducted an analysis" → "analyzed" · "reached an agreement" → "agreed" · "is indicative of" → "indicates."

**7. One idea per paragraph; the first sentence states it.**
- Test: read only the first sentence of every paragraph. If that skeleton doesn't carry the argument, restructure before polishing words.

**8. No filler openers.**
- "It's worth noting that," "In today's world," "As we all know," "Needless to say" — the sentence after the filler is the real opener.

**9. The last line tells the reader what to do or what happens next.**
- Fail: "...and that's why observability matters more than ever."
- Fix: "...start with one dashboard: errors per deploy. Everything else can wait."

**10. Zero entries from the AI-tell ban list below.**

## The AI-tell ban list

Patterns that mark text as machine-written. Zero tolerance in shipped drafts.

**Banned words** (rewrite the sentence, don't synonym-swap):

> delve, elevate, unleash, unlock, leverage (as a verb), robust, seamless, seamlessly, revolutionize, game-changer, cutting-edge, in today's fast-paced world, digital landscape, ever-evolving, navigate (metaphorically), embark, journey (metaphorically), tapestry, testament to, underscore, foster, empower, supercharge, skyrocket, dive in, let's explore

**Banned constructions:**

1. **The negation flex:** "It's not just X — it's Y." / "This isn't about X. It's about Y." One per document at absolute most; the pattern is the tell, not the words.
2. **Rule-of-three overload.** Triads are fine; a triad in every paragraph ("clear, compelling, and effective") is a rhythm fingerprint. Break most of them into one strong item.
3. **The mirrored contrast:** "Where X sees a problem, Y sees an opportunity."
4. **The false question opener:** "So what does this mean for your business?" as a paragraph transition. Just say what it means.
5. **The summary paragraph that re-lists the sections.** If the piece needs a recap, it's too long or too shapeless.
6. **"Whether you're a startup founder or an enterprise CTO..."** — the fake-inclusive audience sweep.
7. **"In conclusion," "Ultimately," "At the end of the day"** as closers.
8. **Colon-title headline reflex:** "Reporting: Why It Matters More Than Ever."

**Banned structures:**

1. Uniform paragraph rhythm — every paragraph 3–4 sentences of similar length. Vary or merge.
2. Bold-lead-in bullet cascades ("**Speed:** ... **Quality:** ... **Cost:** ...") in prose contexts. Bullets are for genuinely parallel facts.
3. Header-per-two-sentences. If a section is two sentences, it isn't a section.
4. Em-dash chains — more than one em-dash construction per paragraph reads as generated.
5. Hedge-stack closings: "Of course, every situation is different, and what works for one team may not work for another." Delete; rule 9 replaces it.

**What humanizing is NOT:**

- Not injected typos, slang, or fake casualness ("Okay so real talk—").
- Not contractions sprinkled mechanically.
- Not first-person anecdotes the author never had. Never invent experiences, customers, or numbers to sound human.
- The honest sources of human texture: specific detail, actual opinion, variable rhythm, and the willingness to say one thing plainly instead of three things safely.

## The editing sweeps

For real editing jobs (a page, a deck, a long email), run ordered passes — one dimension at a time, because a single "make it better" pass catches the loudest problem in each sentence and misses the rest. After each sweep, reread quickly to confirm the earlier sweeps still hold.

**Sweep 1 — Argument.** Does the piece pass rules 1, 7, and 9? Is the structure the right system for the deliverable (check the style map in `SKILL.md`)? Fix structure before touching sentences; polishing a mis-structured draft is wasted work.

**Sweep 2 — Claims.** Every claim gets a source, a number, or a cut (rule 4). Flag anything you cannot verify rather than shipping it.

**Sweep 3 — Sentences.** Rules 2, 3, 5, 6, 8, plus the concision pass in `prose-style.md`. This is the longest sweep.

**Sweep 4 — Tells.** The full ban list above, mechanically. Search the text for the banned words; read for the banned constructions.

**Sweep 5 — Sound.** Read it aloud (rhythm rules in `prose-style.md`). Fix every stumble. Then read only the first and last lines — together they should state the point and the next step.

Report edits to the user as two or three bullets of what changed and why ("cut 40% — mostly hedges and a duplicated argument," "moved the recommendation to sentence one"), not a line-by-line changelog.
