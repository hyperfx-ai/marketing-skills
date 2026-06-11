# Budget Distribution

Where spend is actually going across campaigns.

## When to use

- "Where is our budget going?"
- "Which campaigns are wasting money?"
- Pacing review before adjusting daily budgets.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).

Use the GAQL below through `google_ads_execute_gaql` for both ad-hoc
reporting and refreshable dashboards.

## GAQL

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign_budget.amount_micros,
  campaign_budget.delivery_method,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.clicks
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

## How to interpret

- High `cost_micros` + zero `conversions` over a meaningful window =
  immediate candidate for budget reduction OR for a tracking audit.
  Don't recommend cuts until tracking is ruled out.
- Spend Herfindahl: if 80%+ of spend lives in 2–3 campaigns, the
  account is concentrated; restructure work has high leverage.
- Compare `cost_micros` to `campaign_budget.amount_micros * days` to
  detect under-pacing (budget caps / bidding ceilings).

## Building a dashboard from this report

```python
result = hyper_data_build_dashboard(
    name="Budget Distribution",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_execute_gaql",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT campaign.id, campaign.name, campaign.status, "
                    "campaign_budget.amount_micros, "
                    "campaign_budget.delivery_method, "
                    "metrics.cost_micros, metrics.conversions, "
                    "metrics.conversions_value, metrics.clicks "
                    "FROM campaign "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_budget",
            "mode": "replace",
        },
    },
    sql_data_sources={
        "by_campaign": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, "
                "SUM(metrics_cost_micros)/1e6 AS spend, "
                "SUM(metrics_conversions) AS conversions "
                "FROM gads_budget GROUP BY 1 ORDER BY spend DESC LIMIT 25"
            ),
        },
        "zero_conv_high_spend": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, "
                "SUM(metrics_cost_micros)/1e6 AS spend "
                "FROM gads_budget GROUP BY 1 "
                "HAVING SUM(metrics_conversions) = 0 "
                "AND SUM(metrics_cost_micros) > 50000000 "
                "ORDER BY spend DESC"
            ),
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, DataTable, DataTableColumn, Grid, Heading, Metric, Muted, Text
from prefab_ui.components.charts import BarChart, ChartSeries

with PrefabApp(title="Budget Distribution") as app:
    total_spend = sum(row.get("spend", 0) for row in by_campaign)

    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Budget Distribution")
            Muted("Spend concentration and zero-conversion risk")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Spend", value=f"${total_spend:,.0f}")
            with Card():
                with CardContent():
                    Metric(label="Zero-conversion campaigns", value=f"{len(zero_conv_high_spend):,}")

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text("Spend by campaign", css_class="text-sm font-medium text-muted-foreground mb-2")
                    BarChart(
                        data=by_campaign,
                        x_axis="campaign",
                        series=[ChartSeries(data_key="spend", label="Spend")],
                        height=300,
                    )
            with Card():
                with CardContent():
                    Text("High spend without conversions", css_class="text-sm font-medium text-muted-foreground mb-2")
                    DataTable(
                        columns=[
                            DataTableColumn(key="campaign", header="Campaign"),
                            DataTableColumn(key="spend", header="Spend"),
                        ],
                        rows=zero_conv_high_spend,
                    )
""",
    refresh={"mode": "scheduled", "cron": "0 */6 * * *"},
)
```

## Variants

- Add `metrics.search_impression_share` to flag campaigns that are
  budget-constrained vs. competitor-pressured.
- Group by `campaign.advertising_channel_type` to compare Search vs
  PMax vs Display efficiency separately.
