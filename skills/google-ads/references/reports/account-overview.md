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

The account view fits the library template `ads_overview`: KPI rows, a
daily spend and clicks trend, top campaigns and top ads. Each SQL source
is named after the template variable it fills.

Google returns the int64 metrics (`cost_micros`, `clicks`, `impressions`)
as strings, so every metric is cast with `::numeric` in SQL.

```python
result = data_apps_build(
    name="Account Overview",
    template_name="ads_overview",
    template_context={
        "title": "Account Overview",
        "subtitle": "Last 30 days · Google Ads",
    },
    tool_data_sources={
        "campaign_days": {
            "tool_name": "google_ads_gaql_query",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT segments.date, campaign.id, campaign.name, "
                    "campaign.status, metrics.cost_micros, metrics.clicks, "
                    "metrics.impressions, metrics.conversions, "
                    "metrics.conversions_value "
                    "FROM campaign "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_account_overview",
            "mode": "replace",
            "rows_path": "results",
        },
        "ad_totals": {
            "tool_name": "google_ads_gaql_query",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT ad_group_ad.ad.id, ad_group.name, "
                    "metrics.cost_micros "
                    "FROM ad_group_ad "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND ad_group_ad.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_account_overview_ads",
            "mode": "replace",
            "rows_path": "results",
        },
    },
    sql_data_sources={
        "kpis": {
            "shape": "rows",
            "sql": (
                "SELECT 'Spend' AS label, "
                "'$' || to_char(COALESCE(SUM(metrics_cost_micros::numeric), 0) / 1e6, 'FM999,999,990.00') AS value "
                "FROM gads_account_overview "
                "UNION ALL SELECT 'Impressions', to_char(COALESCE(SUM(metrics_impressions::numeric), 0), 'FM999,999,999') FROM gads_account_overview "
                "UNION ALL SELECT 'Clicks', to_char(COALESCE(SUM(metrics_clicks::numeric), 0), 'FM999,999,999') FROM gads_account_overview "
                "UNION ALL SELECT 'Conversions', to_char(COALESCE(SUM(metrics_conversions::numeric), 0), 'FM999,999,990.0') FROM gads_account_overview"
            ),
        },
        "secondary_kpis": {
            "shape": "rows",
            "sql": (
                "SELECT 'ROAS' AS label, "
                "COALESCE(to_char(SUM(metrics_conversions_value::numeric) / NULLIF(SUM(metrics_cost_micros::numeric) / 1e6, 0), 'FM990.00') || 'x', '–') AS value "
                "FROM gads_account_overview "
                "UNION ALL SELECT 'Cost / conv.', COALESCE('$' || to_char(SUM(metrics_cost_micros::numeric) / 1e6 / NULLIF(SUM(metrics_conversions::numeric), 0), 'FM999,990.00'), '–') FROM gads_account_overview "
                "UNION ALL SELECT 'Conv. rate', COALESCE(to_char(100 * SUM(metrics_conversions::numeric) / NULLIF(SUM(metrics_clicks::numeric), 0), 'FM990.00') || '%', '–') FROM gads_account_overview "
                "UNION ALL SELECT 'Avg. CPC', COALESCE('$' || to_char(SUM(metrics_cost_micros::numeric) / 1e6 / NULLIF(SUM(metrics_clicks::numeric), 0), 'FM990.00'), '–') FROM gads_account_overview"
            ),
        },
        "trend": {
            "shape": "scalar",
            "sql": (
                "SELECT json_build_object("
                "'labels', COALESCE(json_agg(day ORDER BY day), '[]'), "
                "'spend', COALESCE(json_agg(spend ORDER BY day), '[]'), "
                "'clicks', COALESCE(json_agg(clicks ORDER BY day), '[]')) "
                "FROM (SELECT segments_date AS day, "
                "ROUND(SUM(metrics_cost_micros::numeric) / 1e6, 2) AS spend, "
                "SUM(metrics_clicks::numeric) AS clicks "
                "FROM gads_account_overview GROUP BY 1) daily"
            ),
        },
        "top_campaigns": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS name, "
                "ROUND(SUM(metrics_cost_micros::numeric) / 1e6, 2) AS value, "
                "'$' || to_char(SUM(metrics_cost_micros::numeric) / 1e6, 'FM999,999,990.00') AS display "
                "FROM gads_account_overview GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
            ),
        },
        "top_ads": {
            "shape": "rows",
            "sql": (
                "SELECT ad_group_name || ' · ad ' || ad_group_ad_ad_id AS name, "
                "ROUND(SUM(metrics_cost_micros::numeric) / 1e6, 2) AS value, "
                "'$' || to_char(SUM(metrics_cost_micros::numeric) / 1e6, 'FM999,999,990.00') AS display "
                "FROM gads_account_overview_ads GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
            ),
        },
    },
)
```

`data_apps_refresh(data_app_id=...)` runs both GAQL queries again and
re-renders the app; the window stays the last 30 days.

## Variants

- Add `metrics.average_cpc`, `metrics.ctr`, `metrics.search_impression_share`
  to the GAQL when the user wants efficiency context.
- Group by `campaign.advertising_channel_type` to split Search / PMax /
  Display in the same dashboard.
