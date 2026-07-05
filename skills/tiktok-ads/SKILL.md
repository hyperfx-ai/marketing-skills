---
name: tiktok-ads
description: Plan and create TikTok advertising campaigns end-to-end via the Hyper MCP, with strict parameter validation for objective-specific requirements. Use when the user wants to launch TikTok ads, set up TikTok traffic or reach campaigns, configure conversions or app-promotion campaigns, upload TikTok video creatives, or analyze TikTok ad performance. Also triggers on tiktok marketing, tiktok campaign, tiktok ppc, or tiktok ads manager.
icon: tiktok_ads
short_description: Plan and create TikTok Ads with objective-specific validation and reporting.
---

# TikTok Ads

Strategic guide for managing TikTok advertising campaigns. Research deeply, validate parameters carefully, and guide users through the platform's strict objective-specific requirements.

This skill is for **paid TikTok ads** (the TikTok Marketing API surface).

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **TikTok Marketing integration connected** (TikTok Ads Manager / Business Center) at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

If `tiktok_get_advertiser_accounts` is not in the tool list, stop and tell the user to enable Hyper MCP and connect TikTok Marketing.

## Out of scope — defer to other skills

- **Organic TikTok posting** (videos, photos, carousels — no ad spend) → [`tiktok`](../tiktok).
- **Creative generation** (ad copy, images) → [`ad-creative-generation`](../ad-creative-generation); video creatives → [`video-generation`](../video-generation).
- **Cross-platform campaign launches** → use this skill for TikTok, then invoke `meta-ads` / `google-ads` separately.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `tiktok_get_advertiser_accounts` | Discovery: list advertiser IDs available to the connected user. |
| `tiktok_get_campaigns`, `tiktok_create_campaign`, `tiktok_update_campaign`, `tiktok_update_campaign_status` | Campaign lifecycle. |
| `tiktok_get_adgroups`, `tiktok_create_adgroup`, `tiktok_update_adgroup`, `tiktok_update_adgroup_status` | Ad group lifecycle. |
| `tiktok_get_ads`, `tiktok_create_ad`, `tiktok_update_ad_status` | Ad lifecycle. Note: `tiktok_update_ad` does not exist in the MCP — ad content edits (creative, copy, URL) require the TikTok Ads Manager UI. Only status changes (enable / pause / delete) are available via MCP. |
| `tiktok_ad_video_upload`, `tiktok_ad_video_info`, `tiktok_ad_video_search` | Video creative upload + lookup. |
| `tiktok_report_integrated_get` | Performance reporting. |
| `tiktok_create_custom_audience`, `tiktok_list_custom_audiences`, `tiktok_create_lookalike_audience` | Audience management (optional). |

## Phase 1: Account Discovery

### Initial Setup
- Use `tiktok_get_advertiser_accounts()` to get advertiser IDs.
- If multiple accounts: ask the user to select one.
- If single account: inform the user and proceed.

### Bid Benchmarks (optional but recommended)

Before setting bid prices, call `tiktok_ad_benchmarks` to retrieve industry-specific CPM/CPC benchmarks. This prevents using placeholder values that may be too low to win auctions or too high for the user's budget.

```python
tiktok_ad_benchmarks(
    advertiser_id="123456789",
    dimensions=["industry"],
    filtering={"industry": "292801"}  # industry code from tiktok_get_advertiser_accounts
)
```

### Available Campaign Objectives

| Objective | Best For | Key Requirements |
| --- | --- | --- |
| `TRAFFIC` | Drive website visits | `promotion_type="WEBSITE"`, CPC billing |
| `CONVERSIONS` | Drive purchases / leads | Pixel ID, conversion event tracking |
| `REACH` | Brand awareness | Manual placement only, CPM billing, frequency cap |
| `APP_PROMOTION` | App installs | App ID, app store URL |
| `VIDEO_VIEW` | Video engagement | Video creative assets |

## Phase 2: Campaign Creation

### Step 1: Create Campaign

**Budget Requirements:**
- **MINIMUM $50** for campaign-level budgets (TikTok requirement).
- `budget_mode`: `BUDGET_MODE_INFINITE` (CBO), `BUDGET_MODE_DAY`, or `BUDGET_MODE_TOTAL`.

```python
tiktok_create_campaign(
    advertiser_id="123456789",
    campaign_name="Summer Sale 2026",
    objective_type="TRAFFIC",
    budget_mode="BUDGET_MODE_DAY",
    budget=50.0,  # MINIMUM $50/day
    operation_status="ENABLE"
)
```

### Step 2: Create Ad Group

**ALWAYS REQUIRED Parameters:**
- `advertiser_id`, `campaign_id`, `adgroup_name`.
- `location_ids` (e.g., `["6252001"]` for US).
- `schedule_type` and `schedule_start_time` (MUST be a future date).
- `billing_event` (`CPC`, `CPM`, `OCPM`).
- `budget_mode` (REQUIRED for ad groups).

**For TRAFFIC Campaigns:**
```python
tiktok_create_adgroup(
    advertiser_id="123456789",
    campaign_id="1234567890123456",
    adgroup_name="Website Traffic - Summer Sale",
    location_ids=["6252001"],  # US
    schedule_type="SCHEDULE_FROM_NOW",
    schedule_start_time="2026-06-01 00:00:00",  # FUTURE DATE
    billing_event="CPC",
    budget_mode="BUDGET_MODE_DAY",
    budget=30.0,
    promotion_type="WEBSITE",        # REQUIRED for TRAFFIC
    optimization_goal="CLICK",       # REQUIRED (correct spelling)
    bid_price=0.50,
    placement_type="PLACEMENT_TYPE_AUTOMATIC",
    operation_status="ENABLE"
)
```

**For REACH Campaigns:**
```python
tiktok_create_adgroup(
    advertiser_id="123456789",
    campaign_id="1234567890123456",
    adgroup_name="Brand Awareness US",
    location_ids=["6252001"],
    schedule_type="SCHEDULE_FROM_NOW",
    schedule_start_time="2026-06-01 00:00:00",
    billing_event="CPM",                       # REQUIRED for REACH
    budget_mode="BUDGET_MODE_DAY",
    budget=30.0,
    optimization_goal="REACH",
    placement_type="PLACEMENT_TYPE_NORMAL",    # REQUIRED — automatic NOT supported
    placements=["PLACEMENT_TIKTOK"],           # REQUIRED
    bid_price=2.0,                             # REQUIRED
    frequency=3,                               # REQUIRED
    frequency_schedule=7,                      # REQUIRED
    operation_status="ENABLE"
)
```

### Step 3: Upload Creative Assets

Upload one video per creative variant. Capture the returned `video_id` — you'll need it in Step 4.

```python
video_response = tiktok_ad_video_upload(
    advertiser_id="123456789",
    video_file=video_data,
    upload_type="UPLOAD_BY_FILE"
)
video_id = video_response["data"]["video_id"]
```

> Already-uploaded videos can be reused. Use `tiktok_ad_video_search` to find existing videos by name or `tiktok_ad_video_info` to fetch metadata for a known video ID.

### Step 4: Create the Ad

```python
tiktok_create_ad(
    advertiser_id="123456789",
    adgroup_id="1234567890123456",
    ad_name="Summer Sale - Hero Video",
    identity_type="CUSTOMIZED_USER",   # or "AUTH_CODE" for TikTok Account spark ads
    identity_id="<advertiser_identity_id>",
    ad_format="SINGLE_VIDEO",
    video_id=video_id,
    ad_text="Limited-time summer drop. Shop now.",
    landing_page_url="https://example.com/summer",
    call_to_action="SHOP_NOW",
    operation_status="DISABLE"        # create paused, enable after review
)
```

Always create ads paused (`operation_status="DISABLE"`) and only flip them to `ENABLE` once the user has reviewed.

## Critical Parameter Rules

### Common Errors & Solutions

| Error | Solution |
| --- | --- |
| Budget must be at least $50 | TikTok enforces a MINIMUM $50 for campaign budgets. |
| Start time in past | Use a future date in `schedule_start_time` and the **current** year. |
| TikTok API rejects `optimize_goal` in some contexts | Both `optimize_goal` and `optimization_goal` exist in the schema, but prefer `optimization_goal` — it is the field TikTok validates in most objective types. |
| Only supports manual placement | REACH requires `placement_type="PLACEMENT_TYPE_NORMAL"`. |
| Bid needs to be greater than $0 | Set `bid_price` > 0. |
| Please set frequency cap | REACH requires both `frequency` and `frequency_schedule`. |

### Parameter Dependencies

**TRAFFIC objective requires:**
- `promotion_type="WEBSITE"`.
- `optimization_goal="CLICK"`.
- `billing_event="CPC"`.
- `bid_price` > 0.

**REACH objective requires:**
- `optimization_goal="REACH"`.
- `billing_event="CPM"`.
- `placement_type="PLACEMENT_TYPE_NORMAL"`.
- `placements` array (e.g., `["PLACEMENT_TIKTOK"]`).
- `bid_price` > 0.
- `frequency` and `frequency_schedule`.

**CONVERSIONS objective requires:**
- A connected TikTok Pixel and a configured conversion event.
- `optimization_goal="CONVERT"` (or `VALUE` for value-based).
- `billing_event="OCPM"`.
- `pixel_id` and `external_action` set on the ad group.

## Reporting

```python
tiktok_report_integrated_get(
    advertiser_id="123456789",
    report_type="BASIC",
    data_level="AUCTION_AD",
    dimensions=["ad_id"],   # ID-based only — NOT names
    start_date="2026-04-01",
    end_date="2026-04-30",
    metrics=["impressions", "clicks", "ctr", "spend", "cpc", "cpm"],
    page_size=20
)
```

**Reporting Rules:**
- With the `stat_time_day` dimension: maximum 30-day range per call.
- Use ID-based dimensions only (`ad_id`, `campaign_id`, `adgroup_id` — not names).
- Conversion metrics (`conversion`, `cost_per_conversion`, `conversion_rate`, etc.) require a connected pixel and a configured conversion event.
- `data_level` must match the dimension granularity: `AUCTION_AD` with `ad_id`, `AUCTION_ADGROUP` with `adgroup_id`, `AUCTION_CAMPAIGN` with `campaign_id`.

## Safety Rules

**Never:**
- Set ad group budgets below $20/day without warning the user.
- Schedule a campaign with a past `schedule_start_time` (TikTok rejects this with a confusing error).
- Mix REACH ad groups with `PLACEMENT_TYPE_AUTOMATIC` — it will silently fail validation.
- Create ads with `operation_status="ENABLE"` before the user has reviewed creative + targeting.
- Run reports with name-based dimensions — TikTok only accepts ID dimensions.
