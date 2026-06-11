# Building Dashboards And Data Apps

A dashboard is a saved visual report in Hyper. A data app is the same idea, but
it may include controls, refreshes, or tool-backed data.

Hyper dashboards use Prefab. Prefab is the UI system that renders dashboard
components such as cards, metrics, charts, tables, grids, rows, columns,
buttons, and controls.

You build a dashboard by writing Python source with `prefab_ui` components, then
passing that source to `hyper_data_build_dashboard` as `prefab_python`. The
dashboard tool runs that Python in its own renderer sandbox and saves the
rendered dashboard.

## The Tools To Use

Use `hyper_data_build_dashboard` to create or update the dashboard.

Always call `hyper_data_search_ui_components` before writing dashboard code. Use
it to confirm component names and available dashboard UI primitives instead of
assuming imports, component names, or props.

`hyper_data_build_dashboard(name, prefab_python, description, sql_data_sources, tool_data_sources, dashboard_id)`

Required:

- `name`
- `prefab_python`

Optional:

- `description`
- `sql_data_sources` when reading Hyper Database tables
- `tool_data_sources` when first calling another tool and caching its rows
- `dashboard_id` when updating an existing dashboard

## Choose The Data Source

1. If the user gives numbers or asks for a static showcase:
   Put small example data directly inside `prefab_python`.
2. If the data is already in Hyper Database:
   Use `sql_data_sources`. Each SQL source creates a Python variable used inside
   `prefab_python`.
3. If the data must come from another tool, such as Google Ads, Gmail, Slack, or
   another provider:
   Use `tool_data_sources` to call the tool and cache rows. Then use
   `sql_data_sources` to shape those cached rows into dashboard variables.
4. If editing an existing dashboard:
   Pass the existing `dashboard_id` so the dashboard updates in place.

## Build Workflow

1. Pick the closest example below before writing code.
2. Call `hyper_data_search_ui_components` for the components you plan to use,
   such as `card`, `metric`, `chart`, `table`, or `select`.
3. Write `prefab_python` using `prefab_ui`.
4. Start with the page layout: `PrefabApp`, then `Column`, `Grid`, `Card`, and
   `CardContent`.
5. Add 3-4 headline `Metric` cards.
6. Add one main chart and one supporting chart or table.
7. Add detail rows or a `DataTable` when useful.
8. Call `hyper_data_build_dashboard`.
9. If the user needs a shareable link, call `hyper_data_publish_dashboard`.

## Aesthetic Rules

A good dashboard should look like an app, not a plain document.

- Use a light gray page background and place white cards on top.
- Put every KPI, chart, table, and detail section inside a `Card` with
  `CardContent`.
- Use `Column(gap=6, css_class="p-6 bg-muted/30 min-h-screen")` or a similar
  page wrapper.
- Use `Grid(columns=4, gap=4)` for KPI cards.
- Use `Grid(columns=[2, 1], gap=6)` or `Grid(columns=[3, 1], gap=6)` for a main
  chart plus a supporting section.
- Keep chart titles small and muted inside cards.
- Avoid floating charts, oversized headings inside cards, and bare white pages.

## Basic Code Shape

```python
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, Grid, Heading, Metric, Muted, Text
from prefab_ui.components.charts import ChartSeries, LineChart

rows = [
    {"date": "Jan", "revenue": 12000},
    {"date": "Feb", "revenue": 18000},
]

with PrefabApp(title="Revenue Dashboard") as app:
    with Column(gap=6, css_class="p-6 bg-muted/30 min-h-screen"):
        Heading("Revenue Dashboard")
        Muted("Static example data")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Revenue", value="$30K", delta="+12%", trend="up")

        with Card():
            with CardContent():
                Text(
                    "Revenue trend",
                    css_class="text-sm font-medium text-muted-foreground mb-2",
                )
                LineChart(
                    data=rows,
                    x_axis="date",
                    series=[ChartSeries(data_key="revenue", label="Revenue")],
                )
```

## Which Example To Load

- Static/user-provided data: `dashboard-examples/static-marketing-dashboard.md`
- Hyper Database SQL dashboard: `dashboard-examples/sales-sql-dashboard.md`
- Tool-backed dashboard:
  `dashboard-examples/marketing-performance-dashboard.md`
- Live data app with refresh/state:
  `dashboard-examples/system-monitor-data-app.md`

## If A Build Fails

Fix the same `prefab_python` source and call `hyper_data_build_dashboard` again.

Use `hyper_data_search_ui_components` and the closest example as the source of
truth for component names, imports, and structure. Reduce the dashboard to a
small working version, then add sections back one at a time.
