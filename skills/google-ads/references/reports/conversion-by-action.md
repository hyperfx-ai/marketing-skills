# Conversions by Action

Per–conversion-action breakdown across campaigns and dates. Use this
when the user wants to see how each individual conversion event (like
"sign up", "purchase", "qualified lead") performs over time and across
campaigns — not just the aggregate `conversions` metric.

## When to use

- "Show me conversions broken down by action / by event."
- "Which campaigns drive each stage of our funnel?" (paired with
  [conversion-funnel.md](conversion-funnel.md))
- Diagnosing a single noisy conversion action (e.g. duplicate primary).
- Building a stacked area / bar chart of conversion mix over time.

## Inputs

- `customer_id` (required, format `XXX-XXX-XXXX`).
- `date_range` (default: `LAST_30_DAYS`; or explicit `start_date` / `end_date`).
- Optional: `campaign_ids` to scope to a subset.

## GAQL

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  segments.conversion_action,
  segments.conversion_action_name,
  segments.conversion_action_category,
  metrics.conversions,
  metrics.all_conversions,
  metrics.conversions_value
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

**Critical caveat — common failure mode:**

Do **not** select `conversion_action.id` or `conversion_action.name`
against `FROM campaign`. That triggers
`PROHIBITED_RESOURCE_TYPE_IN_SELECT_CLAUSE`. Always use the
`segments.conversion_action*` fields instead. The metric name is
`metrics.conversions` (already segmented by `segments.conversion_action`),
**not** `metrics.conversions_by_conversion_action` (which does not
exist).

Do **not** select `metrics.cost_micros` in this query. Google Ads rejects
`metrics.cost_micros` with `segments.conversion_action*` using
`PROHIBITED_SEGMENT_WITH_METRIC_IN_SELECT_OR_WHERE_CLAUSE`. If cost is
needed, run a second campaign/date query and join downstream:

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  metrics.cost_micros,
  metrics.clicks,
  metrics.impressions
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

Join conversion rows to cost rows on `(segments.date, campaign.id)`. For
ad-hoc analysis, an in-memory pandas/dataframe merge in the sandbox is enough.

If the user wants to enumerate conversion actions independently of
campaigns, query the `conversion_action` resource directly — see
[conversion-tracking.md](conversion-tracking.md).

## How to interpret

- Each row is `(date, campaign, conversion_action)`. A campaign that
  fires three actions yields three rows per day.
- `metrics.conversions` is the segmented count for that action; sum
  across actions in a campaign to recover the campaign-level
  `metrics.conversions`.
- `segments.conversion_action_category` (e.g. `PURCHASE`, `SIGNUP`,
  `LEAD`) lets you group ad-hoc events into business categories.
- Joined cost is campaign/date context, not action-attributed spend. Do not
  sum joined cost across conversion actions unless you intentionally allocate
  campaign/date spend across actions first.

## Building a dashboard from this report

`gaql(...)` and `PERIOD` are the shorthands in
[reporting.md](../reporting.md) Phase 4; expand them in the call.

The per-action query and the cost query are separate datasets. Google Ads
rejects them as one query, and `calc_sql` reads one dataset, so the cost stays
in its own KPI row as campaign context.

```python
artifacts_create(
    type="dashboard",
    name="Conversions by Action",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="conversions:Conversions:decimal,all_conversions:All conversions:decimal,value:Conversion value:currency,actions:Actions with conversions:count"></hyper-kpis>
  <hyper-kpis source="cost_context"
    values="spend:Cost:currency,impressions:Impressions:count,clicks:Clicks:count,avg_cpc:Avg. CPC:cents"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart span="full" kind="line" source="daily" x="day" series="conversions:Conversions" format="decimal" range-param="period" title="Conversions, all actions"></hyper-chart>
    <hyper-chart kind="bar" source="by_action" x="action" series="conversions:Conversions" format="decimal" title="Conversions by action"></hyper-chart>
    <hyper-chart kind="donut" source="by_category" x="category" series="conversions:Conversions" format="decimal" title="Conversions by category"></hyper-chart>
  </div>
  <hyper-table source="by_action" sort="conversions:desc" title="Action detail"
    columns="action:Action:text,conversions:Conversions:decimal,value:Value:currency"></hyper-table>
  <hyper-note>Cost is campaign context for the period. It is not attributed to a conversion action.</hyper-note>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT campaign.id, segments.conversion_action_name, metrics.conversions, "
                "metrics.all_conversions, metrics.conversions_value "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "action": "segments.conversionActionName",
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                    "all_conversions": {"from": "metrics.allConversions", "cast": "number"},
                    "value": {"from": "metrics.conversionsValue", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT SUM(conversions) AS conversions, SUM(all_conversions) AS all_conversions, "
                "SUM(value) AS value, "
                "COUNT(DISTINCT CASE WHEN conversions > 0 THEN action END) AS actions FROM data"
            ),
            "columns": {"conversions": "decimal", "all_conversions": "decimal", "value": "currency", "actions": "count"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "cost_context": {
            "source": gaql(
                "SELECT campaign.id, metrics.cost_micros, metrics.clicks, metrics.impressions "
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
                },
            },
            "calc_sql": (
                "SELECT SUM(spend) AS spend, SUM(clicks) AS clicks, SUM(impressions) AS impressions, "
                "SUM(spend) / NULLIF(SUM(clicks), 0) AS avg_cpc FROM data"
            ),
            "columns": {"spend": "currency", "clicks": "count", "impressions": "count", "avg_cpc": "cents"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "daily": {
            "source": gaql(
                "SELECT segments.date, campaign.id, segments.conversion_action_name, metrics.conversions "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "day": "segments.date",
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": "SELECT day, SUM(conversions) AS conversions FROM data GROUP BY day ORDER BY day",
            "columns": {"day": "date", "conversions": "decimal"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "by_action": {
            "source": gaql(
                "SELECT campaign.id, segments.conversion_action_name, metrics.conversions, "
                "metrics.conversions_value FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "action": "segments.conversionActionName",
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                    "value": {"from": "metrics.conversionsValue", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT action, SUM(conversions) AS conversions, SUM(value) AS value "
                "FROM data GROUP BY action ORDER BY conversions DESC"
            ),
            "columns": {"action": "text", "conversions": "decimal", "value": "currency"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "by_category": {
            "source": gaql(
                "SELECT campaign.id, segments.conversion_action_category, metrics.conversions "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "category": "segments.conversionActionCategory",
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": "SELECT category, SUM(conversions) AS conversions FROM data GROUP BY category ORDER BY conversions DESC",
            "columns": {"category": "text", "conversions": "decimal"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
    },
)
```

## Variants

- **Per ad group**: change `FROM campaign` to `FROM ad_group` and add
  `ad_group.id`, `ad_group.name`. Useful when one ad group fires the
  conversion but the campaign rolls up many.
- **Per ad**: `FROM ad_group_ad` plus `ad_group_ad.ad.id`,
  `ad_group_ad.ad.name`. Heavier but useful for ad-level diagnosis.
- **Filtered to one action**: add
  `AND segments.conversion_action = 'customers/.../conversionActions/12345'`
  to focus on a single event.
