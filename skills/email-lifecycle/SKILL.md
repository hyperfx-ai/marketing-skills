---
name: email-lifecycle
description: Plan, build, and run lifecycle email programs through the Hyper MCP — welcome / onboarding, nurture, re-engagement, win-back, and abandoned-cart sequences across whichever provider fits (Klaviyo for ecommerce, Resend for SaaS / dev tools, Beehiiv for newsletters, Gmail for low-volume ops). Use when the user wants to build an email sequence, set up a welcome flow, recover lapsed users, send a broadcast, manage a list / audience / segment, or asks about lifecycle / drip / nurture campaigns.
icon: klaviyo
short_description: Welcome, nurture, win-back, and cart sequences across Klaviyo, Resend, Beehiiv, and Gmail.
---

# Email Lifecycle

End-to-end lifecycle email — pick the right provider for the job, build the audience, draft the sequence, launch, and measure. Cross-provider patterns at the top; provider-specific tool calls below.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Cold outbound to people who haven't opted in | `cold-email-outreach` |
| Generating images for email creatives | `image-generation` |
| Generating ad creatives that run alongside the lifecycle program | `ad-creative-generation` |
| SEO research / blog content for the newsletter | `seo-research` |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **At least one of these providers** connected at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations):
  - **Klaviyo** — ecommerce, Shopify-heavy lists, behavioral triggers off purchase / browse data
  - **Resend** — product-led / SaaS / dev tools, transactional + lifecycle on the same domain
  - **Beehiiv** — newsletters, paid-tier subscriptions, content-driven lists
  - **Gmail** — small / personal lists, founder-mode broadcasts, ops emails

If none of those tool prefixes (`klaviyo_*`, `resend_*`, `beehiiv_*`, `gmail_*`) appear in the agent's tool list, stop and tell the user to enable the Hyper MCP and connect the provider they intend to use.

## Provider selection

The wrong provider is the most common reason a lifecycle program fails. Pick first.

| You are… | Use | Why |
| --- | --- | --- |
| An ecommerce / DTC brand on Shopify, BigCommerce, WooCommerce | **Klaviyo** | Native ecom event listeners (Placed Order, Started Checkout, Browsed Product), mature flow editor, tight Shopify sync. |
| A SaaS / dev tool / API product sending product + lifecycle on the same domain | **Resend** | Same API for transactional + marketing, audience management, broadcasts, automation runs. Excellent deliverability for product mail. |
| Running a content-led newsletter (free + paid tiers) | **Beehiiv** | Built around the newsletter-as-product model — segments, automations, paid tiers, referral program, post stats. |
| Running a small ops list (≤500 contacts), founder-mode broadcasts | **Gmail** | Zero new infra, label-based segmentation, easy templating. Don't scale beyond ~500 — see [`cold-email-outreach`](../cold-email-outreach) for sender deliverability if you do. |

You can run more than one. The pattern is: Klaviyo for marketing, Resend for transactional + product onboarding (when the brand also runs ecom). Or Beehiiv for the newsletter and Resend for the product. Decide once per program, not per email.

## Tool surface

| Phase | Klaviyo | Resend | Beehiiv | Gmail |
| --- | --- | --- | --- | --- |
| Audience setup | `klaviyo_create_list`, `klaviyo_add_member_to_list`, `klaviyo_create_segment`, `klaviyo_create_profile`, `klaviyo_update_profile` | `resend_create_audience`, `resend_create_contact`, `resend_list_contacts`, `resend_update_contact` | `beehiiv_create_subscription`, `beehiiv_create_segment`, `beehiiv_add_tags`, `beehiiv_list_subscriptions` | `gmail_labels_create`, `gmail_labels_add`, `gmail_labels_remove` |
| Sequence build | `klaviyo_create_campaign`, `klaviyo_update_campaign_message` | `resend_create_automation`, `resend_update_automation`, `resend_get_automation` | `beehiiv_create_post`, `beehiiv_list_automations`, `beehiiv_add_to_automation` | `gmail_drafts_create`, `gmail_drafts_update` |
| Send / launch | `klaviyo_send_campaign`, `klaviyo_get_campaign_send_job` | `resend_send_email`, `resend_send_broadcast` | `beehiiv_create_post` (publish), `beehiiv_update_post` | `gmail_messages_send`, `gmail_drafts_send` |
| Measure | `klaviyo_get_metrics`, `klaviyo_get_metric`, `klaviyo_get_campaign` | `resend_list_automation_runs`, `resend_get_automation_run` | `beehiiv_get_post_stats`, `beehiiv_get_subscription` | `gmail_messages_list` |

Full per-provider mechanics, gotchas, and concrete tool-call examples in [`references/provider-mechanics.md`](./references/provider-mechanics.md).

## Critical rules

1. **Pick the provider before writing copy.** The mechanics of how a flow gets triggered, how a segment gets defined, and what data you can personalize against differ enough that "we'll figure out the provider later" wastes a day.
2. **Always start with the audience, not the email.** A welcome flow with no opt-in source is unsendable. A win-back with no inactivity definition is unsendable. Define the audience first; the copy is downstream.
3. **One purpose per sequence.** A "welcome + onboarding + product education + first purchase nudge" mega-flow is brittle and impossible to measure. Split into separate flows wired together.
4. **Honor unsubscribes globally, not per-list.** When a profile unsubscribes, suppress them across every flow in the workspace — not just the one they unsubscribed from. All four providers expose this; it's not optional.
5. **Test sends with a real seed inbox before going live.** Every provider supports a test send. Do not launch a 10-email sequence to a 50,000-person list without seeing every email render in Gmail / Outlook / Apple Mail / mobile.
6. **Stay under provider rate limits.** Especially for `resend_send_broadcast` (large blast → throttled), `gmail_messages_send` (~500/day soft cap), and `klaviyo_send_campaign` (account-tier dependent).
7. **Track conversion metric, not opens.** Apple Mail Privacy Protection makes open rates ~useless on iOS. Configure conversion events at the provider level (Klaviyo metrics, Resend automation completion, Beehiiv segment transitions) and report on those.

## Workflow

### Phase 1 — Define the lifecycle program

Get the user to commit to:

1. **Trigger** — The event that puts a profile into this flow. Examples: "signed up for the newsletter", "made first purchase", "abandoned cart with > $50 value", "no order in 90 days".
2. **Audience filter** — Beyond the trigger, who qualifies. ("Newsletter signup, but only US-based". "Abandoned cart, but only first-time visitors.")
3. **Goal** — One concrete outcome the flow drives toward. Not "engage them more". Concrete: "first purchase within 14 days", "activate the integration within 7 days", "upgrade to paid within 30 days".
4. **Success metric** — Conversion rate to goal. Open and click are diagnostic, not goal metrics.
5. **Suppression rules** — Who should *never* get this flow even if they hit the trigger. (Existing customers shouldn't get the new-customer welcome. Recent purchasers shouldn't get the win-back.)

If the user can't answer the trigger or the goal, the flow isn't ready to build.

### Phase 2 — Pick the sequence pattern

Five patterns cover ~95% of lifecycle work. See [`references/sequence-patterns.md`](./references/sequence-patterns.md) for full templates with copy, timing, and provider-specific notes.

| Pattern | Trigger | Typical length | Goal |
| --- | --- | --- | --- |
| **Welcome / onboarding** | List signup | 3–5 emails over 7–10 days | First conversion (purchase, activation, paid signup) |
| **Nurture** | Lead magnet download, content opt-in | 4–7 emails over 3–6 weeks | Product-qualified action |
| **Abandoned cart** *(ecom only)* | Started Checkout, no Placed Order | 2–3 emails over 24–72 hours | Complete the purchase |
| **Re-engagement** | Lapsed activity (e.g., no opens in 60d, no purchase in 90d) | 2–3 emails over 7–14 days | Re-open / re-engage |
| **Win-back** | Lapsed customer (no purchase in 180d+) | 2–3 emails over 14–21 days | Repeat purchase |

### Phase 3 — Build the audience

Audience setup is provider-specific. Examples for the most common case (welcome flow):

**Klaviyo** — create the list, then a flow trigger on "Subscribed to List":

```
klaviyo_create_list(list_name="newsletter-2026")
# triggers + flows are configured in Klaviyo UI; the API surface here is
# for adding profiles, building segments, and sending one-off campaigns.
```

**Resend** — create an audience, then an automation triggered by `contact.created`:

```
resend_create_audience(name="newsletter-2026")
resend_create_automation(
  name="welcome-2026",
  trigger="contact.created",
  audience_id="aud_...",
  ...
)
```

**Beehiiv** — subscriptions trigger automations directly when added to a segment / publication:

```
beehiiv_create_subscription(
  publication_id="pub_...",
  email="user@example.com",
  utm_source="signup-form",
)
beehiiv_add_to_automation(
  automation_id="aut_...",
  subscription_id="sub_...",
)
```

**Gmail** — labels are the segment. Start with a label per program:

```
gmail_labels_create(name="lifecycle/welcome-2026")
# manual contact list maintained outside Gmail (Sheets, CSV) — Gmail
# is best for ≤500 contacts, founder-led sends.
```

Provider-specific gotchas (e.g., Klaviyo's profile-merging behavior, Resend's audience-vs-segment distinction) are in [`references/provider-mechanics.md`](./references/provider-mechanics.md).

### Phase 4 — Draft the sequence

For each email in the sequence:

1. **Subject + preview text** — Lifecycle subject lines should look like 1:1 mail when possible (lowercase, short). Different rules than cold email — a welcome from a brand the user just opted into can be slightly more branded.
2. **Body** — One job per email. Welcome touch 1 = "thanks, here's what to expect"; touch 2 = "here's the one thing to do first"; touch 3 = "here's the proof / case study".
3. **CTA** — One per email. Same rules as cold email — interest-based or single-action.
4. **Personalization tokens** — Use whatever the provider exposes (`{{first_name}}`, `{{event.product_name}}`, `{{custom_field.plan_tier}}`). Never use a token without a fallback (`{{first_name|"there"}}`).

Drafts-first by default — for any new sequence, build the first email and *test send it to yourself before moving on*. Provider previews look correct in the editor and broken in production more often than not.

### Phase 5 — Launch

1. **Test send to a seed inbox.** Every provider supports it. Use it for every email before activation.
2. **Activate the flow.** Klaviyo: set status to Live. Resend: enable the automation. Beehiiv: publish the post / set automation to active. Gmail: just send.
3. **Set a 7-day check-in.** Most lifecycle issues (broken token, wrong audience filter, send-time-pacing surprise) show up in the first week. Pull metrics on day 7 and again on day 30.

### Phase 6 — Measure & iterate

Pull the *conversion to goal* metric, not opens or clicks. Open rate post-MPP is noise.

| Provider | Conversion metric source |
| --- | --- |
| Klaviyo | `klaviyo_get_metric(metric_id=<conversion-event>)` — e.g., Placed Order attributed to the flow |
| Resend | `resend_list_automation_runs(automation_id=...)` — count completed runs that hit the goal step |
| Beehiiv | `beehiiv_get_post_stats(post_id=...)` and segment-membership transitions |
| Gmail | `gmail_messages_list(query="label:lifecycle/<program> newer_than:30d")` — look for replies / conversions |

Iteration rule: don't tune copy until the audience is right. If the welcome flow has a 1.2% conversion and the same product organic conversion is 4%, the audience is misaligned (too broad, wrong source, suppression rules missing) — fix that first. Copy comes second.

## Quality check (before launch)

Read the whole sequence end-to-end as if you're a single person receiving it over the planned timing. Reject any sequence that fails:

- The 5-email arc tells *one* coherent story.
- Each email could stand alone if the previous ones bounced.
- Every CTA leads somewhere that still works (no broken links, no canceled offers).
- The unsubscribe link is visible (provider auto-adds, but verify in test send).
- Tokens have fallbacks. No `Hi ,` after a missing first-name.
- Subject lines are different across the sequence — same subject 5x reads as a system glitch.
- The send time isn't 3am in the recipient's time zone.

## Reference workflows

| Reference | When to read |
| --- | --- |
| [`references/sequence-patterns.md`](./references/sequence-patterns.md) | Building a welcome / nurture / abandoned-cart / re-engagement / win-back sequence — full templates with copy, timing, and benchmarks |
| [`references/provider-mechanics.md`](./references/provider-mechanics.md) | Klaviyo flows, Resend automations, Beehiiv segments — concrete tool-call patterns and provider-specific gotchas |
