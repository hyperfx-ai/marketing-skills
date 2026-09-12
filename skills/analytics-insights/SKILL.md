---
name: analytics-insights
description: Drive Google Analytics (GA4), Google Tag Manager, Google Search Console, and BigQuery from chat — tracking plans, GA4 reports, key-event (conversion) setup, custom dimensions and metrics, GTM audits, GSC performance, and GA4 BigQuery export queries. Use when the user wants an analytics audit, a GA4 report, a tracking plan, conversion setup, GTM cleanup, search-performance data, or asks "how is the site performing?" or "are my conversions firing?".
requires_toolkits:
  - google_analytics_toolkit
icon: google_analytics
short_description: Drive GA4, GTM, Search Console, and BigQuery from chat for reports and tracking.
---

# Analytics Insights

Operator skill for the Google measurement stack — GA4, GTM, Search Console, and BigQuery — driven directly from chat. Build a tracking plan, run reports, mark conversions, audit existing setup, and query the warehouse without leaving the conversation.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Keyword research, AI-search visibility, full SEO audit | `seo-research` (HyperSEO toolkit — broader and richer than GSC for keyword work) |
| Google Ads campaign performance | `google-ads` (campaign-level) — but GA4-side conversion attribution lives here |
| Meta / Facebook ads metrics | `meta-ads` |
| Email program metrics | `email-lifecycle` (provider-side) |

GSC and HyperSEO overlap on search-performance data. Rule of thumb: use GSC here for *the user's own site's* impression / click / position data. Use HyperSEO (in `seo-research`) for keyword research, competitor data, AI-search visibility.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **At least one of these connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps):
  - **Google Analytics** — GA4 reports, custom metrics / dimensions, key-event (conversion) management.
  - **Google Tag Manager** — tag / trigger / variable / workspace / version management.
  - **Google Search Console** — search-performance data, sitemaps, URL inspection.
  - **BigQuery** — SQL queries against the GA4 export (or any other dataset).

If `google_analytics_ga4_reports_run`, `google_tag_manager_tags_manage`, `google_search_console_performance_get`, and `bigquery_execute_query` are all missing from the agent's tool list, stop and tell the user to enable the Hyper MCP and connect at least one of these integrations.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call("<name>", {...})` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found, its integration is not connected or not enabled for the workspace: stop and tell the user which integration to connect.

## Tool surface

| Group | Tools |
| --- | --- |
| GA4 — reporting | `google_analytics_ga4_reports_run`, `google_analytics_accounts_list`, `google_analytics_properties_list`, `google_analytics_properties_get` |
| GA4 — properties & data streams | `google_analytics_ga4_properties_create`, `google_analytics_properties_update`, `google_analytics_properties_delete`, `google_analytics_data_streams_create`, `google_analytics_data_streams_list`, `google_analytics_data_streams_get`, `google_analytics_data_streams_update`, `google_analytics_data_streams_delete`, `google_analytics_data_retention_get` *(read-only — no update variant in MCP)*, `google_analytics_data_collection_acknowledge` |
| GA4 — key events (conversions) | `google_analytics_key_events_create`, `google_analytics_key_events_list`, `google_analytics_key_events_get`, `google_analytics_key_events_update`, `google_analytics_key_events_delete` |
| GA4 — custom metrics / dimensions | `google_analytics_custom_metrics_create`, `google_analytics_custom_metrics_list`, `google_analytics_custom_metrics_get`, `google_analytics_custom_metrics_update`, `google_analytics_custom_metrics_archive`, `google_analytics_custom_dimensions_create`, `google_analytics_custom_dimensions_list`, `google_analytics_custom_dimensions_get`, `google_analytics_custom_dimensions_update`, `google_analytics_custom_dimensions_archive` |
| GTM (note: prefixed `gtm_*`, **not** `google_tag_manager_*`) | `gtm_account`, `gtm_container`, `google_tag_manager_workspaces_manage`, `google_tag_manager_tags_manage`, `google_tag_manager_triggers_manage`, `google_tag_manager_variables_manage`, `google_tag_manager_built_in_variables_manage`, `gtm_folder`, `gtm_environment`, `google_tag_manager_versions_manage`, `google_tag_manager_version_headers_manage`, `google_tag_manager_user_permissions_manage`, `gtm_client`, `gtm_template`, `gtm_transformation`, `gtm_zone`, `gtm_destination` |
| Google Search Console | `google_search_console_performance_get`, `google_search_console_sites_list`, `google_search_console_sitemaps_list`, `google_search_console_sitemaps_get`, `google_search_console_sitemaps_submit`, `google_search_console_sitemaps_delete`, `google_search_console_urls_submit` |
| BigQuery | `bigquery_execute_query`, `bigquery_insert_rows` |

## Critical rules

1. **GA4 property IDs — arg name differs by tool.** Three patterns: (a) Reporting tools (`run_ga4_report`, `get_property`) take `property_id="properties/123456789"`. (b) Create and list tools (`create_key_event`, `list_key_events`, `create_custom_dimension`, `list_custom_dimensions`, etc.) take `parent="properties/123456789"`. (c) Get/update/delete tools operate on a specific resource and take `name=` with the full resource path (e.g. `"properties/123456789/keyEvents/12345"`). All three need the `properties/` prefix in some form — passing a bare numeric ID silently fails. When in doubt, check the tool's schema for which arg is marked `required`.
2. **Date ranges are inclusive on both ends.** `start_date="2026-04-01"` and `end_date="2026-04-30"` returns 30 days, not 29. Same for relative dates: `7daysAgo` to `today` is 8 days, not 7.
3. **GA4 sampling kicks in above ~10M events.** For high-volume properties, the GA4 API silently samples results. If precision matters (board reporting, financial attribution), use the **BigQuery GA4 export** instead — see [`references/bigquery-ga4-export.md`](./references/bigquery-ga4-export.md).
4. **Conversions in GA4 are "key events".** GA4 renamed "conversions" to "key events" in 2024. The tools reflect this — use `google_analytics_key_events_create` to mark an event as a conversion. Don't get confused by older docs.
5. **GTM changes need a workspace + version + publish.** Tags / triggers / variables created in a workspace are *not live* until the workspace is committed to a new version and that version is published. Use `google_tag_manager_workspaces_manage` → modify → `google_tag_manager_versions_manage` (create) → publish.
6. **GSC data has a 2–3 day lag.** Don't query "yesterday" in GSC and expect data — query 3+ days back for stable numbers. GA4 has a 24-48h lag for some metrics.
7. **Apple Mail Privacy Protection inflates GA4 "engaged" sessions from email.** Don't trust email-driven engagement numbers in GA4 alone — cross-reference with the email provider's own click data.

## Workflow — pick the right path

The skill covers four distinct jobs. Pick first; the workflows are different.

| The user wants… | Path | Reference |
| --- | --- | --- |
| A report ("how did we do last month?") | Phase R | — |
| To set up tracking ("we need to measure X") | Phase T | [`references/ga4-tracking-plan.md`](./references/ga4-tracking-plan.md) |
| To audit existing GTM / GA4 ("why is conversion data wonky?") | Phase A | [`references/gtm-audit.md`](./references/gtm-audit.md) |
| Precise / unsampled / cross-source analysis | Phase B | [`references/bigquery-ga4-export.md`](./references/bigquery-ga4-export.md) |

### Phase R — Run a report (most common path)

**Quick-read option:** For instant, no-sampling queries against cached GA4 data, try `google_analytics_insights_query` first — it's faster than the full API path and avoids the ~10M-event sampling threshold. Call it with a `query=` SQL string; the tool description lists available columns and the cached table name. If it returns `"No data cached"`, read the `suggestion` field for the workspace-specific table name and retry. For cached GSC data, use `google_search_console_insights_query` with the same pattern. Fall through to Step 4 below for metrics not in the cache.

1. **Confirm the property.** `google_analytics_accounts_list()` → `google_analytics_properties_list(filter="parent:accounts/<account_id>")`. Ask the user to pick if there are multiple. Save the `properties/<id>` for the rest of the conversation.
2. **Pick the date range.** Always confirm. "Last 30 days" is `start_date="30daysAgo"`, `end_date="yesterday"` (avoid `today` — partial-day data is unstable).
3. **Pick metrics + dimensions.** Don't blast 12 metrics × 6 dimensions in one report — the result is unreadable. Pick the 2–3 metrics that answer the user's question and the 1–2 dimensions that segment them meaningfully.
4. **Run the report.**

```
google_analytics_ga4_reports_run(
  property_id="properties/123456789",
  start_date="30daysAgo",
  end_date="yesterday",
  metrics=["activeUsers", "sessions", "conversions", "totalRevenue"],
  dimensions=["sessionDefaultChannelGroup", "deviceCategory"],
)
```

5. **Present results as a table.** Always show the raw numbers alongside any interpretation. "Organic search drove 12,400 sessions (+18% MoM)" beats "organic was up."
6. **One follow-on if the data flags it.** If a metric stands out (e.g., conversion rate dropped 40% on mobile), run *one* targeted follow-up report — don't speculate.

#### Common GA4 metrics & dimensions

The GA4 API uses camelCase names. The most useful:

**Metrics:** `activeUsers`, `sessions`, `screenPageViews`, `bounceRate`, `engagementRate`, `averageSessionDuration`, `conversions`, `eventCount`, `totalRevenue`, `transactions`, `purchaseRevenue`, `userEngagementDuration`.

**Dimensions:** `country`, `city`, `deviceCategory`, `operatingSystem`, `browser`, `sessionDefaultChannelGroup`, `sessionSource`, `sessionMedium`, `sessionCampaignName`, `pagePath`, `eventName`, `date`, `hour`, `landingPage`.

For the full list, the user can browse the [GA4 Data API reference](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema).

### Phase T — Set up tracking

The GA4 API can create properties, data streams, key events, custom metrics, and custom dimensions — but it **can't deploy GTM tags into the page**. That step is GTM-side (or hard-coded in the site). The skill workflow:

1. **Tracking plan first.** Define what events you need to fire, where they fire, and which ones are conversions (key events). Full template in [`references/ga4-tracking-plan.md`](./references/ga4-tracking-plan.md).
2. **GA4-side setup** — create custom dimensions / metrics, mark key events:

```
google_analytics_custom_dimensions_create(
  parent="properties/123456789",
  parameter_name="plan_tier",
  display_name="Plan Tier",
  scope="EVENT",
)

google_analytics_key_events_create(
  parent="properties/123456789",
  event_name="purchase",
  counting_method="ONCE_PER_EVENT",
)
```

3. **GTM-side setup** — create/update tags + triggers + variables in a workspace, then version + publish:

```
google_tag_manager_workspaces_manage(operation="create", account_id="...", container_id="...", name="purchase-tracking-v3")

google_tag_manager_tags_manage(operation="create", workspace_path="...", tag_definition={...})
google_tag_manager_triggers_manage(operation="create", workspace_path="...", trigger_definition={...})
google_tag_manager_variables_manage(operation="create", workspace_path="...", variable_definition={...})

google_tag_manager_versions_manage(operation="create", workspace_path="...", version_name="purchase-tracking-v3")
# then publish via the GTM UI or version operation
```

4. **Validate** — see Phase A.

### Phase A — Audit (the existing setup is broken or suspect)

Most "our analytics is wrong" complaints are one of:

| Symptom | Likely cause | How to confirm |
| --- | --- | --- |
| Conversion event not appearing in GA4 | Event firing in GTM but not reaching GA4 (wrong measurement ID, blocked by consent gate, ad blocker) | `google_analytics_ga4_reports_run` for `eventName=purchase` over the last 7d → if 0, check GTM |
| Conversion count wildly off | Event firing on every page (not just confirmation), or duplicate tags | Audit GTM tags via `google_tag_manager_tags_manage(operation="list")`, check for multiple tags firing on the same trigger |
| Revenue reported differently in GA4 vs the platform of record | Currency mismatch, refund handling, attribution window | Pull both side-by-side, look for refund / currency rows |
| Suddenly mobile traffic dropped to ~0 | Tag firing only on desktop trigger, or a recent GTM publish broke the mobile container | `google_tag_manager_versions_manage(operation="list")` to find recent publishes, diff with previous version |
| GSC clicks ≠ GA4 organic sessions | Always different — different definitions. Don't try to reconcile exactly. | Expected; document and move on |

Detailed audit walkthrough in [`references/gtm-audit.md`](./references/gtm-audit.md).

### Phase B — BigQuery GA4 export (precision / cross-source analysis)

For unsampled data, custom attribution, joining GA4 with order-DB / CRM data, or cohort analysis. Requires the GA4 → BigQuery export to be turned on in the GA4 admin (free for standard properties since 2023).

```
bigquery_execute_query(
  query="""
    SELECT
      event_date,
      COUNT(DISTINCT user_pseudo_id) AS users,
      COUNTIF(event_name = 'purchase') AS purchases,
      SUM(IF(event_name = 'purchase', ecommerce.purchase_revenue, 0)) AS revenue
    FROM `your-project.analytics_123456789.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '20260401' AND '20260430'
    GROUP BY event_date
    ORDER BY event_date
  """
)
```

Schema, common queries, and the full attribution-modeling workflow in [`references/bigquery-ga4-export.md`](./references/bigquery-ga4-export.md).

## Output standards

- **Always present numbers as tables**, not prose. "12,400 sessions, 8.2% bounce, 1.4% conversion" → markdown table.
- **Always include the date range** in the report header. "Apr 1–30, 2026" — undated numbers are useless.
- **Always include the property / site** the report came from. Multi-property organizations get burned by this constantly.
- **Annotate sampling.** If GA4 returns a `samplesReadCount < samplingSpaceSize`, say so explicitly. The user needs to know whether to trust the number for finance / board reporting.
- **Distinguish "ratio metric" from "summable metric".** Bounce rate, engagement rate, conversion rate are *ratios* and don't sum — present them as one number, not a column total.

## Reference workflows

| Reference | When to read |
| --- | --- |
| [`references/ga4-tracking-plan.md`](./references/ga4-tracking-plan.md) | Designing what to track — recommended event schema, custom dimensions / metrics, key-event mapping, naming conventions |
| [`references/gtm-audit.md`](./references/gtm-audit.md) | Auditing an existing GTM container — finding duplicate tags, broken triggers, unused variables, missing consent gates |
| [`references/bigquery-ga4-export.md`](./references/bigquery-ga4-export.md) | Querying the GA4 BigQuery export — schema, common queries (DAU, funnel, attribution, cohort, retention), join patterns |
