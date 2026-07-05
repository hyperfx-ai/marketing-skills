---
name: cold-email-outreach
description: Run end-to-end B2B cold-email outreach through the Hyper MCP — enrich prospects with Apollo, scrape per-prospect signals from company sites and LinkedIn, draft personalized emails using proven hook frameworks, send via Gmail with safe defaults, and route replies into labeled folders. Use when the user wants to write cold emails, run an outbound sequence, prospect a list, build a follow-up cadence, "reach out to leads," or asks why nobody is replying to their cold emails.
icon: gmail
short_description: B2B cold outreach with Apollo prospecting, personalization, Gmail sending, and follow-ups.
---

# Cold Email Outreach

End-to-end cold outreach: research, draft, send, follow up, route replies. Strategy is grounded in proven hook frameworks (number-led / question / pain-point / benefit-first); the execution runs on Apollo, Firecrawl, the LinkedIn scraper, and Gmail through the Hyper MCP.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Lifecycle / nurture sequences for *warm* leads (welcome, onboarding, re-engagement, win-back) | `email-lifecycle` (planned) |
| LinkedIn DMs, connection requests, or Sales Navigator workflows | (planned) |
| Lead scoring, routing, deal-stage updates after a reply | `crm-revops` (planned) |
| Scraping competitor *ads* | `meta-ads-library` |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Gmail integration** connected at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations) — supplies the sending account.
- **Apollo integration** connected — supplies prospect search and email enrichment.
- **Firecrawl** (bundled) — for company-page signals.
- **Optional: LinkedIn scraper** (bundled, runs through Apify) — for richer per-prospect personalization.

If `gmail_messages_send` and `apollo_mixed_people_search` are not in the agent's tool list, stop and tell the user to enable the Hyper MCP and connect Gmail + Apollo.

## Tool surface

| Phase | Tools |
| --- | --- |
| Prospect research | `apollo_mixed_people_search`, `apollo_mixed_companies_search`, `apollo_people_bulk_match` (preferred for 2+ enrich), `apollo_people_match` (single only) |
| Per-prospect signals | `firecrawl_urls_scrape`, `firecrawl_urls_scrape_batch`, `firecrawl_branding_extract`, `firecrawl_screenshots_create`, `scrape_linkedin_profiles` *(conditional — requires LinkedIn Apify integration)* |
| Drafting | `gmail_drafts_create`, `gmail_drafts_update`, `gmail_drafts_get`, `gmail_drafts_list` |
| Sending | `gmail_messages_send`, `gmail_drafts_send`, `gmail_reply_to_message` |
| Reply routing | `gmail_messages_list`, `gmail_get_message`, `gmail_labels_create`, `gmail_labels_add`, `gmail_labels_remove`, `gmail_messages_move_to_label` *(takes `label_id` string, not `label_ids` array)* |

## Critical rules

1. **Never loop `apollo_people_match` for multiple prospects.** For 2+ records always batch into `apollo_people_bulk_match`. Apollo's tool description warns about this explicitly — looping single-match calls burns credits and is much slower.
2. **Default send mode = drafts-first for review.** For any campaign with 4+ prospects, draft the first 1–3 with `gmail_drafts_create`, show them to the user, get explicit approval, then batch-send the rest with `gmail_messages_send`. Never send a full campaign without showing samples first.
3. **One label per campaign.** Create a `cold/<campaign-name>` label with `gmail_labels_create` at the start, apply it to every send, then track replies by searching that label. This is what makes Phase 6 reply routing actually work.
4. **Stay under Gmail's send limits.** ~500 messages/day per consumer Gmail account, ~2,000/day per Workspace user. Space sends out — see [`references/deliverability.md`](./references/deliverability.md) for warming and per-day pacing.
5. **Personalization must connect to the problem.** If the personalized opener could be deleted and the email still makes sense, it isn't doing any work. The opener should naturally bridge into *why you're emailing*.
6. **One ask per email, one CTA.** Interest-based (`Worth exploring?`) beats meeting requests on cold touch 1.
7. **Honor unsubscribes immediately.** Apply an `unsubscribed` label on any "remove me / not interested" reply and never re-target that address from the same Hyper workspace.

## Workflow

### Phase 1 — Define the campaign (always do this first)

Get the user to commit to:

1. **ICP** — Role(s), industry, company size, tech stack, geography. Concrete: "Heads of Growth at US-based pre-seed-to-Series-A B2B SaaS, 10–50 employees, using HubSpot."
2. **The ask** — What does a "yes" look like? (15-min call, async reply, demo, intro to someone else.)
3. **Value prop in one sentence** — "We help X do Y so they can Z."
4. **Proof point** — One specific result: "We helped Notion cut their CAC by 31% in 90 days." (Made up examples are worse than no example — get a real one.)
5. **Trigger / signal (optional but powerful)** — Funding round, hiring, pricing-page change, recent blog post, product launch, leadership change.
6. **Sender + reply-to** — Which Gmail account is sending. (Confirm with `gmail_labels_list` to verify the integration is live.)
7. **Volume + cadence** — Total prospects, max sends/day, follow-up gap pattern.

If they're stuck on any of these, push back. A campaign without proof or a clear ask will not perform regardless of how clever the writing is.

### Phase 2 — Build & enrich the prospect list

```
# Search by ICP
apollo_mixed_people_search(
  person_titles=["Head of Growth", "VP Growth", "Director of Growth"],
  organization_num_employees_ranges=["11,50"],
  person_locations=["United States"],
  per_page=50,
)
```

Then for the prospects you actually want to contact, batch-enrich for emails:

```
# CORRECT — one bulk call for many prospects
apollo_people_bulk_match(
  details=[
    {"first_name": "...", "last_name": "...", "domain": "..."},
    ...up to 10 per call...
  ],
  reveal_personal_emails=True,
)
```

Only fall back to `apollo_people_match` for single-prospect lookups (e.g., the user pastes one LinkedIn URL).

For deeper company-level context (industry, revenue range, tech stack), call `apollo_mixed_companies_search` by organization name on the companies you want to enrich. Note that person search results already include core company fields (headcount, industry, location) — only reach for `apollo_mixed_companies_search` when you need data beyond what the person search returns.

### Phase 3 — Per-prospect signals (the personalization layer)

For each prospect, gather one *specific* observation that connects to the problem you solve. Use the cheapest signal that works:

| Cost | Tool | Use it for |
| --- | --- | --- |
| Free (already have it) | Apollo response fields | Title change, recent role start, company headcount jump, funding |
| Cheap | `firecrawl_urls_scrape` of the careers / pricing / blog page | "You're hiring 4 SDRs", "Pricing pages says enterprise plan launching", "Latest blog post is about X" |
| Cheap (multi-page) | `firecrawl_urls_scrape_batch` | Same observation across many sites in one call |
| Medium | `firecrawl_branding_extract` | Brand voice for the email tone, brand colors if you'll send a follow-up image |
| Higher *(conditional)* | `scrape_linkedin_profiles(profile_urls=[...])` *(requires LinkedIn Apify integration — skip if not connected)* | Recent post, mutual connection, recent job change, school/employer overlap |

Personalization tiers (use the highest tier you can afford for *this* campaign):

- **Tier 1 (mass / low-effort)** — first name + role + company + industry. Acceptable only when the *value prop* is sharp enough to carry the email on its own. Reply rates: low.
- **Tier 2 (signal-based)** — the prospect is in a role/stage where the problem you solve is acute (e.g., a new Head of Growth in their first 60 days). Reply rates: meaningfully better.
- **Tier 3 (observation-based)** — references something from the company site, pricing page, careers page, or a recent product launch. This is the sweet spot.
- **Tier 4 (deep)** — references a recent LinkedIn post, blog post they wrote, or talk they gave. Reserve for high-value targets.

Anything below Tier 2 should be treated with suspicion — `{{FirstName}}` swaps don't count as personalization.

### Phase 4 — Draft emails (drafts-first by default)

Pick a framework that matches the situation. The four shapes that consistently work:

- **Observation → Problem → Proof → Ask** — "You're hiring SDRs. That usually means meetings/SDR ratio is the bottleneck. We helped [company] hit X. Worth exploring?"
- **Question → Value → Ask** — "Struggling with [problem]? We do [Y]. [Company Z] saw [result]. Worth a look?"
- **Trigger → Insight → Ask** — "Congrats on [funding/launch]. That usually creates [Y challenge]. We've helped similar teams with that. Curious?"
- **Story → Bridge → Ask** — "[Similar company] had [problem]. They [solved it this way with us]. Relevant to you?"

See [`references/frameworks.md`](./references/frameworks.md) for full examples and when each shape works best.

**Subject lines.** Short, lowercase, internal-looking. 2–4 words. No emojis, no first names, no urgency tricks. Targets: looks-like-a-colleague-sent-it. Examples: `quick question`, `reply rates`, `hiring ops`, `q3 forecast`, `for {{company}}`. Avoid: `Increase your revenue 10x!`, `John, are you free Thursday?`, `[URGENT] follow-up`.

**Voice rules.**

- Write like a peer, not a vendor. Use contractions. Read it aloud — if it sounds like marketing copy, rewrite it.
- "You/your" should outnumber "I/we" by ≥2:1.
- Every sentence must move the reader toward replying. The best cold emails feel like they could have been *shorter*, not longer.
- Calibrate to seniority: C-suite → ultra-brief and peer-level. Mid-level → more specific value. Technical → precise, no fluff, respect their intelligence.

**What to avoid (these are the AI-tells reviewers immediately spot):**

- "I hope this email finds you well." / "I came across your profile."
- "leverage", "synergy", "best-in-class", "leading provider", "circle back"
- Feature dumps. One proof point beats ten features.
- HTML, images, multiple links.
- Fake `Re:` / `Fwd:` subject lines.
- Identical templates with only `{{FirstName}}` swapped.
- Asking for a 30-minute call on touch 1.

**Drafts-first send pattern (default for any 4+ prospect campaign):**

```
# 1. Create label for the campaign once — capture the returned id
label = gmail_labels_create(name="cold/q3-growth-leads")
campaign_label_id = label["id"]

# 2. Draft the first 1-3 prospects for user review
for p in prospects[:3]:
    gmail_drafts_create(
      to=p["email"],
      subject="quick question",
      body=render_email(framework="observation", prospect=p),
    )

# 3. Show drafts to user, await explicit approval

# 4. After approval, send and label each message
for p in prospects[3:]:
    result = gmail_messages_send(
      to=p["email"],
      subject="quick question",
      body=render_email(framework="observation", prospect=p),
    )
    gmail_labels_add(message_id=result["id"], label_ids=[campaign_label_id])
```

If the user wants every email reviewed, use `gmail_drafts_create` for all of them and send via `gmail_drafts_send` after approval. If the user is confident and the templates are pre-approved (e.g., they've run this campaign shape before), you can skip directly to `gmail_messages_send` from prospect 1. Default behavior is drafts-first.

### Phase 5 — Run the follow-up cadence

3–5 total touches with widening gaps. Each follow-up adds something new — a different angle, fresh proof, a useful resource. "Just checking in" gives the reader no reason to respond.

Default cadence (adjust to the user's situation):

| Touch | Day | Angle | Tool |
| --- | --- | --- | --- |
| 1 | 0 | Initial framework (observation/question/trigger/story) | `gmail_messages_send` |
| 2 | +3 | Reply in the same thread, add a one-line specific proof | `gmail_reply_to_message` |
| 3 | +7 | Different angle (if 1 was observation, try question or value-first) | `gmail_reply_to_message` |
| 4 | +14 | Useful free resource — case study, calculator, teardown | `gmail_reply_to_message` |
| 5 | +21 | Breakup email. "Closing your file unless I hear back. Worth keeping the door open?" | `gmail_reply_to_message` |

Always reply in the original thread (`gmail_reply_to_message` with the `message_id` returned from the touch-1 send) — preserves context and improves deliverability. See [`references/follow-up-sequences.md`](./references/follow-up-sequences.md) for angle rotation, breakup-email templates, and how to prune prospects mid-sequence.

### Phase 6 — Track replies and route them

```
# Pull all replies on the campaign label from the last 7 days
gmail_messages_list(query="label:cold/q3-growth-leads is:unread newer_than:7d")
```

For each reply, read the body with `gmail_get_message(message_id=...)`, classify it, and label:

| Classification | Label | What to do |
| --- | --- | --- |
| Interested ("yes / tell me more / send a calendar") | `cold/q3-growth-leads/interested` | Stop the sequence. Hand off (eventually `crm-revops` once shipped). |
| Objection ("we use X / no budget / try us in Q4") | `cold/q3-growth-leads/objection` | Reply with one specific response, then stop sequence. |
| Not now ("circle back later") | `cold/q3-growth-leads/not-now` | Stop sequence. Re-tag for re-engagement in 90 days. |
| Unsubscribe ("remove me / not interested") | `cold/q3-growth-leads/unsubscribed` | Stop sequence. Add `unsubscribed` global label. Never re-contact. |
| Out-of-office | `cold/q3-growth-leads/ooo` | Pause sequence, resume after the OOO end date in the message. |

Apply classification and clear unread with two separate calls:

```
gmail_labels_add(message_id=..., label_ids=[classification_label_id])
gmail_labels_remove(message_id=..., label_ids=["UNREAD"])
```

Create the sub-labels once with `gmail_labels_create` and capture their IDs before the routing loop.

## Quality check (before any send)

Read each draft against this gut-check. Reject any that fail more than one:

- Does it sound like a human wrote it? (Read it aloud.)
- Would *you* reply if you got this?
- Does every sentence serve the reader, not the sender?
- Is the personalization connected to *the problem you solve* — not just a generic compliment?
- Is there one clear, low-friction ask?
- Does the subject line look like it came from a colleague?
- Is the email under ~120 words on touch 1?

## Reference workflows

For long-form material — read on demand:

| Reference | When to read |
| --- | --- |
| [`references/frameworks.md`](./references/frameworks.md) | Choosing a framework, full examples, calibrating tone by seniority |
| [`references/follow-up-sequences.md`](./references/follow-up-sequences.md) | Building the multi-touch cadence, angle rotation, breakup email templates |
| [`references/deliverability.md`](./references/deliverability.md) | Gmail rate limits, sender warming, SPF/DKIM/DMARC, list hygiene, blocklist recovery |
