# Reporting and GAQL

Report on existing Google Ads accounts using GAQL-backed data. Dashboards are an optional presentation surface, not mandatory output. Every reporting task starts here, then picks the report recipe with the closest data shape from [reports/](reports/).

## Core contract

- Use `google_ads_gaql_query` as the main Google Ads data tool.
- For Search reports, use the typed tools first: `google_ads_impression_share_get`, `google_ads_auction_insights_get`, `google_ads_search_terms_get` and `google_ads_search_term_proposals_get`. They return only Search campaigns. If one is not found, write the GAQL with `google_ads_gaql_query`.
- When `google_ads_auction_insights_get` returns `error`, Google refused auction insights to the developer token of the connection. Tell the user that. Do not report it as "no competitors".
- Written GAQL-backed reports are valid outputs. Build a dashboard only when the user asks for one or when an interactive view materially improves the answer.
- Call `google_ads_gaql_query(customer_id, query)`. Its description gives the GAQL rules. Select the account whose data the report needs.
- Treat rows as evidence, not as automatic recommendations ([heuristics.md](heuristics.md)).
- Keep reporting separate from live account changes.
- Do not mention internal dashboard implementation details to the user unless they explicitly ask how the interface is built.

## Phase 1: Access and scope

1. Read the accounts as [discovery.md](discovery.md) Phase 1 says, before touching account data.
2. Confirm the customer ID if more than one account is available.
3. Confirm the reporting window if the user has not given one.
4. If the user did not ask for a dashboard and the best output is unclear, ask whether they want a written report or an interactive view.

## Phase 2: Pick the report

| The user wants... | Read |
|---|---|
| Full account health snapshot | [reports/account-overview.md](reports/account-overview.md) |
| Why aren't conversions tracking right | [reports/conversion-tracking.md](reports/conversion-tracking.md) |
| Conversions broken down by action / per stage | [reports/conversion-by-action.md](reports/conversion-by-action.md) |
| Lead-gen / B2B multi-stage funnel | [reports/conversion-funnel.md](reports/conversion-funnel.md) |
| Where is spend going | [reports/budget-distribution.md](reports/budget-distribution.md) |
| Wasteful search terms, or new keywords and negatives | [reports/search-terms-waste.md](reports/search-terms-waste.md) |
| Search impression share, or share lost to budget or rank | `google_ads_impression_share_get` (`level` is `campaign` or `keyword`) |
| Which competitors show in the same Search auctions | `google_ads_auction_insights_get` |
| Should we restructure | [reports/campaign-structure.md](reports/campaign-structure.md) |
| Campaign performance over time | [reports/campaign-performance.md](reports/campaign-performance.md) |
| Ad-level performance | [reports/ad-performance.md](reports/ad-performance.md) |

When the user asks for a funnel dashboard, use the conversion funnel recipe.

## Phase 3: Query with GAQL

Use GAQL fields that are selectable with the report resource. For campaign-level conversion action reporting, use campaign metrics segmented by `segments.conversion_action` and `segments.conversion_action_name`.

Do not select `conversion_action.id` or `conversion_action.name` from `FROM campaign`; Google rejects that shape. Query the `conversion_action` resource separately only when you need the inventory of configured conversion actions.

### GAQL Resource Compatibility

**Critical:** Not all Google Ads resources can be joined in a single query.

**search_term_view** — use `segments.keyword.info.*` for keyword text and match type — **never** `ad_group_criterion.*`:

```sql
SELECT
    search_term_view.search_term,
    customer.descriptive_name,
    segments.keyword.info.text,
    segments.keyword.info.match_type,
    campaign.name,
    ad_group.name,
    metrics.clicks,
    metrics.impressions,
    metrics.conversions,
    metrics.cost_micros
FROM search_term_view
WHERE segments.date DURING LAST_7_DAYS
ORDER BY metrics.impressions DESC
```

`ad_group_criterion` is **incompatible** with `search_term_view` as the FROM resource. Selecting `ad_group_criterion.*` fields will always fail with `PROHIBITED_RESOURCE_TYPE_IN_SELECT_CLAUSE`.

**keyword_view** — for keyword performance (Quality Score, bid estimates):
```sql
SELECT
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    metrics.clicks,
    metrics.impressions,
    metrics.historical_quality_score
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
```

## Phase 4: Optional dashboard

Skip this phase for plain written reports. When the user asks for a dashboard, or an interactive view is clearly the best presentation, use the matching report's dashboard section as the implementation recipe.

A dashboard is an Artifact: body HTML made of `<hyper-*>` blocks plus declarative `datasets` that the server runs read-only. The HTML holds no numbers.

1. Run the report's GAQL once with `google_ads_gaql_query`. When it returns no rows, tell the user and create nothing: `calc_sql` fails on an empty result.
2. Call `artifacts_templates_list`, and `artifacts_templates_get` for the blueprint that fits: `ads_overview` for an account view, `table_report` for rows, `tabbed_report` for several sections, `creative_leaderboard` for ranked creatives, else `analytics_overview` or `sales_pipeline`. Use the report recipe's own body when it fits better.
3. Call `artifacts_create` with the body (or `template_name`) and the `datasets` together. Invalid HTML or specs are refused and nothing is saved; fix every returned issue. Never create a scratch or test dashboard.
4. Call `artifacts_display`. Change it later with `artifacts_update`, and re-run the data with `artifacts_refresh`.

### Dataset rules

- Source: `{"kind": "tool", "tool": "google_ads_gaql_query", "args": {"customer_id": ..., "query": ...}}`. Each viewer runs it with their own Google Ads connection. Never put credentials in a dataset or in HTML.
- Loader: `"rows_path": "results"`, then `map`. Rows are nested and camelCase: `metrics.cost_micros` in GAQL is read as `metrics.costMicros`, `ad_group_ad.ad.id` as `adGroupAd.ad.id`.
- Google returns the int64 metrics (`costMicros`, `clicks`, `impressions`) as strings. Cast every metric to `number`, and scale micros once with `"scale": 0.000001`.
- Aggregate in GAQL first: leave out `segments.date` for totals, and use `ORDER BY ... LIMIT` for top lists. Use `calc_sql` (one read-only SQLite SELECT over the table `data`) for ratios and grouping. It reads one dataset, has a small execution budget and takes no parameters.
- Guard ratios with `NULLIF(x, 0)`. A missing value shows as a dash; never turn it into zero.
- Always declare `columns`. Only those columns leave the server, so a public snapshot carries no campaign ID or other raw field you did not choose.
- Declare `params` with `allowed` values and a `default`, and put `{{period}}` in the GAQL. `DURING` takes only Google's preset names. Declare the parameter on every dataset the filter should change.
- `max_age_minutes` caches the rows per viewer. Without it every view calls the Google Ads API.

The recipes use two shorthands. Expand them in the call:

```python
def gaql(query):
    return {
        "kind": "tool",
        "tool": "google_ads_gaql_query",
        "args": {"customer_id": "123-456-7890", "query": query},
    }

PERIOD = {
    "period": {
        "kind": "single",
        "label": "Period",
        "allowed": ["LAST_7_DAYS", "LAST_14_DAYS", "LAST_30_DAYS"],
        "options": [
            {"id": "LAST_7_DAYS", "label": "Last 7 days"},
            {"id": "LAST_14_DAYS", "label": "Last 14 days"},
            {"id": "LAST_30_DAYS", "label": "Last 30 days"},
        ],
        "default": "LAST_30_DAYS",
    }
}
```

### Layout rules

```python
artifacts_create(
    type="dashboard",
    name="Google Ads Report",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="spend:Spend:currency,clicks:Clicks:count,impressions:Impressions:count,avg_cpc:Avg. CPC:cents"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart span="full" kind="line" source="daily" x="day" series="spend:Spend" format="currency" range-param="period" title="Spend"></hyper-chart>
    <hyper-chart kind="bar" source="top_campaigns" x="campaign" series="spend:Spend" format="currency" title="Top campaigns"></hyper-chart>
    <hyper-chart kind="donut" source="by_channel" x="channel" series="spend:Spend" format="currency" title="Spend by channel type"></hyper-chart>
  </div>
  <hyper-table source="top_campaigns" sort="spend:desc" title="Campaigns" columns="campaign:Campaign:text,spend:Spend:cents"></hyper-table>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT campaign.id, metrics.cost_micros, metrics.clicks, metrics.impressions "
                "FROM campaign WHERE segments.date DURING {{period}}"
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
                "SELECT segments.date, campaign.id, metrics.cost_micros "
                "FROM campaign WHERE segments.date DURING {{period}}"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "day": "segments.date",
                    "spend": {"from": "metrics.costMicros", "cast": "number", "scale": 0.000001},
                },
            },
            "calc_sql": "SELECT day, SUM(spend) AS spend FROM data GROUP BY day ORDER BY day",
            "columns": {"day": "date", "spend": "currency"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "top_campaigns": {
            "source": gaql(
                "SELECT campaign.id, campaign.name, metrics.cost_micros FROM campaign "
                "WHERE segments.date DURING {{period}} ORDER BY metrics.cost_micros DESC LIMIT 10"
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
        "by_channel": {
            "source": gaql(
                "SELECT campaign.id, campaign.advertising_channel_type, metrics.cost_micros "
                "FROM campaign WHERE segments.date DURING {{period}}"
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
    },
)
```

- Keep this order: filter bar, KPIs (four columns by default), one two-column grid with the full-width trend first and the breakdowns under it, then tables. A single-series `kind="bar"` draws a ranked bar list.
- Body fragment only: no document wrapper, component classes such as `.card`, literal colors, external scripts or template loops. Colors come from theme tokens.
- Every block binds `source` to a dataset ID and only to declared columns. Inline figures use `<hyper-value>`, methodology uses `<hyper-note>`, a missing source uses `<hyper-empty>`.
- The host header shows data freshness once. Add no timestamps to blocks.
- For in-page tabs use `<hyper-tabs>` and copy its markup from `artifacts_templates_get("tabbed_report")`.
- The currency formats write `$`. Select `customer.currency_code` first. For an account in another currency use the `decimal` format, put the currency code in each label and say it in the dashboard description.

### Sharing

A new dashboard is private. Publish with `artifacts_share(published=True)` only when the user asks. Public visitors read Frozen Snapshots of the projected `columns`, for the declared filter values only, and can never run a query. The snapshot is frozen with the publisher's own Google Ads access, so tell the user whose data becomes public. Set `"public_exposure": "none"` on a dataset that must stay private.

## Phase 5: Response format

Use the template in [report-template.md](report-template.md). State what data was queried, which date range was used, and whether the final output is a written report, a dashboard, or a published dashboard.

## Warehouse data

When the workspace has a Google Ads warehouse connection, inspect its available tables and columns and query the selected connection through `database_query`. Existing warehouse data remains available independently of native Google Ads API calls.

Check Warehouse Data Status for that connection and report its last successful refresh. Name the customer IDs, date boundaries, currency units and metric definitions. Do not assume an hourly cache, fixed table name or fresh rows merely because the connection is healthy. Use `google_ads_gaql_query` when the requested data is not in the configured warehouse.
