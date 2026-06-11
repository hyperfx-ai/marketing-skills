# Google Ads Reporting Workflow

## When to use

Read this before authoring GAQL, optional dashboard sources, or a reporting
response for an existing Google Ads account.

## Core contract

- Use `google_ads_execute_gaql` as the canonical Google Ads data tool.
- Written GAQL-backed reports are valid outputs. Dashboards and data apps are
  optional presentation surfaces.
- Build a dashboard/data app only when the user asks for one or when an
  interactive view materially improves the presentation.
- When building an interface, fetch external rows through `tool_data_sources`,
  save them into a tenant cache table, query that cache with
  `sql_data_sources`, and render the final interface from those variables.
- Do not use the alternate GAQL alias in new examples.
- Do not use custom operator-tool heuristics as authoritative analysis.
- Do not inject Google Ads credentials into the dashboard/data app runtime.
- Keep reporting separate from live account mutations.
- Do not mention internal interface implementation details to the user unless
  they explicitly ask how it is built.

## Phase 1: Access and scope

1. Call `google_ads_list_accounts()` before touching account data.
2. Confirm the customer ID if more than one account is available.
3. Confirm the reporting window if the user has not given one.
4. If the user did not ask for a dashboard/data app and the best output is
   unclear, ask whether they want a written report or an interactive view.

## Phase 2: Choose the report

Pick the narrowest report doc under `reports/`:

- conversion action breakdown: `reports/conversion-by-action.md`
- lead-gen / B2B funnel: `reports/conversion-funnel.md`
- conversion action inventory: `reports/conversion-tracking.md`
- budget distribution: `reports/budget-distribution.md`
- search terms: `reports/search-terms-waste.md`
- campaign performance: `reports/campaign-performance.md`
- ad performance: `reports/ad-performance.md`

When the user asks for a funnel dashboard, use the conversion funnel
recipe. Do not add a new Google Ads tool for that case.

## Phase 3: Query with GAQL

Use GAQL fields that are selectable with the report resource. For
campaign-level conversion action reporting, use campaign metrics
segmented by `segments.conversion_action` and
`segments.conversion_action_name`.

Do not select `conversion_action.id` or `conversion_action.name` from
`FROM campaign`; Google rejects that shape. Query the
`conversion_action` resource separately only when you need the inventory
of configured conversion actions.

## Phase 4: Optional dashboard/data app

Skip this phase for plain written reports. If building an interface, first load
`hyper-database/references/dashboard-building.md`, then use a call shaped like:

```python
hyper_data_build_dashboard(
    name="Google Ads Report",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_execute_gaql",
            "tool_args": {"customer_id": "...", "query": "..."},
            "cache_table": "gads_report_raw",
            "mode": "replace",
        }
    },
    sql_data_sources={...},
    prefab_python="...",
)
```

The tool source name is not a Python variable. It populates the cache
table. SQL sources create the variables used by the interface code.

## Phase 5: Response format

Use the template in `report-template.md`. State what data was queried, which
date range was used, and whether the final output is a written report,
dashboard, data app, or published interface.
