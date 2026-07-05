# Cold Email Frameworks

Four structures that consistently work for cold outbound. Each one is a *shape*, not a template — the sentences should always be written fresh in the prospect's context. Pick the framework that fits the situation; don't force a situation into a framework.

## When to pick which framework

| Framework | Best when | Risk |
| --- | --- | --- |
| Observation → Problem → Proof → Ask | You have a real, specific signal about the prospect's company | Falls flat if the observation isn't actually relevant |
| Question → Value → Ask | The problem you solve is universally felt by the role | Sounds like a survey if the question is too generic |
| Trigger → Insight → Ask | A recent event (funding, launch, hire, leadership change) makes the problem acute | Window closes fast — use within 2–4 weeks of the trigger |
| Story → Bridge → Ask | You have a strong customer story for a similar company | Requires the prospect to see themselves in the story |

## Framework 1 — Observation → Problem → Proof → Ask

The default. Works for ~70% of campaigns. The personalized observation must connect to the problem you solve, otherwise it's just flattery.

### Shape

1. **One sentence observation** (Tier 3 personalization — pulled from `firecrawl_urls_scrape` of the careers / pricing / blog page, or from `scrape_linkedin_profiles`).
2. **The implied problem** (one sentence — the *because* / *which usually means* bridge).
3. **One proof point** (one specific result, named customer or metric — never both vague).
4. **One low-friction ask** (interest-based, not a meeting request).

### Example

```
Subject: hiring sdrs

Saw you're hiring 4 SDRs in NYC. That usually means meetings/SDR is the
gating metric for hitting Q3 targets.

We helped Notion's outbound team go from 1.4 to 3.2 meetings/SDR/week in
60 days by replacing manual research with prefilled signal cards.

Worth a 10-min look?

— Sam
```

### Why it works

- The observation is concrete (`hiring 4 SDRs in NYC`), not generic (`I see you're growing fast`).
- The bridge says *why that matters* without explaining the obvious (the prospect knows their own job).
- The proof point is one specific result, named customer, real metric.
- The ask is "10-min look", not "30-minute call to discuss synergies."

### Common failure modes

- **Observation has no bearing on the problem.** "Saw your CEO went to Stanford" → and? If you can't bridge it to the problem in one sentence, drop it.
- **Two proof points instead of one.** Cuts the perceived sharpness in half.
- **Asking for a meeting on touch 1.** Use "worth a look?" or "useful?" — meeting comes on the reply.

## Framework 2 — Question → Value → Ask

Use when the problem is universally true for the role and you can't get a strong per-prospect signal.

### Shape

1. **One direct question about the problem.**
2. **The way you solve it** (one sentence — what *we* / *the product* does).
3. **One proof or social-proof anchor.**
4. **The ask.**

### Example

```
Subject: reply rates

How are reply rates on your outbound right now?

We've built a way to score prospects by intent before SDRs touch the
list — teams using it land at 8-12% reply rates instead of 2-3%.

Beam, Webflow, and Census run this. Worth a peek at how?

— Sam
```

### Why it works

- The opening question forces the reader to answer it in their head — and if the answer isn't great, the rest of the email is the obvious next step.
- The value sentence is the *mechanism*, not just the outcome.
- Three named customers as social proof is fine when you can't single out one.

### Common failure modes

- **Question is too vague.** "Are you happy with your sales numbers?" — everyone says no, but it doesn't qualify anyone.
- **Question is rhetorical.** "Wouldn't it be great if your team hit quota?" — eye-roll material.
- **Skipping the mechanism and going straight to social proof.** "Notion uses us. Want to chat?" — *what do you actually do?*

## Framework 3 — Trigger → Insight → Ask

Use only when you have a real recent event for the prospect's company. The trigger must be ≤4 weeks old; older than that and you sound like a stalker / late.

### Shape

1. **The trigger** (specific, dated, verifiable).
2. **What the trigger usually means** for the role you're emailing (the insight — show that you understand the *implication*).
3. **The ask** — usually framed as "happy to share what we've seen with similar [stage / situation]."

### Example

```
Subject: post-series-b ops

Saw the $40M Series B announcement last week. Congrats.

The teams I've talked to at the Series B → C transition all run into
the same wall: the SDR motion that worked at Series A doesn't scale
past 25 reps without throwing CAC.

Happy to share what the 3-4 GTM teams I've worked with at this stage
ended up doing. Useful?

— Sam
```

### Why it works

- Trigger is dated, specific, and easy to verify.
- The insight earns trust — you're not pitching, you're naming a problem the prospect almost certainly already feels.
- The ask is consultative, not commercial.

### Common failure modes

- **Trigger is too old.** "Saw your funding round 8 months ago…" → late and weird.
- **Trigger is fake or speculative.** "Heard you might be raising soon" → don't.
- **The insight is generic.** "Funding usually means growing pains." → say something the prospect doesn't already know.

## Framework 4 — Story → Bridge → Ask

Use for high-trust outreach to enterprise / senior buyers when you have a strong customer story for a *very similar* company. The story is the email — the rest is just connective tissue.

### Shape

1. **A 2-sentence customer story** — name, situation, result.
2. **The bridge** — "Reason I'm writing — looks like you might be in a similar spot."
3. **The ask** — usually framed as "want me to walk you through how they did it?"

### Example

```
Subject: ramp's onboarding

Quick story: Ramp's outbound team had 60 SDRs onboarding in 4 months
last year and was losing 30% in the first 90 days because their ICP
research workflow was 3 hours of manual work before any prospect was
touched.

We rebuilt that workflow as a prefill on top of their CRM — onboarding
ramp time dropped from 11 weeks to 5.

Reason I'm writing — saw you're hiring at a similar pace. Want me to
walk you through how they did it?

— Sam
```

### Why it works

- The story is specific enough (numbers, named team, real metric) to feel earned.
- The bridge is the only place the prospect appears — keeps the focus on *value already delivered* rather than what you'd like to do.
- The ask is "want me to walk you through" — much lower friction than "let's set up a call."

### Common failure modes

- **The story doesn't apply.** Story about a 500-person enterprise sales team sent to a 20-person seed-stage startup → instant pass.
- **Two stories.** Cuts the believability of both. Pick one.
- **Skipping numbers.** Story without a metric is gossip.

## Calibrating tone by seniority

The framework stays the same; the *length and posture* change.

### C-suite (CEO, CFO, founder)

- **Target length: 40–60 words.**
- One observation, one proof, one ask. Skip the middle "problem" step — they already know.
- Tone: peer, understated, never explanatory.
- Sign-off with first name only.

```
Subject: q3

Saw the post about Q3 targets. Curious — are you running the SDR
motion in-house or with an agency right now?

We've got a way to cut research time per prospect from 90s to 8s. 
Worth 10 min?

— Sam
```

### Mid-level (Director, Manager)

- **Target length: 80–120 words.**
- Use the full framework. They want to see that you understand the role.
- Tone: knowledgeable peer, slightly more specific.
- Can include the proof customer's name + the metric.

### Technical / IC (Senior SDR, RevOps lead, engineering manager)

- **Target length: 60–100 words.**
- Be precise. They will judge you on accuracy.
- Drop adjectives. Use the actual mechanism: "we score prospects via a 6-feature gradient boost trained on 2.4M historical replies" beats "we use AI to find better leads."
- Tone: respect their time and their intelligence.

## Quick framework chooser

If you can answer **yes** to:

- "Do I have a specific, dated observation about *this* prospect's company?" → Framework 1.
- "Was there a funding round / launch / leadership change in the last 4 weeks?" → Framework 3.
- "Do I have a strong customer story for a near-identical company?" → Framework 4.
- "None of the above, but the problem I solve is universal for this role?" → Framework 2.

If none of those are true, the campaign isn't ready to send. Go back to Phase 1.
