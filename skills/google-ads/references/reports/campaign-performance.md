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

`gaql(...)` and `PERIOD` are the shorthands in
[reporting.md](../reporting.md) Phase 4; expand them in the call.

```python
artifacts_create(
    type="dashboard",
    name="Campaign Performance",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="spend:Spend:currency,conversions:Conversions:decimal,revenue:Revenue:currency,roas:ROAS:roas"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart span="full" kind="line" source="daily" x="day" series="spend:Spend,revenue:Revenue" format="currency" range-param="period" title="Spend and revenue"></hyper-chart>
    <hyper-chart kind="column" source="daily" x="day" series="conversions:Conversions" format="decimal" title="Conversions"></hyper-chart>
    <hyper-chart kind="bar" source="by_campaign" x="campaign" series="spend:Spend" format="currency" title="Spend by campaign"></hyper-chart>
  </div>
  <hyper-table source="by_campaign" sort="spend:desc" page-size="25" title="Campaign detail"
    columns="campaign:Campaign:text,channel:Channel:text,spend:Spend:cents,conversions:Conversions:decimal,roas:ROAS:roas"></hyper-table>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT campaign.id, metrics.cost_micros, metrics.conversions, metrics.conversions_value "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                    "revenue": {"from": "metrics.conversionsValue", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT SUM(spend) AS spend, SUM(conversions) AS conversions, SUM(revenue) AS revenue, "
                "SUM(revenue) / NULLIF(SUM(spend), 0) AS roas FROM data"
            ),
            "columns": {"spend": "currency", "conversions": "decimal", "revenue": "currency", "roas": "roas"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "daily": {
            "source": gaql(
                "SELECT segments.date, campaign.id, metrics.cost_micros, metrics.conversions, metrics.conversions_value "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "day": "segments.date",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                    "revenue": {"from": "metrics.conversionsValue", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT day, SUM(spend) AS spend, SUM(conversions) AS conversions, "
                "SUM(revenue) AS revenue FROM data GROUP BY day ORDER BY day"
            ),
            "columns": {"day": "date", "spend": "currency", "conversions": "decimal", "revenue": "currency"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "by_campaign": {
            "source": gaql(
                "SELECT campaign.id, campaign.name, campaign.advertising_channel_type, "
                "metrics.cost_micros, metrics.conversions, metrics.conversions_value "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED' "
                "ORDER BY metrics.cost_micros DESC LIMIT 25"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "campaign": "campaign.name",
                    "channel": "campaign.advertisingChannelType",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                    "revenue": {"from": "metrics.conversionsValue", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT campaign, channel, spend, conversions, revenue / NULLIF(spend, 0) AS roas "
                "FROM data ORDER BY spend DESC"
            ),
            "columns": {"campaign": "text", "channel": "text", "spend": "cents", "conversions": "decimal", "roas": "roas"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
    },
)
```

## Variants

- Add `metrics.search_impression_share` and
  `metrics.search_top_impression_share` to spot lost-by-budget /
  lost-by-rank issues.
- Group by `segments.device` for desktop vs mobile vs tablet splits.
