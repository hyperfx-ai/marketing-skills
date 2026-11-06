# Pinterest Ads: Campaign Creation

Read [discovery.md](discovery.md) first — the account audit and strategy confirmation must be complete.

## Phase 3: Campaign Structure

### Pinterest campaign hierarchy

```
Ad Account
└── Campaign (objective, budget for CBO)
    └── Ad Group (targeting, bidding, schedule)
        └── Ad (creative Pin + tracking)
```

### Campaign objectives

| Objective | Use case |
| --- | --- |
| `AWARENESS` | Brand visibility, impressions |
| `CONSIDERATION` | Traffic, engagement |
| `VIDEO_VIEW` | Video completion |
| `WEB_CONVERSION` | Purchases, signups, leads |
| `CATALOG_SALES` | Shopping / product catalog |
| `WEB_SESSIONS` | Website visits |

### CBO vs Non-CBO

| Setting | CBO campaign | Non-CBO campaign |
| --- | --- | --- |
| Budget location | Campaign level (`daily_spend_cap` or `lifetime_spend_cap`) | Ad group level (`budget_in_micro_currency`) |
| `is_campaign_budget_optimization` | `true` | `false` |
| Ad group budget | Managed by Pinterest | Set per ad group |

## Phase 4: Campaign Creation

### 1. Create campaign

```python
pinterest_ads_campaigns_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="Spring Collection 2026",
    objective_type="WEB_CONVERSION",
    status="PAUSED",
    daily_spend_cap=50000000,
    is_campaign_budget_optimization=true,
    is_flexible_daily_budgets=true,
)
```

**Parameter requirements:**

- `is_flexible_daily_budgets=true` → requires `is_campaign_budget_optimization=true`.
- `lifetime_spend_cap` → requires `end_time`.
- All spend caps in microcurrency.

### 2. Create ad group

> **CRITICAL**: This tool sends a direct REST call to the Pinterest API v5 (bypassing SDK models). Pass parameter values exactly as documented — strings as strings, integers as integers.

> **CRITICAL**: Ad-group parameters depend heavily on the parent campaign's `objective_type`. Follow the objective-specific templates below exactly.

**`billable_event` values:** `CLICKTHROUGH`, `IMPRESSION`, `VIDEO_V_50_MRC`.

#### Objective / `billable_event` compatibility

| Campaign `objective_type` | Required `billable_event` | `bid_in_micro_currency` | `optimization_goal_metadata` |
| --- | --- | --- | --- |
| `AWARENESS` | `IMPRESSION` | REQUIRED (integer) | Not needed |
| `CONSIDERATION` | `CLICKTHROUGH` | REQUIRED (integer) | Not needed |
| `VIDEO_VIEW` | `VIDEO_V_50_MRC` | Optional | Not needed |
| `WEB_CONVERSION` | `IMPRESSION` | Optional | **REQUIRED** |
| `CATALOG_SALES` | `CLICKTHROUGH` | REQUIRED (integer) | Not needed |
| `WEB_SESSIONS` | `CLICKTHROUGH` | Optional | Not needed |

#### Template: CONSIDERATION campaign (simplest, non-CBO)

```python
pinterest_ads_ad_groups_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="US Women 25-54",
    campaign_id="<CAMPAIGN_ID>",
    billable_event="CLICKTHROUGH",
    bid_in_micro_currency=1000000,
    budget_in_micro_currency=10000000,
    targeting_spec={"LOCATION": ["US"], "GENDER": ["female"], "MINIMUM_AGE": "25", "MAXIMUM_AGE": "54"},
    bid_strategy_type="AUTOMATIC_BID",
    status="PAUSED",
)
```

#### Template: CONSIDERATION campaign (CBO — no ad group budget)

```python
pinterest_ads_ad_groups_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="US Women 25-54",
    campaign_id="<CAMPAIGN_ID>",
    billable_event="CLICKTHROUGH",
    bid_in_micro_currency=1000000,
    targeting_spec={"LOCATION": ["US"], "GENDER": ["female"], "MINIMUM_AGE": "25", "MAXIMUM_AGE": "54"},
    bid_strategy_type="AUTOMATIC_BID",
    status="PAUSED",
)
```

#### Template: WEB_CONVERSION campaign (requires `optimization_goal_metadata`)

> **CRITICAL**: WEB_CONVERSION ad groups MUST use `billable_event="IMPRESSION"` (NOT `CLICKTHROUGH`). They MUST provide `optimization_goal_metadata` with the full nested structure shown below.

> **TYPE SAFETY**: `cpa_goal_value_in_micro_currency` MUST be a **string** (e.g., `"5000000"`), NOT an integer. `conversion_tag_id` MUST be a **string**. `attribution_windows` values MUST be **integers**.

```python
pinterest_ads_ad_groups_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="Conversion - Checkout",
    campaign_id="<CAMPAIGN_ID>",
    billable_event="IMPRESSION",
    targeting_spec={"LOCATION": ["US"]},
    bid_strategy_type="AUTOMATIC_BID",
    status="PAUSED",
    optimization_goal_metadata={
        "conversion_tag_v3_goal_metadata": {
            "attribution_windows": {
                "click_window_days": 30,
                "engagement_window_days": 30,
                "view_window_days": 1,
            },
            "conversion_event": "CHECKOUT",
            "conversion_tag_id": "<CONVERSION_TAG_ID>",
            "cpa_goal_value_in_micro_currency": "5000000",
            "is_roas_optimized": false,
        },
    },
)
```

**`conversion_event` values:** `PAGE_VISIT`, `SIGNUP`, `CHECKOUT`, `CUSTOM`, `VIEW_CATEGORY`, `SEARCH`, `ADD_TO_CART`, `WATCH_VIDEO`, `LEAD`, `APP_INSTALL`.

**`attribution_windows` — only these exact combos are accepted** (click / engage / view):

| `click_window_days` | `engagement_window_days` | `view_window_days` | Shorthand |
| --- | --- | --- | --- |
| 30 | 30 | 30 | 30/30/30 |
| 30 | 30 | 7 | 30/30/7 |
| 30 | 30 | 1 | 30/30/1 (default) |
| 7 | 7 | 7 | 7/7/7 |
| 7 | 7 | 1 | 7/7/1 |
| 7 | 0 | 0 | 7/0/0 |
| 1 | 1 | 1 | 1/1/1 |
| 1 | 0 | 0 | 1/0/0 |

> The tool auto-normalizes: if `attribution_windows` is missing or uses an invalid combo, it defaults to 30/30/1. It also auto-wraps in `conversion_tag_v3_goal_metadata` if the wrapper is missing, coerces `cpa_goal_value_in_micro_currency` to string, and defaults CPA to $10 if omitted.

**`cpa_goal_value_in_micro_currency`**: **STRING** (pattern `^[0-9]+$`). Set high enough to avoid "CPA goal value below bid floor" errors. Example: `"10000000"` = $10 CPA.

**Optional fields in `conversion_tag_v3_goal_metadata`:**

- `is_roas_optimized` (boolean) — set `true` only when `conversion_event="CHECKOUT"` AND `bid_strategy_type="AUTOMATIC_BID"`.
- `learning_mode_type` (string) — `"ACTIVE"` or `"NOT_ACTIVE"`. Omit if not needed.

#### Template: AWARENESS campaign

```python
pinterest_ads_ad_groups_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="Brand Awareness",
    campaign_id="<CAMPAIGN_ID>",
    billable_event="IMPRESSION",
    bid_in_micro_currency=2000000,
    targeting_spec={"LOCATION": ["US"]},
    bid_strategy_type="AUTOMATIC_BID",
    status="PAUSED",
)
```

#### Budget rules for ad groups

- **CBO campaigns**: Do NOT set `budget_in_micro_currency` on the ad group. Budget is controlled at the campaign level.
- **Non-CBO campaigns**: `budget_in_micro_currency` is REQUIRED at the ad group level.

**`bid_strategy_type` values:** `AUTOMATIC_BID`, `MAX_BID`, `TARGET_AVG`.

**`status`**: Always create with `status="PAUSED"` for review. Set to `"ACTIVE"` after user approval.

**`pacing_delivery_type`**: Optional. `"STANDARD"` (default) or `"ACCELERATED"`.

**`targeting_spec` keys** (all values are arrays of strings unless noted):

- `LOCATION` — ISO Alpha-2 country codes or US Nielsen DMA codes (e.g., `["US", "CA"]`, `["807"]`). **Required** (or use `GEO`).
- `GEO` — Region codes (e.g., `["BE-VOV"]`) or postal codes (e.g., `["US-94107"]`). Alternative to `LOCATION`.
- `GENDER` — `["male"]`, `["female"]`, or `["unknown"]`.
- `MINIMUM_AGE` — string `"18"` through `"65"` (use with `MAXIMUM_AGE`, not with `AGE_BUCKET`).
- `MAXIMUM_AGE` — string `"18"` through `"65"` or `"65+"` (use with `MINIMUM_AGE`).
- `AGE_BUCKET` — `["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]` (legacy, cannot combine with `MIN`/`MAX_AGE`).
- `INTEREST` — interest IDs from Pinterest taxonomy.
- `LOCALE` — ISO 639-1 language codes (e.g., `["en"]`).
- `APPTYPE` — `["android_mobile", "android_tablet", "ipad", "iphone", "web", "web_mobile"]`.
- `AUDIENCE_INCLUDE` — audience IDs to include.
- `AUDIENCE_EXCLUDE` — audience IDs to exclude.

### 3. Create ad

```python
pinterest_ads_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    ad_group_id="<AD_GROUP_ID>",
    creative_type="REGULAR",
    pin_id="<PIN_ID>",
    name="Spring Sale Ad",
    status="ACTIVE",
    destination_url="https://example.com/spring-sale",
)
```

**`creative_type` values:** `REGULAR`, `VIDEO`, `SHOPPING`, `CAROUSEL`, `MAX_VIDEO`, `SHOP_THE_PIN`, `IDEA`.
