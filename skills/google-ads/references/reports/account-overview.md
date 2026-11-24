# Account Overview

Full-account health snapshot. Combines spend, conversions, conversion
rate, and cost per conversion in a single dashboard so the agent can
orient before drilling into a specific issue.

## When to use

- "How is the account doing?"
- First report to run for a new client engagement.
- Periodic health check.
- When routing to a more focused report (tracking / budget / search
  terms / structure) requires an aggregate baseline.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).

Use the GAQL below through `google_ads_gaql_query` for both ad-hoc
reporting and refreshable dashboards.

## GAQL

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.cost_micros,
  metrics.clicks,
  metrics.impressions,
  metrics.conversions,
  metrics.conversions_value
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

## How to interpret

- Treat any campaign with significant spend and zero conversions over a
  meaningful window as a tracking-or-budget issue, not a "campaign
  performance" issue.
- ROAS and CPA are downstream signals — surface them only when
  conversion tracking is verified (see
  [conversion-tracking.md](conversion-tracking.md)).
- Aggregate spend without segmenting by date hides pacing problems;
  always include a daily series.

## Building a dashboard from this report

`gaql(...)` and `PERIOD` are the shorthands in
[reporting.md](../reporting.md) Phase 4; expand them in the call.

The account view fits the `ads_overview` blueprint. Read it with
`artifacts_templates_get("ads_overview")`, then create it with
`template_name="ads_overview"` and these datasets mapped to its dataset IDs and
column names, or send this body:

```python
artifacts_create(
    type="dashboard",
    name="Account Overview",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="spend:Spend:currency,impressions:Impressions:count,clicks:Clicks:count,conversions:Conversions:decimal,roas:ROAS:roas,cost_per_conv:Cost / conv.:cents,conv_rate:Conv. rate:percent,avg_cpc:Avg. CPC:cents"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart span="full" kind="line" source="daily" x="day" series="spend:Spend" format="currency" range-param="period" title="Spend"></hyper-chart>
    <hyper-chart kind="bar" source="top_campaigns" x="campaign" series="spend:Spend" format="currency" title="Top campaigns by spend"></hyper-chart>
    <hyper-chart kind="bar" source="top_ads" x="ad" series="spend:Spend" format="currency" title="Top ads by spend"></hyper-chart>
    <hyper-chart span="full" kind="line" source="daily" x="day" series="clicks:Clicks" format="count" title="Clicks"></hyper-chart>
  </div>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT campaign.id, metrics.cost_micros, metrics.clicks, "
                "metrics.impressions, metrics.conversions, metrics.conversions_value "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "clicks": {"from": "metrics.clicks", "cast": "number"},
                    "impressions": {"from": "metrics.impressions", "cast": "number"},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                    "value": {"from": "metrics.conversionsValue", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT SUM(spend) AS spend, SUM(impressions) AS impressions, "
                "SUM(clicks) AS clicks, SUM(conversions) AS conversions, "
                "SUM(value) / NULLIF(SUM(spend), 0) AS roas, "
                "SUM(spend) / NULLIF(SUM(conversions), 0) AS cost_per_conv, "
                "100.0 * SUM(conversions) / NULLIF(SUM(clicks), 0) AS conv_rate, "
                "SUM(spend) / NULLIF(SUM(clicks), 0) AS avg_cpc FROM data"
            ),
            "columns": {
                "spend": "currency", "impressions": "count", "clicks": "count",
                "conversions": "decimal", "roas": "roas", "cost_per_conv": "cents",
                "conv_rate": "percent", "avg_cpc": "cents",
            },
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "daily": {
            "source": gaql(
                "SELECT segments.date, campaign.id, metrics.cost_micros, metrics.clicks "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "day": "segments.date",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "clicks": {"from": "metrics.clicks", "cast": "number"},
                },
            },
            "calc_sql": "SELECT day, SUM(spend) AS spend, SUM(clicks) AS clicks FROM data GROUP BY day ORDER BY day",
            "columns": {"day": "date", "spend": "currency", "clicks": "count"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "top_campaigns": {
            "source": gaql(
                "SELECT campaign.id, campaign.name, metrics.cost_micros FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED' "
                "ORDER BY metrics.cost_micros DESC LIMIT 10"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "campaign": "campaign.name",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                },
            },
            "columns": {"campaign": "text", "spend": "currency"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "top_ads": {
            "source": gaql(
                "SELECT ad_group_ad.ad.id, ad_group.name, metrics.cost_micros "
                "FROM ad_group_ad "
                "WHERE segments.date DURING {{period}} "
                "AND ad_group_ad.status != 'REMOVED' "
                "ORDER BY metrics.cost_micros DESC LIMIT 10"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "ad_group": "adGroup.name",
                    "ad_id": {"from": "adGroupAd.ad.id", "cast": "string"},
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                },
            },
            "calc_sql": "SELECT ad_group || ' · ad ' || ad_id AS ad, spend FROM data ORDER BY spend DESC",
            "columns": {"ad": "text", "spend": "currency"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
    },
)
```

## Variants

- Add `metrics.average_cpc`, `metrics.ctr`, `metrics.search_impression_share`
  to the GAQL when the user wants efficiency context.
- Group by `campaign.advertising_channel_type` to split Search / PMax /
  Display in the same dashboard.
