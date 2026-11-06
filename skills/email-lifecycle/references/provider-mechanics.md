# Provider Mechanics

Concrete tool-call patterns and gotchas per provider. Read the section that matches the provider you picked in Phase 1 of [`SKILL.md`](../SKILL.md). Cross-provider sequence design lives in [`sequence-patterns.md`](./sequence-patterns.md).

## Klaviyo

The richest surface for ecommerce. Klaviyo's mental model is **profiles → lists → segments → flows**. The Hyper MCP exposes ~50 Klaviyo tools; the ones you'll touch most:

| Job | Tool |
| --- | --- |
| Find / create a profile | `klaviyo_profiles_list`, `klaviyo_profiles_get`, `klaviyo_profiles_create`, `klaviyo_profiles_update` |
| Manage lists | `klaviyo_lists_list`, `klaviyo_lists_create`, `klaviyo_list_members_add`, `klaviyo_lists_profiles_list` |
| Manage segments (dynamic audiences) | `klaviyo_segments_list`, `klaviyo_segments_create`, `klaviyo_segments_update`, `klaviyo_segments_profiles_list` |
| Build & send a campaign (one-off broadcast) | `klaviyo_campaigns_create`, `klaviyo_campaign_messages_update`, `klaviyo_campaigns_send`, `klaviyo_campaign_send_jobs_get` |
| Pull conversion / metric data | `klaviyo_metrics_list`, `klaviyo_metrics_get`, `klaviyo_custom_metrics_list`, `klaviyo_custom_metric_metrics_list` |
| Tagging | `klaviyo_tags_list`, `klaviyo_tags_create`, `klaviyo_campaign_tags_add`, `klaviyo_lists_tags_add`, `klaviyo_segments_tags_add` |

### Concrete: build a one-off welcome campaign

```
# 1. Create the audience list
klaviyo_lists_create(list_name="welcome-test-2026")

# 2. Add some test profiles
klaviyo_profiles_create(
  profile={
    "email": "seed@yourdomain.com",
    "first_name": "Seed",
    "properties": {"signup_source": "test"},
  },
)
klaviyo_list_members_add(
  list_id="<list_id>",
  profile_ids=["<profile_id>"],
)

# 3. Build the campaign
klaviyo_campaigns_create(
  name="welcome-2026-touch-1",
  included_audiences=["<list_id>"],
  send_strategy_method="immediate",
)

# 4. Update the message body / subject
klaviyo_campaign_messages_update(
  campaign_message_id="<msg_id>",
  subject="you're in",
  preview_text="here's what to expect",
  body_html="<p>...</p>",
  ...
)

# 5. Send
klaviyo_campaigns_send(campaign_id="<campaign_id>")

# 6. Poll the send job until it's complete
klaviyo_campaign_send_jobs_get(send_job_id="<send_job_id>")
```

For a multi-touch automated welcome **flow** (vs a one-off campaign), the flow itself is configured in Klaviyo's UI — the API surface here is for building audiences, sending one-off broadcasts, and querying metrics. The flow template + trigger + delays are set in Klaviyo and the API is for everything around them.

### Klaviyo gotchas

- **Profile merging.** Klaviyo merges profiles by email *and* by phone if both exist. A profile created with email `a@x.com` and a profile created with phone `+1-555-...` and later both updated with the other field will collapse into one profile. Don't depend on stable profile IDs across creation events.
- **Segment vs list.** Lists are *static memberships* — a profile is on a list because it was added. Segments are *dynamic queries* — membership recomputes whenever underlying properties change. Use lists for opt-in audiences; use segments for behavior-driven audiences ("opened at least one email in 30d", "purchased in last 90d").
- **Custom metrics for non-standard conversions.** If your conversion event isn't `Placed Order` or `Started Checkout`, custom metrics are created automatically from Klaviyo events — you can't create them via API. Use `klaviyo_custom_metrics_list` to list available custom metrics and `klaviyo_custom_metric_metrics_list` to pull attribution data from them.
- **Account tier limits.** Send rate is capped per Klaviyo plan — large blasts to large lists chunk over hours, not seconds. Check `klaviyo_campaign_send_jobs_get` instead of assuming "send_campaign returned, so it's done."
- **Tagging is the cheapest way to organize.** Use `klaviyo_tags_create` + `klaviyo_campaign_tags_add` to group every email in a program (e.g., tag everything in the welcome program with `program:welcome-2026`) — makes pulling metrics across the program trivial.

## Resend

Newer surface. Resend's mental model is **contacts → audiences → automations + broadcasts**, with the *same API* serving transactional sends. Best fit for SaaS / dev tools where you want one mailing infrastructure for product mail and lifecycle.

| Job | Tool |
| --- | --- |
| One-off transactional send | `resend_emails_send` |
| Manage audiences | `resend_audiences_create`, `resend_audiences_list`, `resend_audiences_delete` |
| Manage contacts | `resend_contacts_create`, `resend_contacts_update`, `resend_contacts_list` |
| Build / manage an automation (multi-touch lifecycle flow) | `resend_automations_create`, `resend_automations_update`, `resend_automations_get`, `resend_automations_list`, `resend_automations_stop`, `resend_automations_delete` |
| Inspect runs | `resend_automation_runs_list`, `resend_automation_runs_get` |
| One-off marketing broadcast | `resend_broadcasts_send` |

### Concrete: build an automated welcome sequence

```
# 1. Create the audience
resend_audiences_create(name="newsletter-2026")

# 2. Create the automation
resend_automations_create(
  name="welcome-2026",
  audience_id="<audience_id>",
  trigger="contact.created",
  steps=[
    {"type": "email", "wait": "0", "subject": "you're in", "html": "..."},
    {"type": "wait", "duration": "2d"},
    {"type": "email", "subject": "start with this", "html": "..."},
    {"type": "wait", "duration": "3d"},
    {"type": "email", "subject": "here's how Notion did it", "html": "..."},
  ],
)

# 3. Add a contact (this triggers the automation)
resend_contacts_create(
  audience_id="<audience_id>",
  email="user@example.com",
  first_name="User",
)

# 4. Inspect runs after a few days
resend_automation_runs_list(automation_id="<automation_id>")
```

### Resend gotchas

- **Audience vs segment.** Resend audiences are static membership lists, like Klaviyo lists. There's no native dynamic-segment concept — if you need a segment, maintain it externally (e.g., daily Cloud Run / cron pulling from your DB) and sync via `resend_contacts_update` or `resend_contacts_create` (idempotent on email).
- **Broadcasts are throttled.** A 100k-recipient broadcast does not send all in one minute — Resend paces it. Don't chain a `resend_broadcasts_send` call into a "wait 60s and check inbox" workflow.
- **Domain verification.** Cold transactional + lifecycle on a fresh Resend account requires SPF + DKIM + DMARC on the sending domain (same as Gmail — see [`cold-email-outreach/references/deliverability.md`](../../cold-email-outreach/references/deliverability.md)). Verify in the Resend dashboard before launching.
- **Single API for transactional + marketing.** Powerful, but means a bug in your lifecycle flow can poison your transactional reputation. Use *separate sub-domains* for transactional (`mail.yourdomain.com`) and lifecycle (`updates.yourdomain.com`) — Resend supports both on one account.

## Beehiiv

Newsletter-first. Mental model: **publication → subscriptions → posts → automations**. Best when the product *is* the newsletter (paid tiers, referral, post stats are all first-class).

| Job | Tool |
| --- | --- |
| Get the publication | `beehiiv_publications_list`, `beehiiv_publications_get` |
| Manage subscriptions | `beehiiv_subscriptions_create`, `beehiiv_subscriptions_list`, `beehiiv_subscriptions_get`, `beehiiv_subscriptions_update`, `beehiiv_subscriptions_delete` |
| Tag subscribers | `beehiiv_tags_add` |
| Segments | `beehiiv_segments_list`, `beehiiv_segments_create`, `beehiiv_segments_recalculate`, `beehiiv_segment_subscribers_list` |
| Posts (the unit of content) | `beehiiv_posts_list`, `beehiiv_posts_create`, `beehiiv_posts_update`, `beehiiv_posts_get`, `beehiiv_posts_stats_get`, `beehiiv_posts_delete` |
| Automations (multi-touch flows) | `beehiiv_automations_list`, `beehiiv_automations_get`, `beehiiv_automations_subscribers_add`, `beehiiv_automation_journeys_list` |
| Custom fields | `beehiiv_custom_fields_list`, `beehiiv_custom_fields_create`, `beehiiv_custom_fields_update` |
| Paid tiers | `beehiiv_tiers_list`, `beehiiv_tiers_get`, `beehiiv_tiers_create`, `beehiiv_tiers_update` |
| Referral program | `beehiiv_referral_programs_get` |

### Concrete: add a new subscriber and put them in the welcome automation

```
# 1. Create the subscription (this is the opt-in signal)
beehiiv_subscriptions_create(
  publication_id="<pub_id>",
  email="user@example.com",
  utm_source="signup-form",
  utm_medium="organic",
  custom_fields={"signup_intent": "founder-mode"},
)

# 2. Put them into the welcome automation
beehiiv_automations_subscribers_add(
  automation_id="<aut_id>",
  subscription_id="<sub_id>",
)

# 3. Tag them so you can segment later
beehiiv_tags_add(
  subscription_id="<sub_id>",
  tags=["welcome-2026", "founder-mode"],
)

# 4. Watch the automation journey
beehiiv_automation_journeys_list(automation_id="<aut_id>")
```

### Beehiiv gotchas

- **Posts are content, not flows.** A "post" is a newsletter issue. Multi-touch sequences are *automations*, not chained posts. Don't try to model a welcome flow as 5 sequential posts.
- **Segments need explicit recalculation.** Unlike Klaviyo's auto-recomputing segments, Beehiiv segments need `beehiiv_segments_recalculate` to refresh after underlying data changes. Build it into your weekly cadence.
- **Custom fields drive personalization.** If you want to personalize beyond `{{first_name}}`, define custom fields with `beehiiv_custom_fields_create` *before* signing people up — backfilling is painful.
- **Paid tiers + referral = the value loop.** If you're running a paid newsletter, the referral program is doing more lifecycle work than your email sequences. Pull `beehiiv_referral_programs_get` data into the conversion analysis.

## Gmail (small-list / founder-mode)

Best for under-500 lists where the value of every email is high enough to justify hand-curation. Once you cross 500 contacts, move to Klaviyo / Resend / Beehiiv — see [`cold-email-outreach/references/deliverability.md`](../../cold-email-outreach/references/deliverability.md) for why.

| Job | Tool |
| --- | --- |
| Maintain segment as a label | `gmail_labels_create`, `gmail_labels_add`, `gmail_labels_remove` |
| Draft / send | `gmail_drafts_create`, `gmail_drafts_update`, `gmail_messages_send`, `gmail_drafts_send`, `gmail_messages_reply` |
| Find replies / engagement | `gmail_messages_list` *(accepts Gmail query syntax)*, `gmail_messages_get` |

### Concrete: send a 50-person founder broadcast

```
# 1. Make sure all recipients are tagged
gmail_labels_create(name="lifecycle/q3-investor-update")

# 2. Loop over recipients (maintained externally — Sheets, CSV, DB)
for email in recipient_list:
    result = gmail_messages_send(
      to=email,
      subject="Q3 update",
      body=render_personalized_body(email),
    )
    # Label each sent message (gmail_messages_send has no label_ids arg)
    gmail_labels_add(
      message_id=result["message_id"],
      label_ids=["<label_id_for_lifecycle/q3-investor-update>"],
    )

# 3. Pull replies a week later
gmail_messages_list(query="label:lifecycle/q3-investor-update is:unread newer_than:7d")
```

### Gmail gotchas

- **No native segmentation, no native flows.** All the lifecycle logic lives outside Gmail (in your code / agent). Gmail is purely the send + label + reply layer.
- **Personalization happens at send time.** No template engine — you build the body string per recipient before calling `gmail_messages_send`.
- **Same deliverability rules as cold email.** Even though these are warm contacts, going from 5 sends/day to 500 sends/day overnight will trip Gmail's heuristics. Pace it.
- **Labels are your only segment.** Use a hierarchical label scheme: `lifecycle/<program>` and `lifecycle/<program>/converted`, etc. Then `gmail_messages_list(query="label:lifecycle/<program> -label:lifecycle/<program>/converted")` gives you "still in the program."
