
# Google Ads

Report on existing Google Ads accounts using GAQL-backed data. Dashboards and
data apps are optional presentation surfaces, not mandatory output. Every task starts with
[references/reporting/workflows.md](references/reporting/workflows.md), then picks the report
document with the closest data shape.

For net-new campaign creation, use the main `google-ads` guide (SKILL.md) instead.

## Core contract

- Read [references/reporting/workflows.md](references/reporting/workflows.md) before any GAQL
  or dashboard build.
- Use `google_ads_execute_gaql` as the canonical Google Ads data tool.
- Do not use the alternate GAQL alias in new examples or skills.
- Do not use custom operator-tool heuristics as authoritative Google Ads
  analysis.
- Keep reporting separate from live account changes.
- Written reports are valid outputs. Build a dashboard or data app only when
  the user asks for one or when an interactive view materially improves the
  answer.
- Do not mention internal dashboard implementation details to the user unless
  they explicitly ask how the interface is built.

## Picking a report

| The user wants...                              | Read                                                                       |
|------------------------------------------------|----------------------------------------------------------------------------|
| Full account health snapshot                   | [references/reporting/reports/account-overview.md](references/reporting/reports/account-overview.md) |
| Why aren't conversions tracking right          | [references/reporting/reports/conversion-tracking.md](references/reporting/reports/conversion-tracking.md) |
| Conversions broken down by action / per stage  | [references/reporting/reports/conversion-by-action.md](references/reporting/reports/conversion-by-action.md) |
| Lead-gen / B2B multi-stage funnel              | [references/reporting/reports/conversion-funnel.md](references/reporting/reports/conversion-funnel.md) |
| Where is spend going                           | [references/reporting/reports/budget-distribution.md](references/reporting/reports/budget-distribution.md) |
| Wasteful search terms                          | [references/reporting/reports/search-terms-waste.md](references/reporting/reports/search-terms-waste.md) |
| Should we restructure                          | [references/reporting/reports/campaign-structure.md](references/reporting/reports/campaign-structure.md) |
| Campaign performance over time                 | [references/reporting/reports/campaign-performance.md](references/reporting/reports/campaign-performance.md) |
| Ad-level performance                           | [references/reporting/reports/ad-performance.md](references/reporting/reports/ad-performance.md) |

## Optional dashboard or data app

When the user asks for a dashboard/data app, or an interactive view is clearly
the best presentation, use the report's dashboard section as the agent-facing
implementation recipe. Before building, load the Hyper Database dashboard/data
app reference: `hyper-database/references/dashboard-building.md`.

The implementation pattern is:

1. `tool_data_sources` — the report's GAQL runs through
   `google_ads_execute_gaql` and the rows are saved to a tenant cache
   table (convention: `gads_<report>_<scope>`).
2. `sql_data_sources` — re-aggregate the cache table into named
   variables (KPIs, time series, top lists).
3. Build the interface with cards, KPIs, charts, tables, and a clear visual
   hierarchy.
4. `refresh` — set `{"mode": "scheduled", "cron": "0 * * * *"}` to keep
   the dashboard live; default is manual.

Re-run the same call (or call `hyper_data_refresh_dashboard`) to refresh
without re-invoking the agent.

Before authoring, verify component names with
`hyper_data_search_ui_components`. Read
[references/reporting/report-template.md](references/reporting/report-template.md) for the
reporting response structure.

## When to use the campaign guide instead

Use the main `google-ads` guide (SKILL.md) when the primary task is:

- creating a brand new campaign
- building a blueprint for launch
- setting up a new Search, Display, or PMax campaign
- turning research into campaign assets and configuration

Use this skill when the primary task is:

- building reports or dashboards from any of the above
- explaining Google Ads metrics with GAQL evidence
- creating a conversion-action or funnel dashboard
