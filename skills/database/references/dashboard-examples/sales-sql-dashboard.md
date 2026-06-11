# SQL Sales Dashboard Example

Use this pattern when dashboard values should be queried from Hyper Database.
Keep SQL in `sql_data_sources` and reference injected variables in the
dashboard source.

```python
{
  "name": "Sales Performance Dashboard",
  "description": "Weekly sales analysis with headline metrics and trend detail",
  "prefab_python": """
from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card,
    CardContent,
    Column,
    DataTable,
    DataTableColumn,
    Grid,
    Heading,
    Metric,
    Muted,
    Row,
    Separator,
    Text,
)
from prefab_ui.components.charts import AreaChart, ChartSeries, PieChart

with PrefabApp(title="Sales Performance Dashboard") as app:
    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Sales Dashboard")
            Muted("Current quarter performance")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(
                        label="Revenue Last 7 Days",
                        value=revenue_last_7_days,
                        delta=revenue_delta,
                        trend="up",
                    )
            with Card():
                with CardContent():
                    Metric(label="Active Customers", value=active_customers)
            with Card():
                with CardContent():
                    Metric(label="Average Deal Size", value=avg_deal_size)
            with Card():
                with CardContent():
                    Metric(label="Win Rate", value=win_rate)

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text(
                        "Revenue Trend",
                        css_class="text-sm font-medium text-muted-foreground mb-2",
                    )
                    AreaChart(
                        data=daily_revenue,
                        x_axis="date",
                        series=[ChartSeries(data_key="revenue", label="Revenue")],
                        height=300,
                        y_axis_format="compact",
                    )

            with Card():
                with CardContent():
                    Text(
                        "Revenue by Segment",
                        css_class="text-sm font-medium text-muted-foreground mb-2",
                    )
                    PieChart(
                        data=revenue_by_segment,
                        data_key="revenue",
                        name_key="segment",
                        inner_radius=50,
                        height=300,
                    )

        Separator()

        Text("Top Accounts", css_class="text-lg font-semibold")
        DataTable(
            rows=top_accounts,
            columns=[
                DataTableColumn(key="account_name", header="Account", sortable=True),
                DataTableColumn(key="revenue", header="Revenue", sortable=True),
                DataTableColumn(key="owner", header="Owner", sortable=True),
                DataTableColumn(key="stage", header="Stage", sortable=True),
            ],
            search=True,
            paginated=True,
        )
""",
  "sql_data_sources": {
    "revenue_last_7_days": {
      "sql": "select coalesce(sum(revenue), 0) from sales where date >= current_date - interval '7 days'",
      "shape": "scalar"
    },
    "revenue_delta": {
      "sql": "select '+18.2% YoY'",
      "shape": "scalar"
    },
    "active_customers": {
      "sql": "select count(distinct account_id) from sales where date >= current_date - interval '90 days'",
      "shape": "scalar"
    },
    "avg_deal_size": {
      "sql": "select coalesce(avg(revenue), 0) from sales where date >= current_date - interval '90 days'",
      "shape": "scalar"
    },
    "win_rate": {
      "sql": "select coalesce(round(100.0 * sum(case when stage = 'Closed Won' then 1 else 0 end) / nullif(count(*), 0), 1), 0) from opportunities",
      "shape": "scalar"
    },
    "daily_revenue": {
      "sql": "select date, sum(revenue) as revenue from sales group by date order by date",
      "shape": "rows"
    },
    "revenue_by_segment": {
      "sql": "select segment, sum(revenue) as revenue from sales group by segment order by revenue desc",
      "shape": "rows"
    },
    "top_accounts": {
      "sql": "select account_name, sum(revenue) as revenue, max(owner) as owner, max(stage) as stage from sales group by account_name order by revenue desc limit 10",
      "shape": "rows"
    }
  }
}
```
