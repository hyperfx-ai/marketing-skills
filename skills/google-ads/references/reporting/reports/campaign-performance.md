# Campaign Performance

Time-series view of spend, clicks, conversions, and ROAS per campaign.
The general-purpose performance dashboard — pair with the diagnosis
reports when an issue surfaces.

## When to use

- "How is each campaign performing over time?"
- Weekly / monthly performance review with the client.
- Identifying trend changes (sudden spend spike, conversion drop).
- The default first dashboard for a new client engagement.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).
- Optional: `campaign_ids` filter.

Use the GAQL below through `google_ads_execute_gaql` for both ad-hoc
reporting and refreshable dashboards.

## GAQL

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  campaign.advertising_channel_type,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.ctr,
  metrics.average_cpc
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

## How to interpret

- Daily ROAS = `conversions_value / cost`. Plot as time series; a
  step-down on a known date often correlates with an ad / landing-page
  change.
- A sustained drop in conversions with steady spend = tracking issue
  or seasonality, not necessarily campaign decay.
- Compare campaigns of the same `advertising_channel_type`; cross-type
  comparisons (Search vs PMax) are misleading.

## Building a dashboard from this report

```python
result = hyper_data_build_dashboard(
    name="Campaign Performance",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_execute_gaql",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT segments.date, campaign.id, campaign.name, "
                    "campaign.advertising_channel_type, "
                    "metrics.impressions, metrics.clicks, metrics.cost_micros, "
                    "metrics.conversions, metrics.conversions_value, "
                    "metrics.ctr, metrics.average_cpc "
                    "FROM campaign "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_campaign_performance",
            "mode": "replace",
        },
    },
    sql_data_sources={
        "daily_totals": {
            "shape": "rows",
            "sql": (
                "SELECT segments_date AS date, "
                "SUM(metrics_cost_micros)/1e6 AS spend, "
                "SUM(metrics_conversions) AS conversions, "
                "SUM(metrics_conversions_value) AS revenue "
                "FROM gads_campaign_performance GROUP BY 1 ORDER BY 1"
            ),
        },
        "by_campaign": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, "
                "SUM(metrics_cost_micros)/1e6 AS spend, "
                "SUM(metrics_conversions) AS conversions, "
                "CASE WHEN SUM(metrics_cost_micros) > 0 "
                "THEN SUM(metrics_conversions_value)/(SUM(metrics_cost_micros)/1e6) "
                "ELSE 0 END AS roas "
                "FROM gads_campaign_performance GROUP BY 1 ORDER BY spend DESC LIMIT 25"
            ),
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, DataTable, DataTableColumn, Grid, Heading, Metric, Muted, Text
from prefab_ui.components.charts import AreaChart, ChartSeries

with PrefabApp(title="Campaign Performance") as app:
    total_spend = sum(row.get("spend", 0) for row in by_campaign)
    total_conversions = sum(row.get("conversions", 0) for row in by_campaign)

    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Campaign Performance")
            Muted("Spend, conversions, revenue, and campaign-level efficiency")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Spend", value=f"${total_spend:,.0f}")
            with Card():
                with CardContent():
                    Metric(label="Conversions", value=f"{total_conversions:,.0f}")

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text("Daily performance", css_class="text-sm font-medium text-muted-foreground mb-2")
                    AreaChart(
                        data=daily_totals,
                        x_axis="date",
                        series=[
                            ChartSeries(data_key="spend", label="Spend"),
                            ChartSeries(data_key="conversions", label="Conversions"),
                            ChartSeries(data_key="revenue", label="Revenue"),
                        ],
                        show_legend=True,
                        height=300,
                    )
            with Card():
                with CardContent():
                    Text("Campaign detail", css_class="text-sm font-medium text-muted-foreground mb-2")
                    DataTable(
                        columns=[
                            DataTableColumn(key="campaign", header="Campaign"),
                            DataTableColumn(key="spend", header="Spend"),
                            DataTableColumn(key="conversions", header="Conversions"),
                            DataTableColumn(key="roas", header="ROAS"),
                        ],
                        rows=by_campaign,
                    )
""",
    refresh={"mode": "scheduled", "cron": "0 * * * *"},
)
```

## Variants

- Add `metrics.search_impression_share` and
  `metrics.search_top_impression_share` to spot lost-by-budget /
  lost-by-rank issues.
- Group by `segments.device` for desktop vs mobile vs tablet splits.
