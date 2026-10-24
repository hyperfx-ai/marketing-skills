# Search Terms Waste

Search terms report showing query-level cost, clicks, conversions, and
conversion value.

## When to use

- "What search terms are getting spend?"
- "Which search terms converted?"
- "Show search terms by campaign/ad group."
- Before discussing negatives, inspect the actual search-term evidence.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).
- Optional: `campaign_ids` to scope.
- Threshold: cost-without-conversion floor (default: $10 / 10_000_000
  micros over the window).

Use the GAQL below through `google_ads_gaql_query` for both ad-hoc
reporting and refreshable dashboards.

## GAQL

```sql
SELECT
  search_term_view.search_term,
  search_term_view.status,
  campaign.name,
  ad_group.name,
  metrics.cost_micros,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value
FROM search_term_view
WHERE segments.date BETWEEN '{start}' AND '{end}'
```

## How to interpret

- Highest spend with zero conversions over a meaningful window = top
  candidates for negatives.
- Off-intent terms (job seekers when you sell software, "free" when you
  sell paid, competitor names you don't want to bid on) deserve
  campaign- or account-level negatives, not ad-group-level.
- A single ad group surfacing many wasteful themes signals a structural
  problem; pair with [campaign-structure.md](campaign-structure.md).

## Building a dashboard from this report

```python
result = data_apps_build(
    name="Search Terms Waste",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_gaql_query",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT search_term_view.search_term, search_term_view.status, "
                    "campaign.name, ad_group.name, "
                    "metrics.cost_micros, metrics.clicks, "
                    "metrics.conversions, metrics.conversions_value "
                    "FROM search_term_view "
                    "WHERE segments.date DURING LAST_30_DAYS "
                    "AND metrics.cost_micros > 0 "
                    "ORDER BY metrics.cost_micros DESC LIMIT 10000"
                ),
            },
            "cache_table": "gads_search_terms_1234567890",
            "mode": "replace",
            "rows_path": "results",
        },
    },
    sql_data_sources={
        "top_waste": {
            "shape": "rows",
            "sql": (
                "SELECT search_term_view_search_term AS term, "
                "campaign_name AS campaign, "
                "SUM(metrics_cost_micros::numeric) / 1e6 AS spend, "
                "SUM(metrics_clicks::numeric) AS clicks, "
                "COUNT(*) OVER () AS flagged_terms, "
                "'$' || to_char(SUM(SUM(metrics_cost_micros::numeric)) OVER () / 1e6, 'FM999,999,990.00') AS flagged_spend "
                "FROM gads_search_terms_1234567890 "
                "GROUP BY 1, 2 "
                "HAVING SUM(metrics_conversions::numeric) = 0 "
                "AND SUM(metrics_cost_micros::numeric) > 10000000 "
                "ORDER BY spend DESC LIMIT 50"
            ),
        },
    },
    template_html="""
<div class="grid gap-3" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));">
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">Flagged terms</p>
    <p class="text-2xl font-semibold tabular-nums">{{ top_waste[0].flagged_terms if top_waste else 0 }}</p>
  </section></div>
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">Flagged spend</p>
    <p class="text-2xl font-semibold tabular-nums">{{ top_waste[0].flagged_spend if top_waste else "$0.00" }}</p>
  </section></div>
</div>
<div class="card mt-4">
  <header><h2>Waste candidates</h2><p>The 50 costliest terms with over $10 and no conversion, last 30 days</p></header>
  <section><div class="table-container"><table class="table">
    <thead><tr><th>Search term</th><th>Campaign</th><th>Spend</th><th>Clicks</th></tr></thead>
    <tbody>
    {% for row in top_waste %}
      <tr><td class="break-words">{{ row.term }}</td><td class="break-words">{{ row.campaign }}</td>
        <td class="tabular-nums">${{ "%.2f"|format(row.spend) }}</td>
        <td class="tabular-nums">{{ "%.0f"|format(row.clicks) }}</td></tr>
    {% endfor %}
    </tbody>
  </table></div></section>
</div>
""",
)
```

`data_apps_refresh(data_app_id=...)` runs the GAQL again and re-renders
the app; the window stays the last 30 days.

## Variants

- Group by theme (regex patterns over `search_term`) to surface
  thematic waste rather than per-query waste.
- Add `metrics.average_cpc` to spot expensive-per-click terms even
  when total spend is small.
