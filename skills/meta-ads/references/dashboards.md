# Meta Ads: Dashboard Building

When the user asks for a Meta dashboard or performance report interface, follow the workflow below.

---

## Workflow

### 1. Look at the data first

Answer the analysis part from the synced data as "Querying warehouse tables" in [analytics.md](analytics.md) says. Today's numbers sync about every 15 minutes and the daily report tables once a day.

A dashboard reads `meta_ads_insights_get`, because a dataset source must be a read-only tool and `database_query` is not one. Run it once with the dashboard's own arguments: confirm it returns rows, and read `account_currency`. When it returns no rows, tell the user and create nothing.

### 2. Create the dashboard

A dashboard is an Artifact: body HTML made of `<hyper-*>` blocks plus declarative `datasets` that the server runs read-only. The HTML holds no numbers.

1. Call `artifacts_templates_list`, and `artifacts_templates_get` for the blueprint that fits: `ads_overview` for an account view, `creative_leaderboard` for ranked ads with media, `table_report` for rows, `tabbed_report` for several sections (else `analytics_overview` or `sales_pipeline`).
2. Call `artifacts_create` with `template_name` or your own body, and the `datasets`. Invalid HTML or specs are refused and nothing is saved; fix every returned issue. Never create a scratch or test dashboard.
3. Call `artifacts_display`. Change it later with `artifacts_update`, and re-run the data with `artifacts_refresh`.

### 3. Freshness

Each private view runs the datasets with the viewer's own Meta connection. `max_age_minutes` caches the rows per viewer; without it every view calls the Meta API. The host header shows freshness once, so add no timestamps to blocks.

---

## Dashboard pattern

```python
PERIOD = {
    "period": {
        "kind": "single",
        "label": "Period",
        "allowed": ["last_7d", "last_14d", "last_30d", "last_90d"],
        "options": [
            {"id": "last_7d", "label": "Last 7 days"},
            {"id": "last_14d", "label": "Last 14 days"},
            {"id": "last_30d", "label": "Last 30 days"},
            {"id": "last_90d", "label": "Last 90 days"},
        ],
        "default": "last_30d",
    }
}

def insights(**args):
    return {
        "kind": "tool",
        "tool": "meta_ads_insights_get",
        "args": {
            "object_id": "act_123456789",
            "object_type": "account",
            "date_preset": "{{period}}",
            "include_video_metrics": False,
            **args,
        },
    }

artifacts_create(
    type="dashboard",
    name="Meta Ads Performance",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="spend:Spend:currency,impressions:Impressions:count,clicks:Clicks:count,ctr:CTR:percent"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart span="full" kind="line" source="daily" x="day" series="spend:Spend" format="currency" range-param="period" title="Spend"></hyper-chart>
    <hyper-chart kind="bar" source="top_campaigns" x="campaign" series="spend:Spend" format="currency" title="Spend by campaign"></hyper-chart>
    <hyper-chart kind="donut" source="by_platform" x="platform" series="spend:Spend" format="currency" title="Spend by platform"></hyper-chart>
  </div>
  <hyper-table source="campaigns" sort="spend:desc" page-size="20" title="Campaigns"
    columns="campaign:Campaign:text,spend:Spend:cents,impressions:Impressions:count,clicks:Clicks:count,ctr:CTR:percent,cpc:CPC:cents"></hyper-table>
</main>
""",
    datasets={
        "summary": {
            "source": insights(),
            "loader": {
                "rows_path": "detailed_insights",
                "map": {
                    "spend": {"from": "spend", "cast": "number"},
                    "impressions": {"from": "impressions", "cast": "number"},
                    "clicks": {"from": "clicks", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT SUM(spend) AS spend, SUM(impressions) AS impressions, SUM(clicks) AS clicks, "
                "100.0 * SUM(clicks) / NULLIF(SUM(impressions), 0) AS ctr FROM data"
            ),
            "columns": {"spend": "currency", "impressions": "count", "clicks": "count", "ctr": "percent"},
            "params": PERIOD,
            "max_age_minutes": 30,
        },
        "daily": {
            "source": insights(time_increment="1"),
            "loader": {
                "rows_path": "detailed_insights",
                "map": {"day": "date_start", "spend": {"from": "spend", "cast": "number"}},
            },
            "columns": {"day": "date", "spend": "currency"},
            "params": PERIOD,
            "max_age_minutes": 30,
        },
        "top_campaigns": {
            "source": insights(level="campaign"),
            "loader": {
                "rows_path": "detailed_insights",
                "map": {"campaign": "campaign_name", "spend": {"from": "spend", "cast": "number"}},
            },
            "calc_sql": "SELECT campaign, SUM(spend) AS spend FROM data GROUP BY campaign ORDER BY spend DESC LIMIT 10",
            "columns": {"campaign": "text", "spend": "currency"},
            "params": PERIOD,
            "max_age_minutes": 30,
        },
        "by_platform": {
            "source": insights(breakdowns=["publisher_platform"]),
            "loader": {
                "rows_path": "detailed_insights",
                "map": {"platform": "publisher_platform", "spend": {"from": "spend", "cast": "number"}},
            },
            "columns": {"platform": "text", "spend": "currency"},
            "params": PERIOD,
            "max_age_minutes": 30,
        },
        "campaigns": {
            "source": insights(level="campaign"),
            "loader": {
                "rows_path": "detailed_insights",
                "map": {
                    "campaign": "campaign_name",
                    "spend": {"from": "spend", "cast": "number"},
                    "impressions": {"from": "impressions", "cast": "number"},
                    "clicks": {"from": "clicks", "cast": "number"},
                },
            },
            "calc_sql": (
                "SELECT campaign, spend, impressions, clicks, "
                "100.0 * clicks / NULLIF(impressions, 0) AS ctr, "
                "spend / NULLIF(clicks, 0) AS cpc FROM data ORDER BY spend DESC"
            ),
            "columns": {
                "campaign": "text", "spend": "cents", "impressions": "count",
                "clicks": "count", "ctr": "percent", "cpc": "cents",
            },
            "params": PERIOD,
            "max_age_minutes": 30,
        },
    },
)
```

`PERIOD` and `insights(...)` are shorthands; expand them in the call.

Data rules:

- Meta returns metrics as strings. Cast each one to `number` in the loader `map`. Amounts are already in currency units; apply no scale.
- `allowed` holds only presets from "Valid date presets" in [analytics.md](analytics.md). Declare the parameter on every dataset the filter should change.
- `calc_sql` is one read-only SQLite SELECT over the table `data`. It reads one dataset, takes no parameters, and fails on an empty result. Guard ratios with `NULLIF(x, 0)`; a missing value shows as a dash.
- Conversions are inside the `actions` list, one entry per `action_type`. Map `"actions": "actions"` and sum one type in `calc_sql`: `(SELECT SUM(a.value ->> '$.value') FROM json_each(data.actions) AS a WHERE a.value ->> '$.action_type' = '<action_type>')`. Use `->>`, not `json_extract`, which the SQL check rewrites to a form that never matches. Read the real `action_type` values from your first call, and name the one you used in a `<hyper-note>`.
- Always declare `columns`. Only those columns leave the server, so a public snapshot carries no account ID or other raw field you did not choose.
- The currency formats write `$`. For an account in another currency use the `decimal` format and put the currency code in each label. Never add amounts of two currencies.
- For ranked ads use `level="ad"` with a table. Use `<hyper-creative-grid>` only when the rows carry a cover or video: a `creatives` dataset reads the workspace's ad creatives and carries no performance metrics.

Layout rules:

- Keep the order of the example: filter bar, KPIs (four columns by default), one two-column grid with the full-width trend first, then tables. A single-series `kind="bar"` draws a ranked bar list.
- Body fragment only: no document wrapper, component classes such as `.card`, literal colors, external scripts or template loops. Colors come from theme tokens.
- Inline figures use `<hyper-value>`, methodology uses `<hyper-note>`, a missing source uses `<hyper-empty>`. For in-page tabs use `<hyper-tabs>` and copy its markup from `artifacts_templates_get("tabbed_report")`.

Never put Meta API credentials in a dataset or in HTML.

Keep custom dashboards focused on the user's question. Do not add extra panels or metrics unless asked.

Do not mention internal dashboard implementation details to the user unless they explicitly ask.

## Sharing

A new dashboard is private. Publish with `artifacts_share(published=True)` only when the user asks. Public visitors read Frozen Snapshots of the projected `columns`, for the declared filter values only, and can never run a query. The snapshot is frozen with the publisher's own Meta access, so tell the user whose data becomes public. Set `"public_exposure": "none"` on a dataset that must stay private.

---

## Ad preview handling

After campaign creation, call `meta_ads_ad_previews_get(creative_ids=["<creative_id>"])`. Section 13 of [constraints.md](constraints.md) says where the creative id comes from.

- Never paste or render iframe/html preview snippets directly in chat.
- Summarize which preview formats succeeded or failed.
- Direct the user to the UI artifact to view previews.
