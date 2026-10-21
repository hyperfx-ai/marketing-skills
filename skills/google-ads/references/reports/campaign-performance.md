# Campaign Performance

Time-series view of spend, clicks, conversions, and ROAS per campaign.
The general-purpose performance dashboard — pair with the diagnosis
reports when an issue surfaces.

## When to use

- "How is each campaign performing over time?"
- Weekly / monthly performance review with the client.
- Identifying trend changes (sudden spend spike, conversion drop).
- The default first dashboard for a new client engagement.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).
- Optional: `campaign_ids` filter.

Use the GAQL below through `google_ads_gaql_query` for both ad-hoc
reporting and refreshable dashboards.

## GAQL

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  campaign.advertising_channel_type,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.ctr,
  metrics.average_cpc
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

## How to interpret

- Daily ROAS = `conversions_value / cost`. Plot as time series; a
  step-down on a known date often correlates with an ad / landing-page
  change.
- A sustained drop in conversions with steady spend = tracking issue
  or seasonality, not necessarily campaign decay.
- Compare campaigns of the same `advertising_channel_type`; cross-type
  comparisons (Search vs PMax) are misleading.

## Building a dashboard from this report

Google returns the int64 metrics (`cost_micros`, `clicks`, `impressions`)
as strings, so every metric is cast with `::numeric` in SQL.

```python
result = data_apps_build(
    name="Campaign Performance",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_gaql_query",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT segments.date, campaign.id, campaign.name, "
                    "campaign.advertising_channel_type, "
                    "metrics.impressions, metrics.clicks, metrics.cost_micros, "
                    "metrics.conversions, metrics.conversions_value "
                    "FROM campaign "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_campaign_performance",
            "mode": "replace",
            "rows_path": "results",
        },
    },
    sql_data_sources={
        "kpis": {
            "shape": "rows",
            "sql": (
                "SELECT 'Spend' AS label, '$' || to_char(COALESCE(SUM(metrics_cost_micros::numeric), 0) / 1e6, 'FM999,999,990.00') AS value FROM gads_campaign_performance "
                "UNION ALL SELECT 'Conversions', to_char(COALESCE(SUM(metrics_conversions::numeric), 0), 'FM999,999,990.0') FROM gads_campaign_performance "
                "UNION ALL SELECT 'Revenue', '$' || to_char(COALESCE(SUM(metrics_conversions_value::numeric), 0), 'FM999,999,990.00') FROM gads_campaign_performance "
                "UNION ALL SELECT 'ROAS', COALESCE(to_char(SUM(metrics_conversions_value::numeric) / NULLIF(SUM(metrics_cost_micros::numeric) / 1e6, 0), 'FM990.00') || 'x', '–') FROM gads_campaign_performance"
            ),
        },
        "daily_totals": {
            "shape": "rows",
            "sql": (
                "SELECT segments_date AS date, "
                "ROUND(SUM(metrics_cost_micros::numeric) / 1e6, 2) AS spend, "
                "SUM(metrics_conversions::numeric) AS conversions, "
                "ROUND(SUM(metrics_conversions_value::numeric), 2) AS revenue "
                "FROM gads_campaign_performance GROUP BY 1 ORDER BY 1"
            ),
        },
        "by_campaign": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, "
                "campaign_advertising_channel_type AS channel, "
                "SUM(metrics_cost_micros::numeric) / 1e6 AS spend, "
                "SUM(metrics_conversions::numeric) AS conversions, "
                "COALESCE(SUM(metrics_conversions_value::numeric) / NULLIF(SUM(metrics_cost_micros::numeric) / 1e6, 0), 0) AS roas "
                "FROM gads_campaign_performance GROUP BY 1, 2 ORDER BY spend DESC LIMIT 25"
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
<div class="card mt-4">
  <header><h2>Daily performance</h2><p>Last 30 days</p></header>
  <section><div class="chart h-64"><canvas id="daily" aria-label="Daily spend, conversions and revenue"></canvas></div></section>
</div>
<div class="card mt-4">
  <header><h2>Campaign detail</h2><p>By spend, last 30 days</p></header>
  <section><div class="table-container"><table class="table">
    <thead><tr><th>Campaign</th><th>Channel</th><th>Spend</th><th>Conversions</th><th>ROAS</th></tr></thead>
    <tbody>
    {% for row in by_campaign %}
      <tr><td class="break-words">{{ row.campaign }}</td><td>{{ row.channel }}</td>
        <td class="tabular-nums">${{ "%.2f"|format(row.spend) }}</td>
        <td class="tabular-nums">{{ "%.1f"|format(row.conversions) }}</td>
        <td class="tabular-nums">{{ "%.2f"|format(row.roas) }}x</td></tr>
    {% endfor %}
    </tbody>
  </table></div></section>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
  window.basecoat.chart("#daily", {
    type: "line", labelKey: "date", legend: true,
    data: {{ daily_totals | tojson }},
    series: {
      spend: { label: "Spend", color: "var(--chart-1)" },
      conversions: { label: "Conversions", color: "var(--chart-2)" },
      revenue: { label: "Revenue", color: "var(--chart-3)" }
    }
  });
});
</script>
""",
)
```

`data_apps_refresh(data_app_id=...)` runs the GAQL again and re-renders
the app; the window stays the last 30 days.

## Variants

- Add `metrics.search_impression_share` and
  `metrics.search_top_impression_share` to spot lost-by-budget /
  lost-by-rank issues.
- Group by `segments.device` for desktop vs mobile vs tablet splits.
