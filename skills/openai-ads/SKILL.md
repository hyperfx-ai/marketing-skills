---
name: openai-ads
description: Plan and manage OpenAI Ads (ChatGPT ads) campaigns end-to-end via the Hyper MCP — API-key auth, account discovery, geo targeting, image upload, chat_card and product-feed creatives, custom audiences, conversion tracking, status flow, and insights, with integer-micros money values. Use when the user wants to launch OpenAI ads, ChatGPT ads, chat card ads, manage OpenAI ad groups or audiences, or pull OpenAI Ads insights.
icon: openai_ads
short_description: Plan and manage OpenAI Ads with chat cards, product feeds, audiences, and insights.
---

# OpenAI Ads Campaigns

Strategic guide for managing the OpenAI Advertiser API. All operations go
through `https://api.ads.openai.com/v1`.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **OpenAI Ads integration connected** (an OpenAI Ads API key, scoped to one ad account) at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps).

If `openai_ads_ad_accounts_get` is not in the tool list, stop and tell the user to enable Hyper MCP and connect OpenAI Ads. After connecting, `openai_ads_health_check()` verifies the key — if `connected=false`, the API key is missing, invalid, or expired.

## Out of scope — defer to other skills

- **Creative generation** (ad imagery, copy) → [`ad-creative-generation`](../ad-creative-generation) / [`image-generation`](../image-generation).
- **Cross-platform campaign launches** → use this skill for OpenAI Ads, then invoke `meta-ads` / `google-ads` separately.

## Critical Rules

> **CRITICAL**: Auth is bearer API-key auth, not OAuth. One Ads API key is
> scoped to exactly one ad account. There is no `list ad accounts` endpoint;
> `openai_ads_ad_accounts_get` returns the connected account for that key.

> **CRITICAL**: All money values on inputs are **integer micros**.
> `$1.00 = 1_000_000` micros. `$50/day = 50_000_000`. The
> `daily_spend_limit_micros` minimum is `1_000_000` ($1). The ad group
> `max_bid_micros` is capped at `100_000_000` ($100). Insights responses use
> plain floats in account currency, not micros.

> **CRITICAL**: Always create campaigns, ad groups, and ads with
> `status="paused"`. Surface what was created to the user, then activate
> using the dedicated activate endpoint after approval.

> **CRITICAL**: Ads have `review_status`. New ads enter `in_review` and will
> not serve until `review_status="approved"`, even if `status="active"`.

> **CRITICAL**: `chat_card` creatives require `target_url` and `file_id`.
> Upload the image first via `openai_ads_images_upload`, then pass the returned
> `file_id` to `openai_ads_create`. PNG, 1024x1024, <= 1 MB.

> **IMPORTANT**: Creative types are `chat_card` and `product_ad_template`.
> Product-ad templates get image and destination URL from the selected product
> feed item, so they do not require `file_id` or `target_url`.

> **IMPORTANT**: Campaign `bidding_type` can be `impressions` or `clicks`.
> Ad group `billing_event_type` can be `impression` or `click`.

## Tool surface

| Job | Tools |
| --- | --- |
| Account | `openai_ads_ad_accounts_get`, `openai_ads_update_ad_account`, `openai_ads_activate_ad_account`, `openai_ads_pause_ad_account`, `openai_ads_health_check` |
| Campaigns | `openai_ads_campaigns_create`, `openai_ads_campaigns_get`, `openai_ads_campaigns_list`, `openai_ads_campaigns_update`, `openai_ads_campaigns_pause`, `openai_ads_campaigns_activate`, `openai_ads_campaigns_archive` |
| Ad groups | `openai_ads_ad_groups_create`, `openai_ads_ad_groups_get`, `openai_ads_ad_groups_list`, `openai_ads_ad_groups_update`, `openai_ads_ad_groups_pause`, `openai_ads_ad_groups_activate`, `openai_ads_ad_groups_archive` |
| Ads | `openai_ads_create`, `openai_ads_get`, `openai_ads_list`, `openai_ads_update`, `openai_ads_pause`, `openai_ads_activate`, `openai_ads_archive` |
| Images & targeting | `openai_ads_images_upload`, `openai_ads_search_geo_locations` |
| Audiences | `openai_ads_create_custom_audience`, `openai_ads_create_custom_audience_upload`, `openai_ads_get_custom_audience`, `openai_ads_list_custom_audiences`, `openai_ads_archive_custom_audience` |
| Conversions | `openai_ads_create_conversion_pixel`, `openai_ads_create_conversion_api_key`, `openai_ads_create_conversion_event_setting`, `openai_ads_list_conversion_event_settings`, `openai_ads_get_conversion_insights` |
| Insights | `openai_ads_account_insights_get`, `openai_ads_campaign_insights_get`, `openai_ads_ad_group_insights_get`, `openai_ads_insights_get` |
| Cache snapshot | `openai_ads_cache`, `openai_ads_caches_get`, `openai_ads_caches_refresh` |

## Phase 1: Account Discovery

Run these after connect:

```text
openai_ads_ad_accounts_get()
openai_ads_campaigns_list(limit=100)
openai_ads_list_custom_audiences(limit=100)
openai_ads_list_conversion_event_settings(limit=100)
```

The connect-time context builder may have already populated a cached snapshot.
Prefer:

```text
openai_ads_caches_get()
```

If `success=False` because the cache is empty, refresh once:

```text
openai_ads_caches_refresh()
```

## Phase 2: Plan and Confirm

Before creating anything, confirm with the user:

- Objective in plain language.
- Daily and/or lifetime budget in account currency.
- Target geos: simple country codes like `["US", "GB"]`, or location IDs from `openai_ads_search_geo_locations`.
- Any custom audiences to include or exclude.
- Whether this is a normal `chat_card` campaign or a product-feed campaign.
- Headline (`title`, <= 50 chars), body (<= 100 chars), and click-through URL for `chat_card`.
- One image asset for `chat_card`, either a public URL or a base64 blob.
- Max bid in micros (`max_bid_micros`; for example `2_000_000`).
- Optional `context_hints`, short natural-language phrases that describe when the ad should show.
- Optional conversion event setting IDs to attach to the campaign.

If anything is missing, ask. Do not invent budgets, geos, or copy.

> **All reference files live in `references/`.** Read them at `references/<file>` (e.g. `references/campaign-creation.md`).

## Routing table

| The user wants to… | Read these files first |
|---|---|
| Launch a chat card or product-feed campaign | Phases 1–2 above → [references/campaign-creation.md](references/campaign-creation.md) |
| Target regions / DMAs / custom geo | [references/campaign-creation.md](references/campaign-creation.md) — Geo Targeting |
| Create or manage custom audiences | [references/audiences-and-conversions.md](references/audiences-and-conversions.md) |
| Set up conversion tracking (pixel, API key, event settings) | [references/audiences-and-conversions.md](references/audiences-and-conversions.md) |
| Activate after review | [references/campaign-creation.md](references/campaign-creation.md) — Activation |
| Pull insights / manage status / refresh the cache snapshot | [references/insights-and-operations.md](references/insights-and-operations.md) |

## Safety Rules

**Never:**

- Pass dollar amounts directly. All money inputs are micros.
- Activate a campaign, ad group, ad, or account without explicit user approval.
- Skip image upload for a `chat_card`; it needs a real `file_id`.
- Use geo exclusions; use included geos and audience exclusions instead.
- Assume an ad is delivering just because `status="active"`. Always check `review_status`.
- Treat `archive` as reversible.
- Promise paid traffic on a new ad. New ads sit in `review_status="in_review"` until OpenAI approves them.
