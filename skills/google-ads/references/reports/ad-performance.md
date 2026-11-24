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

`gaql(...)` and `PERIOD` are the shorthands in
[reporting.md](../reporting.md) Phase 4; expand them in the call.

An RSA has no `ad.name`, so the table labels each ad by its ad group and id.

```python
artifacts_create(
    type="dashboard",
    name="Ad Performance",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="spend:Spend:currency,clicks:Clicks:count,conversions:Conversions:decimal,ctr:CTR:percent"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart kind="bar" source="by_type" x="ad_type" series="clicks:Clicks" format="count" title="Clicks by ad type"></hyper-chart>
    <hyper-chart kind="donut" source="by_type" x="ad_type" series="conversions:Conversions" format="decimal" title="Conversions by ad type"></hyper-chart>
  </div>
  <hyper-table source="top_ads" sort="clicks:desc" page-size="25" title="Top ads"
    columns="ad:Ad:text,campaign:Campaign:text,impressions:Impressions:count,clicks:Clicks:count,conversions:Conversions:decimal,spend:Spend:cents"></hyper-table>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT ad_group_ad.ad.id, metrics.impressions, metrics.clicks, "
                "metrics.cost_micros, metrics.conversions "
                "FROM ad_group_ad "
                "WHERE segments.date DURING {{period}} "
                "AND ad_group_ad.status != 'REMOVED' "
                "AND ad_group.status != 'REMOVED' "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "impressions": {"from": "metrics.impressions", "cast": "number"},
                    "clicks": {"from": "metrics.clicks", "cast": "number"},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                },
            },
            "calc_sql": (
                "SELECT SUM(spend) AS spend, SUM(clicks) AS clicks, SUM(conversions) AS conversions, "
                "100.0 * SUM(clicks) / NULLIF(SUM(impressions), 0) AS ctr FROM data"
            ),
            "columns": {"spend": "currency", "clicks": "count", "conversions": "decimal", "ctr": "percent"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "by_type": {
            "source": gaql(
                "SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, metrics.clicks, metrics.conversions "
                "FROM ad_group_ad "
                "WHERE segments.date DURING {{period}} "
                "AND ad_group_ad.status != 'REMOVED' "
                "AND ad_group.status != 'REMOVED' "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "ad_type": "adGroupAd.ad.type",
                    "clicks": {"from": "metrics.clicks", "cast": "number"},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT ad_type, SUM(clicks) AS clicks, SUM(conversions) AS conversions "
                "FROM data GROUP BY ad_type ORDER BY clicks DESC"
            ),
            "columns": {"ad_type": "text", "clicks": "count", "conversions": "decimal"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "top_ads": {
            "source": gaql(
                "SELECT ad_group_ad.ad.id, ad_group.name, campaign.name, "
                "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions "
                "FROM ad_group_ad "
                "WHERE segments.date DURING {{period}} "
                "AND ad_group_ad.status != 'REMOVED' "
                "AND ad_group.status != 'REMOVED' "
                "AND campaign.status != 'REMOVED' "
                "ORDER BY metrics.clicks DESC LIMIT 25"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "ad_group": "adGroup.name",
                    "ad_id": {"from": "adGroupAd.ad.id", "cast": "string"},
                    "campaign": "campaign.name",
                    "impressions": {"from": "metrics.impressions", "cast": "number"},
                    "clicks": {"from": "metrics.clicks", "cast": "number"},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                },
            },
            "calc_sql": (
                "SELECT ad_group || ' · ad ' || ad_id AS ad, campaign, impressions, clicks, "
                "conversions, spend FROM data ORDER BY clicks DESC"
            ),
            "columns": {
                "ad": "text", "campaign": "text", "impressions": "count",
                "clicks": "count", "conversions": "decimal", "spend": "cents",
            },
            "params": PERIOD,
            "max_age_minutes": 60,
        },
    },
)
```

## Variants

- Filter to `ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'` for
  search-only RSA reviews.
- Add `ad_group_ad.ad_strength` to see Google's own quality signal.
- Group by `segments.device` for device-level creative performance.
