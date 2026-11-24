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

`gaql(...)` and `PERIOD` are the shorthands in
[reporting.md](../reporting.md) Phase 4; expand them in the call.

```python
artifacts_create(
    type="dashboard",
    name="Campaign Structure",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="campaigns:Campaigns with activity:count,ad_groups:Ad groups with activity:count,spend:Spend:currency,conversions:Conversions:decimal"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart kind="bar" source="campaigns" x="campaign" series="spend:Spend" format="currency" title="Spend by campaign"></hyper-chart>
    <hyper-chart kind="bar" source="campaigns" x="campaign" series="ad_groups:Ad groups" format="count" title="Ad groups by campaign"></hyper-chart>
  </div>
  <hyper-table source="campaigns" sort="spend:desc" title="Campaigns"
    columns="campaign:Campaign:text,ad_groups:Ad groups:count,spend:Spend:cents"></hyper-table>
  <hyper-table source="ad_group_efficiency" sort="spend:desc" page-size="20" title="Ad group efficiency"
    columns="campaign:Campaign:text,ad_group:Ad group:text,spend:Spend:cents,conversions:Conversions:decimal"></hyper-table>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT campaign.id, ad_group.id, metrics.cost_micros, metrics.conversions, "
                "metrics.impressions FROM ad_group "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED' "
                "AND ad_group.status != 'REMOVED' "
                "AND metrics.impressions > 0"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "campaign_id": {"from": "campaign.id", "cast": "string"},
                    "ad_group_id": {"from": "adGroup.id", "cast": "string"},
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT COUNT(DISTINCT campaign_id) AS campaigns, COUNT(DISTINCT ad_group_id) AS ad_groups, "
                "SUM(spend) AS spend, SUM(conversions) AS conversions FROM data"
            ),
            "columns": {"campaigns": "count", "ad_groups": "count", "spend": "currency", "conversions": "decimal"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "campaigns": {
            "source": gaql(
                "SELECT campaign.id, campaign.name, ad_group.id, metrics.cost_micros, "
                "metrics.impressions FROM ad_group "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED' "
                "AND ad_group.status != 'REMOVED' "
                "AND metrics.impressions > 0"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "campaign": "campaign.name",
                    "ad_group_id": {"from": "adGroup.id", "cast": "string"},
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                },
            },
            "calc_sql": (
                "SELECT campaign, COUNT(DISTINCT ad_group_id) AS ad_groups, SUM(spend) AS spend "
                "FROM data GROUP BY campaign ORDER BY spend DESC LIMIT 25"
            ),
            "columns": {"campaign": "text", "ad_groups": "count", "spend": "cents"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "ad_group_efficiency": {
            "source": gaql(
                "SELECT campaign.name, ad_group.id, ad_group.name, metrics.cost_micros, metrics.conversions "
                "FROM ad_group "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED' "
                "AND ad_group.status != 'REMOVED' "
                "ORDER BY metrics.cost_micros DESC LIMIT 50"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "campaign": "campaign.name",
                    "ad_group": "adGroup.name",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "columns": {"campaign": "text", "ad_group": "text", "spend": "cents", "conversions": "decimal"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
    },
)
```

## Variants

- Filter to `campaign.advertising_channel_type = 'SEARCH'` for
  search-only restructure analysis.
- For PMax, run a separate query `FROM asset_group` (asset_group.id, asset_group.name, campaign.name).
