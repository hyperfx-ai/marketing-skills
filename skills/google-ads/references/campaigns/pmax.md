# Performance Max campaigns (granular build)

> **CRITICAL**: Present the full plan and get explicit user approval before the first mutate ([references/discovery.md](references/discovery.md) must be complete and the summary approved). PMax campaigns MUST be created **PAUSED** — they need at least one asset group before they can serve, and the create tool enforces this.

## Build order

1. **Budget** — `google_ads_campaign_budgets_create(customer_id, body={"name": "...", "amount_micros": 50000000, "explicitly_shared": false})`. A PMax budget must not be shared.
2. **Campaign** — `google_ads_campaigns_create(customer_id, body={...})`:

```json
{
  "name": "PMax Campaign",
  "advertising_channel_type": "PERFORMANCE_MAX",
  "status": "PAUSED",
  "campaign_budget": "customers/1234567890/campaignBudgets/111",
  "maximize_conversions": {},
  "contains_eu_political_advertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"
}
```

   Do NOT set `network_settings`, `manual_cpc` or `manual_cpm`: the validator rejects them. Bidding: the PMax line of [references/constraints.md](references/constraints.md), Bidding. Set `contains_eu_political_advertising` ([references/constraints.md](references/constraints.md), Technical Rules).
3. **Locations** — `google_ads_locations_search` → `google_ads_location_targets_add`.
4. **Image assets** — `google_ads_image_assets_upload` (prefer `file_id` from the workspace file manager). Required ratios: landscape 1.91:1, square 1:1, logo 1:1 (or 4:1).
5. **Asset group** — `google_ads_asset_groups_create` (atomic: creates the asset group, its text assets, and all links in ONE API call, which the API requires):

   Required: `customer_id`, `campaign_id` (numeric id), `final_urls`, `headlines` (3–15, ≤30 chars), `long_headlines` (1–5, ≤90), `descriptions` (2–5, ≤90), `business_name` (≤25 chars), and the three image asset id lists (`marketing_image_asset_ids`, `square_marketing_image_asset_ids`, `logo_asset_ids`). Text fields are lists of plain strings. Image ids are the `asset_id` values that `google_ads_image_assets_upload` returns.
6. **Optional video** — register a YouTube video with `google_ads_video_assets_link(customer_id, youtube_video_id)`, then link it with `google_ads_asset_group_assets_link(customer_id, asset_group_id="<id>", asset_id="<the asset_id that google_ads_video_assets_link returns>", field_type="YOUTUBE_VIDEO")`. Without one, Google auto-generates video from your assets.

## Standalone PMax asset group (existing campaign)

`google_ads_asset_groups_create` also adds asset groups to existing PMax campaigns — same required fields as step 5.

## Campaign dates (API v24)

Optional `"start_date_time": "YYYY-MM-DD 00:00:00"` and `"end_date_time": "YYYY-MM-DD 23:59:59"`. Omit both to let Google set the defaults.

## Verify, then activate

Confirm by GAQL (campaign + asset_group + asset_group_asset), present to the user, then call `google_ads_campaigns_update(customer_id, body={"resource_name": "customers/<cid>/campaigns/<id>", "status": "ENABLED"})` after explicit approval.

Read a section of [references/constraints.md](references/constraints.md) only when a step names it.
