---
name: openai-ads
description: Manage OpenAI Ads campaigns end-to-end — auth, account discovery, image upload, chat_card creative, status flow, and insights — using the openai_ads toolkit. Use when the user wants to launch or manage ads inside ChatGPT, upload chat_card creatives, or pull OpenAI Ads insights.
use_cases:
  - Create OpenAI Ads campaigns, ad groups, and ads
  - Upload ad images and reference them in creatives
  - Manage status (active / paused / archived) at every level
  - Pull performance insights at account, campaign, ad group, and ad level
  - Refresh and inspect a cached snapshot of the account
triggers:
  - openai ads
  - openai advertiser
  - chatgpt ads
  - openai ad campaign
  - openai ad group
  - openai ad
  - chat card ad
  - openai ads insights
requires_toolkits:
  - openai_ads
suggested_toolkits:
  - hyper_database
  - sandbox
  - file_manager
---

# OpenAI Ads Campaigns

Strategic guide for managing the OpenAI Advertiser API. All operations go
through `https://api.ads.openai.com/v1`. One bearer API key is scoped to
exactly one ad account, so all "list ad accounts" patterns from other ad
platforms collapse into "fetch the connected account."

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **OpenAI Ads toolkit** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## Critical Rules

> **CRITICAL**: All money values on inputs are **integer micros**.
> $1.00 = 1_000_000 micros. $50/day = 50_000_000. The `daily_spend_limit_micros`
> minimum is `1_000_000` ($1). The ad group `max_bid_micros` is capped at
> `100_000_000` ($100). Insights responses use plain floats in account
> currency (NOT micros).

> **CRITICAL**: Always create campaigns, ad groups, and ads with
> `status="paused"`. Surface what was created to the user, then activate
> using the dedicated activate endpoint.

> **CRITICAL**: Ads have an extra `review_status` field set by OpenAI's
> review process. New ads enter `in_review`. They WILL NOT serve until
> `review_status="approved"` even if `status="active"`. Watch for
> `review_status="rejected"` and surface the reason to the user.

> **CRITICAL**: To create an ad you need a `file_id`. Always upload the
> image first via `openai_ads_upload_image`, then pass the returned
> `file_id` to `openai_ads_create_ad`. PNG, 1024x1024, ≤ 1 MB.

> **CRITICAL**: When updating an ad's creative, you must pass ALL FOUR
> fields together: `title`, `body`, `target_url`, `file_id`. Partial
> creative updates are not supported by the API.

> **CRITICAL**: One API key = one ad account. There is no "list ad accounts"
> endpoint. `openai_ads_get_ad_account` returns the single account this key
> is scoped to.

> **IMPORTANT**: The only creative type today is `chat_card`. The only
> billing event is `impression`. Don't try other values; they will be
> rejected.

> **IMPORTANT**: Limits are per-creative: `title` max 50 chars, `body` max
> 100 chars, `name` 3-1000 chars. Validate before calling.

## Phase 1: Account Discovery

Run these in parallel after connect:

```
openai_ads_get_ad_account()
openai_ads_list_campaigns(limit=100)
```

The connect-time context builder may have already populated a cached
snapshot. Prefer:

```
openai_ads_get_cache()
```

If `success=False` because the cache is empty, refresh once:

```
openai_ads_refresh_cache()
```

Note the account `id`, `currency_code`, `timezone`. Every subsequent
budget you propose should be in that currency expressed in micros.

## Phase 2: Plan & Confirm

Before creating anything, confirm with the user:

- Objective in plain language ("install Hyper", "downloads", "subscribe").
- Daily and/or lifetime budget in account currency.
- Target geos (`countries` is the simplest knob: ISO-2 codes like `["US", "GB"]`).
- Any geo exclusions.
- Headline (`title`, ≤ 50 chars), body (≤ 100 chars), click-through URL.
- One image asset (PNG, 1024x1024, ≤ 1 MB) — either a public URL or a base64 blob.
- Max bid in micros (`max_bid_micros` — start small, e.g. `2_000_000` = $2 CPM).
- Optional: `context_hints` — short natural-language phrases that describe
  when the ad should show. e.g. `["users asking about marketing automation"]`.

If anything is missing, ask. Do not invent budgets, geos, or copy.

## Phase 3: Build the Hierarchy

```
Ad Account (one per API key)
└── Campaign (budget, geo targeting, dates)
    └── Ad Group (max bid, billing event, context hints)
        └── Ad (chat_card creative, file_id, copy, target_url)
```

### 1. Create the Campaign (PAUSED)

```
openai_ads_create_campaign(
    name="Hyper - US Test",
    status="paused",
    daily_spend_limit_micros=50_000_000,           # $50/day
    targeting_country_codes=["US"],
    description="Initial pilot",
)
```

**Budget rules:**
- At least one of `daily_spend_limit_micros` or `lifetime_spend_limit_micros` must be set.
- Daily minimum is `1_000_000` ($1).
- If you set `start_time` / `end_time`, both are unix epoch seconds.

### 2. Create the Ad Group (PAUSED)

```
openai_ads_create_ad_group(
    campaign_id="CAMPAIGN_ID",
    name="US - Marketing Operators",
    status="paused",
    max_bid_micros=2_000_000,                      # $2 max bid
    context_hints=[
        "user is asking about ad automation",
        "user wants to scale paid acquisition",
    ],
)
```

`billing_event_type` defaults to `"impression"` — the only currently
supported value.

### 3. Upload the Image

```
openai_ads_upload_image(image_url="https://cdn.example.com/asset.png")
# OR
openai_ads_upload_image(
    image_base64=BASE64_BLOB,
    filename="card.png",
    content_type="image/png",
)
```

Capture the returned `file_id`.

### 4. Create the Ad (PAUSED)

```
openai_ads_create_ad(
    ad_group_id="AD_GROUP_ID",
    name="US - Marketing - Variant A",
    title="Run ads on autopilot",                   # ≤ 50 chars
    body="Hyper builds, ships, and optimizes ads for you.",  # ≤ 100 chars
    target_url="https://hyperfx.ai?utm_source=openai_ads",
    file_id=FILE_ID_FROM_UPLOAD,
    status="paused",
)
```

The response includes `review_status`. Surface it.

## Phase 4: Review and Activate

After the user reviews the paused tree:

```
openai_ads_activate_campaign(campaign_id=CID)
openai_ads_activate_ad_group(ad_group_id=AGID)
openai_ads_activate_ad(ad_id=AID)
```

Activation only takes effect at the ad level once `review_status="approved"`.
Poll `openai_ads_get_ad(ad_id=...)` if you need to confirm review state.

## Phase 5: Insights

Insights endpoints are server-aggregated. Pass:

- `time_granularity`: `"hour"`, `"day"`, `"week"`, `"month"`, `"all_time"`.
- `aggregation_level`: `"ad_account" | "campaign" | "ad_group" | "ad"`.
- `time_ranges`: list of inclusive ISO date ranges, e.g.
  `["2026-05-01..2026-05-07"]`.
- `fields`: list of metric + dimension keys, e.g.
  `["spend", "clicks", "impressions", "ctr", "cpc", "cpm", "campaign_id", "campaign_name"]`.
- `filters`: list of `key=value` strings, e.g. `["campaign_id=cmp_xxx"]`.
- `sort`: e.g. `["spend desc"]`.

Money values in insights responses are floats in the account currency
(NOT micros).

```
openai_ads_get_ad_account_insights(
    time_granularity="day",
    aggregation_level="campaign",
    time_ranges=["2026-05-01..2026-05-07"],
    fields=["spend","clicks","impressions","ctr","cpc","campaign_id","campaign_name"],
    sort=["spend desc"],
)
```

For a single campaign use `openai_ads_get_campaign_insights(campaign_id=...)`,
similar for ad groups and ads.

## Status Flow

`paused` ⇄ `active` → `archived` (irreversible) at every level
(campaign, ad group, ad). Use the dedicated tools — do not pass
status changes through `update_*`.

| Tool | Effect |
|---|---|
| `openai_ads_activate_*` | Sets status to `active` |
| `openai_ads_pause_*` | Sets status to `paused` |
| `openai_ads_archive_*` | Sets status to `archived` (final) |

Ads also have:
- `review_status="in_review"` (default) — not delivering yet.
- `review_status="approved"` — eligible to deliver.
- `review_status="rejected"` — needs a new creative.

## Cache Snapshot

The connect-time context builder writes a snapshot of the account into
`integration.toolkit_settings["openai_ads_cache"]`. Use:

- `openai_ads_get_cache()` for cheap read-only access (campaigns, ad groups, ads, account, last-7d insights).
- `openai_ads_refresh_cache()` to refresh it (account + campaigns + ad groups + ads + insights).

Refresh sparingly — once per session is plenty unless something feels stale.

## Pagination

All list endpoints use cursor pagination:

- `limit` (default 20, max 100).
- `after` / `before`: pass the previous response's `last_id` / `first_id`.
- `order`: `"asc"` | `"desc"`.

Responses include `has_more` — keep paging only when true and only when
you actually need everything.

## Health Check

After connecting, run `openai_ads_health_check()`. It returns:

```
{ "connected": true, "ad_account": {...} }
```

If `connected=false`, the API key is missing/invalid/expired. Tell the
user to regenerate from the Ads Manager (Settings → API).

## Safety Rules

**Never:**
- Pass dollar amounts directly. All money inputs are micros.
- Activate a campaign / ad group / ad without explicit user approval.
- Skip the image upload step — `openai_ads_create_ad` needs a real `file_id`.
- Update creative fields partially. Pass all four (`title`, `body`, `target_url`, `file_id`) together.
- Try a creative `type` other than `"chat_card"` or a `billing_event_type` other than `"impression"` — both are rejected.
- Assume an ad is delivering just because `status="active"`. Always check `review_status`.
- Treat `archive` as reversible. It's not.
- Promise paid traffic on a brand-new ad. New ads sit in `review_status="in_review"` until OpenAI approves them.
