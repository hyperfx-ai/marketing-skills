# Business writing systems

Structures for documents that inform and decide: memos, updates, announcements, proposals, press releases, case studies. The shared contract: the reader is senior, interrupted, and will stop reading the moment the document stops paying. Front-load accordingly.

## BLUF / Minto pyramid

**Use for:** exec memos, status updates, recommendations, reports — any document whose reader decides something.

BLUF is "bottom line up front." The Minto pyramid is the full discipline: conclusion first, then the 2–4 grouped arguments that support it, then the evidence under each. The reader can stop at any depth and still leave with the right conclusion.

**Hard rules:**

1. Sentence one is the conclusion or recommendation. Not background, not "the purpose of this memo."
2. Support comes as 2–4 parallel arguments, each stated as a claim, each provable on its own.
3. Nothing appears in the document that does not support the conclusion. Interesting-but-irrelevant gets cut.
4. Order arguments by strength for a friendly reader, by objection for a hostile one.
5. If the reader would ask "so what?" of any paragraph, the paragraph is upside down — its last line is its real first line.

**Before:**

> Over the last quarter we have been evaluating several vendors for the data pipeline migration. The process involved demos, reference calls, and a security review. There were many considerations including cost, support SLAs, and integration complexity. After extensive discussion the team has come to a view.

**After:**

> Recommendation: sign with Vendor B at $84k/yr. Three reasons: (1) it is the only bidder that passed our security review without exceptions, (2) migration effort is 3 weeks vs. 9 for Vendor A, (3) it is $31k/yr cheaper than the incumbent at our volume. Detail on each below; decision needed by Friday to hold pricing.

---

## SCQA — Situation, Complication, Question, Answer

**Use for:** proposals, pitches, one-pagers, case study openings — any document that must earn attention before it argues.

**Hard rules:**

1. Situation is one or two sentences of ground the reader already agrees with. No news here.
2. Complication is the change or tension that makes the status quo untenable. This is the hook.
3. The question is the one the complication forces. Usually implied, not written out.
4. The answer is your proposal — and from there the document continues as a Minto pyramid.
5. Total SCQA opening: under 120 words. It is a doorway, not a hallway.

**Example (proposal opening):**

> Acme's checkout converts at 2.1%, in line with the industry. (Situation.) But 68% of your traffic is now mobile, where your checkout converts at 0.9% — and mobile share is growing 5 points a quarter. (Complication. Implied question: what do we do about mobile checkout?) We propose a 6-week mobile checkout rebuild, targeting 1.8% mobile conversion, worth roughly $340k/yr at current traffic. (Answer — the rest of the document proves it.)

---

## Smart Brevity

**Use for:** announcements, newsletters, internal broadcasts — high-volume reading where the reader triages.

**Hard rules:**

1. A headline of six to ten words, in sentence case, carrying real information.
2. One bold first sentence with the single most important fact.
3. A "Why it matters" line immediately after — the consequence for this reader, not the company.
4. Then short labeled chunks ("The details," "What's next," "The catch"), each 1–3 sentences or a tight bullet list.
5. Nothing over 200 words without asking whether the reader chose the long version. Link out for depth.

**Example (feature announcement):**

> **Scheduled exports ship Monday.**
> Every dashboard can now email itself as a PDF on a schedule you set.
> **Why it matters:** the #1 support request this year — 340 tickets — was "send my boss this dashboard weekly." That workflow is now two clicks.
> **The details:** any dashboard → Share → Schedule. PDF or CSV, daily/weekly/monthly.
> **What's next:** Slack delivery is in beta; reply if you want in.

---

## Inverted pyramid

**Use for:** press releases, incident notices, news-style posts — documents readers abandon at unpredictable points.

**Hard rules:**

1. Paragraph one answers who, what, when, where, why. A reader who stops there is fully informed.
2. Each subsequent paragraph is less essential than the one before. The document must survive being cut from the bottom at any paragraph boundary.
3. Quotes add color and authority, never new load-bearing facts.
4. No teasing. "Read on to find out" structures are the opposite of this system.

---

## Narrative memo (Amazon-style)

**Use for:** big decisions that deserve real scrutiny — strategy docs, annual plans, product bets. The reading is the meeting.

**Hard rules:**

1. Full prose. No bullet lists in the body — bullets hide weak reasoning; sentences expose it.
2. Every claim carries its evidence in the same paragraph, not in an appendix the reader must trust you about.
3. Anticipate the three strongest objections and answer them in the document, in their own section.
4. For product proposals, write the press release and FAQ first (PR-FAQ): if the imagined launch announcement is boring, the product is.
5. Six pages maximum. If it does not fit, the thinking is not done.

---

## Action titles

**Use for:** headings in any deck or document longer than a page. A discipline layered onto other systems, not a standalone one.

**Hard rules:**

1. Every heading is a claim, not a topic. "Churn is concentrated in month 2" — not "Churn analysis."
2. Reading only the headings must deliver the full argument.
3. The body under a heading proves that heading and does nothing else. Evidence that proves a different claim moves under that claim's heading.

**Before → After (deck headings):**

> Background / Market overview / Our approach / Results / Next steps

> Mid-market churn doubled in Q2 → Churn concentrates in month 2, before first value → Customers who complete setup in week 1 retain 3× better → We propose a mandatory onboarding call → Pilot with 50 accounts starts June 1
