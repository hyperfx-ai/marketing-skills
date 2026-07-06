---
name: google-ads
description: Plan and create new Google Ads campaigns and report on existing accounts via the Hyper MCP. Use when the user wants to launch Search, Display, or Performance Max campaigns, build Google Ads reports or dashboards, diagnose conversion tracking, or mentions Google Ads, AdWords, search ads, display ads, Performance Max, PMax, PPC, Google campaigns, Google blueprint, search term reports, budget analysis, conversion funnels, negative keywords, or manager accounts (MCC).
icon: google_ads
short_description: Plan and create Google Ads campaigns and build GAQL-backed reports and dashboards.
---

# Google Ads

Strategic guide for building new Google Ads campaigns and reporting on existing accounts. Research first, consult intelligently, validate everything, and use the blueprint flow for controlled creation. Reporting is GAQL-backed and evidence-first — dashboards are optional presentation surfaces.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Google Ads integration connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps).

If `google_ads_list_accounts` is not in the tool list, stop and tell the user to enable Hyper MCP and connect Google Ads.

## Out of scope

- **Live optimization mutations** (bid adjustments, pausing keywords, restructuring existing campaigns). Reports may *recommend* these changes; applying them needs explicit per-change user approval.
- **Creative generation** (headlines, descriptions, images) → [`ad-creative-generation`](../ad-creative-generation).
- **Cross-platform campaign launches** → use this skill for Google, then invoke `meta-ads` / `tiktok-ads` separately.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `google_ads_list_accounts` | Discover accessible accounts (and MCC sub-accounts). |
| `google_ads_execute_gaql` | Run a GAQL query (conversion actions, search term reports, etc.). |
| `google_ads_search_locations` | Resolve human-readable location names to IDs. |
| `google_ads_list_assets`, `google_ads_upload_image_asset` | Manage image assets for Display / PMax. |
| `google_ads_preview_blueprint`, `google_ads_create_from_blueprint` | Validate + create Search/Display campaigns. |
| `google_ads_preview_pmax_blueprint`, `google_ads_create_from_pmax_blueprint` | Validate + create Performance Max campaigns. |
| `hyper_data_build_dashboard`, `hyper_data_refresh_dashboard` | Optional dashboards / data apps for reports. |

## Rules that must never be forgotten

> **BUDGETS IN MICROS**: $50/day = 50,000,000 micros. Never pass dollar amounts directly.

> **ALWAYS START PAUSED**: Create campaigns with `status="PAUSED"`. Activate only after explicit user approval.

> **PREVIEW BEFORE CREATE**: Always use the blueprint system — build the blueprint JSON, call the **preview** tool, get explicit user approval, then call the **create** tool. Never skip the preview step. The blueprint validates locally, fills smart defaults, resolves locations, and rolls back on failure.

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
5. **Build blueprint → preview → user approval → create (PAUSED)**, re-checking [references/constraints.md](references/constraints.md) at each step
6. **Activate only when the user approves**

Full workflow: Initial Setup → Research (site + GAQL + market) → Analyze (goals, audience, keywords) → Consult (options + trade-offs) → Recommend (structure + bids) → Confirm (summary approved) → Build Blueprint → Preview → User Approval → Create (PAUSED) → Activate (post-approval).

## Routing table

| The user wants to… | Read these files first |
|---|---|
| Create a Search or Display campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/search-display.md](references/campaigns/search-display.md) |
| Create a Performance Max campaign | [references/discovery.md](references/discovery.md) → [references/campaigns/pmax.md](references/campaigns/pmax.md) |
| Add an asset group to an existing PMax campaign | [references/campaigns/pmax.md](references/campaigns/pmax.md) |
| Run a report / GAQL query / analyze performance (any kind) | [references/reporting.md](references/reporting.md) → the matching `references/reports/*.md` recipe |
| Account health snapshot / "how is the account doing?" | [references/reporting.md](references/reporting.md) → [references/reports/account-overview.md](references/reports/account-overview.md) |
| Diagnose conversion tracking | [references/reporting.md](references/reporting.md) → [references/reports/conversion-tracking.md](references/reports/conversion-tracking.md) |
| Find wasteful search terms / negative keyword candidates | [references/reporting.md](references/reporting.md) → [references/reports/search-terms-waste.md](references/reports/search-terms-waste.md) |
| Build a Google Ads dashboard or data app | [references/reporting.md](references/reporting.md) → matching report recipe's dashboard section |
| Work across an MCC / many sub-accounts | [references/mcc.md](references/mcc.md) → [references/reporting.md](references/reporting.md) |
| Goal not yet clear | [references/discovery.md](references/discovery.md) — discovery clarifies the goal |

Reporting responses follow [references/report-template.md](references/report-template.md); keep claims tied to queried data per [references/heuristics.md](references/heuristics.md).
