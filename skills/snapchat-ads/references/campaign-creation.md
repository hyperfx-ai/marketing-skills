# Snapchat Ads: Campaign Structure & Creation

Read [discovery.md](discovery.md) first — org/account selection and assessment must be complete.

## Phase 3: Campaign Structure

### Hierarchy

```
Organization
└── Ad Account ── Creatives ── Media
    └── Campaign (objective, optional budget)
        └── Ad Squad (targeting, bid, budget, optimization_goal, placement)
            └── Ad (links a Creative)
```

### Build order

1. **Campaign** (`status="PAUSED"`)
2. **Media**: `create_media` (container) → `upload_media` (file)
3. **Creative**: `create_creative` using the uploaded `top_snap_media_id`
4. **Ad squad** under the campaign (requires funding source)
5. **Ad** under the ad squad, linking the `creative_id`

Assets (2–3) and the ad squad (4) are independent; the ad (5) needs both a `creative_id` and an `ad_squad_id`.

### Campaign objectives

Pass the classic `objective` string, or newer objectives via `extra={"objective_v2_properties": {"objective_v2_type": "..."}}`.

| `objective` | Use case |
| --- | --- |
| `BRAND_AWARENESS` | Reach / impressions |
| `ENGAGEMENT` | Engagement, story opens |
| `VIDEO_VIEW` | Video views |
| `WEB_VIEW` | Traffic |
| `WEB_CONVERSION` | Purchases, signups, leads (pixel) |
| `APP_INSTALL` / `APP_REENGAGEMENT` | App installs / re-engagement |
| `LEAD_GENERATION` | On-Snap lead forms |
| `CATALOG_SALES` | Dynamic product ads |

`objective_v2_type` values: `AWARENESS_AND_ENGAGEMENT`, `TRAFFIC`, `SALES`, `APP_PROMOTION`, `LEADS`.

## Phase 4: Campaign Creation

### 1. Create campaign

```python
snapchat_ads_create_campaign(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="Spring Launch 2026",
    objective="WEB_CONVERSION",
    status="PAUSED",
    start_time="2026-07-01T00:00:00-07:00",
    daily_budget_micro=50000000,   # $50.00/day, min $20
)
```

`buy_model` is `AUCTION` (default) or `RESERVED`. Use `daily_budget_micro` or `lifetime_spend_cap_micro`.

### 2. Upload media (two steps)

> **MEDIA SPECS — wrong specs cause creative error E2601** ("media cannot be used to create any creative type"). Top Snap image/video must be **1080×1920 px (9:16)**. Images: PNG/JPG, ≤ 5 MB. Video: MP4/MOV, 3–180 s. **If you generate the asset, generate it at 1080×1920.** Snapchat tags valid media with `media_usages` (e.g. `TOP_SNAP`); media with no usable usage is rejected at the creative step.

```python
snapchat_ads_create_media(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="Spring Hero Video",
    type="VIDEO",            # IMAGE | VIDEO | LENS_PACKAGE | PLAYABLE — must match the file
)
# PREFER file_id (a Hyper file id, e.g. a generated image/video). It is read
# straight from storage, so it works even when a public URL isn't reachable
# from the backend. Use file_url only for genuinely external assets.
snapchat_ads_upload_media(
    media_id="<MEDIA_ID>",
    file_id="<HYPER_FILE_ID>",   # or file_url="https://..."
)
```

`upload_media` auto-chunks files larger than 32 MB (up to 1 GB). Confirm the returned `media_status` is `READY` before creating a creative.

### 3. Create creative

```python
snapchat_ads_create_creative(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="Spring Hero Creative",
    type="WEB_VIEW",                  # SNAP_AD | WEB_VIEW | APP_INSTALL | DEEP_LINK | ...
    top_snap_media_id="<MEDIA_ID>",
    headline="Shop the Spring Drop",  # <= 34 chars (required)
    brand_name="Acme",                # <= 32 chars
    call_to_action="SHOP_NOW",
    web_view_properties={"url": "https://example.com/spring"},
)
```

> **`profile_properties` is required for ALL creative types on most accounts** (not just SNAP_AD): `profile_properties={"profile_id": "<PUBLIC_PROFILE_ID>"}`. If you don't have the public profile id, call `snapchat_ads_list_creatives` and copy `profile_properties.profile_id` from any existing creative. Without it, creation fails — previously silently, now with a clear error.

`call_to_action` is type-dependent (WEB_VIEW → `VIEW`/`SHOP_NOW`/`SIGN_UP`; APP_INSTALL → `INSTALL_NOW`/`DOWNLOAD`; DEEP_LINK → `OPEN_APP`/`PLAY`). WEB_VIEW needs `web_view_properties={"url": ...}`; APP_INSTALL/DEEP_LINK use `app_install_properties`/`deep_link_properties`.

### 4. Create ad squad

> **CRITICAL**: Required — `campaign_id`, `name`, `optimization_goal`, `targeting`, `billing_event="IMPRESSION"`, `bid_strategy`, a budget (`daily_budget_micro` OR `lifetime_budget_micro`), and `placement_v2`. `bid_micro` is required unless `bid_strategy="AUTO_BID"`.

```python
snapchat_ads_create_ad_squad(
    campaign_id="<CAMPAIGN_ID>",
    name="US Gen-Z 18-24",
    status="PAUSED",
    type="SNAP_ADS",                     # SNAP_ADS | LENS | FILTER
    optimization_goal="PIXEL_PURCHASE",
    billing_event="IMPRESSION",
    bid_strategy="LOWEST_COST_WITH_MAX_BID",
    bid_micro=3000000,                   # required for non-AUTO_BID
    daily_budget_micro=20000000,         # ad-squad min is $5 (5000000)
    placement_v2={"config": "AUTOMATIC"},
    # pixel_id="<PIXEL_ID>",             # required-ish for PIXEL_* goals
    targeting={
        "geos": [{"country_code": "us"}],
        "demographics": [{"min_age": 18, "max_age": 24}],
        "regulated_content": False,
    },
)
```

**`optimization_goal`:** `IMPRESSIONS`, `SWIPES`, `VIDEO_VIEWS`, `VIDEO_VIEWS_15_SEC`, `USES`, `STORY_OPENS`, `APP_INSTALLS`, `LANDING_PAGE_VIEW`, `LEAD_FORM_SUBMISSIONS`, `PIXEL_PAGE_VIEW`, `PIXEL_ADD_TO_CART`, `PIXEL_PURCHASE`, `PIXEL_SIGNUP`, `APP_ADD_TO_CART`, `APP_PURCHASE`, `APP_SIGNUP`, `APP_REENGAGE_OPEN`, `APP_REENGAGE_PURCHASE`.

**`bid_strategy`:** `AUTO_BID` (no `bid_micro`), `LOWEST_COST_WITH_MAX_BID` (`bid_micro` = max bid), `TARGET_COST` (`bid_micro` = target). `MIN_ROAS` is deprecated.

**`pacing_type`:** `STANDARD` (default) or `ACCELERATED`. **`placement_v2`:** `{"config": "AUTOMATIC"}` or `{"config": "CUSTOM", ...}`.

#### Targeting object

```python
targeting = {
    "regulated_content": False,
    "geos": [{"country_code": "us"}],                 # lowercase ISO country
    "demographics": [{"min_age": 18, "max_age": 34, "gender": "FEMALE"}],
    "interests": [{"category_id": ["<SCLS_ID>"]}],    # from snapchat_ads_search_targeting
    "devices": [{"os_type": "iOS"}],
}
```

#### Optional: forecast before launch

`snapchat_ads_estimate_ad_squad_outcomes` returns daily/weekly reach, conversion, and impression ranges for a proposed squad config — without creating anything. Useful to sanity-check budget/targeting before building:

```python
snapchat_ads_estimate_ad_squad_outcomes(
    ad_account_id="<AD_ACCOUNT_ID>",
    ad_squad={
        "optimization_goal": "IMPRESSIONS",
        "bid_strategy": "AUTO_BID",
        "daily_budget_micro": 50000000,
        "type": "SNAP_ADS",
        "placement_v2": {"config": "AUTOMATIC"},
        "targeting": {"geos": [{"country_code": "us"}]},
        "start_time": "2026-07-01T00:00:00-07:00",
    },
)
```

The tool auto-adds `delivery_constraint`. If it returns OE101/`UNSUPPORTED_DELIVERY_CONSTRAINT`, outcome estimation is likely **unavailable for this account type** (PARTNER accounts are often excluded) — skip forecasting and use the Snapchat Ads Manager reach planner instead.

#### Optional: audience size + suggested bid

Two lighter planning calls that work per targeting spec — use them to fill in the squad's numbers instead of guessing:

```python
# Reach range for a proposed squad spec (or pass ad_squad_id for an existing squad)
snapchat_ads_get_audience_size(
    ad_account_id="<AD_ACCOUNT_ID>",
    ad_squad_spec={
        "type": "SNAP_ADS",
        "optimization_goal": "APP_INSTALLS",
        "placement": "CONTENT",
        "daily_budget_micro": 50000000,
        "targeting": {"geos": [{"country_code": "us"}],
                      "demographics": [{"age_groups": ["21-24"]}]},
    },
)   # -> audience_size_minimum / audience_size_maximum

# Snapchat's suggested bid range (micro-currency) for a goal + targeting —
# use this to set bid_micro for LOWEST_COST_WITH_MAX_BID / TARGET_COST
snapchat_ads_get_bid_estimate(
    ad_account_id="<AD_ACCOUNT_ID>",
    optimization_goal="IMPRESSIONS",
    targeting={"geos": [{"country_code": "us"}]},
)   # -> bid_estimate_minimum / bid_estimate_maximum
```

Both also accept `ad_squad_id` to evaluate an existing squad after creation.

### 5. Create ad

> **Omit `type`** — it's auto-derived from the creative (a WEB_VIEW creative needs a `REMOTE_WEBPAGE` ad, SNAP_AD→SNAP_AD, APP_INSTALL→APP_INSTALL, DEEP_LINK→DEEP_LINK). Only set `type` to override.

```python
snapchat_ads_create_ad(
    ad_squad_id="<AD_SQUAD_ID>",
    name="Spring Hero Ad",
    creative_id="<CREATIVE_ID>",
    status="PAUSED",
)
```
