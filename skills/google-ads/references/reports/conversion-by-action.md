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

The data app runs the GAQL through `tool_data_sources`, re-aggregates the
cached rows with `sql_data_sources`, and binds those variables in its
template. Cache table convention: `gads_<report>_<scope>`.

```python
result = data_apps_build(
    name="Conversions by Action",
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
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_conv_by_action_1234567890",
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
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_campaign_cost_1234567890",
            "mode": "replace",
            "rows_path": "results",
        },
    },
    sql_data_sources={
        "totals_by_action": {
            "shape": "rows",
            "sql": (
                "SELECT segments_conversion_action_name AS action, "
                "SUM(metrics_conversions::numeric) AS conversions "
                "FROM gads_conv_by_action_1234567890 "
                "GROUP BY 1 ORDER BY conversions DESC"
            ),
        },
        "kpis": {
            "shape": "rows",
            "sql": (
                "SELECT 'Conversions' AS label, to_char(COALESCE(SUM(metrics_conversions::numeric), 0), 'FM999,999,990.0') AS value FROM gads_conv_by_action_1234567890 "
                "UNION ALL SELECT 'Cost', '$' || to_char(COALESCE(SUM(metrics_cost_micros::numeric), 0) / 1e6, 'FM999,999,990.00') FROM gads_campaign_cost_1234567890"
            ),
        },
        "trend": {
            "shape": "rows",
            "sql": (
                "SELECT segments_date AS date, "
                "SUM(metrics_conversions::numeric) AS conversions "
                "FROM gads_conv_by_action_1234567890 GROUP BY 1 ORDER BY 1"
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
    <header><h2>Conversion trend</h2><p>All actions, by day</p></header>
    <section><div class="chart h-64"><canvas id="trend" aria-label="Conversions by day"></canvas></div></section>
  </div>
  <div class="card min-w-0">
    <header><h2>Conversions by action</h2></header>
    <section><div class="chart h-64"><canvas id="by_action" aria-label="Conversions by action"></canvas></div></section>
  </div>
</div>
<div class="card mt-4">
  <header><h2>Action detail</h2></header>
  <section><div class="table-container"><table class="table">
    <thead><tr><th>Action</th><th>Conversions</th></tr></thead>
    <tbody>
    {% for row in totals_by_action %}
      <tr><td class="break-words">{{ row.action }}</td><td class="tabular-nums">{{ "%.1f"|format(row.conversions) }}</td></tr>
    {% endfor %}
    </tbody>
  </table></div></section>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
  window.basecoat.chart("#trend", {
    type: "line", labelKey: "date",
    data: {{ trend | tojson }},
    series: { conversions: { label: "Conversions", color: "var(--chart-1)", dataset: { fill: true, tension: 0.35 } } }
  });
  window.basecoat.chart("#by_action", {
    type: "bar", labelKey: "action", options: { indexAxis: "y" },
    data: {{ totals_by_action | tojson }},
    series: { conversions: { label: "Conversions", color: "var(--chart-2)" } }
  });
});
</script>
""",
)
```

`data_apps_refresh(data_app_id=...)` runs both GAQL queries again and
re-renders the app; the window stays the last 30 days.

## Variants

- **Per ad group**: change `FROM campaign` to `FROM ad_group` and add
  `ad_group.id`, `ad_group.name`. Useful when one ad group fires the
  conversion but the campaign rolls up many.
- **Per ad**: `FROM ad_group_ad` plus `ad_group_ad.ad.id`,
  `ad_group_ad.ad.name`. Heavier but useful for ad-level diagnosis.
- **Filtered to one action**: add
  `AND segments.conversion_action = 'customers/.../conversionActions/12345'`
  to focus on a single event.
