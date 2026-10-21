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

Google returns the int64 metrics (`cost_micros`, `clicks`, `impressions`)
as strings, so every metric is cast with `::numeric` in SQL.

```python
# After the agent has mapped action names to ordered stages, e.g.
# stages = ["application_submitted", "lead_reached",
#           "scheduled_for_training", "showed_for_training",
#           "launched_from_training", "rep_that_sells"]
result = data_apps_build(
    name="Lead-Gen Funnel",
    tool_data_sources={
        "raw_conversions": {
            "tool_name": "google_ads_gaql_query",
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
            "rows_path": "results",
        },
        "raw_cost": {
            "tool_name": "google_ads_gaql_query",
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
            "rows_path": "results",
        },
    },
    sql_data_sources={
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
                "  SUM(metrics_conversions::numeric) AS conversions "
                "  FROM gads_funnel_raw "
                "  WHERE segments_conversion_action_name IN ("
                "    'application_submitted', 'lead_reached', "
                "    'scheduled_for_training', 'showed_for_training', "
                "    'launched_from_training', 'rep_that_sells'"
                "  ) GROUP BY 1, 2"
                ") SELECT stage, conversions, "
                "COALESCE(to_char(100 * conversions / NULLIF(LAG(conversions) OVER (ORDER BY stage_order), 0), 'FM990.0') || '%', '–') "
                "AS step_rate "
                "FROM ordered ORDER BY stage_order"
            ),
        },
        "kpis": {
            "shape": "rows",
            "sql": (
                "SELECT 'Conversions' AS label, to_char(COALESCE(SUM(metrics_conversions::numeric), 0), 'FM999,999,990.0') AS value FROM gads_funnel_raw "
                "UNION ALL SELECT 'Cost', '$' || to_char(COALESCE(SUM(metrics_cost_micros::numeric), 0) / 1e6, 'FM999,999,990.00') FROM gads_funnel_cost"
            ),
        },
        "stage_trend": {
            "shape": "rows",
            "sql": (
                "SELECT segments_date AS date, "
                "SUM(metrics_conversions::numeric) AS conversions "
                "FROM gads_funnel_raw GROUP BY 1 ORDER BY 1"
            ),
        },
    },
    template_html="""
<div class="grid gap-3" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));">
  {% for kpi in kpis %}
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">{{ kpi.label }}</p>
    <p class="text-2xl font-semibold tabular-nums">{{ kpi.value }}</p>
  </section></div>
  {% endfor %}
</div>
<div class="grid gap-4 mt-4" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr));">
  <div class="card min-w-0">
    <header><h2>Stage totals</h2><p>In funnel order</p></header>
    <section><div class="chart h-64"><canvas id="stages" aria-label="Conversions by funnel stage"></canvas></div></section>
  </div>
  <div class="card min-w-0">
    <header><h2>Conversion trend</h2><p>All stages, by day</p></header>
    <section><div class="chart h-64"><canvas id="trend" aria-label="Conversions by day"></canvas></div></section>
  </div>
</div>
<div class="card mt-4">
  <header><h2>Step rates</h2><p>Each stage over the stage before it</p></header>
  <section><div class="table-container"><table class="table">
    <thead><tr><th>Stage</th><th>Conversions</th><th>Step rate</th></tr></thead>
    <tbody>
    {% for row in step_rates %}
      <tr><td class="break-words">{{ row.stage }}</td>
        <td class="tabular-nums">{{ "%.1f"|format(row.conversions) }}</td>
        <td class="tabular-nums">{{ row.step_rate }}</td></tr>
    {% endfor %}
    </tbody>
  </table></div></section>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
  window.basecoat.chart("#stages", {
    type: "bar", labelKey: "stage", options: { indexAxis: "y" },
    data: {{ step_rates | tojson }},
    series: { conversions: { label: "Conversions", color: "var(--chart-1)" } }
  });
  window.basecoat.chart("#trend", {
    type: "line", labelKey: "date",
    data: {{ stage_trend | tojson }},
    series: { conversions: { label: "Conversions", color: "var(--chart-2)", dataset: { fill: true, tension: 0.35 } } }
  });
});
</script>
""",
)
```

`data_apps_refresh(data_app_id=...)` runs both GAQL queries again and
re-renders the app.

## Variants

- **Step rates**: add an `sql_data_sources` entry that uses window
  functions (`LAG`) to compute `conversions / lag_conversions` between
  ordered stages and bind it to a separate KPI row.
- **Per campaign**: filter `WHERE campaign.id = ...` to compare funnel
  shapes between campaigns.
- **Allocated cost per stage**: join campaign/date cost to conversion rows,
  then apply an explicit allocation rule before presenting stage cost.
