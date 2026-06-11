#  System Monitor Data App Example

Use this pattern when a dashboard/data app depends on another tool. The agent
should call `hyper_data_build_dashboard` with `tool_data_sources`; it should not
write or launch a standalone MCP server.

Tool sources populate cache tables. SQL sources then shape those cached rows
into variables for the data app.

```python
hyper_data_build_dashboard(
    name="System Monitor",
    description=" operations dashboard with live host metrics",
    tool_data_sources={
        "system_stats": {
            "tool_name": "system_monitor_snapshot",
            "tool_args": {
                "include_processes": True,
                "history_points": 100,
            },
            "cache_table": "system_monitor_snapshot_latest",
            "mode": "replace",
            "rows_path": "rows",
        }
    },
    sql_data_sources={
        "cpu_pct": {
            "sql": "select cpu_pct from system_monitor_snapshot_latest order by captured_at desc limit 1",
            "shape": "scalar",
        },
        "memory_pct": {
            "sql": "select memory_pct from system_monitor_snapshot_latest order by captured_at desc limit 1",
            "shape": "scalar",
        },
        "disk_pct": {
            "sql": "select disk_pct from system_monitor_snapshot_latest order by captured_at desc limit 1",
            "shape": "scalar",
        },
        "uptime": {
            "sql": "select uptime from system_monitor_snapshot_latest order by captured_at desc limit 1",
            "shape": "scalar",
        },
        "host_label": {
            "sql": "select hostname || ' · ' || platform from system_monitor_snapshot_latest order by captured_at desc limit 1",
            "shape": "scalar",
        },
        "history_rows": {
            "sql": "select captured_at as time, cpu_pct as cpu, memory_pct as memory from system_monitor_snapshot_latest order by captured_at",
            "shape": "rows",
        },
        "top_process_rows": {
            "sql": "select process_name, pid, cpu_pct, memory_pct from system_monitor_snapshot_latest where process_name is not null order by cpu_pct desc limit 8",
            "shape": "rows",
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import (
    Badge,
    Card,
    CardContent,
    Column,
    Grid,
    Heading,
    Metric,
    Muted,
    Progress,
    Row,
    Separator,
    Text,
)
from prefab_ui.components.charts import AreaChart, ChartSeries
from prefab_ui.components.data_table import DataTable, DataTableColumn

with PrefabApp(title="System Monitor") as app:
    with Column(gap=6, css_class="p-6"):
        with Row(gap=3, align="center"):
            Heading("System Monitor")
            Badge(host_label, variant="outline")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="CPU", value=f"{cpu_pct}%")
                    Progress(value=cpu_pct)
            with Card():
                with CardContent():
                    Metric(label="Memory", value=f"{memory_pct}%")
                    Progress(value=memory_pct)
            with Card():
                with CardContent():
                    Metric(label="Disk", value=f"{disk_pct}%")
                    Progress(value=disk_pct)
            with Card():
                with CardContent():
                    Metric(label="Uptime", value=uptime)
                    Muted("Latest tool snapshot")

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text("CPU & Memory", css_class="text-sm font-medium text-muted-foreground mb-2")
                    AreaChart(
                        data=history_rows,
                        series=[
                            ChartSeries(data_key="cpu", label="CPU %"),
                            ChartSeries(data_key="memory", label="Memory %"),
                        ],
                        x_axis="time",
                        curve="smooth",
                        show_legend=True,
                        height=300,
                        animate=False,
                    )
            with Card():
                with CardContent():
                    Text("Top Processes", css_class="text-sm font-medium text-muted-foreground mb-2")
                    DataTable(
                        rows=top_process_rows,
                        columns=[
                            DataTableColumn(key="process_name", header="Process"),
                            DataTableColumn(key="cpu_pct", header="CPU"),
                            DataTableColumn(key="memory_pct", header="Memory"),
                        ],
                    )

        Separator()
        Text("Process detail", css_class="text-lg font-semibold")
        DataTable(
            rows=top_process_rows,
            columns=[
                DataTableColumn(key="process_name", header="Process", sortable=True),
                DataTableColumn(key="pid", header="PID", sortable=True),
                DataTableColumn(key="cpu_pct", header="CPU", sortable=True),
                DataTableColumn(key="memory_pct", header="Memory", sortable=True),
            ],
        )
""",
)
```
