---
name: meta-ads
description: Plan and create Meta (Facebook + Instagram) advertising campaigns end-to-end via the Hyper MCP, defaulting to Advantage+ automation. Use when the user wants to launch Meta ads, Facebook ads, Instagram ads, Advantage+ campaigns, carousel ads, dynamic creative ads, set up Meta conversion tracking, or build Meta performance dashboards. Also triggers on phrases like meta campaign, facebook campaign, advantage+, or meta blueprint.
use_cases:
  - Create Meta Ads campaigns
  - Create Facebook ads
  - Create Instagram ads
  - Configure Advantage+ campaigns
  - Upload Meta ad creative media
  - Preview Meta ad creatives
  - Analyze Meta ad performance
  - Build Meta Ads dashboards
  - Query cached Meta insights data
  - Set up carousel and dynamic creative ads
triggers:
  - meta ads
  - facebook ads
  - instagram ads
  - meta campaign
  - facebook campaign
  - instagram campaign
  - advantage+
  - meta dashboard
  - facebook dashboard
requires_toolkits:
  - meta_ads
suggested_toolkits:
  - firecrawl
  - file_manager
  - hyper_database
  - sandbox
---

# Meta Ads

Strategic guide for managing Meta advertising campaigns with emphasis on Advantage+ automation, and building dashboards from cached data.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Meta Business integration connected** (Facebook + Instagram, with at least one ad account and one Page) at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).
- **Firecrawl integration connected** for site research and screenshot grounding (see Phase 1).

If `meta_business_list_ad_accounts` is not in the tool list, stop and tell the user to enable Hyper MCP and connect Meta Business.

If you suspect a connection issue (missing ad accounts, page publishing failures, or permission errors), call `meta_business_get_health_check()` and report the diagnostics to the user before proceeding.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `meta_business_list_ad_accounts`, `meta_business_list_owned_pages` | Discovery. |
| `meta_business_list_instagram_accounts` | Retrieve `instagram_user_id` required for Instagram-placement ads. |
| `meta_business_get_health_check` | Diagnose integration connectivity (ad account access, page linking, pixel, token permissions). |
| `meta_business_preview_blueprint`, `meta_business_create_from_blueprint` | Validate + create campaigns end-to-end. |
| `meta_business_create_campaign`, `meta_business_create_ad_set`, `meta_business_create_ad`, `meta_business_upload_ad_image` | Manual step-by-step path (rare). |
| `meta_business_get_ad_details`, `meta_business_get_ad_previews` | Fetch creative ID from ad, then generate previews before activation. |
| `firecrawl_extract_branding`, `firecrawl_screenshot` | Capture site context + visual grounding for creative direction. |

## Core Approach

You are a strategic marketing partner. Research deeply, analyze comprehensively, optimize relentlessly. Never assume or invent information. **Always default to Advantage+ automation** (95% of cases) unless explicitly requested otherwise.

## Critical Rules

> **CRITICAL**: Always pass budgets in **CENTS** to the API. $20.00 = 2000. Never use dollar amounts directly. Every budget and bid parameter is in cents.

> **CRITICAL**: For Advantage+ campaigns, set budget at **CAMPAIGN level ONLY**. Ad set budget MUST be null. Never set budget at both campaign and ad set levels simultaneously.

> **CRITICAL**: For Manual campaigns, set budget at **AD SET level ONLY**. Do not set campaign-level budget for manual campaigns.

> **CRITICAL**: `targeting_automation` MUST be nested **inside** the `targeting` object, not at the top level.

> **CRITICAL**: Never silently change campaign objectives or optimization goals. Always get explicit user consent first.

> **CRITICAL**: Campaign objectives CANNOT be changed after ad sets exist. You must create a new campaign instead.

> **IMPORTANT**: Always default to Advantage+ unless the user explicitly requests manual control.

> **IMPORTANT**: Always create campaigns with status "PAUSED" initially. Never launch live without user review.

> **IMPORTANT**: Blueprint-created ads are PAUSED by default. For the manual path, always pass `status: "PAUSED"` explicitly.

> **IMPORTANT**: OUTCOME_LEADS, OUTCOME_APP_PROMOTION, and OUTCOME_SALES campaigns MUST include `promoted_object` in the ad set.

> **IMPORTANT**: Always generate and show ad previews to the user before activation.

> **CRITICAL (Creative Input Quality)**: For website-based campaigns, you must capture at least one real website screenshot with Firecrawl and use that screenshot as a visual reference for ad creative direction before creating ads.

## Phase 1: Research & Discovery

### Initial Discovery (run in parallel)
- Call `meta_business_list_ad_accounts` with `{"detail": "id_only"}`. Store the selected `account_id` for all subsequent calls.
- Call `meta_business_list_owned_pages` with `{"account_id": "<selected_account_id>", "detail": "id_only"}`.
- If multiple accounts: ask user to select one; if single account: inform user and proceed.
- If `pages` is empty, warn the user that the ad account may not be connected to a Meta Business. Use `meta_business_search_pages(query="<brand name>")` to locate the Page manually, or ask them to connect it in the Meta Business integration settings.

### Deep Marketing Research (MANDATORY)
**Never skip this phase:**

1. **Website/Product Analysis**: Fetch and scan provided URL, follow relevant internal pages, run targeted web searches for competitive context.
   - Run `firecrawl_extract_branding` on the primary site URL.
   - Run `firecrawl_screenshot` on the primary site URL to capture at least one current page screenshot. The screenshot is automatically saved and described.
   - Treat the screenshot as required visual grounding for creative direction (layout, hierarchy, tone, imagery style).

2. **Strategic Assessment**: Identify conversion goal, primary buyer persona, key differentiators, value proposition.
   - **DO NOT ask about target audiences** — Advantage+ uses broad targeting by default.

3. **CTA Selection**: Must match conversion goal. Available: LEARN_MORE, SHOP_NOW, SIGN_UP, DOWNLOAD, BOOK_NOW, GET_OFFER, etc.

4. **Budget Requirements**: MUST obtain amount + currency, daily vs lifetime, dates if lifetime.

## Phase 2: Campaign Configuration

### Campaign Type Decision Tree

**Default Path (95% of cases): Advantage+ Campaign**
- Broad targeting with simple geo location (maximum AI optimization).
- Campaign-level budget.
- All placements enabled.

**Alternative Paths (5% — only if explicitly requested):**
- Advantage+ with Targeting Hints (user explicitly requests interests/demographics).
- Manual Campaign (user wants full control).

### Advantage+ Configuration

**Three levers must be ON for Advantage state:**
1. **Budget**: Campaign-level (not ad set).
2. **Audience**: `targeting_automation: {"advantage_audience": 1}`.
3. **Placements**: Automatic (unrestricted).

**Campaign Setup:**
- Set `daily_budget` or `lifetime_budget` at CAMPAIGN level (in cents: $20 = 2000).
- Status: "PAUSED" initially.

**Ad Set Setup:**
- Budget: Must be null (campaign controls budget).
- Targeting: `{"geo_locations": {"countries": ["US"]}, "targeting_automation": {"advantage_audience": 1}}`.
  - **CRITICAL**: targeting_automation MUST be inside targeting object.
- Placements: Leave unrestricted.

### Budget Format

> **CRITICAL**: All budgets and bids are in **CENTS**. $20.00 = 2000. $5.50 = 550. $100 = 10000.

- Lifetime budgets require `start_time` and `end_time`.

## Phase 3: Campaign Creation (Blueprint System — PREFERRED)

> **CRITICAL**: Use the blueprint system whenever possible. It validates locally, fills smart defaults (optimization goal, bid strategy, page/pixel IDs), and rolls back on failure.

### Workflow: Preview → Confirm → Create

1. Build the blueprint JSON from research.
2. Call `meta_business_preview_blueprint(blueprint={...})` to validate and show the user.
3. Get explicit user approval.
4. Call `meta_business_create_from_blueprint(blueprint={...})`.

### Blueprint Structure

```json
{
  "account_id": "act_1234567890",
  "name": "Campaign Name",
  "objective": "OUTCOME_SALES",
  "campaign_type": "advantage_plus",
  "daily_budget": 2000,
  "status": "PAUSED",
  "url_tags": "utm_source=meta&utm_medium=paid",
  "ad_sets": [
    {
      "name": "US Broad Audience",
      "targeting": {
        "geo_locations": {"countries": ["US"]},
        "targeting_automation": {"advantage_audience": 1}
      },
      "pixel_id": null,
      "page_id": null,
      "custom_event_type": "PURCHASE",
      "ads": [
        {
          "name": "Single Image Ad",
          "link": "https://example.com",
          "primary_text": "Your ad copy here",
          "headline": "Headline here",
          "description": "Description here",
          "image_hash": "abc123",
          "call_to_action": "SHOP_NOW"
        }
      ]
    }
  ]
}
```

### Blueprint Features

| Feature | Details |
| --- | --- |
| **Smart defaults** | Optimization goal, billing event, destination type auto-filled from objective. |
| **Auto-resolution** | `page_id`, `pixel_id`, `instagram_user_id` auto-resolved when only one exists. |
| **Objective validation** | Per-objective rules enforce required fields, allowed values, promoted objects. |
| **Budget placement** | CBO (campaign level) vs ABO (ad set level) auto-detected. |
| **Cleanup on failure** | Reports `created`, `failed`, and `remaining` for recovery. |

### Ad Creative Formats

**Single image/video**:
```json
{
  "link": "https://example.com",
  "primary_text": "Ad copy",
  "headline": "Headline",
  "image_hash": "abc123",
  "call_to_action": "LEARN_MORE"
}
```

**Carousel** (2–10 cards):
```json
{
  "link": "https://example.com",
  "primary_text": "Check out our products",
  "carousel_cards": [
    {"image_hash": "hash1", "headline": "Product 1", "link": "https://example.com/1"},
    {"image_hash": "hash2", "headline": "Product 2", "link": "https://example.com/2"}
  ]
}
```

**Dynamic creative** (Meta auto-optimizes combinations):
```json
{
  "link": "https://example.com",
  "text_variations": {
    "primary_texts": ["Copy option 1", "Copy option 2"],
    "headlines": ["Headline A", "Headline B"],
    "descriptions": ["Desc 1", "Desc 2"]
  },
  "image_hash": "abc123"
}
```

### Advantage+ vs Manual in Blueprint

- **Advantage+**: Set `campaign_type: "advantage_plus"`, budget at campaign level, broad targeting with `targeting_automation`.
- **Manual**: Set `campaign_type: "manual"`, budget at ad set level, detailed targeting allowed.

### Creative Asset Preparation

Before building the blueprint, prepare image assets:

1. Capture screenshot from website: `firecrawl_screenshot` on the landing page URL.
2. Generate ad image using the screenshot as reference input to image generation.
3. Upload: `meta_business_upload_ad_image(account_id="<account_id>", image_url="<url>")` → returns `image_hash`.
4. Use `image_hash` in the blueprint's ad objects.

### Previews

After creation, generate previews:

1. For each ad ID returned by `meta_business_create_from_blueprint`, fetch the creative ID:
   ```json
   meta_business_get_ad_details(ad_id="<ad_id>")
   ```
   Extract `creative.id` from the response.

2. Call `meta_business_get_ad_previews` with the creative IDs:
   ```json
   meta_business_get_ad_previews(
     creative_ids=["<creative_id>"],
     ad_formats=["INSTAGRAM_STANDARD", "DESKTOP_FEED_STANDARD"]
   )
   ```

ALWAYS show previews to the user before activation.

Preview response handling:
- Never paste or render iframe/html snippets directly in chat.
- Summarize which preview formats succeeded/failed.
- Direct the user to view previews via the UI artifact.

## Phase 3 (Alternative): Manual Step-by-Step Creation

Use this only when the blueprint system is insufficient (e.g., complex creative overrides).

### 1. Create Campaign

Call `meta_business_create_campaign` with:
```json
{
  "account_id": "<account_id>",
  "name": "Campaign Name",
  "objective": "OUTCOME_SALES",
  "status": "PAUSED",
  "daily_budget": 2000
}
```
- `account_id` and `name` are required.
- `daily_budget` at campaign level for Advantage+ only (in cents: $20/day = 2000).
- Omit budget for manual campaigns.

### 2. Create Ad Set

Call `meta_business_create_ad_set`. You must specify `mode` to indicate the campaign type.

**Advantage+ ad set** (`mode = "advantage_plus"`):
```json
{
  "mode": "advantage_plus",
  "input_data": {
    "account_id": "act_1234567890",
    "name": "Advantage+ US Adults",
    "campaign_id": "1234567890",
    "optimization_goal": "LINK_CLICKS",
    "billing_event": "IMPRESSIONS",
    "targeting": {
      "geo_locations": {"countries": ["US"]},
      "targeting_automation": {"advantage_audience": 1}
    }
  }
}
```

**Manual ad set** (`mode = "manual"`):
```json
{
  "mode": "manual",
  "input_data": {
    "account_id": "act_1234567890",
    "name": "Manual IG Women 25-45",
    "campaign_id": "1234567890",
    "optimization_goal": "LINK_CLICKS",
    "billing_event": "IMPRESSIONS",
    "daily_budget": 5000,
    "targeting": {
      "geo_locations": {"countries": ["US"]},
      "age_min": 25,
      "age_max": 45,
      "genders": [2],
      "publisher_platforms": ["instagram"],
      "instagram_positions": ["stream", "story"]
    }
  }
}
```

> If you receive a "Bid amount required" error: DO NOT change `optimization_goal`. STOP and ask user for direction.

**Promoted Object Requirements by Objective:**

| Objective | Required `promoted_object` | Example |
| --- | --- | --- |
| **OUTCOME_LEADS** | YES — MUST include | `{"page_id": "<PAGE_ID>"}` |
| **OUTCOME_APP_PROMOTION** | YES — MUST include | `{"application_id": "<APP_ID>", "object_store_url": "<URL>"}` |
| **OUTCOME_SALES** | YES for OFFSITE_CONVERSIONS | `{"pixel_id": "<PIXEL_ID>", "custom_event_type": "PURCHASE"}` |
| **OUTCOME_ENGAGEMENT** | Optional but recommended | `{"page_id": "<PAGE_ID>"}` |

### 3. Upload Creative Assets

Call `meta_business_upload_ad_image` with a URL or file ID — `account_id` is required:

```json
{ "account_id": "<account_id>", "image_url": "<generated_or_hosted_image_url>" }
```

Or if the image is stored in Hyper file storage:
```json
{ "account_id": "<account_id>", "file_id": "<file_id>" }
```

### 4. Create Ad

Call `meta_business_create_ad` — all fields go inside `input_data`:
```json
{
  "input_data": {
    "account_id": "<account_id>",
    "name": "Ad Name",
    "adset_id": "<adset_id>",
    "status": "PAUSED",
    "creative": {
      "object_story_spec": {
        "page_id": "<page_id>",
        "instagram_user_id": "<instagram_user_id>",
        "link_data": {
          "link": "<destination_url>",
          "image_hash": "<image_hash>",
          "call_to_action": {"type": "LEARN_MORE"},
          "message": "<ad_text>",
          "name": "<headline>",
          "description": "<description>"
        }
      }
    }
  }
}
```

> Use `meta_business_list_instagram_accounts(account_id="<account_id>")` to get `instagram_user_id`. Required for ads that run on Instagram placements.

## Objective Prerequisites

| Objective | Requirements |
| --- | --- |
| OUTCOME_SALES | Pixel/CAPI + valid conversion events. |
| OUTCOME_LEADS | Lead form OR website pixel with lead events. |
| OUTCOME_APP_PROMOTION | App configured in app store. |
| OUTCOME_TRAFFIC | Valid destination URL. |
| OUTCOME_ENGAGEMENT/AWARENESS | No additional requirements beyond Page. |

## Done Condition

The workflow is complete when:
1. Campaign, ad set(s), and ad(s) are created with status **PAUSED**.
2. Ad previews have been generated and shown to the user.
3. The user has given explicit approval to activate.

Only then call `meta_business_update_campaign(campaign_id="<id>", status="ACTIVE")` to go live. Never activate without this confirmation.

## Beyond campaign creation

| Task | Reference |
| --- | --- |
| Full account audit (structure, performance, ad sets, creatives, recommendations) | `references/account-audit.md` |
| Cached insights, 90-day ad-level insights, dashboard workflow | `references/insights-and-dashboards.md` |
| Competitor ad research in the Meta Ad Library | [`meta-ads-library`](../meta-ads-library) |
| Generating ad creatives and copy variants | [`ad-creative-generation`](../ad-creative-generation) |
