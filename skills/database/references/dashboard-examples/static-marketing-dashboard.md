# Static Marketing Dashboard Example

Use this pattern when the user provides the data directly or the dataset is
small enough to define inline. Do not require SQL for this case.

```python
hyper_data_build_dashboard(
    name="Marketing Snapshot",
    description="Static KPI dashboard from user-provided channel metrics",
    prefab_python="""
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
from prefab_ui.components.charts import BarChart, ChartSeries

channel_rows = [
    {"channel": "Search", "leads": 124, "cost": 4200, "conversion": 7.8},
    {"channel": "Social", "leads": 76, "cost": 3100, "conversion": 4.9},
    {"channel": "Email", "leads": 42, "cost": 800, "conversion": 12.2},
]

total_leads = sum(row["leads"] for row in channel_rows)
total_cost = sum(row["cost"] for row in channel_rows)
cost_per_lead = round(total_cost / total_leads)
best_channel = max(channel_rows, key=lambda row: row["conversion"])

with PrefabApp(title="Marketing Snapshot") as app:
    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Marketing Snapshot")
            Muted("Static channel performance")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Total Leads", value=total_leads)
            with Card():
                with CardContent():
                    Metric(label="Spend", value=f"${total_cost:,}")
            with Card():
                with CardContent():
                    Metric(label="Cost per Lead", value=f"${cost_per_lead}")
            with Card():
                with CardContent():
                    Metric(label="Best Channel", value=best_channel["channel"])

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text(
                        "Leads by channel",
                        css_class="text-sm font-medium text-muted-foreground mb-2",
                    )
                    BarChart(
                        data=channel_rows,
                        x_axis="channel",
                        series=[ChartSeries(data_key="leads", label="Leads")],
                        height=280,
                    )

            with Card():
                with CardContent():
                    Text(
                        "Conversion leaders",
                        css_class="text-sm font-medium text-muted-foreground mb-2",
                    )
                    with Column(gap=2):
                        for row in sorted(
                            channel_rows,
                            key=lambda item: item["conversion"],
                            reverse=True,
                        ):
                            with Row(justify="between", align="center"):
                                Text(row["channel"])
                                Muted(f"{row['conversion']}%")

        Separator()

        Text("Channel detail", css_class="text-lg font-semibold")
        DataTable(
            rows=channel_rows,
            columns=[
                DataTableColumn(key="channel", header="Channel", sortable=True),
                DataTableColumn(key="leads", header="Leads", sortable=True),
                DataTableColumn(key="cost", header="Cost", sortable=True),
                DataTableColumn(key="conversion", header="Conversion", sortable=True),
            ],
            search=True,
            paginated=False,
        )
""",
)
```
