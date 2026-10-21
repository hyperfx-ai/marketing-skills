# Reporting and GAQL

Report on existing Google Ads accounts using GAQL-backed data. Dashboards and data apps are optional presentation surfaces, not mandatory output. Every reporting task starts here, then picks the report recipe with the closest data shape from [reports/](reports/).

## Core contract

- Use `google_ads_gaql_query` as the canonical Google Ads data tool.
- Written GAQL-backed reports are valid outputs. Build a dashboard or data app only when the user asks for one or when an interactive view materially improves the answer.
- Read the `google_ads_gaql_query` descriptor and select the account whose data the report needs.
- Treat rows as evidence, not as automatic recommendations ([heuristics.md](heuristics.md)).
- Keep reporting separate from live account changes.
- Do not mention internal dashboard implementation details to the user unless they explicitly ask how the interface is built.

## Phase 1: Access and scope

1. Call `google_ads_accounts_list()` before touching account data.
2. Confirm the customer ID if more than one account is available.
3. Confirm the reporting window if the user has not given one.
4. If the user did not ask for a dashboard/data app and the best output is unclear, ask whether they want a written report or an interactive view.

## Phase 2: Pick the report

| The user wants... | Read |
|---|---|
| Full account health snapshot | [reports/account-overview.md](reports/account-overview.md) |
| Why aren't conversions tracking right | [reports/conversion-tracking.md](reports/conversion-tracking.md) |
| Conversions broken down by action / per stage | [reports/conversion-by-action.md](reports/conversion-by-action.md) |
| Lead-gen / B2B multi-stage funnel | [reports/conversion-funnel.md](reports/conversion-funnel.md) |
| Where is spend going | [reports/budget-distribution.md](reports/budget-distribution.md) |
| Wasteful search terms | [reports/search-terms-waste.md](reports/search-terms-waste.md) |
| Should we restructure | [reports/campaign-structure.md](reports/campaign-structure.md) |
| Campaign performance over time | [reports/campaign-performance.md](reports/campaign-performance.md) |
| Ad-level performance | [reports/ad-performance.md](reports/ad-performance.md) |

When the user asks for a funnel dashboard, use the conversion funnel recipe.

## Phase 3: Query with GAQL

Use GAQL fields that are selectable with the report resource. For campaign-level conversion action reporting, use campaign metrics segmented by `segments.conversion_action` and `segments.conversion_action_name`.

Do not select `conversion_action.id` or `conversion_action.name` from `FROM campaign`; Google rejects that shape. Query the `conversion_action` resource separately only when you need the inventory of configured conversion actions.

### GAQL Resource Compatibility

**Critical:** Not all Google Ads resources can be joined in a single query.

**search_term_view** — use `segments.keyword.info.*` for keyword text and match type — **never** `ad_group_criterion.*`:

```sql
SELECT
    search_term_view.search_term,
    customer.descriptive_name,
    segments.keyword.info.text,
    segments.keyword.info.match_type,
    campaign.name,
    ad_group.name,
    metrics.clicks,
    metrics.impressions,
    metrics.conversions,
    metrics.cost_micros
FROM search_term_view
WHERE segments.date DURING LAST_7_DAYS
ORDER BY metrics.impressions DESC
```

`ad_group_criterion` is **incompatible** with `search_term_view` as the FROM resource. Selecting `ad_group_criterion.*` fields will always fail with `PROHIBITED_RESOURCE_TYPE_IN_SELECT_CLAUSE`.

**keyword_view** — for keyword performance (Quality Score, bid estimates):
```sql
SELECT
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    metrics.clicks,
    metrics.impressions,
    metrics.historical_quality_score
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
```

## Phase 4: Optional dashboard/data app

Skip this phase for plain written reports. When the user asks for a dashboard or data app, or an interactive view is clearly the best presentation, use the matching report's dashboard section as the implementation recipe.

Before authoring a custom dashboard:
- Inspect the live `data_apps_build` tool schema first — it documents the accepted data-source shapes and UI components. Do not invent dashboard patterns or component names.

The implementation pattern is:

1. `tool_data_sources` — the report's GAQL runs live through `google_ads_gaql_query`, and the rows under `results` are saved to a cache table named for the report and the customer (`gads_<report>_<customer id>`), so two accounts never share one table. Pass `"rows_path": "results"`, the key that holds the rows. Run the GAQL once with `google_ads_gaql_query` before the build: when it returns no rows, tell the user and build nothing, because a first build with no rows makes a cache table with no columns and fails.
2. `sql_data_sources` — re-aggregate the cache table into named variables (KPIs, time series, top lists). Google returns the int64 metrics (`cost_micros`, `clicks`, `impressions`) as strings, so cast every metric with `::numeric`.
3. The template — `template_name="ads_overview"` for an account view of KPIs, a spend and clicks trend, top campaigns and top ads; else `template_html`, a body with cards, KPIs, charts and tables that binds only the SQL variables.
   The recipes write amounts with `$`. Select `customer.currency_code` first, and for an account in another currency use its symbol and say the currency in the subtitle.
4. Refresh is manual: `data_apps_refresh(data_app_id=...)` runs the GAQL again and re-renders the app with no agent run.

```python
data_apps_build(
    name="Google Ads Report",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_gaql_query",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT segments.date, metrics.cost_micros, metrics.clicks "
                    "FROM customer WHERE segments.date DURING LAST_30_DAYS"
                ),
            },
            "cache_table": "gads_report_raw_1234567890",
            "mode": "replace",
            "rows_path": "results",
        }
    },
    sql_data_sources={
        "daily": {
            "shape": "rows",
            "sql": (
                "SELECT segments_date AS date, "
                "ROUND(SUM(metrics_cost_micros::numeric) / 1e6, 2) AS spend, "
                "SUM(metrics_clicks::numeric) AS clicks "
                "FROM gads_report_raw_1234567890 GROUP BY 1 ORDER BY 1"
            ),
        },
    },
    template_html="""
<div class="card">
  <header><h2>Spend and clicks</h2><p>Last 30 days</p></header>
  <section><div class="chart h-64"><canvas id="daily" aria-label="Daily spend and clicks"></canvas></div></section>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
  window.basecoat.chart("#daily", {
    type: "line", labelKey: "date", legend: true,
    data: {{ daily | tojson }},
    series: {
      spend: { label: "Spend", color: "var(--chart-1)" },
      clicks: { label: "Clicks", color: "var(--chart-2)" }
    }
  });
});
</script>
""",
)
```

The tool source name is not a template variable. It populates the cache table. SQL sources create the variables used by the template. Do not inject Google Ads credentials into the data app.

## Phase 5: Response format

Use the template in [report-template.md](report-template.md). State what data was queried, which date range was used, and whether the final output is a written report, dashboard, data app, or published interface.

## Warehouse data

When the workspace has a Google Ads warehouse connection, inspect its available tables and columns and query the selected connection through `database_query`. Existing warehouse data remains available independently of native Google Ads API calls.

Check Warehouse Data Status for that connection and report its last successful refresh. Name the customer IDs, date boundaries, currency units and metric definitions. Do not assume an hourly cache, fixed table name or fresh rows merely because the connection is healthy. Use `google_ads_gaql_query` when the requested data is not in the configured warehouse.
