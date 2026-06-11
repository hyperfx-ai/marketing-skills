# Account Overview

Full-account health snapshot. Combines spend, conversions, conversion
rate, and cost per conversion in a single dashboard so the agent can
orient before drilling into a specific issue.

## When to use

- "How is the account doing?"
- First report to run for a new client engagement.
- Periodic health check.
- When routing to a more focused report (tracking / budget / search
  terms / structure) requires an aggregate baseline.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).

Use the GAQL below through `google_ads_execute_gaql` for both ad-hoc
reporting and refreshable dashboards.

## GAQL

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.cost_micros,
  metrics.clicks,
  metrics.impressions,
  metrics.conversions,
  metrics.conversions_value
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

## How to interpret

- Treat any campaign with significant spend and zero conversions over a
  meaningful window as a tracking-or-budget issue, not a "campaign
  performance" issue.
- ROAS and CPA are downstream signals — surface them only when
  conversion tracking is verified (see
  [conversion-tracking.md](conversion-tracking.md)).
- Aggregate spend without segmenting by date hides pacing problems;
  always include a daily series.

## Building a dashboard from this report

```python
result = hyper_data_build_dashboard(
    name="Account Overview",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_execute_gaql",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT segments.date, campaign.id, campaign.name, "
                    "campaign.status, metrics.cost_micros, metrics.clicks, "
                    "metrics.impressions, metrics.conversions, "
                    "metrics.conversions_value "
                    "FROM campaign "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_account_overview",
            "mode": "replace",
        },
    },
    sql_data_sources={
        "total_spend": {
            "shape": "scalar",
            "sql": (
                "SELECT COALESCE(SUM(metrics_cost_micros), 0)/1e6 "
                "FROM gads_account_overview"
            ),
        },
        "total_conversions": {
            "shape": "scalar",
            "sql": (
                "SELECT COALESCE(SUM(metrics_conversions), 0) "
                "FROM gads_account_overview"
            ),
        },
        "daily": {
            "shape": "rows",
            "sql": (
                "SELECT segments_date AS date, "
                "SUM(metrics_cost_micros)/1e6 AS spend, "
                "SUM(metrics_conversions) AS conversions "
                "FROM gads_account_overview GROUP BY 1 ORDER BY 1"
            ),
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, Grid, Heading, Metric, Muted, Text
from prefab_ui.components.charts import AreaChart, ChartSeries

with PrefabApp(title="Account Overview") as app:
    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Account Overview")
            Muted("Last 30 days")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Spend", value=f"${total_spend:,.0f}")
            with Card():
                with CardContent():
                    Metric(label="Conversions", value=f"{total_conversions:,.0f}")

        with Card():
            with CardContent():
                Text("Daily spend and conversions", css_class="text-sm font-medium text-muted-foreground mb-2")
                AreaChart(
                    data=daily,
                    x_axis="date",
                    series=[
                        ChartSeries(data_key="spend", label="Spend"),
                        ChartSeries(data_key="conversions", label="Conversions"),
                    ],
                    show_legend=True,
                    height=300,
                )
""",
    refresh={"mode": "scheduled", "cron": "0 * * * *"},
)
```

## Variants

- Add `metrics.average_cpc`, `metrics.ctr`, `metrics.search_impression_share`
  to the GAQL when the user wants efficiency context.
- Group by `campaign.advertising_channel_type` to split Search / PMax /
  Display in the same dashboard.
