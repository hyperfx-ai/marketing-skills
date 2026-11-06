# GA4 Tracking Plan

A tracking plan is the contract between the product (what we instrument) and the analytics surface (what we report on). Build it *before* writing any GTM tags. Skipping this step is the #1 reason GA4 setups end up unusable six months in.

## What a tracking plan contains

For each event you intend to fire:

1. **Event name** — `snake_case`, verb-led (e.g., `purchase`, `start_checkout`, `play_video`).
2. **Trigger** — when the event fires. Be precise: "click on `[data-ev=cta-pricing]`" beats "user clicks a button."
3. **Parameters** — the data you ship with the event. Each parameter has a name, type, source, example value.
4. **Is it a key event (conversion)?** — yes / no.
5. **Where it's set up** — GTM tag name, or hardcoded in the codebase.
6. **Owner** — who's responsible if it breaks.

Anything missing from this list will burn the team later.

## Recommended event taxonomy

GA4 has [recommended events](https://support.google.com/analytics/answer/9267735) that get special treatment in the UI (auto-populated reports, predictive audiences). Use them where they fit; only invent custom events for things they don't cover.

### For all sites

| Event | When | Key event? |
| --- | --- | --- |
| `page_view` | Every page load (auto with GA4 base config) | No |
| `scroll` | 90% scroll depth (auto with enhanced measurement) | No |
| `click` | Outbound link click (auto with enhanced measurement) | No |
| `view_search_results` | Site search (auto with enhanced measurement) | No |
| `file_download` | PDF / docx / zip download (auto with enhanced measurement) | No |
| `form_submit` *(custom or auto)* | Form submitted | Often (lead form) |
| `sign_up` | Account creation completed | Yes |
| `login` | Returning user logs in | No |

### For ecommerce (use exactly these names — they unlock the GA4 Monetization reports)

| Event | When | Key event? |
| --- | --- | --- |
| `view_item_list` | Product list / collection page viewed | No |
| `view_item` | Product detail page viewed | No |
| `select_item` | Product clicked from a list | No |
| `add_to_cart` | Item added to cart | No |
| `view_cart` | Cart viewed | No |
| `begin_checkout` | Checkout started | Often |
| `add_payment_info` | Payment info added | No |
| `add_shipping_info` | Shipping info added | No |
| `purchase` | Order completed | **Yes** |
| `refund` | Order refunded (full or partial) | No |

For the ecom events, GA4 expects specific parameter names — `currency`, `value`, `items[]` with `item_id`, `item_name`, `price`, `quantity`. Off-spec parameters silently fall out of the Monetization reports.

### For SaaS / product-led

| Event | When | Key event? |
| --- | --- | --- |
| `sign_up` | Account created | Yes |
| `start_trial` | Free trial started | Yes |
| `complete_onboarding` | First-run setup finished | Yes (activation) |
| `feature_use_<name>` | Specific feature used (rate-limit to once per session) | Sometimes |
| `upgrade_plan` | Plan upgraded | **Yes** |
| `downgrade_plan` | Plan downgraded | No (but track) |
| `cancel_subscription` | Subscription canceled | No (but track) |

## Custom dimensions vs custom metrics vs event params

GA4 distinguishes:

- **Event parameters** — data attached to a single event. Available in the API as `event_params.<name>` in the BigQuery export.
- **User properties** — attached to a user, persist across sessions. Use for plan tier, signup cohort, account type.
- **Custom dimensions** — *register* an event parameter or user property as a dimension you can group by in GA4 reports. **Until you register it, you can't use it as a dimension in the GA4 UI or `run_ga4_report`.**
- **Custom metrics** — *register* a numeric event parameter as a metric you can sum / average. Same deal: unregistered = unreportable.

**Rule:** every parameter you want to *report on* must be registered as either a custom dimension (string) or custom metric (number). Register them ahead of the event firing — backfill doesn't happen for older data.

```
google_analytics_custom_dimensions_create(
  parent="properties/123456789",       # note: arg is "parent", not "property_id"
  parameter_name="plan_tier",          # the event param name
  display_name="Plan Tier",            # what shows in the UI
  scope="EVENT",                       # or "USER" for user properties
  description="Plan the user is on at time of event",
)

google_analytics_custom_metrics_create(
  parent="properties/123456789",       # note: arg is "parent", not "property_id"
  parameter_name="lesson_seconds",
  display_name="Lesson Duration (s)",
  measurement_unit="SECONDS",
  scope="EVENT",
)
```

GA4 limits: 50 custom event-scoped dimensions, 25 user-scoped, 50 custom metrics per property (standard tier). Use them sparingly — registered dimensions are forever (you can archive but not delete).

## Naming conventions

A consistent naming scheme is the single highest-leverage thing in a tracking plan. Pick one and enforce.

- **Events: `snake_case`, verb-led.** `add_to_cart`, not `addedToCart` or `Add to Cart`. Aligns with GA4 recommended events.
- **Parameters: `snake_case`, noun.** `item_id`, `plan_tier`, `referrer_path`. Avoid abbreviations.
- **Custom dimensions: human-readable display names.** "Plan Tier", "Signup Cohort". The display name is what shows in reports — `plan_tier` is fine for the param, "Plan Tier" is what the user sees.
- **Boolean params: prefix with `is_` or `has_`.** `is_returning_user`, `has_active_subscription`.
- **Don't use reserved names.** GA4 reserves `ga_session_id`, `_session_id`, `firebase_*`, etc. The list is in the GA4 docs.

## Mapping the plan to key events

Not every event is a conversion. Mark only the ones that map to *business outcomes*:

| Site type | Typical key events |
| --- | --- |
| Ecommerce | `purchase`, sometimes `begin_checkout` (for funnel midpoint reporting) |
| SaaS | `sign_up`, `start_trial`, `complete_onboarding`, `upgrade_plan` |
| Lead-gen / B2B | `form_submit` (with `form_id=demo-request`), `book_meeting` |
| Content / publisher | `subscribe_newsletter`, time-on-site engagement (custom) |

Mark with `google_analytics_key_events_create`:

```
google_analytics_key_events_create(
  parent="properties/123456789",     # note: arg is "parent", not "property_id"
  event_name="purchase",
  counting_method="ONCE_PER_EVENT",  # or ONCE_PER_SESSION
)
```

`counting_method` matters:
- `ONCE_PER_EVENT` — every fire counts. Use for purchases, form submits.
- `ONCE_PER_SESSION` — first fire in a session counts. Use for low-friction events like "viewed pricing page" you might mark as a soft conversion.

## Example tracking plan (excerpt — SaaS)

```
| Event              | Trigger                           | Params                                          | Key event? | Setup        | Owner |
|--------------------|-----------------------------------|-------------------------------------------------|-----------|--------------|-------|
| page_view          | Every page                        | page_path, page_title                           | No        | GA4 auto     | growth |
| sign_up            | After /api/users POST 201         | method (email|google), plan_tier_intent         | Yes       | GTM tag #14  | growth |
| start_trial        | After /api/billing/trials POST    | plan, trial_days                                | Yes       | GTM tag #15  | growth |
| complete_onboarding| After last onboarding step        | onboarding_seconds                              | Yes       | GTM tag #16  | product |
| upgrade_plan       | On Stripe webhook checkout.success| from_plan, to_plan, mrr_delta_cents             | Yes       | server-side  | finance |
| feature_use_export | On click of [data-ev=export-csv]  | report_type, row_count                          | No        | GTM tag #22  | product |
```

The "Setup" column tells the auditor *where to look* when something breaks. The "Owner" column tells you *who to ping*.

## Anti-patterns

- **One mega-event with 30 parameters.** Splits the data badly and hits GA4 param limits. Split into multiple events with focused param sets.
- **Same event name fired in multiple meanings.** `click` with no qualifying parameter is useless. Either name the events differently (`click_cta_hero`, `click_cta_pricing`) or attach a `cta_id` parameter.
- **Sending PII as parameters.** GA4 explicitly prohibits emails, phone numbers, full names. Hash or remove before sending.
- **Forgetting to register the dimension.** Param fires, never appears in the UI. Hours of confusion.
- **Renaming events after launch.** GA4 treats renamed events as new — old data won't merge. Pick names carefully the first time.

## What to do with this plan

1. **Review with engineering and product.** They have to fire the events; sign-off is non-negotiable.
2. **Implement in GTM first** for marketing-page events, **server-side** for billing / auth events.
3. **Register the custom dimensions and metrics in GA4** before any event ships.
4. **QA in GA4 DebugView** for the first week — every new event should show up there in real time.
5. **Document the plan somewhere durable** (Notion, Confluence, repo README) — the plan is the source of truth, not the GTM container.
