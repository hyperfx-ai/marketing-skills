# Constraints and rules

Re-check this file at each creation step.

## Granular tools

The granular tools fill no defaults and do not roll back. When a later step fails, remove what was made with `google_ads_campaigns_remove` / `google_ads_campaign_budgets_remove` (`body={"resource_name": ...}`).

## Bidding

Bidding is one object on the campaign body:

| Object | Inner fields | Notes |
| --- | --- | --- |
| `target_spend: {}` | — | Maximize Clicks. |
| `maximize_conversions` | `target_cpa_micros` (optional) | Requires conversion tracking. |
| `maximize_conversion_value` | `target_roas` (optional) | Requires conversion values. |
| `target_cpa` | `target_cpa_micros` | Sets a target cost per acquisition. |
| `target_roas` | `target_roas` | Sets a target return on ad spend. |
| `manual_cpc: {}` | — | Manual cost-per-click. |

Smart Bidding needs conversion tracking.

> For PMax, put `target_cpa_micros` inside `maximize_conversions`, or `target_roas` inside `maximize_conversion_value`, yourself. Nothing translates `target_cpa` / `target_roas`.

## Technical Rules

- Budget in micros: $50 → 50,000,000.
- Create PAUSED; activate only after approval.
- Location resolution: `google_ads_locations_search` to resolve names, then `google_ads_location_targets_add`.
- RSA limits: headlines ≤30 chars (min 3), descriptions ≤90 chars (min 2).
- Creative source: only from the actual site; no generic claims.
- Upload images with `google_ads_image_assets_upload`, or reuse existing ones from `google_ads_assets_list(customer_id, type="IMAGE")`.

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
