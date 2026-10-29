# BigQuery GA4 Export

The GA4 → BigQuery export is the single most under-used analytics asset most teams have. It gives you:

- **Unsampled data** — no GA4 API sampling, no matter how big the property.
- **Event-level granularity** — every event row, queryable.
- **Joinability** — join GA4 data with your order DB, CRM, billing data.
- **Custom attribution** — any model you can write in SQL, not just the four GA4 ships.
- **Cohort and retention queries** — clean window functions instead of GA4's locked-in cohort report.

Free for standard GA4 properties since 2023. Configure in GA4 Admin → BigQuery Linking. After it's set up, every day's events arrive as a `events_YYYYMMDD` table in `<project>.analytics_<property_id>.events_*`.

## Schema cheat sheet

The export has one row per event. Key columns:

| Column | Type | What |
| --- | --- | --- |
| `event_date` | STRING | `YYYYMMDD` (use `_TABLE_SUFFIX` for partition pruning) |
| `event_timestamp` | INT64 | Microseconds since epoch (UTC) |
| `event_name` | STRING | The event name (`purchase`, `page_view`, etc.) |
| `event_params` | RECORD (REPEATED) | Array of `{key, value: {string_value, int_value, double_value, float_value}}` |
| `user_id` | STRING | Set if you set it via `gtag('config', '...', {user_id})` |
| `user_pseudo_id` | STRING | GA4-assigned pseudo-anonymous client ID |
| `user_properties` | RECORD (REPEATED) | Array of `{key, value: ...}` |
| `device.*` | RECORD | `category`, `mobile_brand_name`, `operating_system`, `browser` |
| `geo.*` | RECORD | `country`, `region`, `city`, `continent` |
| `traffic_source.*` | RECORD | `name`, `medium`, `source` |
| `session_traffic_source_last_click.*` | RECORD | The session's last-click attribution |
| `ecommerce.*` | RECORD | `purchase_revenue`, `transaction_id`, `total_item_quantity` |
| `items` | RECORD (REPEATED) | Cart contents — `item_id`, `item_name`, `price`, `quantity` |

Two patterns dominate:

**Extract a parameter:** unnest `event_params` and pick by key.

```sql
(SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_path') AS page_path
```

**Build session ID:** GA4 doesn't ship a session ID column directly — derive it from `user_pseudo_id` + `ga_session_id` event param.

```sql
CONCAT(
  user_pseudo_id,
  '.',
  CAST((SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS STRING)
) AS session_id
```

## Query templates (copy + adapt)

Replace `your-project.analytics_123456789` with your actual project and property ID throughout.

### 1. Daily active users + sessions

```sql
SELECT
  PARSE_DATE('%Y%m%d', event_date) AS date,
  COUNT(DISTINCT user_pseudo_id) AS daily_active_users,
  COUNT(DISTINCT CONCAT(
    user_pseudo_id, '.',
    CAST((SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS STRING)
  )) AS sessions
FROM `your-project.analytics_123456789.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20260401' AND '20260430'
GROUP BY date
ORDER BY date;
```

### 2. Top pages by views

```sql
SELECT
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_path') AS page_path,
  COUNT(*) AS page_views,
  COUNT(DISTINCT user_pseudo_id) AS unique_users
FROM `your-project.analytics_123456789.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20260401' AND '20260430'
  AND event_name = 'page_view'
GROUP BY page_path
ORDER BY page_views DESC
LIMIT 50;
```

### 3. Conversion funnel (begin_checkout → purchase)

```sql
WITH steps AS (
  SELECT
    user_pseudo_id,
    MAX(IF(event_name = 'view_item', 1, 0)) AS step_1_view,
    MAX(IF(event_name = 'add_to_cart', 1, 0)) AS step_2_add,
    MAX(IF(event_name = 'begin_checkout', 1, 0)) AS step_3_checkout,
    MAX(IF(event_name = 'purchase', 1, 0)) AS step_4_purchase
  FROM `your-project.analytics_123456789.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20260401' AND '20260430'
  GROUP BY user_pseudo_id
)
SELECT
  SUM(step_1_view)     AS viewed_item,
  SUM(step_2_add)      AS added_to_cart,
  SUM(step_3_checkout) AS began_checkout,
  SUM(step_4_purchase) AS purchased,
  ROUND(SUM(step_4_purchase) / NULLIF(SUM(step_1_view), 0) * 100, 2) AS overall_conversion_pct
FROM steps;
```

### 4. Revenue by source/medium (last-click attribution)

```sql
SELECT
  session_traffic_source_last_click.manual_campaign.source AS source,
  session_traffic_source_last_click.manual_campaign.medium AS medium,
  COUNT(DISTINCT ecommerce.transaction_id) AS purchases,
  SUM(ecommerce.purchase_revenue) AS revenue
FROM `your-project.analytics_123456789.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20260401' AND '20260430'
  AND event_name = 'purchase'
GROUP BY source, medium
ORDER BY revenue DESC;
```

### 5. New vs returning users

```sql
WITH first_seen AS (
  SELECT
    user_pseudo_id,
    MIN(PARSE_DATE('%Y%m%d', event_date)) AS first_date
  FROM `your-project.analytics_123456789.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20260101' AND '20260430'
  GROUP BY user_pseudo_id
)
SELECT
  PARSE_DATE('%Y%m%d', e.event_date) AS date,
  COUNT(DISTINCT IF(fs.first_date = PARSE_DATE('%Y%m%d', e.event_date), e.user_pseudo_id, NULL)) AS new_users,
  COUNT(DISTINCT IF(fs.first_date < PARSE_DATE('%Y%m%d', e.event_date), e.user_pseudo_id, NULL)) AS returning_users
FROM `your-project.analytics_123456789.events_*` e
JOIN first_seen fs USING (user_pseudo_id)
WHERE _TABLE_SUFFIX BETWEEN '20260401' AND '20260430'
GROUP BY date
ORDER BY date;
```

### 6. Weekly retention cohort (week-over-week)

```sql
WITH first_visit AS (
  SELECT
    user_pseudo_id,
    DATE_TRUNC(PARSE_DATE('%Y%m%d', MIN(event_date)), WEEK) AS cohort_week
  FROM `your-project.analytics_123456789.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20260101' AND '20260430'
  GROUP BY user_pseudo_id
),
visits AS (
  SELECT DISTINCT
    user_pseudo_id,
    DATE_TRUNC(PARSE_DATE('%Y%m%d', event_date), WEEK) AS visit_week
  FROM `your-project.analytics_123456789.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20260101' AND '20260430'
)
SELECT
  fv.cohort_week,
  DATE_DIFF(v.visit_week, fv.cohort_week, WEEK) AS weeks_since_first_visit,
  COUNT(DISTINCT v.user_pseudo_id) AS users
FROM first_visit fv
JOIN visits v USING (user_pseudo_id)
GROUP BY cohort_week, weeks_since_first_visit
ORDER BY cohort_week, weeks_since_first_visit;
```

### 7. Joining with your order database

The most powerful query in the bunch. Assumes the site sets `user_id` on `gtag('config', ..., {user_id})` and that ID matches your DB.

```sql
WITH ga AS (
  SELECT
    user_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS visit_date,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_path') AS page_path
  FROM `your-project.analytics_123456789.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20260401' AND '20260430'
    AND user_id IS NOT NULL
)
SELECT
  ga.user_id,
  ga.page_path,
  COUNT(*) AS page_visits,
  ANY_VALUE(orders.lifetime_revenue_cents) AS lifetime_revenue_cents,
  ANY_VALUE(orders.plan_tier) AS plan_tier
FROM ga
LEFT JOIN `your-project.your_dataset.orders` orders USING (user_id)
GROUP BY user_id, page_path
ORDER BY page_visits DESC
LIMIT 100;
```

This unlocks questions GA4 can never answer alone: *"What's the LTV of users who hit our pricing page in the last 30 days?"*

## Running queries through the database toolkit

```
database_query(
  query="""
    SELECT event_date, COUNT(DISTINCT user_pseudo_id) AS dau
    FROM `your-project.analytics_123456789.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '20260401' AND '20260430'
    GROUP BY event_date
    ORDER BY event_date
  """,
)
```

The query runs on the workspace's saved BigQuery connection; save one first with `database_connections_create`. No tool writes rows into BigQuery.

## Performance + cost rules

- **Always partition-prune.** Use `_TABLE_SUFFIX BETWEEN 'YYYYMMDD' AND 'YYYYMMDD'` to limit which daily tables get scanned. A query without this against a year of GA4 events is *expensive*.
- **Don't `SELECT *`.** Pick the columns you need. GA4 events have ~30 nested fields; selecting all of them on a year of data is a wallet event.
- **Cache exploratory queries.** BigQuery caches identical queries for 24h at no cost. Iterating on a query? Don't rewrite the date range every time — cache hit gets you free re-runs.
- **Use the `intraday_*` tables for today's data.** GA4 export populates `intraday_YYYYMMDD` for the current day, then collapses into `events_YYYYMMDD` ~24h later. If you need today's data, query both with `events_*` glob.

## Schema gotchas

- **`event_date` is a STRING (`YYYYMMDD`).** Convert with `PARSE_DATE('%Y%m%d', event_date)` before doing date arithmetic.
- **`event_timestamp` is microseconds.** `TIMESTAMP_MICROS(event_timestamp)` to get a real timestamp.
- **Nested params require `UNNEST`.** This is the #1 thing new GA4 BigQuery users get stuck on. Use the patterns above as templates.
- **Ecommerce data lives in `ecommerce.*` and `items` (repeated).** `purchase` events have populated `ecommerce.purchase_revenue`; `add_to_cart` events have populated `items` but no `ecommerce` revenue.
- **`user_id` is NULL for anonymous users.** Don't filter on it unless you specifically want logged-in users.
