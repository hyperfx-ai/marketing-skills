---
name: amazon-ads
description: Plan and create Amazon Sponsored Products campaigns end-to-end via the Hyper MCP. Use when the user wants to launch Amazon Ads, set up Sponsored Products, manage keyword targeting and bids, configure ASIN or category product targeting, add negative keywords, automate budget rules, analyze ACoS / ROAS, or generate Sponsored Products reports. Also triggers on amazon ppc, amazon campaign, amazon keywords, or amazon report.
use_cases:
  - Create Amazon Sponsored Products campaigns
  - Manage keyword targeting and bids
  - Set up product targeting (ASIN/category)
  - Add negative keywords to reduce wasted spend
  - Configure budget rules for automation
  - Analyze campaign performance and ACoS
  - Generate SP reports (campaign, search term, targeting)
  - Check integration health and profile setup
  - Create campaigns with multi-profile support
triggers:
  - amazon ads
  - sponsored products
  - amazon campaign
  - amazon ppc
  - acos
  - amazon keywords
  - product targeting
  - amazon report
  - amazon budget rule
requires_toolkits:
  - amazon_ads
suggested_toolkits:
  - hyper_database
  - sandbox
  - file_manager
---

# Amazon Ads

Strategic guide for managing Amazon Ads Sponsored Products campaigns. Research first, validate products, optimize for ACoS targets.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Amazon Ads integration connected** at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

If `amazon_ads_list_profiles` is not in the tool list, stop and tell the user to enable Hyper MCP and connect Amazon Ads.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `amazon_ads_list_profiles`, `amazon_ads_run_health_check` | Profile discovery + integration health. |
| `amazon_ads_list_campaigns`, `amazon_ads_create_campaign`, `amazon_ads_update_campaign` | Campaign lifecycle. |
| `amazon_ads_create_ad_group`, `amazon_ads_create_product_ad` | Ad group + product ad creation. |
| `amazon_ads_create_keyword`, `amazon_ads_create_negative_keyword`, `amazon_ads_create_campaign_negative_keyword` | Keyword targeting. |
| `amazon_ads_create_product_target`, `amazon_ads_create_negative_product_target` | Product (ASIN/category) targeting. |
| `amazon_ads_create_budget_rule`, `amazon_ads_list_budget_rules` | Budget automation. |
| `amazon_ads_create_report`, `amazon_ads_get_report_status` | Performance reporting. |
| `amazon_ads_get_bid_recommendations` | Theme-based bid recommendations. |

## Critical Rules

> **CRITICAL**: Keyword, negative keyword, product ad, and product target operations require BOTH `ad_group_id` AND `campaign_id`. Omitting `campaign_id` causes validation errors.

> **CRITICAL**: Keywords and product targets cannot coexist in the same ad group. Choose one targeting type per ad group.

> **CRITICAL**: AUTO campaigns only allow negative keywords and negative product targets. Positive keywords and product targets are rejected.

> **CRITICAL**: Campaign dates use `YYYY-MM-DD` format. Budget rule dates use `YYYYMMDD` format. Do not mix these up.

> **CRITICAL**: Create campaigns with state `"PAUSED"`. Never launch live without user review.

> **CRITICAL**: Negative product targets only support `ASIN_SAME_AS` and `ASIN_BRAND_SAME_AS` expressions. Category exclusions are not supported.

> **CRITICAL**: All enum values must be UPPERCASE: `PAUSED`, `ENABLED`, `BROAD`, `PHRASE`, `EXACT`, `NEGATIVE_EXACT`, `NEGATIVE_PHRASE`, `MANUAL`, `AUTO`.

> **IMPORTANT**: Portfolio operations return 404 for vendor accounts. Use campaign-level management instead.

> **IMPORTANT**: Budget rule listing may return empty even after successful creation. Track rule IDs from creation responses.

> **IMPORTANT**: All budgets are in dollars (not cents, not micros). $25 daily budget = `25`.

## Phase 1: Profile Discovery

Call `amazon_ads_list_profiles()` to list advertising profiles.

- Each profile corresponds to a marketplace (US, BR, CA, MX, UK, DE, JP, etc.).
- Profiles are either **seller** or **vendor** type.
- If multiple: ask the user which marketplace to focus on.
- If single: inform the user and proceed.
- Note the `profileId` — it's required for every subsequent API call.

**Health Check**: Call `amazon_ads_run_health_check()` to verify OAuth tokens, profile access, and billing status.

## Phase 2: Account Assessment

### Existing Campaign Audit
```
amazon_ads_list_campaigns(profile_id=PROFILE_ID)
```
Review active campaigns, budgets, and targeting types (auto vs manual).

### Product Research
- Get the ASINs the user wants to advertise (real ASINs only — never invent them).
- Ask about product category, price point, and margins.
- Calculate target ACoS: `(ad spend / ad revenue) × 100`.
- Understand the competitive landscape.

### Keyword Research
- Review search term reports from existing campaigns.
- Identify high-performing keywords.
- Plan match types: EXACT for proven terms, PHRASE for discovery, BROAD for expansion.
- Identify negative keywords to exclude.

### Bid Strategy
Ask about budget and goals:
- `LEGACY_FOR_SALES` (default): Amazon lowers bids when less likely to convert.
- `AUTO_FOR_SALES`: Dynamic bids, up and down.
- `MANUAL`: Full control over bid amounts.

### Confirm Criticals
- Daily budget.
- Target ACoS.
- ASINs to advertise.
- Target marketplace(s).
- Auto vs manual targeting preference.

## Phase 3: Campaign Structure

### Recommended Structure

```
Campaign (targeting type: MANUAL or AUTO)
└── Ad Group (default bid)
    ├── Product Ads (ASINs)
    ├── Keywords (MANUAL campaigns only)
    └── Product Targets (MANUAL campaigns only, mutually exclusive with keywords)
```

### Structure Decision Tree

```
AUTO Campaign:
  → Single campaign
  → Single ad group (broad matching)
  → Add product ads (ASINs)
  → Campaign-level negative keywords
  → Let Amazon optimize

MANUAL Campaign:
  → Separate ad groups by targeting theme
  → Each ad group: keywords OR product targets (not both)
  → Specific bids per keyword/target
  → Campaign and ad-group level negatives
```

### Best Practices
- Separate auto and manual campaigns.
- Group related ASINs in the same ad group.
- Use EXACT match for high-intent keywords.
- Add negatives at campaign level for broad exclusions.
- Start with conservative bids and increase based on ACoS data.

## Phase 4: Pre-Creation Summary (Must Be Approved)

```
Campaign Strategy for [Product/Brand]

Profile: [profileId] ([marketplace])
Account Type: [seller/vendor]
ASINs: [list]
Target ACoS: [X]%
Daily Budget: $[X]
Targeting: [AUTO/MANUAL/both]
Bidding Strategy: [strategy]
Keywords: [count] across [match types]
Negatives: [count] terms excluded

Approve to proceed?
```

Wait for explicit approval.

## Phase 5: Campaign Creation

### 1. Create Campaign
```
amazon_ads_create_campaign(
    profile_id=PROFILE_ID,
    name="SP - Manual - [Product]",
    targeting_type="MANUAL",
    daily_budget=25,
    start_date="2026-03-01",
    state="PAUSED",
    bidding_strategy="legacy_for_sales"
)
```
Returns: `campaignId`.

### 2. Create Ad Group
```
amazon_ads_create_ad_group(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    name="[Product] - Exact Keywords",
    default_bid=0.75,
    state="PAUSED"
)
```
Returns: `adGroupId`.

### 3. Add Product Ads
```
amazon_ads_create_product_ad(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    asin="B0XXXXXXXXX",
    state="PAUSED"
)
```

### 4. Add Keywords (MANUAL campaigns only)
```
amazon_ads_create_keyword(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    keyword_text="wireless earbuds",
    match_type="EXACT",
    bid=0.85
)
```

### 5. Add Negative Keywords (Campaign Level)
```
amazon_ads_create_campaign_negative_keyword(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    keyword_text="cheap",
    match_type="NEGATIVE_PHRASE"
)
```

### 6. Add Negative Keywords (Ad Group Level)
```
amazon_ads_create_negative_keyword(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    keyword_text="refurbished",
    match_type="NEGATIVE_EXACT"
)
```

### 7. Product Targeting (alternative to keywords — separate ad group)
```
amazon_ads_create_product_target(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    expression=[{"type": "ASIN_SAME_AS", "value": "B0COMPETITOR"}],
    bid=0.60,
    state="PAUSED"
)
```

Available expression types:
- `ASIN_SAME_AS`: target a specific ASIN.
- `ASIN_CATEGORY_SAME_AS`: target an entire category.
- `ASIN_BRAND_SAME_AS`: target a brand (requires numeric brand ID).

### 8. Negative Product Targets (Ad Group Level)
```
amazon_ads_create_negative_product_target(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    expression=[{"type": "ASIN_SAME_AS", "value": "B0EXCLUDE"}],
    state="ENABLED"
)
```

Only `ASIN_SAME_AS` and `ASIN_BRAND_SAME_AS` are supported for negative targets.

## Phase 6: Budget Rules & Automation

### Schedule-Based Rules

Auto-increase budget on specific dates:

```
amazon_ads_create_budget_rule(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    rule_type="SCHEDULE",
    name="Holiday Boost",
    budget_increase_percent=50,
    start_date="20261201",
    end_date="20261225"
)
```

### Performance-Based Rules

Auto-increase budget when metrics are met:

```
amazon_ads_create_budget_rule(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    rule_type="PERFORMANCE",
    name="High ROAS Rule",
    budget_increase_percent=25,
    performance_metric="ROAS",
    comparison_operator="GREATER_THAN_OR_EQUAL_TO",
    threshold=5.0,
    start_date="20260301"
)
```

Performance metrics: `ACOS`, `CTR`, `CVR`, `ROAS`.

> **CRITICAL**: Budget rule dates use `YYYYMMDD` format (not `YYYY-MM-DD`).

## Reporting & Analysis

### Create Performance Report
```
amazon_ads_create_report(
    profile_id=PROFILE_ID,
    report_type="spCampaigns",
    columns=["impressions", "clicks", "cost", "spend"],
    start_date="2026-02-01",
    end_date="2026-02-28",
    group_by=["campaign"],
    time_unit="SUMMARY"
)
```

### Check Report Status
```
amazon_ads_get_report_status(profile_id=PROFILE_ID, report_id=REPORT_ID)
```

Reports are async. Status transitions: PENDING → PROCESSING → COMPLETED.

### Report Types
| Type | Description |
| --- | --- |
| `spCampaigns` | Campaign-level metrics. |
| `spAdGroups` | Ad group-level metrics. |
| `spAdvertisedProduct` | ASIN-level metrics. |
| `spTargeting` | Keyword/target metrics. |
| `spSearchTerm` | Search term report. |

### Report Configuration
- `group_by` is **required**: `campaign`, `adGroup`, or `campaignPlacement`.
- Valid columns include: `impressions`, `clicks`, `cost`, `spend`, `sales7d`, `purchases7d`, `unitsSoldClicks7d`, `clickThroughRate`, `costPerClick`.
- Columns like `campaignId` and `campaignName` are **not allowed** in the columns list.

### Key Metrics
| Metric | Formula |
| --- | --- |
| ACoS | ad spend / ad revenue × 100 |
| ROAS | ad revenue / ad spend |
| TACoS | ad spend / total revenue × 100 |
| CTR | clicks / impressions × 100 |
| CPC | cost / clicks |
| CVR | orders / clicks × 100 |

## Bid Recommendations

Get theme-based bid recommendations for an existing ad group:

```
amazon_ads_get_bid_recommendations(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    ad_group_id=AD_GROUP_ID,
    targeting_expressions=[
        {"type": "KEYWORD_BROAD_MATCH", "value": "wireless earbuds"},
        {"type": "KEYWORD_EXACT_MATCH", "value": "bluetooth headphones"},
        {"type": "CLOSE_MATCH"},
        {"type": "LOOSE_MATCH"}
    ]
)
```

Available targeting expression types:
- `CLOSE_MATCH`, `LOOSE_MATCH`, `SUBSTITUTES`, `COMPLEMENTS` (auto targeting).
- `KEYWORD_BROAD_MATCH`, `KEYWORD_EXACT_MATCH`, `KEYWORD_PHRASE_MATCH` (keyword targeting).

## Multi-Profile Management

Amazon Ads supports multiple profiles per integration:
- US (USD) — primary marketplace.
- Brazil (BRL) — regional expansion.
- Canada (CAD) — North America.
- Mexico (MXN) — regional expansion.

**Cross-Profile Strategy**:
- Create similar campaigns on high-performing profiles.
- Adjust bids by marketplace (currency and competition differ).
- Track unified ROI by aggregating per-profile reports in chat.

## Campaign Statuses

- `PAUSED`: Created but not live (safe default).
- `ENABLED`: Running and spending budget.
- `ARCHIVED`: Deleted (cannot be restored).

## Known Limitations

| Issue | Workaround |
| --- | --- |
| Portfolio operations return 404 (vendor) | Use campaign-level grouping + naming conventions. |
| Budget rule listing may return empty | Track rule IDs from creation responses. |
| Category recommendations may fail (500) | Use manual research or dashboard. |

## Campaign Workflow

Discovery → Research (products + keywords) → Strategy (auto vs manual) → Approve Summary → Create (PAUSED) → Add Keywords/Products → Add Negatives → Test (1–3 days) → Optimize → Activate.

## Safety Rules

**Never:**
- Assume ASINs or keywords — always ask.
- Skip the research/audit phase.
- Create campaigns without explicit approval.
- Set campaigns to ENABLED without user consent.
- Ignore ACoS targets when recommending bids.
- Add products the user hasn't confirmed.
- Mix keywords and product targets in the same ad group.
- Omit `campaign_id` from keyword/product operations.
