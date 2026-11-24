# Conversion Tracking

Conversion-action inventory report. Use it to list configured
conversion actions and their metadata before building action-specific
dashboards.

## When to use

- "Which conversion actions exist?"
- "Which conversion actions are enabled?"
- "What are the conversion action categories and settings?"
- Before building a funnel dashboard that needs user-mapped stages.

## Inputs

- `customer_id` (required).

Use the GAQL below through `google_ads_gaql_query` when you need
conversion-action metadata. This is separate from campaign-level
conversion metrics, which use `segments.conversion_action*`.

## GAQL

```sql
SELECT
  conversion_action.id,
  conversion_action.name,
  conversion_action.category,
  conversion_action.type,
  conversion_action.status,
  conversion_action.primary_for_goal,
  conversion_action.counting_type,
  conversion_action.click_through_lookback_window_days
FROM conversion_action
WHERE conversion_action.status != 'REMOVED'
```

## How to interpret

- **No enabled conversion actions** → optimization is blind; halt all
  Smart Bidding advice until at least one is configured.
- **Several actions with `conversion_action.primary_for_goal = TRUE` in the same category** (e.g. two
  primary purchase actions) → Smart Bidding double-counts; recommend
  demoting one to secondary.
- **`PURCHASE` category but `counting_type = MANY_PER_CLICK`** is rare
  and usually a misconfiguration; flag for review.
- **Lookback window mismatches** between online + offline actions can
  produce inconsistent attribution.

## Building a dashboard from this report

`gaql(...)` and `PERIOD` are the shorthands in
[reporting.md](../reporting.md) Phase 4; expand them in the call.

The inventory has no date window, so this dashboard declares no parameter.

```python
artifacts_create(
    type="dashboard",
    name="Conversion Tracking Audit",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-kpis source="summary"
    values="actions:Actions:count,enabled_actions:Enabled:count,primary_actions:Primary:count,categories:Categories:count"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart kind="bar" source="by_category" x="category" series="total_actions:Actions" format="count" title="Actions by category"></hyper-chart>
    <hyper-chart kind="bar" source="by_category" x="category" series="primary_actions:Primary actions" format="count" title="Primary actions by category" hint="More than one primary action in a category can double-count"></hyper-chart>
  </div>
  <hyper-table source="actions" sort="name:asc" page-size="20" title="Action inventory"
    columns="name:Action:text,category:Category:text,type:Type:text,status:Status:text,is_primary:Primary:text,counting:Counting:text,lookback_days:Lookback days:count"></hyper-table>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT conversion_action.id, conversion_action.name, conversion_action.category, "
                "conversion_action.status, conversion_action.primary_for_goal "
                "FROM conversion_action "
                "WHERE conversion_action.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "category": "conversionAction.category",
                    "status": "conversionAction.status",
                    "is_primary": {"from": "conversionAction.primaryForGoal", "cast": "boolean"},
                },
            },
            "calc_sql": (
                "SELECT COUNT(*) AS actions, "
                "SUM(CASE WHEN status = 'ENABLED' THEN 1 ELSE 0 END) AS enabled_actions, "
                "SUM(CASE WHEN is_primary THEN 1 ELSE 0 END) AS primary_actions, "
                "COUNT(DISTINCT category) AS categories FROM data"
            ),
            "columns": {"actions": "count", "enabled_actions": "count", "primary_actions": "count", "categories": "count"},
            "max_age_minutes": 60,
        },
        "by_category": {
            "source": gaql(
                "SELECT conversion_action.id, conversion_action.name, conversion_action.category, "
                "conversion_action.status, conversion_action.primary_for_goal "
                "FROM conversion_action "
                "WHERE conversion_action.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "category": "conversionAction.category",
                    "is_primary": {"from": "conversionAction.primaryForGoal", "cast": "boolean"},
                },
            },
            "calc_sql": (
                "SELECT category, COUNT(*) AS total_actions, "
                "SUM(CASE WHEN is_primary THEN 1 ELSE 0 END) AS primary_actions "
                "FROM data GROUP BY category ORDER BY total_actions DESC"
            ),
            "columns": {"category": "text", "total_actions": "count", "primary_actions": "count"},
            "max_age_minutes": 60,
        },
        "actions": {
            "source": gaql(
                "SELECT conversion_action.id, conversion_action.name, "
                "conversion_action.category, conversion_action.type, "
                "conversion_action.status, conversion_action.primary_for_goal, "
                "conversion_action.counting_type, "
                "conversion_action.click_through_lookback_window_days "
                "FROM conversion_action "
                "WHERE conversion_action.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "name": "conversionAction.name",
                    "category": "conversionAction.category",
                    "type": "conversionAction.type",
                    "status": "conversionAction.status",
                    "primary_for_goal": {"from": "conversionAction.primaryForGoal", "cast": "boolean"},
                    "counting": "conversionAction.countingType",
                    "lookback_days": {"from": "conversionAction.clickThroughLookbackWindowDays", "cast": "integer"},
                },
            },
            "calc_sql": (
                "SELECT name, category, type, status, "
                "CASE WHEN primary_for_goal THEN 'Yes' ELSE 'No' END AS is_primary, "
                "counting, lookback_days FROM data ORDER BY name"
            ),
            "columns": {
                "name": "text", "category": "text", "type": "text", "status": "text",
                "is_primary": "text", "counting": "text", "lookback_days": "count",
            },
            "max_age_minutes": 60,
        },
    },
)
```

## Variants

- Add the `by_action` dataset of [conversion-by-action.md](conversion-by-action.md)
  beside the inventory to show actual conversion volume per action.
- Filter to `category = 'PURCHASE'` for ecommerce-only audits.
