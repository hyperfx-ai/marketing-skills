---
name: meta-ads
description: Plan, create, and review Meta (Facebook + Instagram) advertising campaigns through the Hyper MCP. Use when the user wants to launch Meta ads, run Partnership Ads or branded-content ads, promote creator posts, use Instagram Partnership Ad codes, configure Advantage+, analyze performance, audit an account, or build dashboards.
requires_toolkits:
  - meta_ads
  - meta_business
icon: meta_ads
short_description: Create Meta campaigns and Partnership Ads; audit performance and build dashboards.
---

# Meta Ads

Strategic guide for creating and managing Meta advertising campaigns, Partnership Ads, performance analysis, and dashboards. **Default to Advantage+** unless the user explicitly requests manual control.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Competitor or public ad research (Meta Ads Library) | `meta-ads-library` |
| Ad creative generation (images, copy variants) | `ad-creative-generation` |
| Google Ads campaigns | `google-ads` |
| Pinterest / TikTok / Amazon paid campaigns | `pinterest-ads`, `tiktok-ads`, `amazon-ads` |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Meta Business integration connected** (Facebook + Instagram, with at least one ad account and one Page) at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps).
- **Firecrawl integration connected** for site research and screenshot grounding (discovery phase).

If `meta_ads_adaccount_list` is not in the tool list, stop and tell the user to enable Hyper MCP and connect Meta Business.

If you suspect a connection issue (missing ad accounts, page publishing failures, or permission errors), call `meta_ads_health_check()` and report the diagnostics before proceeding.

## Tool names

Use the **exact tool name from your connected tool list**. Canonical names are `meta_ads_*` (listed below). On Hyper platform chat, legacy `meta_business_*` names (e.g. `meta_business_list_ad_accounts`) and the retired plural names (e.g. `meta_ads_campaigns_create`) resolve to the same tools via aliases — if a call fails with "tool not found", search the live catalog for the canonical name.

| Group | Tools |
| --- | --- |
| Discovery | `meta_ads_adaccount_list`, `meta_ads_owned_pages_list`, `meta_ads_pages_search`, `meta_accounts_list`, `meta_ads_instagram_accounts_list` |
| Health & sync | `meta_ads_health_check`, `meta_ads_health_get` |
| Tracking assets | `meta_ads_ad_pixels_list`, `meta_ads_ad_pixels_get`, `meta_ads_custom_audiences_list`, `meta_ads_lookalike_audiences_list`, `meta_ads_targeting_search` |
| Step-by-step creation (preferred) | `meta_ads_campaign_create`, `meta_ads_adset_create`, `meta_ads_ad_create`, `meta_ads_ad_images_upload`, `meta_ads_ad_videos_upload`, `meta_ads_creative_create` |
| Read & preview | `meta_ads_campaign_get`, `meta_ads_campaigns_search`, `meta_ads_adset_list`, `meta_ads_ad_list`, `meta_ads_ad_get`, `meta_ads_ad_previews_get` |
| Partnership Ads | `meta_ads_partnership_ad_partners_list`, `meta_ads_partnership_advertisable_content_list`, `meta_ads_partnership_ad_validate`, `meta_ads_partnership_ad_create`, `meta_ads_partnership_existing_post_validate`, `meta_ads_partnership_existing_post_create` |
| Managed Page content | `meta_ads_page_posts_list`, `meta_ads_page_post_comments_list` |
| Insights & dashboards | `meta_ads_insights_get`, `hyper_data_build_dashboard`, `database_query` |
| Launch & edits | `meta_ads_campaigns_activate`, `meta_ads_campaign_update`, `meta_ads_adset_update`, `meta_ads_ad_update` |
| Automated rules | `meta_ads_adrule_create`, `meta_ads_adrule_list`, `meta_ads_adrule_get`, `meta_ads_adrule_update`, `meta_ads_adrule_delete`, `meta_ads_adrule_history_list` |
| Site research | `firecrawl_branding_extract`, `firecrawl_screenshots_create` |

CLI users: translate tool names with the `hyper-cli` skill (`hyperai search "<tool name>"`).

---

## Rules that must never be forgotten

> **BUDGETS IN CENTS**: $20.00 = 2000. $5.50 = 550. $100 = 10000. Never pass dollar amounts directly.

> **ACTIVATE, DON'T UPDATE**: Use `meta_ads_campaigns_activate(campaign_id)` to go live. Never `meta_ads_campaign_update(status="ACTIVE")` — that silently leaves ad sets and ads PAUSED so nothing serves.

> **ALWAYS START PAUSED**: Create campaigns with `status="PAUSED"`. Never launch live without user review.

> **PARTNERSHIP ADS USE DEDICATED TOOLS**: Read [references/partnership-ads.md](references/partnership-ads.md). Existing creator posts and Instagram Partnership Ad codes use `meta_ads_partnership_existing_post_validate` and `meta_ads_partnership_existing_post_create`. Newly uploaded media uses `meta_ads_partnership_ad_validate` and `meta_ads_partnership_ad_create` and requires exactly one `image_hash` or `video_id`. Never swap the creator publishing identity with the brand sponsor identity.

> **BUILD STEP BY STEP**: Create campaigns with the individual tools — `meta_ads_campaign_create` → `meta_ads_adset_create` → `meta_ads_creative_create` → `meta_ads_ad_create`, capturing each id from the previous response. (The old blueprint tools were removed.) The tools validate requests before sending — campaign objective rules, bid-strategy/bid-amount pairing, billing-event/optimization-goal compatibility, budget coherence — but objective-specific ad-set fields (`optimization_goal`, `promoted_object`) are YOUR responsibility: match them to the campaign objective using the reference file for the campaign type.

> **REGULATED ADVERTISERS NEED `special_ad_categories`**: For gambling, financial, housing, employment, credit, or political advertisers, declare the category on `meta_ads_campaign_create` (e.g. `special_ad_categories=["ONLINE_GAMBLING_AND_GAMING"]`).

> **FIXED RUN WINDOWS GO ON THE AD SET**: When the user gives a run duration or dates ("run it for 7 days", "through end of month"), set `start_time` AND `end_time` (ISO 8601) on `meta_ads_adset_create`. A daily-budget ad set with no `end_time` runs continuously until manually paused — the requested window is silently lost.

> **GROUND COPY IN THE DESTINATION PAGE (RESEARCH FIRST)**: When the brief centers on a URL ("build a campaign for https://..."), fetch that page FIRST (`web_pages_fetch`) — before discovery and before writing any copy — and ground ad copy in what the page actually says (product name, value props, offer). Never invent copy for a page you have not read; even when the user supplies exact copy or headlines, fetch the page to verify the destination matches the offer.

> **EU-TARGETED AD SETS NEED DSA FIELDS**: If an ad set targets the EU, set `dsa_beneficiary` and `dsa_payor` on `meta_ads_adset_create` (who benefits from / pays for the ad) — required under the EU Digital Services Act, or delivery is restricted.

> **UTMs ON EVERY DESTINATION AD (`url_tags`)**: Set `url_tags` (UTM params, e.g. `utm_source=meta&utm_medium=paid&utm_campaign=...`) on every creative that drives to a destination — downstream measurement (e.g. AppsFlyer + a data warehouse) stitches on these, so an ad without UTMs is effectively unmeasurable. Use the advertiser's canonical template; if you don't have one, ask rather than ship untracked.

See [references/constraints.md](references/constraints.md) for the full constraint set.

> **All reference files live in `references/`.** Read them at `references/<file>` (e.g. `references/discovery.md`). They are not in the same directory as this SKILL.md.

---

## Core process

Every task follows this sequence. Do not skip steps.

1. **Identify the goal** — creation, analysis, or both?
2. **Check the routing table** and read the referenced files before calling any tools
3. **Make a written plan** — state campaign type, budget in cents, optimization goal, and sequence of steps; for Partnership Ads also state source type, creator, sponsor, ad account, ad set, and destination; show it before acting
4. **Execute step by step**, re-checking [references/constraints.md](references/constraints.md) at each creation step
5. **Show ad previews** before activation
6. **Activate only when the user approves** using `meta_ads_campaigns_activate()`

**Automated / scheduled runs:** If there is no user present to interact with (e.g. a scheduled task), skip steps 3 and 6. Do not write a plan and wait for confirmation — proceed directly. Do not activate unless activation was explicitly included in the task instructions.

---

## Routing table

| The user wants to… | Read these files first |
|---|---|
| Create a sales / conversion campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/sales.md](references/campaigns/sales.md) |
| Create a leads campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/leads.md](references/campaigns/leads.md) |
| Create a traffic campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/traffic.md](references/campaigns/traffic.md) |
| Create an awareness or engagement campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/awareness-engagement.md](references/campaigns/awareness-engagement.md) |
| Create an app promotion campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/app-promotion.md](references/campaigns/app-promotion.md) |
| Create a campaign (any objective) | [references/discovery.md](references/discovery.md) → the matching `references/campaigns/*.md` above, then build step by step |
| Discover authorized partners or eligible partner content | [references/partnership-ads.md](references/partnership-ads.md) |
| Validate or create a Partnership Ad from an existing post or ad code | [references/partnership-ads.md](references/partnership-ads.md) |
| Validate or create a new Partnership Ad from uploaded media | [references/partnership-ads.md](references/partnership-ads.md) |
| Read managed Facebook Page posts or comments | [references/partnership-ads.md](references/partnership-ads.md#managed-page-content) |
| Analyze performance / query insights | [references/analytics.md](references/analytics.md) |
| Audit an account / find optimization opportunities | [references/account-audit.md](references/account-audit.md) |
| Set up automated rules (auto-pause, budget guards, alerts) | [references/automated-rules.md](references/automated-rules.md) |
| Build a Meta dashboard or data app | [references/analytics.md](references/analytics.md) → [references/dashboards.md](references/dashboards.md) |
| Analyze performance, then create a campaign | [references/analytics.md](references/analytics.md) → [references/discovery.md](references/discovery.md) → relevant campaign file |
| Build a funnel / multiple campaigns at once (TOF/MOF/BOF) | [references/multi-campaign-funnel.md](references/multi-campaign-funnel.md) → [references/discovery.md](references/discovery.md) → per-tier campaign files |
| Objective not yet known | [references/discovery.md](references/discovery.md) — discovery clarifies the goal |

---

## Worked examples

- Full sales campaign (ecommerce, Advantage+, step-by-step): [references/examples/sales-ecommerce.md](references/examples/sales-ecommerce.md)
- Full leads campaign (B2B SaaS, website pixel, step-by-step): [references/examples/leads-form.md](references/examples/leads-form.md)
