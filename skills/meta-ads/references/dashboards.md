# Meta Ads: Dashboard Building

When the user asks for a Meta dashboard or performance report interface, follow the workflow below.

---

## Workflow: cached data first, then build

### 1. Use cached data

Read the Meta context block (`connections_info(toolkit_id="meta_ads")`) for the table name and last sync timestamp. Query the synced data with `database_query(query=..., connection="lakehouse")` in ClickHouse SQL, SELECT only, before making any live Meta API calls.

### 2. Build the dashboard

Build the dashboard using `data_apps_build` with `name`, `template_html` (or `template_name` + `template_context`), `tool_data_sources` and `sql_data_sources` (see the custom pattern below). Read the `database` skill first. Inspect the live tool schema before calling — it documents the accepted data-source shapes and UI components. Do not invent dashboard patterns.

### 3. Cache refresh policy

Today's numbers sync about every 15 minutes and the daily report tables once a day; `connections_info(toolkit_id="meta_ads")` names the last sync. For up-to-the-minute numbers, call `meta_ads_insights_get`; there is no manual sync tool.

If no cached data exists yet, use Meta API tools directly as a fallback and cache the results.

---

## Custom dashboard pattern

Use `tool_data_sources` to fetch from Meta API and save to a cache table. Use `sql_data_sources` to query the cache for UI variables. Pass `scalar` or `rows` shapes explicitly — do not embed raw SQL in UI props.

```python
data_apps_build(
    name="Meta Ads Performance",
    tool_data_sources={
        "meta_campaigns": {
            "tool_name": "meta_ads_insights_get",
            "tool_args": {
                "object_id": "act_123456789",
                "object_type": "account",
                "level": "campaign",
                "date_preset": "last_30d",
                "include_actions": True
            },
            "cache_table": "meta_campaign_perf_30d",
            "rows_path": "detailed_insights",
            "mode": "replace"
        }
    },
    sql_data_sources={
        "spend_by_campaign": {
            "sql": "SELECT campaign_name, SUM(spend) as spend FROM meta_campaign_perf_30d GROUP BY campaign_name ORDER BY spend DESC",
            "shape": "rows"
        },
        "total_spend": {
            "sql": "SELECT SUM(spend) as total FROM meta_campaign_perf_30d",
            "shape": "scalar"
        }
    },
    template_html="""
<div class="grid grid-cols-1 gap-4">
  <div class="card" data-size="sm"><section>
    <p class="text-xs text-muted-foreground">Spend, last 30 days</p>
    <p class="text-2xl font-semibold tabular-nums">{{ "%.0f"|format(total_spend) }}</p>
  </section></div>
  <div class="card"><section><div class="table-container"><table class="table">
    {% for row in spend_by_campaign %}<tr><td>{{ row.campaign_name }}</td><td>{{ "%.0f"|format(row.spend) }}</td></tr>{% endfor %}
  </table></div></section></div>
</div>"""
)
```

Do not inject Meta API credentials into the dashboard/data app runtime.

Keep custom dashboards focused on the user's question. Do not add extra panels or metrics unless asked.

Do not mention internal dashboard implementation details to the user unless they explicitly ask.

---

## Ad preview handling

After campaign creation, call `meta_ads_ad_previews_get(creative_ids=["<creative_id>"])` — read the creative id with `meta_ads_ad_get(ad_id=..., fields="creative")` (`creative.id`), or use the id that `meta_ads_creative_create` returned. Note: `ad_id` is not a valid parameter.

- Never paste or render iframe/html preview snippets directly in chat.
- Summarize which preview formats succeeded or failed.
- Direct the user to the UI artifact to view previews.
