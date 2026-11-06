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

```python
result = data_apps_build(
    name="Budget Distribution",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_gaql_query",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT campaign.id, campaign.name, campaign.status, "
                    "campaign_budget.amount_micros, "
                    "campaign_budget.delivery_method, "
                    "metrics.cost_micros, metrics.conversions, "
                    "metrics.conversions_value, metrics.clicks "
                    "FROM campaign "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND campaign.status != 'REMOVED'"
                ),
            },
            "cache_table": "gads_budget_1234567890",
            "mode": "replace",
            "rows_path": "results",
        },
    },
    sql_data_sources={
        "by_campaign": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, "
                "ROUND(SUM(metrics_cost_micros::numeric) / 1e6, 2) AS spend, "
                "SUM(metrics_conversions::numeric) AS conversions "
                "FROM gads_budget_1234567890 GROUP BY 1 ORDER BY spend DESC LIMIT 25"
            ),
        },
        "zero_conv_high_spend": {
            "shape": "rows",
            "sql": (
                "SELECT campaign_name AS campaign, "
                "SUM(metrics_cost_micros::numeric) / 1e6 AS spend "
                "FROM gads_budget_1234567890 GROUP BY 1 "
                "HAVING SUM(metrics_conversions::numeric) = 0 "
                "AND SUM(metrics_cost_micros::numeric) > 50000000 "
                "ORDER BY spend DESC"
            ),
        },
        "total_spend": {
            "shape": "scalar",
            "sql": (
                "SELECT '$' || to_char(COALESCE(SUM(metrics_cost_micros::numeric), 0) / 1e6, 'FM999,999,990.00') "
                "FROM gads_budget_1234567890"
            ),
        },
    },
    template_html="""
<div class="grid gap-3" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));">
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">Spend</p>
    <p class="text-2xl font-semibold tabular-nums">{{ total_spend }}</p>
  </section></div>
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">Zero-conversion campaigns</p>
    <p class="text-2xl font-semibold tabular-nums">{{ zero_conv_high_spend | length }}</p>
  </section></div>
</div>
<div class="card mt-4">
  <header><h2>Spend by campaign</h2><p>Last 30 days</p></header>
  <section><div class="chart h-64"><canvas id="by_campaign" aria-label="Spend by campaign"></canvas></div></section>
</div>
<div class="card mt-4">
  <header><h2>High spend without conversions</h2><p>Over $50 and no conversion</p></header>
  <section><div class="table-container"><table class="table">
    <thead><tr><th>Campaign</th><th>Spend</th></tr></thead>
    <tbody>
    {% for row in zero_conv_high_spend %}
      <tr><td class="break-words">{{ row.campaign }}</td><td class="tabular-nums">${{ "%.2f"|format(row.spend) }}</td></tr>
    {% endfor %}
    </tbody>
  </table></div></section>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
  window.basecoat.chart("#by_campaign", {
    type: "bar", labelKey: "campaign", options: { indexAxis: "y" },
    data: {{ by_campaign | tojson }},
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

- Add `metrics.search_impression_share` to flag campaigns that are
  budget-constrained vs. competitor-pressured.
- Group by `campaign.advertising_channel_type` to compare Search vs
  PMax vs Display efficiency separately.
