---
name: google-ads
description: Plan and create new Google Ads campaigns end-to-end via the Hyper MCP, and report on existing accounts with GAQL-backed evidence (conversions, funnels, search terms, budgets, dashboards). Use when the user wants to launch Search, Display, or Performance Max campaigns, build Google Ads reports, or mentions AdWords, PMax, PPC, negative keywords, or MCC accounts. For ongoing optimization, defer to a future google-ads-operator sibling skill.
use_cases:
  - Create Google Ads campaigns
  - Set up search campaigns
  - Set up display campaigns
  - Set up Performance Max campaigns
  - Configure Smart Bidding
  - Research keywords for ads
  - Create campaigns with blueprint system
  - Launch net-new campaigns from research
  - Preview Google Ads blueprints before creation
triggers:
  - google ads
  - adwords
  - search ads
  - display ads
  - performance max
  - pmax
  - ppc
  - google campaign
  - google blueprint
  - search term report
  - negative keywords
  - manager account
  - mcc
requires_toolkits:
  - google_ads
suggested_toolkits:
  - sandbox
  - file_manager
---

# Google Ads

Strategic guide for building new Google Ads campaigns. Research first, consult intelligently, validate everything, and use the blueprint flow for controlled creation.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Google Ads integration connected** at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

If `google_ads_list_accounts` is not in the tool list, stop and tell the user to enable Hyper MCP and connect Google Ads.

## Routing

- **Reporting on existing accounts** (GAQL-backed reports, conversion breakdowns, funnels, search terms, budget views, optional dashboards) → read `references/reporting.md` first; per-report recipes live under `references/reporting/reports/`.
- **Campaign creation** (Search, Display, PMax) → this guide, below.

## Out of scope

- **Ongoing optimization** (search-term cleanup, bid adjustments, ad testing, restructuring existing campaigns) → defer to a future `google-ads-operator` skill.
- **Creative generation** (headlines, descriptions, images) → [`ad-creative-generation`](../ad-creative-generation).
- **Cross-platform campaign launches** → use this skill for Google, then invoke `meta-ads` / `tiktok-ads` separately.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `google_ads_list_accounts` | Discover accessible accounts (and MCC sub-accounts). |
| `google_ads_execute_gaql` | Run a GAQL query (conversion actions, search term reports, etc.). |
| `google_ads_search_locations` | Resolve human-readable location names to IDs. |
| `google_ads_list_assets`, `google_ads_upload_image_asset` | Manage image assets for Display / PMax. |
| `google_ads_preview_blueprint`, `google_ads_create_from_blueprint` | Validate + create Search/Display campaigns. |
| `google_ads_preview_pmax_blueprint`, `google_ads_create_from_pmax_blueprint` | Validate + create Performance Max campaigns. |

## Phase 1: Initial Setup

Call `google_ads_list_accounts()` to list accessible accounts.

- If multiple: ask the user to select one.
- If single: inform the user and proceed.

**CRITICAL**: Verify account access before any operations.

## Phase 2: Discovery & Research (MANDATORY)

### Research Steps
1. Get the real domain (ask; don't infer).
2. Scan the site end-to-end: home, product/service, pricing, about, FAQs, locations, contact, landing pages.
3. Understand funnel & goals: primary conversions, CTAs, forms/checkout, thank-you pages.
4. Extract messaging: value props, differentiators, proof, offers.

### Conversion Tracking Check
Before asking questions, run the purpose-built diagnostic (simpler than a hand-rolled GAQL query):
```
google_ads_diagnose_conversion_tracking(customer_id="<from list_accounts>")
```

This returns all conversion actions, their status, and any tracking signal issues in one call. If the user's MCP doesn't expose `google_ads_diagnose_conversion_tracking`, fall back to GAQL:
```
google_ads_execute_gaql(
  customer_id="<from list_accounts>",
  query="""
    SELECT conversion_action.id, conversion_action.name,
           conversion_action.status, conversion_action.type
    FROM conversion_action
    WHERE conversion_action.status = 'ENABLED'
  """
)
```

> **`google_ads_execute_gaql` vs `google_ads_run_gaql`:** `execute_gaql` works on manager accounts (MCC) and sub-accounts. `run_gaql` is only available on non-manager accounts. Use `execute_gaql` consistently — it works everywhere.

### Market & Keyword Research
- Inspect SERPs, competitors, and themes.
- Propose keyword candidates (intent-aligned).
- Identify initial negatives.

### Confirm Criticals
- Daily budget (+currency).
- Served geos.
- Constraints.
- Tracking status.

## Phase 3: Consultation

Act as a partner, not order-taker:
- Present findings (site + GAQL + market).
- Recommend bidding (default Smart Bidding when tracking exists) with trade-offs.
- Propose structure (campaign → themed ad groups → keywords + match types).
- Suggest locations via `google_ads_search_locations(customer_id="...", location_names="New York")`. Note: `location_names` is a single string, not an array — pass a city, state, country, or postal code and the tool returns matching geo target IDs.
- Set budget expectations via benchmark ranges.
- Show reasoning for each choice.

## Phase 4: Pre-Creation Summary (Must Be Approved)

```
Campaign Strategy for [Business Name]

Sources: [URL], GAQL
Conversion Setup: [GAQL findings]
Primary Goal: [objective + why]
Bidding: [strategy + why]
Budget: $[X]/day (expectations)
Locations: [targets + rationale]
Keyword Themes: [themes + match types + 2-3 examples]
Messaging: [angles pulled from site]
Trade-offs/Risks: [bullets]

Approve to proceed?
```

Wait for explicit approval. No emojis. No assumptions.

## Phase 5: Campaign Creation (Blueprint System)

> **CRITICAL**: Always use the blueprint system for campaign creation. It validates locally, fills smart defaults, resolves locations, and rolls back on failure.

### Workflow: Preview → Confirm → Create

1. Build the blueprint JSON from research.
2. Call the **preview** tool to validate and show the user what will be created.
3. Get explicit user approval.
4. Call the **create** tool.

### Search & Display Campaigns

**Preview**: `google_ads_preview_blueprint(blueprint={...})`
**Create**: `google_ads_create_from_blueprint(blueprint={...})`

```json
{
  "customer_id": "1234567890",
  "name": "Campaign Name",
  "budget_amount_micros": 50000000,
  "advertising_channel_type": "SEARCH",
  "bidding_strategy": "MAXIMIZE_CLICKS",
  "status": "PAUSED",
  "location_names": ["New York", "Los Angeles"],  // array in blueprints; note: google_ads_search_locations takes a single string for manual lookup
  "conversion_action_ids": ["1234567890"],
  "ad_schedules": [
    {"day_of_week": "MONDAY", "start_hour": 9, "end_hour": 17}
  ],
  "sitelinks": [
    {"link_text": "Free Trial", "final_urls": ["https://example.com/trial"]}
  ],
  "callouts": [{"callout_text": "Free Shipping"}],
  "ad_groups": [
    {
      "name": "Ad Group 1",
      "keywords": [
        {"text": "marketing software", "match_type": "PHRASE"},
        {"text": "competitor brand", "match_type": "EXACT", "negative": true}
      ],
      "ads": [
        {
          "headlines": ["Headline 1", "Headline 2", "Headline 3"],
          "descriptions": ["Description 1", "Description 2"],
          "final_urls": ["https://example.com"]
        }
      ],
      "audiences": [{"audience_id": "1234567890"}]
    }
  ]
}
```

For **Display** campaigns, set `"advertising_channel_type": "DISPLAY"` and use `display_ads` instead of `ads`:
```json
"display_ads": [{
  "headlines": ["Headline 1", "Headline 2", "Headline 3"],
  "long_headline": "Longer headline up to 90 characters",
  "descriptions": ["Description 1", "Description 2"],
  "business_name": "Business Name",
  "final_urls": ["https://example.com"],
  "marketing_image_asset_ids": ["1234567890"],
  "square_marketing_image_asset_ids": ["1234567891"],
  "logo_asset_ids": ["1234567892"]
}]
```

> **CRITICAL (Display)**: All three image asset types are REQUIRED:
> - `marketing_image_asset_ids` — landscape 1.91:1 (e.g. 1200×628).
> - `square_marketing_image_asset_ids` — square 1:1 (e.g. 1200×1200).
> - `logo_asset_ids` — square 1:1 or landscape 4:1.

### Performance Max Campaigns

**Preview**: `google_ads_preview_pmax_blueprint(blueprint={...})`
**Create**: `google_ads_create_from_pmax_blueprint(blueprint={...})`

```json
{
  "customer_id": "1234567890",
  "name": "PMax Campaign",
  "budget_amount_micros": 50000000,
  "bidding_strategy": "MAXIMIZE_CONVERSIONS",
  "status": "PAUSED",
  "location_names": ["United States"],
  "conversion_action_ids": ["1234567890"],
  "asset_groups": [
    {
      "name": "Asset Group 1",
      "headlines": ["Headline 1", "Headline 2", "Headline 3"],
      "long_headlines": ["Longer headline up to 90 characters"],
      "descriptions": ["Description 1", "Description 2"],
      "business_name": "Business Name",
      "final_urls": ["https://example.com"],
      "marketing_image_asset_ids": ["1234567890"],
      "square_marketing_image_asset_ids": ["1234567891"],
      "logo_asset_ids": ["1234567892"]
    }
  ]
}
```

> **CRITICAL (PMax)**: All three image asset types are REQUIRED with correct aspect ratios. The preview tool validates ratios before creation.

### Blueprint Features

| Feature | Details |
| --- | --- |
| **Smart defaults** | Budget name, start date, network settings, ad group type auto-filled. |
| **Location resolution** | Pass `location_names` (human-readable) instead of IDs. |
| **Client-side validation** | Char limits, match types, image ratios checked before any API call. |
| **Batch operations** | Keywords, extensions, ad schedules batched for efficiency. |
| **Cleanup on failure** | Entire campaign removed if any step fails after campaign creation. |
| **Ad extensions** | Sitelinks, callouts, structured snippets — created and linked automatically. |
| **Ad scheduling** | Day-parting at campaign level via `ad_schedules`. |
| **Audiences** | Target or exclude audiences per ad group. |
| **Conversion actions** | Link specific conversion actions via `conversion_action_ids`. |

### Bidding Strategies

| Strategy | Fields | Notes |
| --- | --- | --- |
| `MANUAL_CPC` | — | Manual cost-per-click. |
| `MAXIMIZE_CLICKS` | — | Default, good starting point. |
| `MAXIMIZE_CONVERSIONS` | `target_cpa_micros` (optional) | Requires conversion tracking. |
| `MAXIMIZE_CONVERSION_VALUE` | `target_roas` (optional) | Requires conversion values. |
| `TARGET_CPA` | `target_cpa_micros` (required) | Sets a target cost per acquisition. |
| `TARGET_ROAS` | `target_roas` (required) | Sets a target return on ad spend. |

> For PMax: `TARGET_CPA` and `TARGET_ROAS` are translated to constraints within `MAXIMIZE_CONVERSIONS` / `MAXIMIZE_CONVERSION_VALUE`.

### Technical Rules

- Budget in micros: $50 → 50,000,000.
- Create PAUSED; activate only after approval.
- Location resolution: use `location_names` in blueprint (auto-resolved) or `google_ads_search_locations` for manual lookup.
- RSA limits: headlines ≤30 chars (min 3), descriptions ≤90 chars (min 2).
- Creative source: only from the actual site; no generic claims.
- Image assets must already exist in the account (use `google_ads_list_assets` to find them).

## Campaign Workflow

Initial Setup → Research (site + GAQL + market) → Analyze (goals, audience, keywords) → Consult (options + trade-offs) → Recommend (structure + bids) → Confirm (summary approved) → Build Blueprint → Preview → User Approval → Create (PAUSED) → Activate (post-approval).

## GAQL Resource Compatibility

**Critical:** Not all Google Ads resources can be joined in a single query.

### search_term_view
Use `segments.keyword.info.*` for keyword text and match type — **never** `ad_group_criterion.*`:

```sql
SELECT
    search_term_view.search_term,
    customer.descriptive_name,
    segments.keyword.info.text,
    segments.keyword.info.match_type,
    campaign.name,
    ad_group.name,
    metrics.clicks,
    metrics.impressions,
    metrics.conversions,
    metrics.cost_micros
FROM search_term_view
WHERE segments.date DURING LAST_7_DAYS
ORDER BY metrics.impressions DESC
```

`ad_group_criterion` is **incompatible** with `search_term_view` as the FROM resource. Selecting `ad_group_criterion.*` fields will always fail with `PROHIBITED_RESOURCE_TYPE_IN_SELECT_CLAUSE`.

### keyword_view
For keyword performance (Quality Score, bid estimates):
```sql
SELECT
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    metrics.clicks,
    metrics.impressions,
    metrics.historical_quality_score
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
```

## Multi-Account Workflows (MCC)

When a user provides a manager account (MCC) with multiple sub-accounts:

### Batching Rule
**Never query more than 5 sub-accounts in a single run.** Each `google_ads_execute_gaql` call goes through a proxy with a timeout. Querying 10+ accounts sequentially in one loop reliably causes 504 timeouts.

Process in batches of 5 and aggregate results before proceeding:
```
Batch 1: accounts[0:5]   → collect results
Batch 2: accounts[5:10]  → collect results
Batch 3: accounts[10:15] → collect results
...merge all batches...
```

Announce progress to the user: `"Processing accounts 1-5 of 23..."`.

### 504 Timeout Recovery
If a `google_ads_execute_gaql` call times out (504 / "Google Ads API timed out after retries"):
1. The tool already retries 3× internally — do not retry immediately.
2. Reduce the scope: narrow the date range, add a `LIMIT`, or split the account list further.
3. Tell the user which accounts succeeded and which failed; do not silently drop accounts.

### Cross-Account Search Term Report (Most Common Use Case)

For MCC search term reports across many sub-accounts:

```
1. Get all accounts: google_ads_list_accounts()
   Filter to sub-accounts: [a for a in result.accounts if not a["manager"]]
2. For each batch of 5 accounts:
   - Run search_term_view GAQL (using segments.keyword.info.*, NOT ad_group_criterion).
   - Collect results tagged with customer.descriptive_name.
3. Merge all batches into a single dataset.
4. Write to Google Sheets or CSV file for the user.
```

Minimum required columns for a search term report:
- Search Term, Account Name, Keyword, Match Type, Campaign, Ad Group.
- Clicks, Impressions, Conversions, Cost.
- Add Negative (Yes/No — your recommendation).

## Critical Safety Rules

**Never:**
- Assume URL/budget/location IDs.
- Skip research.
- Invent keywords/copy.
- Apply rigid "best practices" without context.
- Build without buy-in.
- Skip the preview step before creation.
- Join `ad_group_criterion` with `search_term_view` in GAQL.
- Query more than 5 accounts in a single batch.

## Cached Data (optional, when `google_ads_query_insights` is exposed)

If the MCP exposes `google_ads_query_insights`, use it for large multi-account performance queries — it reads from a local cache refreshed hourly and avoids API timeouts entirely.

### Query Performance

Call `google_ads_query_insights` — its built-in description includes the exact table name, schema, and example queries. Read the tool description first, then pass a SQL query targeting that table. Typical pattern:

```
google_ads_query_insights(
  query="SELECT date, campaign_name, SUM(cost_micros) as spend, SUM(clicks) as clicks
         FROM <table>
         WHERE customer_id = '1234567890'
           AND date >= CURRENT_DATE - INTERVAL '7 days'
         GROUP BY date, campaign_name ORDER BY date DESC"
)
```

Replace `<table>` with the table name shown in the `google_ads_query_insights` tool description. Cache is refreshed hourly — no manual sync needed.

> **If the tool returns a "no data cached" error**, check the `suggestion` field in the response — it will contain the correct workspace-specific table name. Retry the query using that suggested table name instead.

Key columns available (verify in tool description):
- **Hierarchy:** `date`, `customer_id`, `campaign_id`, `campaign_name`, `campaign_status`
- **Volume:** `impressions`, `clicks`, `cost_micros` (÷ 1,000,000 for dollars)
- **Conversions:** `conversions`, `conversions_value`, `conversion_rate`
- **Efficiency:** `ctr`, `average_cpc`, `average_cpm`

Supports standard SQL aggregations and window functions. For cross-account queries, omit the `customer_id` filter and `GROUP BY` it instead.
