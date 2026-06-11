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

Use the GAQL below through `google_ads_execute_gaql` for both ad-hoc
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
result = hyper_data_build_dashboard(
    name="Campaign Structure",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_execute_gaql",
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
            "cache_table": "gads_structure",
            "mode": "replace",
        },
    },
    sql_data_sources={
        "ad_groups_per_campaign": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, "
                "COUNT(DISTINCT ad_group_id) AS ad_groups, "
                "SUM(metrics_cost_micros)/1e6 AS spend "
                "FROM gads_structure GROUP BY 1 ORDER BY spend DESC LIMIT 25"
            ),
        },
        "ad_group_efficiency": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, ad_group_name AS ad_group, "
                "SUM(metrics_cost_micros)/1e6 AS spend, "
                "SUM(metrics_conversions) AS conversions "
                "FROM gads_structure GROUP BY 1, 2 "
                "ORDER BY spend DESC LIMIT 50"
            ),
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, DataTable, DataTableColumn, Grid, Heading, Metric, Muted, Text
from prefab_ui.components.charts import BarChart, ChartSeries

with PrefabApp(title="Campaign Structure") as app:
    total_ad_groups = sum(row.get("ad_groups", 0) for row in ad_groups_per_campaign)

    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Campaign Structure")
            Muted("Ad group distribution and efficiency")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Campaigns", value=f"{len(ad_groups_per_campaign):,}")
            with Card():
                with CardContent():
                    Metric(label="Ad Groups", value=f"{total_ad_groups:,.0f}")

        with Grid(columns=[2, 1], gap=6):
            with Card():
                with CardContent():
                    Text("Ad groups and spend", css_class="text-sm font-medium text-muted-foreground mb-2")
                    BarChart(
                        data=ad_groups_per_campaign,
                        x_axis="campaign",
                        series=[
                            ChartSeries(data_key="ad_groups", label="Ad Groups"),
                            ChartSeries(data_key="spend", label="Spend"),
                        ],
                        show_legend=True,
                        height=300,
                    )
            with Card():
                with CardContent():
                    Text("Ad group efficiency", css_class="text-sm font-medium text-muted-foreground mb-2")
                    DataTable(
                        columns=[
                            DataTableColumn(key="campaign", header="Campaign"),
                            DataTableColumn(key="ad_group", header="Ad Group"),
                            DataTableColumn(key="spend", header="Spend"),
                            DataTableColumn(key="conversions", header="Conversions"),
                        ],
                        rows=ad_group_efficiency,
                    )
""",
    refresh={"mode": "manual"},
)
```

## Variants

- Filter to `campaign.advertising_channel_type = 'SEARCH'` for
  search-only restructure analysis.
- Add `ad_group.type` to distinguish standard vs PMax asset groups.
