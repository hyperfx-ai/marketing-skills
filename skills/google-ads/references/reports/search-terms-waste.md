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

For an ad-hoc report, use the typed tools:

- `google_ads_search_terms_get(customer_id, date_range, campaign_ids)`:
  one row per search term, ad group and matched keyword, sorted by cost.
  `status` is Google's value: `ADDED` is already a keyword, `EXCLUDED`
  is already a negative, `NONE` is neither.
- `google_ads_search_term_proposals_get(customer_id, date_range,
  campaign_ids, min_conversions_for_keyword, min_cost_micros_for_negative)`:
  keyword and negative proposals from `NONE` terms. Each proposal sums
  one term in one ad group and carries its source rows. It changes
  nothing. Defaults: 2 conversions for a keyword; 0 conversions and
  50,000,000 micros cost for a negative.
- When `row_limit_reached` is true, narrow the dates or the campaigns.

If these tools are not found, or for a refreshable dashboard, use the
GAQL below through `google_ads_gaql_query`.

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

## Before proposing negatives

Read the negatives the account already has. Run each query through `google_ads_gaql_query`. Do this also for the negatives from `google_ads_search_term_proposals_get`: that tool does not read negative keyword lists.

```sql
SELECT shared_set.id, shared_set.name, shared_set.type, shared_criterion.keyword.text, shared_criterion.keyword.match_type
FROM shared_criterion
WHERE shared_set.type IN ('NEGATIVE_KEYWORDS', 'ACCOUNT_LEVEL_NEGATIVE_KEYWORDS')
```

```sql
SELECT campaign.name, shared_set.name
FROM campaign_shared_set
WHERE shared_set.type = 'NEGATIVE_KEYWORDS' AND campaign_shared_set.status = 'ENABLED'
```

```sql
SELECT campaign.name, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
FROM campaign_criterion
WHERE campaign_criterion.negative = TRUE AND campaign_criterion.type = 'KEYWORD'
```

- Propose a negative only for a term that no list and no campaign negative holds.
- When a list holds the term but the campaign does not use the list, propose attaching the list.
- Name the lists you read in the answer.

## How to interpret

- Highest spend with zero conversions over a meaningful window = top
  candidates for negatives.
- Off-intent terms (job seekers when you sell software, "free" when you
  sell paid, competitor names you don't want to bid on) deserve
  campaign- or account-level negatives, not ad-group-level.
- A single ad group surfacing many wasteful themes signals a structural
  problem; pair with [campaign-structure.md](campaign-structure.md).

## Building a dashboard from this report

`gaql(...)` and `PERIOD` are the shorthands in
[reporting.md](../reporting.md) Phase 4; expand them in the call.

The query reads the 2,000 costliest rows, which keeps `calc_sql` inside its
execution budget. Say so in the report when the account has more. The threshold
in `HAVING` is in account currency units, after the loader has scaled micros.

```python
artifacts_create(
    type="dashboard",
    name="Search Terms Waste",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="flagged_terms:Flagged terms:count,flagged_spend:Flagged spend:currency,flagged_clicks:Flagged clicks:count,avg_cpc:Avg. CPC:cents"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart kind="bar" source="by_campaign" x="campaign" series="spend:Flagged spend" format="currency" title="Flagged spend by campaign"></hyper-chart>
    <hyper-chart kind="bar" source="by_campaign" x="campaign" series="terms:Flagged terms" format="count" title="Flagged terms by campaign"></hyper-chart>
  </div>
  <hyper-table source="top_waste" sort="spend:desc" page-size="25" title="Waste candidates"
    hint="The costliest terms over the threshold with no conversion"
    columns="term:Search term:text,campaign:Campaign:text,spend:Spend:cents,clicks:Clicks:count"
    empty-text="No term passed the threshold without a conversion."></hyper-table>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT search_term_view.search_term, campaign.name, metrics.cost_micros, "
                "metrics.clicks, metrics.conversions "
                "FROM search_term_view "
                "WHERE segments.date DURING {{period}} "
                "AND metrics.cost_micros > 0 "
                "ORDER BY metrics.cost_micros DESC LIMIT 2000"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "term": "searchTermView.searchTerm",
                    "campaign": "campaign.name",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "clicks": {"from": "metrics.clicks", "cast": "number"},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT COUNT(*) AS flagged_terms, COALESCE(SUM(spend), 0) AS flagged_spend, "
                "COALESCE(SUM(clicks), 0) AS flagged_clicks, "
                "SUM(spend) / NULLIF(SUM(clicks), 0) AS avg_cpc "
                "FROM (SELECT term, campaign, SUM(spend) AS spend, SUM(clicks) AS clicks FROM data "
                "GROUP BY term, campaign HAVING SUM(conversions) = 0 AND SUM(spend) > 10) AS flagged"
            ),
            "columns": {"flagged_terms": "count", "flagged_spend": "currency", "flagged_clicks": "count", "avg_cpc": "cents"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "by_campaign": {
            "source": gaql(
                "SELECT search_term_view.search_term, campaign.name, metrics.cost_micros, "
                "metrics.clicks, metrics.conversions "
                "FROM search_term_view "
                "WHERE segments.date DURING {{period}} "
                "AND metrics.cost_micros > 0 "
                "ORDER BY metrics.cost_micros DESC LIMIT 2000"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "term": "searchTermView.searchTerm",
                    "campaign": "campaign.name",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "clicks": {"from": "metrics.clicks", "cast": "number"},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT campaign, COUNT(*) AS terms, SUM(spend) AS spend "
                "FROM (SELECT term, campaign, SUM(spend) AS spend FROM data "
                "GROUP BY term, campaign HAVING SUM(conversions) = 0 AND SUM(spend) > 10) AS flagged "
                "GROUP BY campaign ORDER BY spend DESC LIMIT 10"
            ),
            "columns": {"campaign": "text", "terms": "count", "spend": "currency"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "top_waste": {
            "source": gaql(
                "SELECT search_term_view.search_term, campaign.name, metrics.cost_micros, "
                "metrics.clicks, metrics.conversions "
                "FROM search_term_view "
                "WHERE segments.date DURING {{period}} "
                "AND metrics.cost_micros > 0 "
                "ORDER BY metrics.cost_micros DESC LIMIT 2000"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "term": "searchTermView.searchTerm",
                    "campaign": "campaign.name",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                    "clicks": {"from": "metrics.clicks", "cast": "number"},
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT term, campaign, SUM(spend) AS spend, SUM(clicks) AS clicks FROM data "
                "GROUP BY term, campaign HAVING SUM(conversions) = 0 AND SUM(spend) > 10 "
                "ORDER BY spend DESC LIMIT 50"
            ),
            "columns": {"term": "text", "campaign": "text", "spend": "cents", "clicks": "count"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
    },
)
```

## Variants

- Group by theme (regex patterns over `search_term`) to surface
  thematic waste rather than per-query waste.
- Add `metrics.average_cpc` to spot expensive-per-click terms even
  when total spend is small.
