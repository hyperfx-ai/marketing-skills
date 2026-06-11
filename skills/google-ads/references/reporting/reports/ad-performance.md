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

```python
result = hyper_data_build_dashboard(
    name="Ad Performance",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_execute_gaql",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT ad_group_ad.ad.id, ad_group_ad.ad.name, "
                    "ad_group_ad.ad.type, ad_group_ad.status, "
                    "ad_group.name, campaign.name, "
                    "metrics.impressions, metrics.clicks, metrics.cost_micros, "
                    "metrics.conversions, metrics.ctr, metrics.average_cpc "
                    "FROM ad_group_ad "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND ad_group_ad.status != 'REMOVED' "
                    "AND ad_group.status != 'REMOVED' "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_ad_performance",
            "mode": "replace",
        },
    },
    sql_data_sources={
        "top_ads": {
            "shape": "rows",
            "sql": (
                "SELECT ad_group_ad_ad_name AS ad_name, "
                "campaign_name AS campaign, "
                "ad_group_name AS ad_group, "
                "SUM(metrics_impressions) AS impressions, "
                "SUM(metrics_clicks) AS clicks, "
                "SUM(metrics_conversions) AS conversions, "
                "SUM(metrics_cost_micros)/1e6 AS spend "
                "FROM gads_ad_performance "
                "GROUP BY 1, 2, 3 ORDER BY clicks DESC LIMIT 25"
            ),
        },
        "by_type": {
            "shape": "rows",
            "sql": (
                "SELECT ad_group_ad_ad_type AS ad_type, "
                "SUM(metrics_clicks) AS clicks, "
                "SUM(metrics_conversions) AS conversions "
                "FROM gads_ad_performance GROUP BY 1 ORDER BY clicks DESC"
            ),
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, DataTable, DataTableColumn, Grid, Heading, Metric, Muted, Text
from prefab_ui.components.charts import BarChart, ChartSeries

with PrefabApp(title="Ad Performance") as app:
    total_clicks = sum(row.get("clicks", 0) for row in top_ads)
    total_conversions = sum(row.get("conversions", 0) for row in top_ads)

    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Ad Performance")
            Muted("Top ads and creative format mix")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Clicks", value=f"{total_clicks:,.0f}")
            with Card():
                with CardContent():
                    Metric(label="Conversions", value=f"{total_conversions:,.0f}")

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text("Performance by ad type", css_class="text-sm font-medium text-muted-foreground mb-2")
                    BarChart(
                        data=by_type,
                        x_axis="ad_type",
                        series=[
                            ChartSeries(data_key="clicks", label="Clicks"),
                            ChartSeries(data_key="conversions", label="Conversions"),
                        ],
                        show_legend=True,
                        height=300,
                    )
            with Card():
                with CardContent():
                    Text("Top ads", css_class="text-sm font-medium text-muted-foreground mb-2")
                    DataTable(
                        columns=[
                            DataTableColumn(key="ad_name", header="Ad"),
                            DataTableColumn(key="campaign", header="Campaign"),
                            DataTableColumn(key="ad_group", header="Ad Group"),
                            DataTableColumn(key="impressions", header="Impressions"),
                            DataTableColumn(key="clicks", header="Clicks"),
                            DataTableColumn(key="conversions", header="Conversions"),
                            DataTableColumn(key="spend", header="Spend"),
                        ],
                        rows=top_ads,
                    )
""",
    refresh={"mode": "scheduled", "cron": "0 */6 * * *"},
)
```

## Variants

- Filter to `ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'` for
  search-only RSA reviews.
- Add `ad_group_ad.ad_strength` to see Google's own quality signal.
- Group by `segments.device` for device-level creative performance.
