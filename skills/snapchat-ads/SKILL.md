---
name: snapchat-ads
description: Plan and create Snapchat Ads campaigns end-to-end via the Hyper MCP — campaign, ad squad, ad build order with media upload, creatives, targeting, Snap Pixel conversion tracking, and sync / async reporting, using micro-currency budgets and JSON-Patch partial updates. Use when the user wants to launch Snapchat ads, build ad squads, upload Snap creatives, set up Snap Pixel tracking, or analyze Snapchat ad performance. Also triggers on snap ads, snapchat campaign, or snapchat ads manager.
icon: snapchat_ads
short_description: Plan and create Snapchat Ads with ad squads, creatives, Snap Pixel, and reporting.
---

# Snapchat Ads Campaigns

Strategic guide for managing Snapchat advertising via the Snapchat Marketing API v1. The toolkit is a raw-HTTP client, so parameter types must be sent exactly as documented — strings as strings, integers as integers, and all money in **micro-currency**.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Snapchat Ads integration connected** (a Snap Business account with ad account access) at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

If `snapchat_ads_list_organizations` is not in the tool list, stop and tell the user to enable Hyper MCP and connect Snapchat Ads. Creating ad squads or serving ads also requires an **active funding source** on the ad account — campaigns, media, and creatives can be created without one.

## Out of scope — defer to other skills

- **Creative generation** (ad copy, images, video) → [`ad-creative-generation`](../ad-creative-generation) / [`video-generation`](../video-generation).
- **Cross-platform campaign launches** → use this skill for Snapchat, then invoke `meta-ads` / `tiktok-ads` separately.

## Critical Rules

> **CRITICAL**: All budgets and bids are in **micro-currency**. $1.00 = 1,000,000 micros. $50/day = `50000000`. Never pass dollar amounts directly. Minimum campaign daily budget / lifetime spend cap is **$20** (`20000000`).

> **CRITICAL**: Create campaigns, ad squads, and ads with `status="PAUSED"`. Never launch live without explicit user review. Because everything defaults to PAUSED, you can build a full campaign and delete it without spending — ideal for demos.

> **CRITICAL**: Updates are **JSON-Patch partial updates** — pass only the fields you want to change, parented on the PARENT entity. `snapchat_ads_update_campaign` needs `ad_account_id`; `snapchat_ads_update_ad_squad` needs `campaign_id` (NOT ad_account_id); `snapchat_ads_update_ad` needs `ad_squad_id`.

> **CRITICAL**: Account-level stats (`entity_type="adaccounts"`) only support `fields="spend"`. For impressions / swipes / conversions, query at the **campaign, adsquad, ad, creative, or media** level.

> **CRITICAL**: There is **no `time_range` preset** (e.g. `LAST_30_DAYS` does not exist). Pass `start_time` and `end_time` (ISO 8601). Omitting both returns **lifetime** totals, not a recent window.

> **CRITICAL**: Ad squad `billing_event` is always `IMPRESSION`. `bid_micro` is required for `bid_strategy="LOWEST_COST_WITH_MAX_BID"` and `"TARGET_COST"`; omit it for `"AUTO_BID"`.

> **IMPORTANT**: Creating an ad squad requires an active **funding source** on the ad account. If the account is PENDING / unfunded, ad squad creation fails — that is a billing state, not a bug.

> **IMPORTANT**: Creatives require `top_snap_media_id` (an uploaded media id) and a `headline` (≤ 34 chars). `brand_name` is ≤ 32 chars.

## Tool surface

| Group | Tools |
| --- | --- |
| Org & accounts | `snapchat_ads_list_organizations`, `snapchat_ads_list_ad_accounts`, `snapchat_ads_get_ad_account` |
| Campaigns | `snapchat_ads_list_campaigns`, `snapchat_ads_get_campaign`, `snapchat_ads_create_campaign`, `snapchat_ads_update_campaign`, `snapchat_ads_delete_campaign` |
| Ad squads | `snapchat_ads_list_ad_squads`, `snapchat_ads_get_ad_squad`, `snapchat_ads_create_ad_squad`, `snapchat_ads_update_ad_squad`, `snapchat_ads_delete_ad_squad`, `snapchat_ads_estimate_ad_squad_outcomes` |
| Ads | `snapchat_ads_list_ads`, `snapchat_ads_get_ad`, `snapchat_ads_create_ad`, `snapchat_ads_update_ad`, `snapchat_ads_delete_ad` |
| Creatives | `snapchat_ads_list_creatives`, `snapchat_ads_get_creative`, `snapchat_ads_create_creative` |
| Media | `snapchat_ads_list_media`, `snapchat_ads_create_media`, `snapchat_ads_upload_media` |
| Reporting | `snapchat_ads_get_stats`, `snapchat_ads_create_stats_report`, `snapchat_ads_get_stats_report` |
| Conversion | `snapchat_ads_list_pixels`, `snapchat_ads_list_custom_conversions` |
| Targeting | `snapchat_ads_search_targeting` |

> **All reference files live in `references/`.** Read them at `references/<file>` (e.g. `references/discovery.md`).

## Routing table

| The user wants to… | Read these files first |
|---|---|
| Launch a Snapchat campaign | [references/discovery.md](references/discovery.md) → [references/campaign-creation.md](references/campaign-creation.md) |
| Upload media / create creatives / ad squads / ads | [references/campaign-creation.md](references/campaign-creation.md) |
| Resolve targeting (geo, demo, interests, devices) | [references/targeting.md](references/targeting.md) |
| Set up Snap Pixel / custom conversions | [references/conversions-and-reporting.md](references/conversions-and-reporting.md) |
| Pull stats / async reports / update or delete entities | [references/conversions-and-reporting.md](references/conversions-and-reporting.md) |
| Goal not yet clear | [references/discovery.md](references/discovery.md) — discovery clarifies the goal |

## Campaign Workflow

Discover org/account → audit account → research (objective, audience, budget, assets) → confirm strategy → create campaign (`PAUSED`) → upload media → create creative → create ad squad → create ad → review with user → activate (`update_*` to `ACTIVE`).

## Known Limitations

| Issue | Workaround |
| --- | --- |
| Creative creation fails (historically a silent null error) | Almost always a missing `profile_properties.profile_id` (required for ALL creative types) — pull one from `list_creatives`. The tool now raises a clear error instead of a null "success". |
| Ad creation fails with a type mismatch | Omit `type` so it's derived from the creative (WEB_VIEW → REMOTE_WEBPAGE, etc.). |
| Forecast returns OE101 / UNSUPPORTED_DELIVERY_CONSTRAINT | The tool auto-adds `delivery_constraint`; if it persists, outcome estimation is unavailable for the account type (often PARTNER) — use the Ads Manager reach planner. |
| DAY-granularity stats reject the time range (E1008) | Handled automatically — pass `ad_account_id` to `get_stats`/`create_stats_report` and the tool aligns to account-timezone midnight + hour boundaries. |
| Media rejected with E2601 ("cannot be used to create any creative type") | The file doesn't meet specs — use a 1080×1920 (9:16) PNG/JPG ≤ 5 MB image or 1080×1920 MP4/MOV. Re-generate the asset at the right size, re-upload, and confirm `media_status` is `READY`. |
| Upload fails on file_path / internal URL (Errno 2 / DNS error) | Pass `file_id` (the Hyper file id) instead — it reads from storage directly. Avoid server-local paths and internal `files.*` URLs. |
| Account-level stats reject non-`spend` fields (error E1008) | Query other metrics at campaign/adsquad/ad/creative/media level. |
| No `time_range`/date preset | Pass `start_time` + `end_time`; omitting them returns lifetime totals. |
| Ad squad creation fails on unfunded accounts | Add a funding source; campaigns/media/creatives still work without one. |
| `bid_micro` required for non-AUTO_BID strategies | Provide `bid_micro` for `LOWEST_COST_WITH_MAX_BID` / `TARGET_COST`. |
| Media > 32 MB | Handled automatically (chunked upload, up to 1 GB). |
| Partial updates | Use the update tools (PATCH) with the correct parent id — never resend the whole object. |

## Safety Rules

**Never:**

- Assume organization, ad account, campaign, media, or creative IDs — look them up or ask.
- Skip the account audit phase.
- Create campaigns, ad squads, or ads without explicit user approval.
- Set anything to `ACTIVE` without user consent.
- Pass dollar amounts instead of micro-currency.
- Query non-`spend` metrics at the `adaccounts` level.
- Use a `time_range` preset — always pass `start_time`/`end_time`.
- Use `LOWEST_COST_WITH_MAX_BID` / `TARGET_COST` without `bid_micro`.
- Pass the wrong parent id to update tools (ad squad → `campaign_id`, ad → `ad_squad_id`).
