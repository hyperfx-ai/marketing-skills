---
name: amazon-ads
description: Plan and create Amazon Sponsored Products campaigns end-to-end via the Hyper MCP. Use when the user wants to launch Amazon Ads, set up Sponsored Products, manage keyword targeting and bids, configure ASIN or category product targeting, add negative keywords, automate budget rules, analyze ACoS / ROAS, or generate Sponsored Products reports. Also triggers on amazon ppc, amazon campaign, amazon keywords, or amazon report.
icon: amazon_ads
short_description: Plan and create Amazon Sponsored Products campaigns with targeting and budget rules.
---

# Amazon Ads

Strategic guide for managing Amazon Ads Sponsored Products campaigns. Research first, validate products, optimize for ACoS targets.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Amazon Ads integration connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps).

If `amazon_ads_list_profiles` is not in the tool list, stop and tell the user to enable Hyper MCP and connect Amazon Ads.

## Out of scope — defer to other skills

- **Creative generation** (product imagery, copy) → [`ad-creative-generation`](../ad-creative-generation) / [`image-generation`](../image-generation).
- **Cross-platform campaign launches** → use this skill for Amazon, then invoke `meta-ads` / `google-ads` separately.

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

## Core process

Discovery → Research (products + keywords) → Strategy (auto vs manual) → Approve Summary → Create (PAUSED) → Add Keywords/Products → Add Negatives → Test (1–3 days) → Optimize → Activate only with user approval.

> **All reference files live in `references/`.** Read them at `references/<file>` (e.g. `references/discovery.md`).

## Routing table

| The user wants to… | Read these files first |
|---|---|
| Launch a Sponsored Products campaign | [references/discovery.md](references/discovery.md) → [references/campaign-creation.md](references/campaign-creation.md) |
| Add keywords / negatives / product targets to an existing campaign | [references/campaign-creation.md](references/campaign-creation.md) |
| Automate budgets (schedule or performance rules) | [references/budget-rules.md](references/budget-rules.md) |
| Analyze performance / ACoS / search terms | [references/reporting.md](references/reporting.md) |
| Get bid recommendations | [references/reporting.md](references/reporting.md) |
| Work across marketplaces (multi-profile) | [references/reporting.md](references/reporting.md) |
| Goal not yet clear | [references/discovery.md](references/discovery.md) — discovery clarifies the goal |

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
