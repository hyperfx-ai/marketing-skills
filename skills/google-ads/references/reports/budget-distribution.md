# Budget Distribution

Where spend is actually going across campaigns.

## When to use

- "Where is our budget going?"
- "Which campaigns are wasting money?"
- Pacing review before adjusting daily budgets.

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
  campaign.status,
  campaign_budget.amount_micros,
  campaign_budget.delivery_method,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.clicks
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

## How to interpret

- High `cost_micros` + zero `conversions` over a meaningful window =
  immediate candidate for budget reduction OR for a tracking audit.
  Don't recommend cuts until tracking is ruled out.
- Spend Herfindahl: if 80%+ of spend lives in 2–3 campaigns, the
  account is concentrated; restructure work has high leverage.
- Compare `cost_micros` to `campaign_budget.amount_micros * days` to
  detect under-pacing (budget caps / bidding ceilings).

## Building a dashboard from this report

`gaql(...)` and `PERIOD` are the shorthands in
[reporting.md](../reporting.md) Phase 4; expand them in the call.

```python
artifacts_create(
    type="dashboard",
    name="Budget Distribution",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="spend:Spend:currency,campaigns:Campaigns with spend:count,top3_share:Spend in top 3:percent,zero_conv_campaigns:High spend without conversions:count"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart kind="bar" source="by_campaign" x="campaign" series="spend:Spend" format="currency" title="Spend by campaign"></hyper-chart>
    <hyper-chart kind="donut" source="by_channel" x="channel" series="spend:Spend" format="currency" title="Spend by channel type"></hyper-chart>
  </div>
  <hyper-table source="zero_conv_high_spend" sort="spend:desc" title="High spend without conversions"
    hint="Over 50 in account currency and no conversion in the period"
    columns="campaign:Campaign:text,spend:Spend:cents" empty-text="No campaign spent over the threshold without a conversion."></hyper-table>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT campaign.id, metrics.cost_micros, metrics.conversions FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED' "
                "ORDER BY metrics.cost_micros DESC"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT SUM(spend) AS spend, "
                "SUM(CASE WHEN spend > 0 THEN 1 ELSE 0 END) AS campaigns, "
                "100.0 * SUM(CASE WHEN position <= 3 THEN spend ELSE 0 END) / NULLIF(SUM(spend), 0) AS top3_share, "
                "SUM(CASE WHEN conversions = 0 AND spend > 50 THEN 1 ELSE 0 END) AS zero_conv_campaigns "
                "FROM (SELECT spend, COALESCE(conversions, 0) AS conversions, "
                "ROW_NUMBER() OVER (ORDER BY spend DESC) AS position FROM data) AS ranked"
            ),
            "columns": {"spend": "currency", "campaigns": "count", "top3_share": "percent", "zero_conv_campaigns": "count"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "by_campaign": {
            "source": gaql(
                "SELECT campaign.id, campaign.name, metrics.cost_micros, metrics.conversions FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED' "
                "ORDER BY metrics.cost_micros DESC LIMIT 25"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "campaign": "campaign.name",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "columns": {"campaign": "text", "spend": "currency", "conversions": "decimal"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "by_channel": {
            "source": gaql(
                "SELECT campaign.id, campaign.advertising_channel_type, metrics.cost_micros FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "channel": "campaign.advertisingChannelType",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                },
            },
            "calc_sql": "SELECT channel, SUM(spend) AS spend FROM data GROUP BY channel ORDER BY spend DESC",
            "columns": {"channel": "text", "spend": "currency"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "zero_conv_high_spend": {
            "source": gaql(
                "SELECT campaign.id, campaign.name, metrics.cost_micros, metrics.conversions FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED' "
                "AND metrics.conversions = 0 "
                "AND metrics.cost_micros > 50000000 "
                "ORDER BY metrics.cost_micros DESC"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "campaign": "campaign.name",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                },
            },
            "columns": {"campaign": "text", "spend": "cents"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
    },
)
```

## Variants

- Add `metrics.search_impression_share` to flag campaigns that are
  budget-constrained vs. competitor-pressured.
- Group by `campaign.advertising_channel_type` to compare Search vs
  PMax vs Display efficiency separately.
