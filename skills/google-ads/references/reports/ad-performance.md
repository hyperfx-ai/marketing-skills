# Ad Performance

Ad-level (RSA / asset) performance across campaigns. Drives creative
optimization, ad rotation diagnosis, and asset-replacement decisions.

## When to use

- "Which ads are working / failing?"
- Before rotating creatives or pausing underperforming RSAs.
- After uploading new asset variants to compare against the baseline.
- Diagnosing low-CTR ad groups that may be a creative problem rather
  than a targeting one.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).
- Optional: `campaign_ids` to scope.

## GAQL

```sql
SELECT
  ad_group_ad.ad.id,
  ad_group_ad.ad.name,
  ad_group_ad.ad.type,
  ad_group_ad.status,
  ad_group.name,
  campaign.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.ctr,
  metrics.average_cpc
FROM ad_group_ad
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND ad_group_ad.status != 'REMOVED'
  AND ad_group.status != 'REMOVED'
  AND campaign.status != 'REMOVED'
```

## How to interpret

- High-impression / low-CTR ads = creative or relevance problem;
  candidates for headline / description rotation.
- Low-impression ads (relative to peers in the same ad group) =
  ad_strength / serving issue, not necessarily a performance issue.
- An RSA dominating impressions inside an ad group should be the
  benchmark when proposing variants.

## Building a dashboard from this report

An RSA has no `ad.name`, so the table labels each ad by its ad group and id.

```python
result = data_apps_build(
    name="Ad Performance",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_gaql_query",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, "
                    "ad_group_ad.status, ad_group.name, campaign.name, "
                    "metrics.impressions, metrics.clicks, metrics.cost_micros, "
                    "metrics.conversions "
                    "FROM ad_group_ad "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND ad_group_ad.status != 'REMOVED' "
                    "AND ad_group.status != 'REMOVED' "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_ad_performance_1234567890",
            "mode": "replace",
            "rows_path": "results",
        },
    },
    sql_data_sources={
        "kpis": {
            "shape": "rows",
            "sql": (
                "SELECT 'Clicks' AS label, to_char(COALESCE(SUM(metrics_clicks::numeric), 0), 'FM999,999,999') AS value FROM gads_ad_performance_1234567890 "
                "UNION ALL SELECT 'Conversions', to_char(COALESCE(SUM(metrics_conversions::numeric), 0), 'FM999,999,990.0') FROM gads_ad_performance_1234567890 "
                "UNION ALL SELECT 'Spend', '$' || to_char(COALESCE(SUM(metrics_cost_micros::numeric), 0) / 1e6, 'FM999,999,990.00') FROM gads_ad_performance_1234567890"
            ),
        },
        "top_ads": {
            "shape": "rows",
            "sql": (
                "SELECT ad_group_name || ' · ad ' || ad_group_ad_ad_id AS ad, "
                "campaign_name AS campaign, "
                "SUM(metrics_impressions::numeric) AS impressions, "
                "SUM(metrics_clicks::numeric) AS clicks, "
                "SUM(metrics_conversions::numeric) AS conversions, "
                "SUM(metrics_cost_micros::numeric) / 1e6 AS spend "
                "FROM gads_ad_performance_1234567890 "
                "GROUP BY 1, 2 ORDER BY clicks DESC LIMIT 25"
            ),
        },
        "by_type": {
            "shape": "rows",
            "sql": (
                "SELECT ad_group_ad_ad_type AS ad_type, "
                "SUM(metrics_clicks::numeric) AS clicks, "
                "SUM(metrics_conversions::numeric) AS conversions "
                "FROM gads_ad_performance_1234567890 GROUP BY 1 ORDER BY clicks DESC"
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
  <header><h2>Clicks by ad type</h2><p>Last 30 days</p></header>
  <section><div class="chart h-64"><canvas id="by_type" aria-label="Clicks by ad type"></canvas></div></section>
</div>
<div class="card mt-4">
  <header><h2>Top ads</h2><p>By clicks, last 30 days</p></header>
  <section><div class="table-container"><table class="table">
    <thead><tr><th>Ad</th><th>Campaign</th><th>Impressions</th><th>Clicks</th><th>Conversions</th><th>Spend</th></tr></thead>
    <tbody>
    {% for row in top_ads %}
      <tr><td class="break-words">{{ row.ad }}</td><td class="break-words">{{ row.campaign }}</td>
        <td class="tabular-nums">{{ "%.0f"|format(row.impressions) }}</td>
        <td class="tabular-nums">{{ "%.0f"|format(row.clicks) }}</td>
        <td class="tabular-nums">{{ "%.1f"|format(row.conversions) }}</td>
        <td class="tabular-nums">${{ "%.2f"|format(row.spend) }}</td></tr>
    {% endfor %}
    </tbody>
  </table></div></section>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
  window.basecoat.chart("#by_type", {
    type: "bar", labelKey: "ad_type",
    data: {{ by_type | tojson }},
    series: { clicks: { label: "Clicks", color: "var(--chart-1)" } }
  });
});
</script>
""",
)
```

`data_apps_refresh(data_app_id=...)` runs the GAQL again and re-renders
the app; the window stays the last 30 days.

## Variants

- Filter to `ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'` for
  search-only RSA reviews.
- Add `ad_group_ad.ad_strength` to see Google's own quality signal.
- Group by `segments.device` for device-level creative performance.
