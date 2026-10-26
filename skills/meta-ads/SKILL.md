---
name: meta-ads
description: Plan and create Meta (Facebook + Instagram) advertising campaigns end-to-end via the Hyper MCP, defaulting to Advantage+ automation. Use when the user wants to launch Meta ads, Facebook ads, Instagram ads, Advantage+ campaigns, carousel ads, dynamic creative ads, set up Meta conversion tracking, analyze performance, audit a Meta ads account, or build Meta performance dashboards. Also triggers on phrases like meta campaign, facebook campaign, advantage+, or meta account audit.
requires_toolkits:
  - meta_ads
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
- **Meta Ads integration connected** (Facebook + Instagram, with at least one ad account and one Page) at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps).
- **Firecrawl toolkit enabled** for site research and screenshot grounding (discovery phase).

If `meta_ads_adaccount_list` is not found, the integration to connect is Meta Ads.

If you suspect a connection issue (missing ad accounts, page publishing failures, or permission errors), call `meta_ads_health_check()` and report the diagnostics before proceeding.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| Hyper chat | Call the tool by its name; `search_tools(queries=["<provider> <action>"])` shows its parameters | `<name>(...)` |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call_read("<name>", {...})`, `call_write` or `call_destructive`: the one that `describe` names in `call_with` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found: in Hyper chat, find its toolkit id with `discover_toolkits` and pass it to `enable_toolkit`. On an MCP client or the CLI, tell the user which integration to connect in Hyper.

## Tool names

Use the exact tool name that `search_tools` (Hyper chat) or `search` / `describe` (MCP) returns. Canonical names are `meta_ads_*` (listed below). An older name resolves to its canonical tool through an alias.

| Group | Tools |
| --- | --- |
| Discovery | `connections_info` (Hyper chat), `meta_ads_adaccount_list`, `meta_ads_owned_pages_list`, `meta_ads_pages_search`, `meta_accounts_list`, `meta_ads_instagram_accounts_list` |
| Health & sync | `meta_ads_health_check`, `meta_ads_health_get` |
| Tracking assets | `meta_ads_ad_pixels_list`, `meta_ads_ad_pixels_get`, `meta_ads_dataset_quality_get`, `meta_ads_dataset_stats_list`, `meta_ads_custom_audiences_list`, `meta_ads_lookalike_audiences_list`, `meta_ads_targeting_search` |
| Step-by-step creation (preferred) | `meta_ads_campaign_create`, `meta_ads_adset_create`, `meta_ads_ad_create`, `meta_ads_ad_images_upload`, `meta_ads_creative_create` |
| Read & preview | `meta_ads_campaign_get`, `meta_ads_campaigns_search`, `meta_ads_adset_list`, `meta_ads_ad_sets_list`, `meta_ads_adset_get`, `meta_ads_ad_list`, `meta_ads_list`, `meta_ads_ad_get`, `meta_ads_creative_list`, `meta_ads_creative_get`, `meta_ads_custom_audience_get`, `meta_ads_ad_previews_get` |
| Insights & dashboards | `meta_ads_insights_get`, `data_apps_build`, `database_tables_list`, `database_tables_describe`, `database_query` |
| Launch & edits | `meta_ads_campaigns_activate`, `meta_ads_campaign_update`, `meta_ads_adset_update`, `meta_ads_ad_update` |
| Automated rules | `meta_ads_adrule_create`, `meta_ads_adrule_list`, `meta_ads_adrule_get`, `meta_ads_adrule_update`, `meta_ads_adrule_delete`, `meta_ads_adrule_history_list` |
| Site research | `firecrawl_branding_extract`, `firecrawl_screenshots_create` |

CLI users: translate tool names with the `hyper-cli` skill (`hyperai search "<tool name>"`).

---

## Rules that must never be forgotten

> **BUDGETS IN CENTS**: $20.00 = 2000. $5.50 = 550. $100 = 10000. Never pass dollar amounts directly.

> **NAME THE CURRENCY**: Each amount names its account's currency: `account_currency` on each `meta_ads_insights_get` row, or `currency` from `meta_ads_adaccount_list`. Never add amounts of two currencies.

> **SMALL SAMPLES**: A cost per result from fewer than 10 conversions gets one line that the sample is too small to judge. Do not rank or cut a campaign on that cost alone.

> **ACTIVATE, DON'T UPDATE**: Use `meta_ads_campaigns_activate(campaign_id)` to go live. Never `meta_ads_campaign_update(status="ACTIVE")` — that silently leaves ad sets and ads PAUSED so nothing serves.

> **ALWAYS START PAUSED**: Create campaigns with `status="PAUSED"`. Never launch live without user review.

> **BUILD STEP BY STEP**: Create campaigns with the individual tools — `meta_ads_campaign_create` → `meta_ads_adset_create` → `meta_ads_creative_create` → `meta_ads_ad_create`, capturing each id from the previous response. (The old blueprint tools were removed.) The tools validate requests before sending — campaign objective rules, bid-strategy/bid-amount pairing, billing-event/optimization-goal compatibility, budget coherence — but objective-specific ad-set fields (`optimization_goal`, `promoted_object`) are YOUR responsibility: match them to the campaign objective using the reference file for the campaign type.

> **REGULATED ADVERTISERS NEED `special_ad_categories`**: For gambling, financial, housing, employment, credit, or political advertisers, declare the category on `meta_ads_campaign_create` (e.g. `special_ad_categories=["ONLINE_GAMBLING_AND_GAMING"]`). For HOUSING, EMPLOYMENT, FINANCIAL_PRODUCTS_SERVICES or ISSUES_ELECTIONS_POLITICS, also set `special_ad_category_country` (e.g. `["US"]`).

> **FIXED RUN WINDOWS GO ON THE AD SET**: When the user gives a run duration or dates ("run it for 7 days", "through end of month"), set `start_time` AND `end_time` (ISO 8601) on `meta_ads_adset_create`. A daily-budget ad set with no `end_time` runs continuously until manually paused — the requested window is silently lost.

> **PIXEL EVENT COUNTS COME FROM THE DATASET**: For how many events a pixel received (Purchase volume, a drop week over week), call `meta_ads_dataset_stats_list`. Send the pixel id as `dataset_id`, with `start_time` and `end_time`. Make one call per period. For Event Match Quality, call `meta_ads_dataset_quality_get` with the pixel id as `dataset_id`. `meta_ads_insights_get` counts only the conversions that Meta attributes to ads, not every event the pixel received.

> **GROUND COPY IN THE DESTINATION PAGE (RESEARCH FIRST)**: When the brief centers on a URL ("build a campaign for https://..."), fetch that page FIRST (`web_pages_fetch`) — before discovery and before writing any copy — and ground ad copy in what the page actually says (product name, value props, offer). Never invent copy for a page you have not read; even when the user supplies exact copy or headlines, fetch the page to verify the destination matches the offer.

> **EU-TARGETED AD SETS NEED DSA FIELDS**: If an ad set targets the EU, set `dsa_beneficiary` and `dsa_payor` on `meta_ads_adset_create` (who benefits from / pays for the ad) — required under the EU Digital Services Act, or delivery is restricted.

> **UTMs ON EVERY DESTINATION AD (`url_tags`)**: Set `url_tags` (UTM params, e.g. `utm_source=meta&utm_medium=paid&utm_campaign=...`) on every creative that drives to a destination — downstream measurement (e.g. AppsFlyer + a data warehouse) stitches on these, so an ad without UTMs is effectively unmeasurable. Use the advertiser's canonical template; if you don't have one, ask rather than ship untracked.

See [references/constraints.md](references/constraints.md) for the full constraint set.

---

## Core process

Every task follows this sequence. Do not skip steps.

1. **Identify the goal** — creation, analysis, or both?
2. **Check the routing table** before calling any tools
3. **Make a written plan** — state campaign type, budget in cents, optimization goal, and sequence of steps; show it before acting
4. **Execute step by step** by the campaign file, whose rules list the constraints of its type. Read a section of [references/constraints.md](references/constraints.md) only when a step names it
5. **Show ad previews** before activation
6. **Activate only when the user approves** using `meta_ads_campaigns_activate()`

**Automated / scheduled runs:** If there is no user present to interact with (e.g. a scheduled task), skip steps 3 and 6, and read only the campaign file of the routing row: the task's instructions are its plan. Do not write a plan and wait for confirmation — proceed directly. Do not activate unless activation was explicitly included in the task instructions.

---

## Routing table

| The user wants to… | Read these files first |
|---|---|
| Create a sales / conversion campaign | Plan: [references/discovery.md](references/discovery.md). Build, after the user approves the plan: [references/campaigns/sales.md](references/campaigns/sales.md) |
| Create a leads campaign | Plan: [references/discovery.md](references/discovery.md). Build, after the user approves the plan: [references/campaigns/leads.md](references/campaigns/leads.md) |
| Create a traffic campaign | Plan: [references/discovery.md](references/discovery.md). Build, after the user approves the plan: [references/campaigns/traffic.md](references/campaigns/traffic.md) |
| Create an awareness or engagement campaign | Plan: [references/discovery.md](references/discovery.md). Build, after the user approves the plan: [references/campaigns/awareness-engagement.md](references/campaigns/awareness-engagement.md) |
| Create an app promotion campaign | Plan: [references/discovery.md](references/discovery.md). Build, after the user approves the plan: [references/campaigns/app-promotion.md](references/campaigns/app-promotion.md) |
| Create a campaign (any objective) | Plan: [references/discovery.md](references/discovery.md). Build, after the user approves the plan: the matching `references/campaigns/*.md` above |
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
