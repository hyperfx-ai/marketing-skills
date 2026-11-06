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

Use the GAQL below through `google_ads_gaql_query` when you need
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
- **Several actions with `conversion_action.primary_for_goal = TRUE` in the same category** (e.g. two
  primary purchase actions) → Smart Bidding double-counts; recommend
  demoting one to secondary.
- **`PURCHASE` category but `counting_type = MANY_PER_CLICK`** is rare
  and usually a misconfiguration; flag for review.
- **Lookback window mismatches** between online + offline actions can
  produce inconsistent attribution.

## Building a dashboard from this report

```python
result = data_apps_build(
    name="Conversion Tracking Audit",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_gaql_query",
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
            "cache_table": "gads_conv_actions_1234567890",
            "mode": "replace",
            "rows_path": "results",
        },
    },
    sql_data_sources={
        "by_category": {
            "shape": "rows",
            "sql": (
                "SELECT conversion_action_category AS category, "
                "COUNT(*) AS total_actions, "
                "SUM(CASE WHEN conversion_action_primary_for_goal THEN 1 ELSE 0 END) AS primary_actions "
                "FROM gads_conv_actions_1234567890 GROUP BY 1 ORDER BY 1"
            ),
        },
        "actions": {
            "shape": "rows",
            "sql": (
                "SELECT conversion_action_name AS name, "
                "conversion_action_category AS category, "
                "conversion_action_status AS status, "
                "CASE WHEN conversion_action_primary_for_goal THEN 'Yes' ELSE 'No' END AS is_primary "
                "FROM gads_conv_actions_1234567890 ORDER BY name"
            ),
        },
        "primary_total": {
            "shape": "scalar",
            "sql": (
                "SELECT COUNT(*) FROM gads_conv_actions_1234567890 "
                "WHERE conversion_action_primary_for_goal"
            ),
        },
    },
    template_html="""
<div class="grid gap-3" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));">
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">Actions</p>
    <p class="text-2xl font-semibold tabular-nums">{{ actions | length }}</p>
  </section></div>
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">Primary actions</p>
    <p class="text-2xl font-semibold tabular-nums">{{ primary_total }}</p>
  </section></div>
</div>
<div class="card mt-4">
  <header><h2>Actions by category</h2><p>Total and primary</p></header>
  <section><div class="chart h-64"><canvas id="by_category" aria-label="Conversion actions by category"></canvas></div></section>
</div>
<div class="card mt-4">
  <header><h2>Action inventory</h2><p>Every action that is not removed</p></header>
  <section><div class="table-container"><table class="table">
    <thead><tr><th>Action</th><th>Category</th><th>Status</th><th>Primary</th></tr></thead>
    <tbody>
    {% for row in actions %}
      <tr><td class="break-words">{{ row.name }}</td><td>{{ row.category }}</td><td>{{ row.status }}</td><td>{{ row.is_primary }}</td></tr>
    {% endfor %}
    </tbody>
  </table></div></section>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
  window.basecoat.chart("#by_category", {
    type: "bar", labelKey: "category", legend: true,
    data: {{ by_category | tojson }},
    series: {
      total_actions: { label: "Total", color: "var(--chart-1)" },
      primary_actions: { label: "Primary", color: "var(--chart-2)" }
    }
  });
});
</script>
""",
)
```

`data_apps_refresh(data_app_id=...)` runs the GAQL again and re-renders
the app.

## Variants

- Join with the `conversion-by-action.md` cache table to overlay actual
  conversion volume on each action's setup status.
- Filter to `category = 'PURCHASE'` for ecommerce-only audits.
