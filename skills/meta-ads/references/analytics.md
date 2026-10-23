# Meta Ads: Performance Analytics

Use this for querying performance data, ad-level insights, and historical reporting.

---

## Where Meta performance data comes from

Synced Meta reports are in the workspace warehouse. `connections_info(toolkit_id="meta_ads")`
names the table and the last sync. Read it with `database_query(query=..., connection="lakehouse")`.
Use `meta_ads_insights_get` for live data or data that is not synced. There is no Meta sync tool.

| Situation | Use |
|---|---|
| Any performance check, trend, or drilldown | `meta_ads_insights_get` |
| Campaign created in this session | `meta_ads_insights_get` or `meta_ads_campaign_get(campaign_id=..., fields="name,objective,status,daily_budget,lifetime_budget,bid_strategy")` |
| History longer than the API returns conveniently, or a join against non-Meta data | The synced warehouse table — see "Querying warehouse tables" below |

> **Important**: always name the date range you queried when you report numbers back. Meta
> attribution shifts as conversions land, so the same window can return different totals on
> different days.

---

## Querying insights via the Meta API

### Account-level campaign summary

```json
{
  "object_id": "act_123456789",
  "object_type": "account",
  "level": "campaign",
  "date_preset": "last_30d",
  "include_actions": true
}
```

### Ad set breakdown

```json
{
  "object_id": "act_123456789",
  "object_type": "account",
  "level": "adset",
  "date_preset": "last_30d",
  "include_actions": true
}
```

### Ad-level breakdown (use for historical or drilldown)

Use `level: "ad"` to get ad-level data across the full account. Do **not** iterate every ad ID individually — that is slow and will hit rate limits.

```json
{
  "object_id": "act_123456789",
  "object_type": "account",
  "level": "ad",
  "date_preset": "last_90d",
  "include_actions": true
}
```

Use `object_type: "ad"` only when drilling into a single specific ad.

Use `time_increment: "1"` only when daily rows are needed (daily spend trends, delivery dates). It significantly increases response size — avoid for summary queries.

---

## Valid date presets

`date_preset` accepts only Meta's fixed preset values. Do **not** invent values — they will be rejected by the API with no clear error message.

**Valid presets:**

```
today               yesterday           last_3d             last_7d
last_14d            last_28d            last_30d            last_90d
last_week_mon_sun   last_week_sun_sat   last_month          last_quarter
last_year           this_week_mon_today this_week_sun_today this_month
this_quarter        this_year           maximum             data_maximum
```

**These do NOT exist and will be rejected:**
`last_60d`, `last_1d`, `last_180d`, `last_6_months`, `last_45d`

**For any window without a matching preset, use `time_range` instead:**

```json
{
  "time_range": {
    "since": "2026-04-01",
    "until": "2026-05-31"
  }
}
```

`since`/`until` are `YYYY-MM-DD`. `time_range` overrides `date_preset` when both are present.

For all-time / lifetime data: `"date_preset": "maximum"` (optionally with `"time_increment": "all_days"`).

Do not claim Meta only supports 7 or 28 days unless an actual API response says so.

---

## Querying warehouse tables

Read the synced Meta reports through the `database` toolkit — the single database path in Hyper.
Pass `connection="lakehouse"` to each call, and write ClickHouse SQL (SELECT only):

1. Call `database_tables_list(connection="lakehouse")` to discover what the warehouse holds.
2. Call `database_tables_describe(tables=[...], connection="lakehouse")` on the table you found to get its real columns.
3. Query it with `database_query(query=..., connection="lakehouse")`.

**Never guess a table name or a column name.** The queries below are shapes, not literals —
substitute the real table and the real column names you got from steps 1 and 2. If the
connected database holds no Meta data, use `meta_ads_insights_get` instead.

### Daily spend trend

```sql
SELECT
  campaign_name,
  date_start,
  SUM(spend) AS total_spend,
  SUM(impressions) AS total_impressions
FROM <table from database_tables_list>
GROUP BY campaign_name, date_start
ORDER BY date_start DESC
LIMIT 100;
```

### Campaign performance summary

```sql
SELECT
  campaign_name,
  SUM(spend) AS spend,
  SUM(impressions) AS impressions,
  SUM(clicks) AS clicks,
  ROUND(toFloat64(SUM(clicks)) / NULLIF(SUM(impressions), 0) * 100, 2) AS ctr_pct,
  ROUND(toFloat64(SUM(spend)) / NULLIF(SUM(clicks), 0), 2) AS cpc
FROM <table from database_tables_list>
GROUP BY campaign_name
ORDER BY spend DESC;
```

### Ad set cost-per-conversion

```sql
SELECT
  adset_name,
  SUM(spend) AS spend,
  SUM(conversions) AS conversions,
  CASE
    WHEN SUM(conversions) > 0 THEN ROUND(toFloat64(SUM(spend)) / SUM(conversions), 2)
    ELSE NULL
  END AS cost_per_conversion
FROM <table from database_tables_list>
GROUP BY adset_name
ORDER BY spend DESC;
```

Default to `meta_ads_insights_get`. Reach for a warehouse table only when the workspace has
one and the request genuinely needs it.

---

## Replicating an existing campaign (analyze → create)

When the task is "find the best performer and build a new campaign modelled on it," inspect the source with `meta_ads_campaign_get(campaign_id=..., fields="name,objective,status,daily_budget,lifetime_budget,bid_strategy")` and `meta_ads_adset_list` (section 15 of [constraints.md](constraints.md)), then build the new campaign via the matching objective workflow ([discovery.md](discovery.md) → relevant `campaigns/<objective>.md`).

> Read the source ad set's `promoted_object`, `bid_strategy` and `bid_amount` as section 15 of [constraints.md](constraints.md) says, or with `meta_ads_adset_get(adset_id=..., fields="promoted_object,bid_strategy,bid_amount")`. Do not assume the source had no pixel because a field is missing. When replicating a sales or leads campaign, re-derive `promoted_object` yourself: look up the pixel with `meta_ads_ad_pixels_list`, infer the `custom_event_type` from the conversion events visible in the source's insights (e.g. PURCHASE, LEAD, COMPLETE_REGISTRATION), and set it explicitly on the new ad set per the objective workflow.

Carry forward from the source: objective, targeting (age/geo/advantage_audience), and budget mode (campaign-level CBO vs ad-set). Re-derive everything pixel/promoted_object-related rather than trusting the GET response.

### Duplicating a campaign and swapping creatives

For "duplicate this campaign exactly but with new creatives":

1. **Read the source structure**: `meta_ads_campaign_get(campaign_id=..., fields="name,objective,status,daily_budget,lifetime_budget,bid_strategy")`, `meta_ads_ad_sets_list(campaign_id=...)`, `meta_ads_list(ad_set_id=...)`. Read each creative's destination as section 15 of [constraints.md](constraints.md) says.
2. **Recreate** campaign → ad set → ad via the matching objective workflow, copying objective, targeting, and budget mode. Re-derive `promoted_object` (see warning above). Name the new campaign as the user specified.
3. **Swap creatives**: upload the new images (`meta_ads_ad_images_upload`), then either build a fresh inline `object_story_spec` on the new ad or create new creatives with `meta_ads_creative_create` and attach by `creative_id`.
4. **Verify before deleting anything**: confirm the new ads were created and the new creatives are attached (`meta_ads_list(ad_set_id=...)` / `meta_ads_creative_get(creative_id=..., fields="link_url,object_story_spec,url_tags")`).
5. **Only then** delete old draft creatives with `meta_ads_creative_delete` (or `meta_ads_ad_delete` for ads). Never delete the source until the replacement is confirmed.

Leave the new campaign PAUSED unless the user said to activate.
