# Campaign Structure

Campaign and ad-group structure view for understanding where spend,
clicks, and conversions sit across account organization.

## When to use

- "Show me campaign and ad group structure."
- "Which ad groups are getting spend?"
- "How are campaigns and ad groups performing together?"
- Before launching a parallel campaign, inspect whether the existing
  account already covers the same theme.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).

Use the GAQL below through `google_ads_gaql_query` for both ad-hoc
reporting and refreshable dashboards.

## GAQL

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.advertising_channel_type,
  ad_group.id,
  ad_group.name,
  metrics.cost_micros,
  metrics.conversions,
  metrics.clicks,
  metrics.impressions
FROM ad_group
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
  AND ad_group.status != 'REMOVED'
```

## How to interpret

- One campaign carrying many ad groups with very different conversion
  rates → segmentation candidates.
- Brand-matching ad groups inside the same campaign as generic
  non-brand ad groups → recommend a brand split (huge bidding leverage).
- Ad groups with very low impression share inside high-spend campaigns
  → likely competing internally with another ad group; consolidation
  candidates.

## Building a dashboard from this report

```python
result = data_apps_build(
    name="Campaign Structure",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_gaql_query",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT campaign.id, campaign.name, "
                    "campaign.advertising_channel_type, "
                    "ad_group.id, ad_group.name, "
                    "metrics.cost_micros, metrics.conversions, "
                    "metrics.clicks, metrics.impressions "
                    "FROM ad_group "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND campaign.status != 'REMOVED' "
                    "AND ad_group.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_structure_1234567890",
            "mode": "replace",
            "rows_path": "results",
        },
    },
    sql_data_sources={
        "ad_groups_per_campaign": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, "
                "COUNT(DISTINCT ad_group_id) AS ad_groups, "
                "ROUND(SUM(metrics_cost_micros::numeric) / 1e6, 2) AS spend "
                "FROM gads_structure_1234567890 GROUP BY 1 ORDER BY spend DESC LIMIT 25"
            ),
        },
        "ad_group_efficiency": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, ad_group_name AS ad_group, "
                "SUM(metrics_cost_micros::numeric) / 1e6 AS spend, "
                "SUM(metrics_conversions::numeric) AS conversions "
                "FROM gads_structure_1234567890 GROUP BY 1, 2 "
                "ORDER BY spend DESC LIMIT 50"
            ),
        },
        "ad_group_total": {
            "shape": "scalar",
            "sql": "SELECT COUNT(DISTINCT ad_group_id) FROM gads_structure_1234567890",
        },
        "campaign_total": {
            "shape": "scalar",
            "sql": "SELECT COUNT(DISTINCT campaign_id) FROM gads_structure_1234567890",
        },
    },
    template_html="""
<div class="grid gap-3" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));">
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">Campaigns with activity</p>
    <p class="text-2xl font-semibold tabular-nums">{{ campaign_total }}</p>
  </section></div>
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">Ad groups with activity</p>
    <p class="text-2xl font-semibold tabular-nums">{{ ad_group_total }}</p>
  </section></div>
</div>
<div class="card mt-4">
  <header><h2>Spend by campaign</h2><p>Last 30 days</p></header>
  <section><div class="chart h-64"><canvas id="structure" aria-label="Spend by campaign"></canvas></div></section>
</div>
<div class="card mt-4">
  <header><h2>Campaigns</h2><p>Ad groups with activity and spend, last 30 days</p></header>
  <section><div class="table-container"><table class="table">
    <thead><tr><th>Campaign</th><th>Ad groups</th><th>Spend</th></tr></thead>
    <tbody>
    {% for row in ad_groups_per_campaign %}
      <tr><td class="break-words">{{ row.campaign }}</td>
        <td class="tabular-nums">{{ row.ad_groups }}</td>
        <td class="tabular-nums">${{ "%.2f"|format(row.spend) }}</td></tr>
    {% endfor %}
    </tbody>
  </table></div></section>
</div>
<div class="card mt-4">
  <header><h2>Ad group efficiency</h2><p>By spend, last 30 days</p></header>
  <section><div class="table-container"><table class="table">
    <thead><tr><th>Campaign</th><th>Ad group</th><th>Spend</th><th>Conversions</th></tr></thead>
    <tbody>
    {% for row in ad_group_efficiency %}
      <tr><td class="break-words">{{ row.campaign }}</td><td class="break-words">{{ row.ad_group }}</td>
        <td class="tabular-nums">${{ "%.2f"|format(row.spend) }}</td>
        <td class="tabular-nums">{{ "%.1f"|format(row.conversions) }}</td></tr>
    {% endfor %}
    </tbody>
  </table></div></section>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
  window.basecoat.chart("#structure", {
    type: "bar", labelKey: "campaign", options: { indexAxis: "y" },
    data: {{ ad_groups_per_campaign | tojson }},
    series: { spend: { label: "Spend", color: "var(--chart-1)" } }
  });
});
</script>
""",
)
```

`data_apps_refresh(data_app_id=...)` runs the GAQL again and re-renders
the app; the window stays the last 30 days.

## Variants

- Filter to `campaign.advertising_channel_type = 'SEARCH'` for
  search-only restructure analysis.
- Add `ad_group.type` to distinguish standard vs PMax asset groups.
