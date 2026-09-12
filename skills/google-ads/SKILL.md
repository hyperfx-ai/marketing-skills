---
name: google-ads
description: Plan and create new Google Ads campaigns and report on existing accounts via the Hyper MCP. Use when the user wants to launch Search, Display, Performance Max, Video, Demand Gen, Shopping, or App campaigns, build Google Ads reports or dashboards, diagnose conversion tracking, or mentions Google Ads, AdWords, search ads, display ads, Performance Max, PMax, PPC, Google campaigns, search term reports, budget analysis, conversion funnels, negative keywords, or manager accounts (MCC).
requires_toolkits:
  - google_ads
icon: google_ads
short_description: Plan and create Google Ads campaigns and build GAQL-backed reports and dashboards.
---

# Google Ads

Strategic guide for building new Google Ads campaigns and reporting on existing accounts. Research first, consult intelligently, validate everything, and build with the granular resource tools in dependency order (budget → campaign → targeting → ad groups → ads / asset groups). The API has exactly one campaign create — `google_ads_campaigns_create` — and the campaign type is just `advertising_channel_type`; type-specific requirements are enforced by the tools' built-in validators, which return corrective errors. Reporting is GAQL-backed and evidence-first — dashboards are optional presentation surfaces.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Google Ads integration connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps).

If `search("google_ads_accounts_list")` does not find `google_ads_accounts_list`, stop and tell the user to enable Hyper MCP and connect Google Ads.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call("<name>", {...})` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found, its integration is not connected or not enabled for the workspace: stop and tell the user which integration to connect.

## Out of scope

- **Live optimization mutations** (bid adjustments, pausing keywords, restructuring existing campaigns). Reports may *recommend* these changes; applying them needs explicit per-change user approval.
- **Creative generation** (headlines, descriptions, images) → [`ad-creative-generation`](../ad-creative-generation).
- **Cross-platform campaign launches** → use this skill for Google, then invoke `meta-ads` / `tiktok-ads` separately.

## Tool surface

Reads are GAQL (`google_ads_gaql_query` covers every resource). Writes are one tool per resource operation, named `google_ads_<resource>_<create|update|remove>`; create/update take `(customer_id, body)` where `body` is the bare resource object in snake_case.

| Tool | Purpose |
| --- | --- |
| `google_ads_accounts_list` | Discover accessible accounts (and MCC sub-accounts). |
| `google_ads_gaql_query` | Run a GAQL query (conversion actions, search terms, any resource). |
| `google_ads_campaign_budgets_create` | Create the budget first (micros!). |
| `google_ads_campaigns_create` / `_update` / `_remove` | The ONE campaign create — every `advertising_channel_type` (SEARCH, DISPLAY, PERFORMANCE_MAX, VIDEO, DEMAND_GEN, SHOPPING, MULTI_CHANNEL for App). |
| `google_ads_ad_groups_create` / `_update`, `google_ads_ad_groups_delete` | Ad groups under a campaign. |
| `google_ads_ad_group_ads_create` / `_update` / `_remove` | Ads (typed: `responsive_search_ad`, `responsive_display_ad`, video / demand-gen ad types). |
| `google_ads_keywords_create` / `_update` / `_delete` / `_list` | Keywords (positive and negative). |
| `google_ads_locations_search`, `google_ads_location_targets_add` | Resolve location names, target them. |
| `google_ads_image_assets_upload` | Image assets — accepts `file_id` from the workspace file manager, `image_url`, or base64. |
| `google_ads_video_assets_link` | Register a YouTube video ID as a video asset (the Ads API cannot host video files — videos must be on YouTube). |
| `google_ads_asset_groups_create` | PMax asset group (atomic: text + image assets in one call). |
| `google_ads_conversion_actions_create`, `google_ads_user_lists_create`, `google_ads_bidding_strategies_create`, `google_ads_shared_sets_create`, … | Full per-resource CRUD surface — same naming pattern. |
| `google_ads_request` | Raw escape hatch for any uncovered endpoint. |
| `data_apps_build`, `data_apps_refresh` | Optional dashboards / data apps for reports. |

## Rules that must never be forgotten

> **BUDGETS IN MICROS**: $50/day = 50,000,000 micros. Never pass dollar amounts directly.

> **ALWAYS START PAUSED**: Create campaigns with `status="PAUSED"`. Activate only after explicit user approval.

> **SUMMARIZE BEFORE CREATE**: Present the full build plan (budget, campaign settings, targeting, ad groups, ads/assets) and get explicit user approval before the first mutate. Create in dependency order and reference each created resource by the `resource_name` the mutate returns. The tools validate bodies against the real API schema (writable fields, enum values) plus channel-type rules and return corrective errors — fix and retry rather than guessing.

> **NEVER INVENT**: Don't assume URLs, budgets, or location IDs. Don't skip research. Don't invent keywords or copy — creative comes only from the actual site. Don't build without user buy-in.

> **GAQL GUARDRAILS**: Never join `ad_group_criterion` with `search_term_view`. Never query more than 5 sub-accounts in a single batch.

See [references/constraints.md](references/constraints.md) for the full constraint set.

> **All reference files live in `references/`.** Read them at `references/<file>` (e.g. `references/discovery.md`). They are not in the same directory as this SKILL.md.

## Core process

Every campaign build follows this sequence. Do not skip steps.

1. **Identify the goal** — new campaign, reporting/analysis, or both?
2. **Check the routing table** and read the referenced files before calling any tools
3. **Discovery is mandatory for creation** ([references/discovery.md](references/discovery.md)) — account setup, site scan, conversion tracking check, market research, consultation
4. **Present the pre-creation summary** and wait for explicit approval
5. **Build in dependency order (budget → campaign PAUSED → targeting → ad groups → ads/assets)** after approval, re-checking [references/constraints.md](references/constraints.md) at each step
6. **Activate only when the user approves**

Full workflow: Initial Setup → Research (site + GAQL + market) → Analyze (goals, audience, keywords) → Consult (options + trade-offs) → Recommend (structure + bids) → Confirm (summary approved) → Create in dependency order (PAUSED) → Verify by GAQL → Activate (post-approval).

## Routing table

| The user wants to… | Read these files first |
|---|---|
| Create a Search or Display campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/search-display.md](references/campaigns/search-display.md) |
| Create a Performance Max campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/pmax.md](references/campaigns/pmax.md) |
| Add an asset group to an existing PMax campaign | [references/campaigns/pmax.md](references/campaigns/pmax.md) |
| Create a Video, Demand Gen, Shopping, or App campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/other-types.md](references/campaigns/other-types.md) |
| Run a report / GAQL query / analyze performance (any kind) | [references/reporting.md](references/reporting.md) → the matching `references/reports/*.md` recipe |
| Account health snapshot / "how is the account doing?" | [references/reporting.md](references/reporting.md) → [references/reports/account-overview.md](references/reports/account-overview.md) |
| Diagnose conversion tracking | [references/reporting.md](references/reporting.md) → [references/reports/conversion-tracking.md](references/reports/conversion-tracking.md) |
| Find wasteful search terms / negative keyword candidates | [references/reporting.md](references/reporting.md) → [references/reports/search-terms-waste.md](references/reports/search-terms-waste.md) |
| Build a Google Ads dashboard or data app | [references/reporting.md](references/reporting.md) → matching report recipe's dashboard section |
| Work across an MCC / many sub-accounts | [references/mcc.md](references/mcc.md) → [references/reporting.md](references/reporting.md) |
| Goal not yet clear | [references/discovery.md](references/discovery.md) — discovery clarifies the goal |

Reporting responses follow [references/report-template.md](references/report-template.md); keep claims tied to queried data per [references/heuristics.md](references/heuristics.md).
