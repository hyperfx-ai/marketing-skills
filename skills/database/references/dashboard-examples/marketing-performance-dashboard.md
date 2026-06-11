# Marketing Performance Dashboard Example

Use this when the dashboard requires data from another tool. The agent should
declare `tool_data_sources` to call the tool and cache rows, then use
`sql_data_sources` to shape dashboard variables from the cache table.

```python
hyper_data_build_dashboard(
    name="Marketing Performance Dashboard",
    description="Marketing dashboard backed by a tool cache table and SQL data sources",
    tool_data_sources={
        "raw_campaign_performance": {
            "tool_name": "meta_ads_get_campaign_performance",
            "tool_args": {
                "date_preset": "last_30d",
                "fields": ["campaign", "channel", "spend", "conversions", "revenue"],
            },
            "cache_table": "meta_campaign_performance_last_30d",
            "mode": "replace",
            "rows_path": "rows",
        }
    },
    sql_data_sources={
        "total_spend": {
            "sql": "select '$' || to_char(sum(spend), 'FM999,999') from meta_campaign_performance_last_30d",
            "shape": "scalar",
        },
        "total_conversions": {
            "sql": "select sum(conversions) from meta_campaign_performance_last_30d",
            "shape": "scalar",
        },
        "cost_per_acquisition": {
            "sql": "select '$' || round(sum(spend) / nullif(sum(conversions), 0), 0) from meta_campaign_performance_last_30d",
            "shape": "scalar",
        },
        "roas": {
            "sql": "select round(sum(revenue) / nullif(sum(spend), 0), 1) || 'x' from meta_campaign_performance_last_30d",
            "shape": "scalar",
        },
        "campaign_rows": {
            "sql": "select campaign, spend, conversions, round(spend / nullif(conversions, 0), 0) as cpa, round(revenue / nullif(spend, 0), 1) as roas from meta_campaign_performance_last_30d order by spend desc",
            "shape": "rows",
        },
        "channel_rows": {
            "sql": "select channel, sum(spend) as spend, round(sum(revenue) / nullif(sum(spend), 0), 1) as roas from meta_campaign_performance_last_30d group by channel order by spend desc",
            "shape": "rows",
        },
        "spend_delta": {"sql": "select '+12% vs prior period'", "shape": "scalar"},
        "conversion_delta": {"sql": "select '+18% vs prior period'", "shape": "scalar"},
        "cpa_delta": {"sql": "select '-9% vs prior period'", "shape": "scalar"},
        "roas_delta": {"sql": "select '+0.4x vs prior period'", "shape": "scalar"},
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, Grid, Heading, Metric, Muted, Row, Separator, Text
from prefab_ui.components.charts import BarChart, ChartSeries
from prefab_ui.components.data_table import DataTable, DataTableColumn

with PrefabApp(title="Marketing Performance Dashboard") as app:
    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Marketing Performance Dashboard")
            Muted("Tool rows cached first, then SQL shapes dashboard variables")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Spend", value=total_spend, delta=spend_delta, trend="up")
            with Card():
                with CardContent():
                    Metric(label="Conversions", value=total_conversions, delta=conversion_delta, trend="up")
            with Card():
                with CardContent():
                    Metric(label="CPA", value=cost_per_acquisition, delta=cpa_delta, trend="down")
            with Card():
                with CardContent():
                    Metric(label="ROAS", value=roas, delta=roas_delta, trend="up")

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text("Spend and conversions by campaign", css_class="text-sm font-medium text-muted-foreground mb-2")
                    BarChart(
                        data=campaign_rows,
                        x_axis="campaign",
                        series=[
                            ChartSeries(data_key="spend", label="Spend"),
                            ChartSeries(data_key="conversions", label="Conversions"),
                        ],
                        height=300,
                    )
            with Card():
                with CardContent():
                    Text("Channel mix", css_class="text-sm font-medium text-muted-foreground mb-2")
                    DataTable(
                        rows=channel_rows,
                        columns=[
                            DataTableColumn(key="channel", header="Channel"),
                            DataTableColumn(key="spend", header="Spend"),
                            DataTableColumn(key="roas", header="ROAS"),
                        ],
                    )

        Separator()
        Text("Campaign detail", css_class="text-lg font-semibold")
        DataTable(
            rows=campaign_rows,
            columns=[
                DataTableColumn(key="campaign", header="Campaign", sortable=True),
                DataTableColumn(key="spend", header="Spend", sortable=True),
                DataTableColumn(key="conversions", header="Conversions", sortable=True),
                DataTableColumn(key="cpa", header="CPA", sortable=True),
                DataTableColumn(key="roas", header="ROAS", sortable=True),
            ],
            search=True,
            paginated=True,
        )
""",
)
```
