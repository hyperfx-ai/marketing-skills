# Conversions by Action

Per–conversion-action breakdown across campaigns and dates. Use this
when the user wants to see how each individual conversion event (like
"sign up", "purchase", "qualified lead") performs over time and across
campaigns — not just the aggregate `conversions` metric.

## When to use

- "Show me conversions broken down by action / by event."
- "Which campaigns drive each stage of our funnel?" (paired with
  [conversion-funnel.md](conversion-funnel.md))
- Diagnosing a single noisy conversion action (e.g. duplicate primary).
- Building a stacked area / bar chart of conversion mix over time.

## Inputs

- `customer_id` (required, format `XXX-XXX-XXXX`).
- `date_range` (default: `LAST_30_DAYS`; or explicit `start_date` / `end_date`).
- Optional: `campaign_ids` to scope to a subset.

## GAQL

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  segments.conversion_action,
  segments.conversion_action_name,
  segments.conversion_action_category,
  metrics.conversions,
  metrics.all_conversions,
  metrics.conversions_value
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

**Critical caveat — common failure mode:**

Do **not** select `conversion_action.id` or `conversion_action.name`
against `FROM campaign`. That triggers
`PROHIBITED_RESOURCE_TYPE_IN_SELECT_CLAUSE`. Always use the
`segments.conversion_action*` fields instead. The metric name is
`metrics.conversions` (already segmented by `segments.conversion_action`),
**not** `metrics.conversions_by_conversion_action` (which does not
exist).

Do **not** select `metrics.cost_micros` in this query. Google Ads rejects
`metrics.cost_micros` with `segments.conversion_action*` using
`PROHIBITED_SEGMENT_WITH_METRIC_IN_SELECT_OR_WHERE_CLAUSE`. If cost is
needed, run a second campaign/date query and join downstream:

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  metrics.cost_micros,
  metrics.clicks,
  metrics.impressions
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

Join conversion rows to cost rows on `(segments.date, campaign.id)`. For
ad-hoc analysis, an in-memory pandas/dataframe merge in the sandbox is enough;
no cache table is required.

If the user wants to enumerate conversion actions independently of
campaigns, query the `conversion_action` resource directly — see
[conversion-tracking.md](conversion-tracking.md).

## How to interpret

- Each row is `(date, campaign, conversion_action)`. A campaign that
  fires three actions yields three rows per day.
- `metrics.conversions` is the segmented count for that action; sum
  across actions in a campaign to recover the campaign-level
  `metrics.conversions`.
- `segments.conversion_action_category` (e.g. `PURCHASE`, `SIGNUP`,
  `LEAD`) lets you group ad-hoc events into business categories.
- Joined cost is campaign/date context, not action-attributed spend. Do not
  sum joined cost across conversion actions unless you intentionally allocate
  campaign/date spend across actions first.

## Building a dashboard from this report

The dashboard/data app tool reads tool-sourced data via `tool_data_sources`,
re-aggregates it via `sql_data_sources`, and binds the variables in the
interface source. Cache table convention: `gads_<report>_<scope>`.

```python
result = hyper_data_build_dashboard(
    name="Conversions by Action",
    tool_data_sources={
        "raw_conversions": {
            "tool_name": "google_ads_execute_gaql",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT segments.date, campaign.id, campaign.name, "
                    "segments.conversion_action, segments.conversion_action_name, "
                    "segments.conversion_action_category, metrics.conversions, "
                    "metrics.all_conversions, metrics.conversions_value "
                    "FROM campaign "
                    "WHERE segments.date BETWEEN '2026-03-01' AND '2026-05-12' "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_conv_by_action",
            "mode": "replace",
        },
        "raw_cost": {
            "tool_name": "google_ads_execute_gaql",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT segments.date, campaign.id, campaign.name, "
                    "metrics.cost_micros, metrics.clicks, metrics.impressions "
                    "FROM campaign "
                    "WHERE segments.date BETWEEN '2026-03-01' AND '2026-05-12' "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_campaign_cost",
            "mode": "replace",
        },
    },
    sql_data_sources={
        "totals_by_action": {
            "shape": "rows",
            "sql": (
                "SELECT segments_conversion_action_name AS action, "
                "SUM(metrics_conversions) AS conversions "
                "FROM gads_conv_by_action "
                "GROUP BY 1 ORDER BY conversions DESC"
            ),
        },
        "cost_totals": {
            "shape": "rows",
            "sql": (
                "SELECT SUM(metrics_cost_micros)/1e6 AS cost "
                "FROM gads_campaign_cost"
            ),
        },
        "trend": {
            "shape": "rows",
            "sql": (
                "SELECT segments_date AS date, "
                "segments_conversion_action_name AS action, "
                "SUM(metrics_conversions) AS conversions "
                "FROM gads_conv_by_action GROUP BY 1, 2 ORDER BY 1"
            ),
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, DataTable, DataTableColumn, Grid, Heading, Metric, Muted, Text
from prefab_ui.components.charts import AreaChart, BarChart, ChartSeries

with PrefabApp(title="Conversions by Action") as app:
    total_conversions = sum(row.get("conversions", 0) for row in totals_by_action)
    total_cost = (cost_totals[0].get("cost", 0) if cost_totals else 0)

    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Conversions by Action")
            Muted("Conversion mix, trend, and campaign spend context")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Conversions", value=f"{total_conversions:,.0f}")
            with Card():
                with CardContent():
                    Metric(label="Cost", value=f"${total_cost:,.0f}")

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text("Conversion trend", css_class="text-sm font-medium text-muted-foreground mb-2")
                    AreaChart(
                        data=trend,
                        x_axis="date",
                        series=[ChartSeries(data_key="conversions", label="Conversions")],
                        height=300,
                    )
            with Card():
                with CardContent():
                    Text("Conversions by action", css_class="text-sm font-medium text-muted-foreground mb-2")
                    BarChart(
                        data=totals_by_action,
                        x_axis="action",
                        series=[ChartSeries(data_key="conversions", label="Conversions")],
                        height=300,
                    )

        with Card():
            with CardContent():
                Text("Action detail", css_class="text-sm font-medium text-muted-foreground mb-2")
                DataTable(
                    columns=[
                        DataTableColumn(key="action", header="Action"),
                        DataTableColumn(key="conversions", header="Conversions"),
                    ],
                    rows=totals_by_action,
                )
""",
    refresh={"mode": "scheduled", "cron": "0 * * * *"},
)
```

## Variants

- **Per ad group**: change `FROM campaign` to `FROM ad_group` and add
  `ad_group.id`, `ad_group.name`. Useful when one ad group fires the
  conversion but the campaign rolls up many.
- **Per ad**: `FROM ad_group_ad` plus `ad_group_ad.ad.id`,
  `ad_group_ad.ad.name`. Heavier but useful for ad-level diagnosis.
- **Filtered to one action**: add
  `AND segments.conversion_action = 'customers/.../conversionActions/12345'`
  to focus on a single event.
