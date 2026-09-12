---
name: reddit-ads
description: Plan and create Reddit Ads campaigns end-to-end via the Hyper MCP — campaign, ad group, ad build order with subreddit / interest / geo targeting, promoted posts, custom and saved audiences, Reddit pixel conversion tracking, and reporting, with micro-currency budgets. Use when the user wants to launch Reddit ads, promote a Reddit post, target subreddits, set up a Reddit pixel, or pull Reddit ad reports. Also triggers on reddit campaign, reddit ppc, or reddit ads manager.
requires_toolkits:
  - reddit_ads
icon: reddit_ads
short_description: Plan and create Reddit Ads with promoted posts, targeting, pixels, and reporting.
---

# Reddit Ads Campaigns

Strategic guide for managing Reddit advertising via the Reddit Ads API v3. The toolkit is a raw-HTTP client, so parameter types must be sent exactly as documented — strings as strings, integers as integers, and all money in **micro-currency**.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Reddit Ads integration connected** (a Reddit Ads business account with ad account access) at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps).

If `reddit_ads_get_me` / `reddit_ads_list_businesses` is not found by `search`, stop and tell the user to enable Hyper MCP and connect Reddit Ads. Serving ads also requires an active **funding instrument** on the ad account — campaigns and ad groups can be created without one, but the account must be funded for ads to run.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call("<name>", {...})` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found, its integration is not connected or not enabled for the workspace: stop and tell the user which integration to connect.

## Out of scope — defer to other skills

- **Organic Reddit research** (mining subreddit discussions, pain points, voice-of-customer) → [`customer-research`](../customer-research).
- **Creative generation** (ad copy, images) → [`ad-creative-generation`](../ad-creative-generation).
- **Cross-platform campaign launches** → use this skill for Reddit, then invoke `meta-ads` / `google-ads` / `tiktok-ads` separately.

## Critical Rules

> **CRITICAL**: All budgets and bids are in **micro-currency**. $1.00 = 1,000,000 micros. A $50/day budget is `goal_value=50000000`; a $0.50 CPC is `bid_value=500000`. Never pass dollar amounts directly.

> **CRITICAL**: Create campaigns, ad groups, and ads with `configured_status="PAUSED"` (the toolkit default). Never launch live without explicit user review. Because everything defaults to PAUSED, you can build a full campaign and archive it without spending — ideal for demos.

> **CRITICAL**: Discovery flows through **businesses**, not a flat account list: `reddit_ads_get_me` → `reddit_ads_list_businesses` → `reddit_ads_list_ad_accounts(business_id=...)`. There is no top-level "list all ad accounts" call.

> **CRITICAL**: An **ad promotes a post** — it needs a `post_id` (or a `profile_id` + creation), not raw creative fields. Before creating an ad, find an existing post (`reddit_ads_list_posts`) or create one (`reddit_ads_create_post`). Only **community posts** can be promoted via the API.

> **CRITICAL**: The ad group `targeting.communities` array takes **subreddit NAMES, not the `t5_` IDs** that `search_targeting` returns. Use the `name` field from the search results: `"communities": ["marketing", "SaaS", "Entrepreneur"]` — passing `t5_...` IDs fails with "You cannot set invalid communities". (`interests` does use the IDs; `geolocations` uses country codes like `"US"`.)

> **CRITICAL**: Resolve targeting with `reddit_ads_search_targeting` before building — never guess values. `targeting` is a named parameter on `create_ad_group`; pass any other variant-heavy fields (audiences, schedule) via `input_data`.

> **CRITICAL**: `start_time` is **required when creating an ad group** (ISO 8601). On a **campaign**, `start_time` is only valid with CBO enabled — for non-CBO campaigns, omit it at the campaign level and set it on the ad group, or you get "Cannot set start_time for a campaign without having campaign budget optimization enabled."

> **CRITICAL**: `bid_value` is **always required** for `bid_type` CPC/CPM/CPV/CPV6 — even with `bid_strategy="MAXIMIZE_VOLUME"`. Set a cap (e.g. `bid_value=600000` = $0.60) or get one from `reddit_ads_generate_bid_suggestion`.

> **CRITICAL**: There is **no instant hard delete**. Reddit requires an entity to be **ARCHIVED for 3+ hours** before it can be permanently DELETED. `reddit_ads_delete_*` tries the real delete and **falls back to archiving** (which stops delivery) when it isn't deletable yet. Check the returned `configured_status` (ARCHIVED vs DELETED) and tell the user a hard delete is possible ~3h after archiving.

> **CRITICAL**: Reporting (`reddit_ads_get_report`) requires `fields`, `starts_at`, and `ends_at`. Spend metrics come back in **micro-currency**.

> **IMPORTANT**: Campaigns require `name`, `objective`, and (to serve) a `funding_instrument_id` — list them with `reddit_ads_list_funding_instruments`. Conversion-optimized ad groups need a `conversion_pixel_id` (`reddit_ads_list_pixels`). From **2026-07-13**, ad groups and CBO campaigns require `conversion_pixel_id`.

> **IMPORTANT**: Lead generation works as a campaign **objective** (`LEAD_GENERATION`), but lead-gen **form management is not available** via this toolkit (it needs a feature-gated scope) — build lead-gen forms in Reddit Ads Manager.

> **CRITICAL** (CONVERSIONS campaigns): the ad group `optimization_goal` is **required** and, for **standard (non-CBO) CONVERSIONS campaigns, the only accepted value is `CLICKS`**. `SIGN_UP`, `PAGE_VISIT`, `PURCHASE`, etc. are valid enum values but are **rejected for this campaign type** ("Conversion goal ... is not valid for Conversions Campaigns"). Reddit validates in two layers — enum membership, then campaign-type allowance. Use `optimization_goal="CLICKS"`; the CONVERSIONS objective still governs delivery.

> **CRITICAL** (post types): valid post `type` values are **`IMAGE`, `VIDEO`, `CAROUSEL`, `TEXT`** — **not `LINK`**. **`TEXT` posts are "free-form ads": they cannot carry a `click_url` and CANNOT be used in CONVERSIONS-campaign ads.** For any ad with a destination (especially CONVERSIONS), promote an **IMAGE / VIDEO / CAROUSEL** post.

> **CRITICAL** (creating posts with new media): prefer **`reddit_ads_create_structured_post`** — it takes media as a **URL that Reddit downloads and re-hosts**, so it needs no pre-uploaded asset. Creation is an **async job**: the tool polls up to `wait_seconds` (default 45) and returns the job; on `status="SUCCESS"` use `job.post_id` as the ad's `post_id`, else poll `reddit_ads_get_structured_post_job`. IMAGE needs `media_url` + `destination_url`; VIDEO also needs `thumbnail_url`; CAROUSEL takes 1–6 `{image_url, destination_url, ...}` cards; `PROMOTED_POST` promotes an existing SFW community post by id. `call_to_action` is a **display label** (`"Sign Up"`, `"Learn More"`), never `"SIGN_UP"`. The legacy **`reddit_ads_create_post`** cannot fetch media by URL — its `content[].media_url` must reference an **already-uploaded** Reddit asset (`reddit_ads_list_creative_assets`), CTA lives **inside `content[]`**, and TEXT posts must have an **empty** `content[]`. Use the legacy tool only to reuse an existing asset.

> **IMPORTANT**: Posts are **immutable** after creation except comments — to change headline/media/destination, create a new structured post. `reddit_ads_update_post(post_id=..., allow_comments=...)` only toggles comments (set `is_structured_post=True` for structured posts).

## Tool surface

| Group | Tools |
| --- | --- |
| Identity & discovery | `reddit_ads_get_me`, `reddit_ads_list_businesses`, `reddit_ads_list_ad_accounts`, `reddit_ads_get_ad_account`, `reddit_ads_list_funding_instruments` |
| Campaigns | `reddit_ads_list_campaigns`, `reddit_ads_get_campaign`, `reddit_ads_create_campaign`, `reddit_ads_update_campaign`, `reddit_ads_delete_campaign` |
| Ad groups | `reddit_ads_list_ad_groups`, `reddit_ads_get_ad_group`, `reddit_ads_create_ad_group`, `reddit_ads_update_ad_group`, `reddit_ads_delete_ad_group` |
| Ads | `reddit_ads_list_ads`, `reddit_ads_get_ad`, `reddit_ads_create_ad`, `reddit_ads_update_ad`, `reddit_ads_delete_ad` |
| Posts & creative | `reddit_ads_list_profiles`, `reddit_ads_get_profile`, `reddit_ads_list_posts`, `reddit_ads_create_post`, `reddit_ads_get_post`, `reddit_ads_update_post`, `reddit_ads_list_creative_assets`, `reddit_ads_get_creative_asset` |
| Structured posts (media by URL) | `reddit_ads_create_structured_post`, `reddit_ads_get_structured_post_job`, `reddit_ads_list_structured_posts`, `reddit_ads_get_structured_post` |
| Targeting | `reddit_ads_search_targeting`, `reddit_ads_suggest_keywords`, `reddit_ads_validate_keywords`, `reddit_ads_validate_geolocations` |
| Audiences | `reddit_ads_list_custom_audiences`, `reddit_ads_create_custom_audience`, `reddit_ads_get_custom_audience`, `reddit_ads_delete_custom_audience`, `reddit_ads_update_custom_audience_users`, `reddit_ads_list_saved_audiences`, `reddit_ads_create_saved_audience`, `reddit_ads_get_saved_audience`, `reddit_ads_update_saved_audience` |
| Pixels & Conversions API | `reddit_ads_list_pixels`, `reddit_ads_list_pixels_by_business`, `reddit_ads_post_conversion_events`, `reddit_ads_get_pixel_last_fired_at` |
| Forecasting & access | `reddit_ads_generate_bid_suggestion`, `reddit_ads_get_reach_forecast`, `reddit_ads_get_feature_access` |
| Apps / SKAdNetwork | `reddit_ads_list_apps`, `reddit_ads_get_skan_availability`, `reddit_ads_get_app_last_fired_at_report` |
| Reporting & history | `reddit_ads_get_report`, `reddit_ads_get_account_history` |

> **All reference files live in `references/`.** Read them at `references/<file>` (e.g. `references/discovery.md`).

## Routing table

| The user wants to… | Read these files first |
|---|---|
| Launch a Reddit campaign (any objective) | [references/discovery.md](references/discovery.md) → [references/campaign-creation.md](references/campaign-creation.md) |
| Promote a post / create a post (incl. media by URL) | [references/campaign-creation.md](references/campaign-creation.md) |
| Forecast reach before launch | [references/discovery.md](references/discovery.md) |
| Manage custom or saved audiences / resolve targeting | [references/audiences-and-targeting.md](references/audiences-and-targeting.md) |
| Set up pixel / Conversions API tracking | [references/conversions-and-reporting.md](references/conversions-and-reporting.md) |
| Pull reports / update or delete entities | [references/conversions-and-reporting.md](references/conversions-and-reporting.md) |
| Goal not yet clear | [references/discovery.md](references/discovery.md) — discovery clarifies the goal |

## Campaign Workflow

Discover business/account → audit account → research (objective, targeting, budget, post) → resolve targeting IDs → confirm strategy → create campaign (`PAUSED`) → create ad group → find/create post → create ad → review with user → activate (`update_*` to `ACTIVE`).

## Known Limitations

| Issue | Workaround |
| --- | --- |
| No instant hard delete; "A campaign must be archived before it can be deleted" / "cannot be deleted until three hours after it was archived" | Expected — `delete_*` auto-archives (stops delivery); hard delete is possible ~3h after archiving. Re-run delete later to remove permanently. |
| Ad creation needs a `post_id` | Promote an existing community post (`list_posts`) or create one (`create_post`); only community posts can be promoted via the API. |
| Conversion ad groups rejected without a pixel | Set `conversion_pixel_id` (from `list_pixels`). Required for ad groups / CBO from 2026-07-13. |
| Campaign won't serve | Attach a `funding_instrument_id` (from `list_funding_instruments`); the account must be funded. |
| Lead-gen forms can't be created via API | Build the form in Reddit Ads Manager; the API only sets the `LEAD_GENERATION` objective. |
| Variant create fields (targeting, schedule, creative) aren't named params | Pass them through `input_data` (a dict), which is merged into the request body. |
| No flat ad-account list | Discover via `get_me → list_businesses → list_ad_accounts(business_id)`. |
| `"You cannot set invalid communities: {t5_...}"` | The `targeting.communities` array wants subreddit **names**, not the `t5_` IDs from `search_targeting`. Use the `name` field. |
| `"Cannot set start_time ... without ... campaign budget optimization"` | Campaign-level `start_time` is CBO-only. Omit it on non-CBO campaigns; set `start_time` on the ad group. |
| Ad group create: `"Input should be a valid datetime"` on `start_time` | `start_time` is **required** on ad groups — always pass it. |
| `bid_value` demanded despite `MAXIMIZE_VOLUME` | `bid_value` is always required for CPC/CPM/CPV/CPV6. Provide a cap or use `generate_bid_suggestion`. |
| `generate_bid_suggestion`: `"Additional fields not permitted"` / `"'start_time' is a required property"` | `duration` is an ISO start/end range (`{"start_time": ..., "end_time": ...}`), not `{"days": N}`. |
| Varnish **503** on create | Transient Reddit backend error. Verify no duplicate was created (`list_campaigns`) before retrying. |
| `effective_status` shows `PENDING_APPROVAL` right after create | Normal even for PAUSED entities (ad review) — it clears automatically; not a failure. |
| CONVERSIONS ad group: `"Conversion goal (optimization goal) is required"` / `"... is not valid for Conversions Campaigns"` | `optimization_goal` is required and, for non-CBO CONVERSIONS, must be `CLICKS` (SIGN_UP/PAGE_VISIT/PURCHASE are rejected for this campaign type). |
| `"'LINK' is not one of [CAROUSEL, IMAGE, TEXT, VIDEO]"` | Post `type` must be IMAGE/VIDEO/CAROUSEL/TEXT — there is no LINK type. |
| Ad create: `"Posts used for ads in Conversion campaigns cannot be free-form ad"` / `"Free form ads cannot have a click url"` | TEXT posts are free-form — use IMAGE/VIDEO/CAROUSEL for CONVERSIONS ads. |
| IMAGE post: `"Image is required"` | With legacy `create_post`, put the asset in `content[].media_url` (an already-uploaded Reddit asset from `list_creative_assets`); a `post_url` alone is not enough. To create from a fresh media URL, use `reddit_ads_create_structured_post` instead. |
| Structured post job not done yet (`status` `QUEUED`/`PROCESSING`) | Creation is async; the create tool polls to `wait_seconds` (default 45). If still pending, poll `reddit_ads_get_structured_post_job(post_creation_job_id=...)` until `SUCCESS` (then use `post_id`) or `CLIENT_ERROR`/`SERVER_ERROR` (read `error_message`). |
| Need to change a post's headline/media/destination | Not possible — posts are immutable. Create a new structured post. `reddit_ads_update_post` only toggles `allow_comments`. |
| Post: `call_to_action "Additional fields not permitted"` | `call_to_action` belongs **inside `content[]`**, not top-level, and uses display labels (`"Sign Up"`), not enum constants (`"SIGN_UP"`). |
| TEXT post: `"Post content must be empty for this post type"` | TEXT posts can't carry a `content[]` block — only IMAGE/VIDEO/CAROUSEL do. |
| Dollar amounts | Always micro-currency (×1,000,000). |

## Safety Rules

**Never:**

- Assume business, ad account, campaign, post, pixel, or targeting IDs — look them up or ask.
- Skip the account audit phase.
- Create campaigns, ad groups, or ads without explicit user approval.
- Set anything to `ACTIVE` without user consent.
- Pass dollar amounts instead of micro-currency.
- Create an ad without a valid `post_id`.
- Promise an instant permanent delete — Reddit requires ARCHIVED for 3+ hours first.
- Guess targeting IDs — resolve them with `reddit_ads_search_targeting`.
