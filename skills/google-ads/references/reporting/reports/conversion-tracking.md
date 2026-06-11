# Conversion Tracking

Conversion-action inventory report. Use it to list configured
conversion actions and their metadata before building action-specific
dashboards.

## When to use

- "Which conversion actions exist?"
- "Which conversion actions are enabled?"
- "What are the conversion action categories and settings?"
- Before building a funnel dashboard that needs user-mapped stages.

## Inputs

- `customer_id` (required).

Use the GAQL below through `google_ads_execute_gaql` when you need
conversion-action metadata. This is separate from campaign-level
conversion metrics, which use `segments.conversion_action*`.

## GAQL

```sql
SELECT
  conversion_action.id,
  conversion_action.name,
  conversion_action.category,
  conversion_action.type,
  conversion_action.status,
  conversion_action.primary_for_goal,
  conversion_action.counting_type,
  conversion_action.click_through_lookback_window_days
FROM conversion_action
WHERE conversion_action.status != 'REMOVED'
```

## How to interpret

- **No enabled conversion actions** → optimization is blind; halt all
  Smart Bidding advice until at least one is configured.
- **Multiple `PRIMARY_FOR_GOAL` actions in the same category** (e.g. two
  primary purchase actions) → Smart Bidding double-counts; recommend
  demoting one to secondary.
- **`PURCHASE` category but `counting_type = MANY_PER_CLICK`** is rare
  and usually a misconfiguration; flag for review.
- **Lookback window mismatches** between online + offline actions can
  produce inconsistent attribution.

## Building a dashboard from this report

```python
result = hyper_data_build_dashboard(
    name="Conversion Tracking Audit",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_execute_gaql",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT conversion_action.id, conversion_action.name, "
                    "conversion_action.category, conversion_action.type, "
                    "conversion_action.status, conversion_action.primary_for_goal, "
                    "conversion_action.counting_type, "
                    "conversion_action.click_through_lookback_window_days "
                    "FROM conversion_action "
                    "WHERE conversion_action.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_conv_actions",
            "mode": "replace",
        },
    },
    sql_data_sources={
        "by_category": {
            "shape": "rows",
            "sql": (
                "SELECT conversion_action_category AS category, "
                "COUNT(*) AS total_actions, "
                "SUM(CASE WHEN conversion_action_primary_for_goal THEN 1 ELSE 0 END) AS primary_actions "
                "FROM gads_conv_actions GROUP BY 1 ORDER BY 1"
            ),
        },
        "actions": {
            "shape": "rows",
            "sql": (
                "SELECT conversion_action_name AS name, "
                "conversion_action_category AS category, "
                "conversion_action_status AS status, "
                "conversion_action_primary_for_goal AS primary "
                "FROM gads_conv_actions ORDER BY name"
            ),
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, DataTable, DataTableColumn, Grid, Heading, Metric, Muted, Text
from prefab_ui.components.charts import BarChart, ChartSeries

with PrefabApp(title="Conversion Tracking Audit") as app:
    primary_actions = sum(row.get("primary_actions", 0) for row in by_category)

    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Conversion Tracking Audit")
            Muted("Configured actions, primary actions, and status")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Actions", value=f"{len(actions):,}")
            with Card():
                with CardContent():
                    Metric(label="Primary Actions", value=f"{primary_actions:,.0f}")

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text("Actions by category", css_class="text-sm font-medium text-muted-foreground mb-2")
                    BarChart(
                        data=by_category,
                        x_axis="category",
                        series=[
                            ChartSeries(data_key="total_actions", label="Total"),
                            ChartSeries(data_key="primary_actions", label="Primary"),
                        ],
                        show_legend=True,
                        height=300,
                    )
            with Card():
                with CardContent():
                    Text("Action inventory", css_class="text-sm font-medium text-muted-foreground mb-2")
                    DataTable(
                        columns=[
                            DataTableColumn(key="name", header="Action"),
                            DataTableColumn(key="category", header="Category"),
                            DataTableColumn(key="status", header="Status"),
                            DataTableColumn(key="primary", header="Primary"),
                        ],
                        rows=actions,
                    )
""",
    refresh={"mode": "manual"},
)
```

## Variants

- Join with the `conversion-by-action.md` cache table to overlay actual
  conversion volume on each action's setup status.
- Filter to `category = 'PURCHASE'` for ecommerce-only audits.
