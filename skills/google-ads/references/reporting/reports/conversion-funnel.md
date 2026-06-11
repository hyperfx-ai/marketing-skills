# Conversion Funnel

Multi-stage conversion funnel for lead-gen / B2B accounts. Pivots
per-action conversion data into ordered funnel stages and computes
step-conversion rates between stages.

## When to use

- Lead-gen / B2B accounts with multiple sequential stages (e.g.
  application_submitted → lead_reached → scheduled → showed → won).
- "What's the drop-off between [stage A] and [stage B]?"
- "Which stage is the bottleneck?"
- Pricing or onboarding optimization rooted in funnel data.

For a flat per-action breakdown without ordering, use
[conversion-by-action.md](conversion-by-action.md) instead.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).
- An ordered list of conversion-action names (or IDs) that defines the
  funnel. **The agent must discover these first** — no funnel ordering
  is hard-coded.

## GAQL

### Step 1 — discover the user's conversion actions

```sql
SELECT
  conversion_action.id,
  conversion_action.name,
  conversion_action.category,
  conversion_action.status
FROM conversion_action
WHERE conversion_action.status != 'REMOVED'
```

Show the result to the user and ask them to map each action to a funnel
stage in order. **Do not assume a six-stage funnel** (or any stage count) —
funnels are workspace-specific.

### Step 2 — pull per-action data

Same shape as [conversion-by-action.md](conversion-by-action.md):

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

The same caveat applies: **only** segment via
`segments.conversion_action*`, never `conversion_action.id` against
`FROM campaign` (raises `PROHIBITED_RESOURCE_TYPE_IN_SELECT_CLAUSE`).
The metric is `metrics.conversions`, not the nonexistent
`metrics.conversions_by_conversion_action`.

Do **not** include `metrics.cost_micros` in the per-action query. Google Ads
rejects cost with `segments.conversion_action*` using
`PROHIBITED_SEGMENT_WITH_METRIC_IN_SELECT_OR_WHERE_CLAUSE`. If cost is needed,
run a separate campaign/date query:

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
one-off analysis, join in memory with pandas or an equivalent dataframe in the
sandbox; cache tables are only needed for dashboard/data-app builds.

## How to interpret

- Pivot the raw rows so each user-mapped stage becomes a column,
  values are stage totals.
- Step conversion rate = `stage_n / stage_n-1`.
- Joined cost is campaign/date context. Do not present it as action-attributed
  cost per stage unless the report explicitly defines an allocation rule.
- State the user-provided stage mapping in the final report. Do not
  infer action order from names alone.

## Building a dashboard from this report

```python
# After the agent has mapped action names to ordered stages, e.g.
# stages = ["application_submitted", "lead_reached",
#           "scheduled_for_training", "showed_for_training",
#           "launched_from_training", "rep_that_sells"]
result = hyper_data_build_dashboard(
    name="Lead-Gen Funnel",
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
            "cache_table": "gads_funnel_raw",
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
            "cache_table": "gads_funnel_cost",
            "mode": "replace",
        },
    },
    sql_data_sources={
        "stage_totals": {
            "shape": "rows",
            "sql": (
                "SELECT segments_conversion_action_name AS stage, "
                "CASE segments_conversion_action_name "
                "WHEN 'application_submitted' THEN 1 "
                "WHEN 'lead_reached' THEN 2 "
                "WHEN 'scheduled_for_training' THEN 3 "
                "WHEN 'showed_for_training' THEN 4 "
                "WHEN 'launched_from_training' THEN 5 "
                "WHEN 'rep_that_sells' THEN 6 END AS stage_order, "
                "SUM(metrics_conversions) AS conversions "
                "FROM gads_funnel_raw "
                "WHERE segments_conversion_action_name IN ("
                "  'application_submitted', 'lead_reached', "
                "  'scheduled_for_training', 'showed_for_training', "
                "  'launched_from_training', 'rep_that_sells'"
                ") GROUP BY 1, 2 ORDER BY 2"
            ),
        },
        "step_rates": {
            "shape": "rows",
            "sql": (
                "WITH ordered AS ("
                "  SELECT segments_conversion_action_name AS stage, "
                "  CASE segments_conversion_action_name "
                "  WHEN 'application_submitted' THEN 1 "
                "  WHEN 'lead_reached' THEN 2 "
                "  WHEN 'scheduled_for_training' THEN 3 "
                "  WHEN 'showed_for_training' THEN 4 "
                "  WHEN 'launched_from_training' THEN 5 "
                "  WHEN 'rep_that_sells' THEN 6 END AS stage_order, "
                "  SUM(metrics_conversions) AS conversions "
                "  FROM gads_funnel_raw "
                "  WHERE segments_conversion_action_name IN ("
                "    'application_submitted', 'lead_reached', "
                "    'scheduled_for_training', 'showed_for_training', "
                "    'launched_from_training', 'rep_that_sells'"
                "  ) GROUP BY 1, 2"
                ") SELECT stage, conversions, "
                "conversions / NULLIF(LAG(conversions) OVER (ORDER BY stage_order), 0) "
                "AS step_rate "
                "FROM ordered ORDER BY stage_order"
            ),
        },
        "cost_totals": {
            "shape": "rows",
            "sql": (
                "SELECT SUM(metrics_cost_micros)/1e6 AS cost "
                "FROM gads_funnel_cost"
            ),
        },
        "stage_trend": {
            "shape": "rows",
            "sql": (
                "SELECT segments_date AS date, "
                "segments_conversion_action_name AS stage, "
                "SUM(metrics_conversions) AS conversions "
                "FROM gads_funnel_raw GROUP BY 1, 2 ORDER BY 1"
            ),
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, DataTable, DataTableColumn, Grid, Heading, Metric, Muted, Text
from prefab_ui.components.charts import AreaChart, BarChart, ChartSeries

with PrefabApp(title="Lead-Gen Funnel") as app:
    total_conversions = sum(row.get("conversions", 0) for row in stage_totals)
    total_cost = (cost_totals[0].get("cost", 0) if cost_totals else 0)

    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Lead-Gen Funnel")
            Muted("Stage volume, trend, and step-rate health")

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
                    Text("Stage trend", css_class="text-sm font-medium text-muted-foreground mb-2")
                    AreaChart(
                        data=stage_trend,
                        x_axis="date",
                        series=[ChartSeries(data_key="conversions", label="Conversions")],
                        height=300,
                    )
            with Card():
                with CardContent():
                    Text("Stage totals", css_class="text-sm font-medium text-muted-foreground mb-2")
                    BarChart(
                        data=stage_totals,
                        x_axis="stage",
                        series=[ChartSeries(data_key="conversions", label="Conversions")],
                        height=300,
                    )

        with Grid(columns=[1, 1], gap=6):
            with Card():
                with CardContent():
                    Text("Stage detail", css_class="text-sm font-medium text-muted-foreground mb-2")
                    DataTable(
                        columns=[
                            DataTableColumn(key="stage", header="Stage"),
                            DataTableColumn(key="conversions", header="Conversions"),
                        ],
                        rows=stage_totals,
                    )
            with Card():
                with CardContent():
                    Text("Step rates", css_class="text-sm font-medium text-muted-foreground mb-2")
                    DataTable(
                        columns=[
                            DataTableColumn(key="stage", header="Stage"),
                            DataTableColumn(key="conversions", header="Conversions"),
                            DataTableColumn(key="step_rate", header="Step Rate"),
                        ],
                        rows=step_rates,
                    )
""",
    refresh={"mode": "scheduled", "cron": "0 * * * *"},
)
```

## Variants

- **Step rates**: add an `sql_data_sources` entry that uses window
  functions (`LAG`) to compute `conversions / lag_conversions` between
  ordered stages and bind it to a separate KPI row.
- **Per campaign**: filter `WHERE campaign.id = ...` to compare funnel
  shapes between campaigns.
- **Allocated cost per stage**: join campaign/date cost to conversion rows,
  then apply an explicit allocation rule before presenting stage cost.
