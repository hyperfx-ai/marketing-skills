# Provider Mechanics

Concrete tool-call patterns and gotchas per provider. Read the section that matches the provider you picked in Phase 1 of [`SKILL.md`](../SKILL.md). Cross-provider sequence design lives in [`sequence-patterns.md`](./sequence-patterns.md).

## Klaviyo

The richest surface for ecommerce. Klaviyo's mental model is **profiles → lists → segments → flows**. The Hyper MCP exposes ~50 Klaviyo tools; the ones you'll touch most:

| Job | Tool |
| --- | --- |
| Find / create a profile | `klaviyo_get_profiles`, `klaviyo_get_profile`, `klaviyo_create_profile`, `klaviyo_update_profile` |
| Manage lists | `klaviyo_get_lists`, `klaviyo_create_list`, `klaviyo_add_member_to_list`, `klaviyo_get_profiles_for_list` |
| Manage segments (dynamic audiences) | `klaviyo_get_segments`, `klaviyo_create_segment`, `klaviyo_update_segment`, `klaviyo_get_profiles_for_segment` |
| Build & send a campaign (one-off broadcast) | `klaviyo_create_campaign`, `klaviyo_update_campaign_message`, `klaviyo_send_campaign`, `klaviyo_get_campaign_send_job` |
| Pull conversion / metric data | `klaviyo_get_metrics`, `klaviyo_get_metric`, `klaviyo_get_custom_metrics`, `klaviyo_get_metrics_for_custom_metric` |
| Tagging | `klaviyo_get_tags`, `klaviyo_create_tag`, `klaviyo_tag_campaigns`, `klaviyo_tag_lists`, `klaviyo_tag_segments` |

### Concrete: build a one-off welcome campaign

```
# 1. Create the audience list
klaviyo_create_list(list_name="welcome-test-2026")

# 2. Add some test profiles
klaviyo_create_profile(
  profile={
    "email": "seed@yourdomain.com",
    "first_name": "Seed",
    "properties": {"signup_source": "test"},
  },
)
klaviyo_add_member_to_list(
  list_id="<list_id>",
  profile_ids=["<profile_id>"],
)

# 3. Build the campaign
klaviyo_create_campaign(
  name="welcome-2026-touch-1",
  included_audiences=["<list_id>"],
  send_strategy_method="immediate",
)

# 4. Update the message body / subject
klaviyo_update_campaign_message(
  campaign_message_id="<msg_id>",
  subject="you're in",
  preview_text="here's what to expect",
  body_html="<p>...</p>",
  ...
)

# 5. Send
klaviyo_send_campaign(campaign_id="<campaign_id>")

# 6. Poll the send job until it's complete
klaviyo_get_campaign_send_job(send_job_id="<send_job_id>")
```

For a multi-touch automated welcome **flow** (vs a one-off campaign), the flow itself is configured in Klaviyo's UI — the API surface here is for building audiences, sending one-off broadcasts, and querying metrics. The flow template + trigger + delays are set in Klaviyo and the API is for everything around them.

### Klaviyo gotchas

- **Profile merging.** Klaviyo merges profiles by email *and* by phone if both exist. A profile created with email `a@x.com` and a profile created with phone `+1-555-...` and later both updated with the other field will collapse into one profile. Don't depend on stable profile IDs across creation events.
- **Segment vs list.** Lists are *static memberships* — a profile is on a list because it was added. Segments are *dynamic queries* — membership recomputes whenever underlying properties change. Use lists for opt-in audiences; use segments for behavior-driven audiences ("opened at least one email in 30d", "purchased in last 90d").
- **Custom metrics for non-standard conversions.** If your conversion event isn't `Placed Order` or `Started Checkout`, custom metrics are created automatically from Klaviyo events — you can't create them via API. Use `klaviyo_get_custom_metrics` to list available custom metrics and `klaviyo_get_metrics_for_custom_metric` to pull attribution data from them.
- **Account tier limits.** Send rate is capped per Klaviyo plan — large blasts to large lists chunk over hours, not seconds. Check `klaviyo_get_campaign_send_job` instead of assuming "send_campaign returned, so it's done."
- **Tagging is the cheapest way to organize.** Use `klaviyo_create_tag` + `klaviyo_tag_campaigns` to group every email in a program (e.g., tag everything in the welcome program with `program:welcome-2026`) — makes pulling metrics across the program trivial.

## Resend

Newer surface. Resend's mental model is **contacts → audiences → automations + broadcasts**, with the *same API* serving transactional sends. Best fit for SaaS / dev tools where you want one mailing infrastructure for product mail and lifecycle.

| Job | Tool |
| --- | --- |
| One-off transactional send | `resend_send_email` |
| Manage audiences | `resend_create_audience`, `resend_list_audiences`, `resend_delete_audience` |
| Manage contacts | `resend_create_contact`, `resend_update_contact`, `resend_list_contacts` |
| Build / manage an automation (multi-touch lifecycle flow) | `resend_create_automation`, `resend_update_automation`, `resend_get_automation`, `resend_list_automations`, `resend_stop_automation`, `resend_delete_automation` |
| Inspect runs | `resend_list_automation_runs`, `resend_get_automation_run` |
| One-off marketing broadcast | `resend_send_broadcast` |

### Concrete: build an automated welcome sequence

```
# 1. Create the audience
resend_create_audience(name="newsletter-2026")

# 2. Create the automation
resend_create_automation(
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
resend_create_contact(
  audience_id="<audience_id>",
  email="user@example.com",
  first_name="User",
)

# 4. Inspect runs after a few days
resend_list_automation_runs(automation_id="<automation_id>")
```

### Resend gotchas

- **Audience vs segment.** Resend audiences are static membership lists, like Klaviyo lists. There's no native dynamic-segment concept — if you need a segment, maintain it externally (e.g., daily Cloud Run / cron pulling from your DB) and sync via `resend_update_contact` or `resend_create_contact` (idempotent on email).
- **Broadcasts are throttled.** A 100k-recipient broadcast does not send all in one minute — Resend paces it. Don't chain a `resend_send_broadcast` call into a "wait 60s and check inbox" workflow.
- **Domain verification.** Cold transactional + lifecycle on a fresh Resend account requires SPF + DKIM + DMARC on the sending domain (same as Gmail — see [`cold-email-outreach/references/deliverability.md`](../../cold-email-outreach/references/deliverability.md)). Verify in the Resend dashboard before launching.
- **Single API for transactional + marketing.** Powerful, but means a bug in your lifecycle flow can poison your transactional reputation. Use *separate sub-domains* for transactional (`mail.yourdomain.com`) and lifecycle (`updates.yourdomain.com`) — Resend supports both on one account.

## Beehiiv

Newsletter-first. Mental model: **publication → subscriptions → posts → automations**. Best when the product *is* the newsletter (paid tiers, referral, post stats are all first-class).

| Job | Tool |
| --- | --- |
| Get the publication | `beehiiv_list_publications`, `beehiiv_get_publication` |
| Manage subscriptions | `beehiiv_create_subscription`, `beehiiv_list_subscriptions`, `beehiiv_get_subscription`, `beehiiv_update_subscription`, `beehiiv_delete_subscription` |
| Tag subscribers | `beehiiv_add_tags` |
| Segments | `beehiiv_list_segments`, `beehiiv_create_segment`, `beehiiv_recalculate_segment`, `beehiiv_list_segment_subscribers` |
| Posts (the unit of content) | `beehiiv_list_posts`, `beehiiv_create_post`, `beehiiv_update_post`, `beehiiv_get_post`, `beehiiv_get_post_stats`, `beehiiv_delete_post` |
| Automations (multi-touch flows) | `beehiiv_list_automations`, `beehiiv_get_automation`, `beehiiv_add_to_automation`, `beehiiv_list_automation_journeys` |
| Custom fields | `beehiiv_list_custom_fields`, `beehiiv_create_custom_field`, `beehiiv_update_custom_field` |
| Paid tiers | `beehiiv_list_tiers`, `beehiiv_get_tier`, `beehiiv_create_tier`, `beehiiv_update_tier` |
| Referral program | `beehiiv_get_referral_program` |

### Concrete: add a new subscriber and put them in the welcome automation

```
# 1. Create the subscription (this is the opt-in signal)
beehiiv_create_subscription(
  publication_id="<pub_id>",
  email="user@example.com",
  utm_source="signup-form",
  utm_medium="organic",
  custom_fields={"signup_intent": "founder-mode"},
)

# 2. Put them into the welcome automation
beehiiv_add_to_automation(
  automation_id="<aut_id>",
  subscription_id="<sub_id>",
)

# 3. Tag them so you can segment later
beehiiv_add_tags(
  subscription_id="<sub_id>",
  tags=["welcome-2026", "founder-mode"],
)

# 4. Watch the automation journey
beehiiv_list_automation_journeys(automation_id="<aut_id>")
```

### Beehiiv gotchas

- **Posts are content, not flows.** A "post" is a newsletter issue. Multi-touch sequences are *automations*, not chained posts. Don't try to model a welcome flow as 5 sequential posts.
- **Segments need explicit recalculation.** Unlike Klaviyo's auto-recomputing segments, Beehiiv segments need `beehiiv_recalculate_segment` to refresh after underlying data changes. Build it into your weekly cadence.
- **Custom fields drive personalization.** If you want to personalize beyond `{{first_name}}`, define custom fields with `beehiiv_create_custom_field` *before* signing people up — backfilling is painful.
- **Paid tiers + referral = the value loop.** If you're running a paid newsletter, the referral program is doing more lifecycle work than your email sequences. Pull `beehiiv_get_referral_program` data into the conversion analysis.

## Gmail (small-list / founder-mode)

Best for under-500 lists where the value of every email is high enough to justify hand-curation. Once you cross 500 contacts, move to Klaviyo / Resend / Beehiiv — see [`cold-email-outreach/references/deliverability.md`](../../cold-email-outreach/references/deliverability.md) for why.

| Job | Tool |
| --- | --- |
| Maintain segment as a label | `gmail_labels_create`, `gmail_labels_add`, `gmail_labels_remove` |
| Draft / send | `gmail_drafts_create`, `gmail_drafts_update`, `gmail_messages_send`, `gmail_drafts_send`, `gmail_reply_to_message` |
| Find replies / engagement | `gmail_messages_list` *(accepts Gmail query syntax)*, `gmail_get_message` |

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
