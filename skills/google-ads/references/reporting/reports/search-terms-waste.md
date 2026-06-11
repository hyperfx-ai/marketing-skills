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

Use the GAQL below through `google_ads_execute_gaql` for both ad-hoc
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
result = hyper_data_build_dashboard(
    name="Search Terms Waste",
    tool_data_sources={
        "raw": {
            "tool_name": "google_ads_execute_gaql",
            "tool_args": {
                "customer_id": "123-456-7890",
                "query": (
                    "SELECT search_term_view.search_term, search_term_view.status, "
                    "campaign.name, ad_group.name, "
                    "metrics.cost_micros, metrics.clicks, "
                    "metrics.conversions, metrics.conversions_value "
                    "FROM search_term_view "
                    "WHERE segments.date DURING LAST_30_DAYS"
                ),
            },
            "cache_table": "gads_search_terms",
            "mode": "replace",
        },
    },
    sql_data_sources={
        "top_waste": {
            "shape": "rows",
            "sql": (
                "SELECT search_term_view_search_term AS term, "
                "campaign_name AS campaign, "
                "SUM(metrics_cost_micros)/1e6 AS spend, "
                "SUM(metrics_clicks) AS clicks "
                "FROM gads_search_terms "
                "GROUP BY 1, 2 "
                "HAVING SUM(metrics_conversions) = 0 "
                "AND SUM(metrics_cost_micros) > 10000000 "
                "ORDER BY spend DESC LIMIT 50"
            ),
        },
    },
    prefab_python="""
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, Column, DataTable, DataTableColumn, Grid, Heading, Metric, Muted, Text

with PrefabApp(title="Search Terms Waste") as app:
    wasted_spend = sum(row.get("spend", 0) for row in top_waste)

    with Column(gap=6, css_class="p-6"):
        with Column(gap=1):
            Heading("Search Terms Waste")
            Muted("Highest-spend terms with weak or missing conversion value")

        with Grid(columns=4, gap=4):
            with Card():
                with CardContent():
                    Metric(label="Flagged Terms", value=f"{len(top_waste):,}")
            with Card():
                with CardContent():
                    Metric(label="Flagged Spend", value=f"${wasted_spend:,.0f}")

        with Card():
            with CardContent():
                Text("Waste candidates", css_class="text-sm font-medium text-muted-foreground mb-2")
                DataTable(
                    columns=[
                        DataTableColumn(key="term", header="Search Term"),
                        DataTableColumn(key="campaign", header="Campaign"),
                        DataTableColumn(key="spend", header="Spend"),
                        DataTableColumn(key="clicks", header="Clicks"),
                    ],
                    rows=top_waste,
                )
""",
    refresh={"mode": "scheduled", "cron": "0 */6 * * *"},
)
```

## Variants

- Group by theme (regex patterns over `search_term`) to surface
  thematic waste rather than per-query waste.
- Add `metrics.average_cpc` to spot expensive-per-click terms even
  when total spend is small.
