# Video, Demand Gen, Shopping, and App campaigns

Same one create tool — `google_ads_campaigns_create` — with the channel type and its required settings. The validators return corrective errors for missing channel requirements. Always: budget first, campaign **PAUSED**, targeting, then the type's ad/asset layer. Present the full plan and get explicit user approval before the first mutate.

## Video (YouTube)

- Campaign: `"advertising_channel_type": "VIDEO"` + a bidding scheme (`target_cpm` / `maximize_conversions` per goal).
- Videos must be on YouTube — the Ads API cannot host video files. Register each with `google_ads_video_assets_link(customer_id, youtube_video_id)`.
- Ad group (`google_ads_ad_groups_create`), then a video ad via `google_ads_ad_group_ads_create` with the matching typed ad object (e.g. `video_responsive_ad` referencing the video asset).

## Demand Gen

- Campaign: `"advertising_channel_type": "DEMAND_GEN"`, `maximize_conversions` or `target_cpa`.
- Ad group, then `demand_gen_multi_asset_ad` / `demand_gen_carousel_ad` / `demand_gen_video_responsive_ad` on `google_ads_ad_group_ads_create` — images via `google_ads_image_assets_upload`, videos via YouTube link.

## Shopping

- Requires a linked Merchant Center account: `"shopping_setting": {"merchant_id": ...}` on the campaign body — the create is rejected without it. Find linked accounts by GAQL on `product_link`.
- `"advertising_channel_type": "SHOPPING"`. Standard Shopping: ad group + `shopping_product_ad` (no creative fields — products come from the feed) + listing-group criteria via `google_ads_ad_group_criteria_create` (`listing_group` field).

## App

- Campaign: `"advertising_channel_type": "MULTI_CHANNEL"` with `"app_campaign_setting": {"app_id": "...", "app_store": "GOOGLE_APP_STORE"|"APPLE_APP_STORE", "bidding_strategy_goal_type": ...}` — required, enforced by the validator.
- Assets (text/image/video) attach at campaign level; Google assembles the ads.

## Anything else

Every remaining resource has the same `google_ads_<resource>_<create|update|remove>` tools (conversion actions, user lists, bidding strategies, shared sets, labels, experiments, …); reads are GAQL; `google_ads_request` covers any uncovered endpoint.
