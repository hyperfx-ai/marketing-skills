---
name: meta-ads
description: Plan and create Meta (Facebook + Instagram) advertising campaigns end-to-end via the Hyper MCP, defaulting to Advantage+ automation. Use when the user wants to launch Meta ads, Facebook ads, Instagram ads, Advantage+ campaigns, carousel ads, dynamic creative ads, set up Meta conversion tracking, analyze performance, audit a Meta ads account, or build Meta performance dashboards. Also triggers on phrases like meta campaign, facebook campaign, advantage+, meta account audit, or meta blueprint.
icon: meta_ads
short_description: Plan and create Meta ad campaigns with Advantage+ defaults, audits, and dashboards.
---

# Meta Ads

Strategic guide for creating and managing Meta advertising campaigns, analyzing performance, and building dashboards from cached data. **Default to Advantage+** unless the user explicitly requests manual control.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Competitor or public ad research (Meta Ads Library) | `meta-ads-library` |
| Ad creative generation (images, copy variants) | `ad-creative-generation` |
| Google Ads campaigns | `google-ads` |
| Pinterest / TikTok / Amazon paid campaigns | `pinterest-ads`, `tiktok-ads`, `amazon-ads` |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Meta Business integration connected** (Facebook + Instagram, with at least one ad account and one Page) at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).
- **Firecrawl integration connected** for site research and screenshot grounding (discovery phase).

If `meta_ads_ad_accounts_list` is not in the tool list, stop and tell the user to enable Hyper MCP and connect Meta Business.

If you suspect a connection issue (missing ad accounts, page publishing failures, or permission errors), call `meta_ads_health_check()` and report the diagnostics before proceeding.

## Tool names

Use the **exact tool name from your connected tool list**. Canonical names are `meta_ads_*` (listed below). On Hyper platform chat, legacy `meta_business_*` aliases (e.g. `meta_business_list_ad_accounts`) resolve to the same tools — if a call fails with "tool not found", search the live catalog for the canonical name.

| Group | Tools |
| --- | --- |
| Discovery | `meta_ads_ad_accounts_list`, `meta_ads_owned_pages_list`, `meta_ads_pages_search`, `meta_accounts_list`, `meta_ads_instagram_accounts_list` |
| Health & sync | `meta_ads_health_check`, `meta_business_sync` |
| Tracking assets | `meta_ads_ad_pixels_list`, `meta_ads_ad_pixels_get`, `meta_ads_custom_audiences_list`, `meta_ads_lookalike_audiences_list`, `meta_ads_targeting_search` |
| Step-by-step creation (preferred) | `meta_ads_campaigns_create`, `meta_ads_ad_sets_create`, `meta_ads_create`, `meta_ads_ad_images_upload`, `meta_ads_ad_creatives_create` |
| Blueprint path (avoid — see rule below) | `meta_ads_blueprints_preview`, `meta_ads_campaign_blueprints_create` |
| Read & preview | `meta_ads_campaigns_get`, `meta_ads_campaigns_search`, `meta_ads_ad_sets_list`, `meta_ads_list`, `meta_ads_get`, `meta_ads_ad_previews_get` |
| Insights & dashboards | `meta_ads_insights_get`, `meta_business_sync`, `hyper_data_build_dashboard`, `database_query` |
| Launch & edits | `meta_ads_campaigns_activate`, `meta_ads_campaigns_update`, `meta_ads_ad_sets_update`, `meta_ads_update` |
| Site research | `firecrawl_branding_extract`, `firecrawl_screenshots_create` |

CLI users: translate tool names with the `hyper-cli` skill (`hyperai search "<tool name>"`).

---

## Rules that must never be forgotten

> **BUDGETS IN CENTS**: $20.00 = 2000. $5.50 = 550. $100 = 10000. Never pass dollar amounts directly.

> **ACTIVATE, DON'T UPDATE**: Use `meta_ads_campaigns_activate(campaign_id)` to go live. Never `meta_ads_campaigns_update(status="ACTIVE")` — that silently leaves ad sets and ads PAUSED so nothing serves.

> **ALWAYS START PAUSED**: Create campaigns with `status="PAUSED"`. Never launch live without user review.

> **BUILD STEP BY STEP, NOT VIA BLUEPRINT**: Create campaigns with the individual tools — `meta_ads_campaigns_create` → `meta_ads_ad_sets_create` → `meta_ads_ad_creatives_create` → `meta_ads_create`, capturing each id from the previous response. Do NOT use the blueprint tools (`meta_ads_blueprints_preview` / `meta_ads_campaign_blueprints_create`). The step-by-step tools validate each object against its campaign objective (e.g. they enforce the correct `optimization_goal` and `promoted_object`), so mistakes are caught up front instead of silently producing an invalid campaign.

> **REGULATED ADVERTISERS NEED `special_ad_categories`**: For gambling, financial, housing, employment, credit, or political advertisers, declare the category on `meta_ads_campaigns_create` (e.g. `special_ad_categories=["ONLINE_GAMBLING_AND_GAMING"]`). The blueprint cannot set this — another reason regulated builds use the step-by-step path.

> **EU-TARGETED AD SETS NEED DSA FIELDS**: If an ad set targets the EU, set `dsa_beneficiary` and `dsa_payor` on `meta_ads_ad_sets_create` (who benefits from / pays for the ad) — required under the EU Digital Services Act, or delivery is restricted.

> **UTMs ON EVERY DESTINATION AD (`url_tags`)**: Set `url_tags` (UTM params, e.g. `utm_source=meta&utm_medium=paid&utm_campaign=...`) on every creative that drives to a destination — downstream measurement (e.g. AppsFlyer + a data warehouse) stitches on these, so an ad without UTMs is effectively unmeasurable. Use the advertiser's canonical template; if you don't have one, ask rather than ship untracked.

See [references/constraints.md](references/constraints.md) for the full constraint set.

> **All reference files live in `references/`.** Read them at `references/<file>` (e.g. `references/discovery.md`). They are not in the same directory as this SKILL.md.

---

## Core process

Every task follows this sequence. Do not skip steps.

1. **Identify the goal** — creation, analysis, or both?
2. **Check the routing table** and read the referenced files before calling any tools
3. **Make a written plan** — state campaign type, budget in cents, optimization goal, and sequence of steps; show it before acting
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
| Analyze performance / query insights | [references/analytics.md](references/analytics.md) |
| Audit an account / find optimization opportunities | [references/account-audit.md](references/account-audit.md) |
| Build a Meta dashboard or data app | [references/analytics.md](references/analytics.md) → [references/dashboards.md](references/dashboards.md) |
| Analyze performance, then create a campaign | [references/analytics.md](references/analytics.md) → [references/discovery.md](references/discovery.md) → relevant campaign file |
| Build a funnel / multiple campaigns at once (TOF/MOF/BOF) | [references/multi-campaign-funnel.md](references/multi-campaign-funnel.md) → [references/discovery.md](references/discovery.md) → per-tier campaign files |
| Objective not yet known | [references/discovery.md](references/discovery.md) — discovery clarifies the goal |

---

## Worked examples

- Full sales campaign (ecommerce, Advantage+, step-by-step): [references/examples/sales-ecommerce.md](references/examples/sales-ecommerce.md)
- Full leads campaign (B2B SaaS, website pixel, step-by-step): [references/examples/leads-form.md](references/examples/leads-form.md)
