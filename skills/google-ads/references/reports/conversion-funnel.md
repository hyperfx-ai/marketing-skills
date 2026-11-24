# Conversion Funnel

Multi-stage conversion funnel for lead-gen / B2B accounts. Pivots
per-action conversion data into ordered funnel stages and computes
step-conversion rates between stages.

## When to use

- Lead-gen / B2B accounts with multiple sequential stages (e.g.
  application_submitted → lead_reached → scheduled → showed → won).
- "What's the drop-off between [stage A] and [stage B]?"
- "Which stage is the bottleneck?"
- Pricing or onboarding optimization rooted in funnel data.

For a flat per-action breakdown without ordering, use
[conversion-by-action.md](conversion-by-action.md) instead.

## Inputs

- `customer_id` (required).
- `date_range` (default: `LAST_30_DAYS`).
- An ordered list of conversion-action names (or IDs) that defines the
  funnel. **The agent must discover these first** — no funnel ordering
  is hard-coded.

## GAQL

### Step 1 — discover the user's conversion actions

```sql
SELECT
  conversion_action.id,
  conversion_action.name,
  conversion_action.category,
  conversion_action.status
FROM conversion_action
WHERE conversion_action.status != 'REMOVED'
```

Show the result to the user and ask them to map each action to a funnel
stage in order. **Do not assume a six-stage funnel** (or any stage count) —
funnels are workspace-specific.

### Step 2 — pull per-action data

Same shape as [conversion-by-action.md](conversion-by-action.md):

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  segments.conversion_action,
  segments.conversion_action_name,
  segments.conversion_action_category,
  metrics.conversions,
  metrics.all_conversions,
  metrics.conversions_value
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

The same caveat applies: **only** segment via
`segments.conversion_action*`, never `conversion_action.id` against
`FROM campaign` (raises `PROHIBITED_RESOURCE_TYPE_IN_SELECT_CLAUSE`).
The metric is `metrics.conversions`, not the nonexistent
`metrics.conversions_by_conversion_action`.

Do **not** include `metrics.cost_micros` in the per-action query. Google Ads
rejects cost with `segments.conversion_action*` using
`PROHIBITED_SEGMENT_WITH_METRIC_IN_SELECT_OR_WHERE_CLAUSE`. If cost is needed,
run a separate campaign/date query:

```sql
SELECT
  segments.date,
  campaign.id,
  campaign.name,
  metrics.cost_micros,
  metrics.clicks,
  metrics.impressions
FROM campaign
WHERE segments.date BETWEEN '{start}' AND '{end}'
  AND campaign.status != 'REMOVED'
```

Join conversion rows to cost rows on `(segments.date, campaign.id)`. For
one-off analysis, join in memory with pandas or an equivalent dataframe in the
sandbox. A dashboard keeps them as two datasets.

## How to interpret

- Pivot the raw rows so each user-mapped stage becomes a column,
  values are stage totals.
- Step conversion rate = `stage_n / stage_n-1`.
- Joined cost is campaign/date context. Do not present it as action-attributed
  cost per stage unless the report explicitly defines an allocation rule.
- State the user-provided stage mapping in the final report. Do not
  infer action order from names alone.

## Building a dashboard from this report

`gaql(...)` and `PERIOD` are the shorthands in
[reporting.md](../reporting.md) Phase 4; expand them in the call.

Put the user's own action names, in the order they confirmed, in `STAGES`. It is
the start of three `calc_sql` queries; write it out in each one.

```python
# After the user has mapped action names to ordered stages, e.g.
# application_submitted, lead_reached, scheduled_for_training,
# showed_for_training, launched_from_training, rep_that_sells
STAGES = (
    "WITH stages(stage_order, stage) AS (VALUES "
    "(1, 'application_submitted'), (2, 'lead_reached'), "
    "(3, 'scheduled_for_training'), (4, 'showed_for_training'), "
    "(5, 'launched_from_training'), (6, 'rep_that_sells')) "
)
artifacts_create(
    type="dashboard",
    name="Lead-Gen Funnel",
    html="""
<main class="@container flex flex-col gap-2.5">
  <hyper-filter-bar params="period"></hyper-filter-bar>
  <hyper-kpis source="summary"
    values="first_stage:First stage:decimal,last_stage:Last stage:decimal,end_to_end:End-to-end rate:percent,conversions:All stage conversions:decimal"></hyper-kpis>
  <hyper-kpis source="cost_context"
    values="spend:Cost:currency,impressions:Impressions:count,clicks:Clicks:count,avg_cpc:Avg. CPC:cents"></hyper-kpis>
  <div class="grid grid-cols-1 gap-2.5 @3xl:grid-cols-2">
    <hyper-chart span="full" kind="line" source="daily" x="day" series="conversions:Conversions" format="decimal" range-param="period" title="Conversions, all stages"></hyper-chart>
    <hyper-chart kind="bar" source="step_rates" x="stage" series="conversions:Conversions" format="decimal" title="Stage totals" hint="In funnel order"></hyper-chart>
    <hyper-chart kind="bar" source="step_rates" x="stage" series="step_rate:Step rate" format="percent" title="Step rates" hint="Each stage over the stage before it"></hyper-chart>
  </div>
  <hyper-table source="step_rates" sort="stage_order:asc" title="Funnel detail"
    columns="stage_order:Step:count,stage:Stage:text,conversions:Conversions:decimal,step_rate:Step rate:percent"></hyper-table>
  <hyper-note>Stages are in the order confirmed with the account owner. Cost is campaign context and is not attributed to a stage.</hyper-note>
</main>
""",
    datasets={
        "summary": {
            "source": gaql(
                "SELECT campaign.id, segments.conversion_action_name, metrics.conversions "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "action": "segments.conversionActionName",
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": STAGES + (
                ", totals AS (SELECT s.stage_order, COALESCE(SUM(d.conversions), 0) AS conversions "
                "FROM stages s LEFT JOIN data d ON d.action = s.stage GROUP BY s.stage_order) "
                "SELECT MAX(CASE WHEN stage_order = 1 THEN conversions END) AS first_stage, "
                "MAX(CASE WHEN stage_order = (SELECT MAX(stage_order) FROM totals) THEN conversions END) AS last_stage, "
                "100.0 * MAX(CASE WHEN stage_order = (SELECT MAX(stage_order) FROM totals) THEN conversions END) "
                "/ NULLIF(MAX(CASE WHEN stage_order = 1 THEN conversions END), 0) AS end_to_end, "
                "SUM(conversions) AS conversions FROM totals"
            ),
            "columns": {"first_stage": "decimal", "last_stage": "decimal", "end_to_end": "percent", "conversions": "decimal"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "cost_context": {
            "source": gaql(
                "SELECT campaign.id, metrics.cost_micros, metrics.clicks, metrics.impressions "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
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
        "step_rates": {
            "source": gaql(
                "SELECT campaign.id, segments.conversion_action_name, metrics.conversions "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "action": "segments.conversionActionName",
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": STAGES + (
                ", totals AS (SELECT s.stage_order, s.stage, COALESCE(SUM(d.conversions), 0) AS conversions "
                "FROM stages s LEFT JOIN data d ON d.action = s.stage GROUP BY s.stage_order, s.stage) "
                "SELECT stage_order, stage, conversions, "
                "100.0 * conversions / NULLIF(LAG(conversions) OVER (ORDER BY stage_order), 0) AS step_rate "
                "FROM totals ORDER BY stage_order"
            ),
            "columns": {"stage_order": "count", "stage": "text", "conversions": "decimal", "step_rate": "percent"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
        "daily": {
            "source": gaql(
                "SELECT segments.date, campaign.id, segments.conversion_action_name, metrics.conversions "
                "FROM campaign "
                "WHERE segments.date DURING {{period}} "
                "AND campaign.status != 'REMOVED'"
            ),
            "loader": {
                "rows_path": "results",
                "map": {
                    "day": "segments.date",
                    "action": "segments.conversionActionName",
                    "conversions": {"from": "metrics.conversions", "cast": "number"},
                },
            },
            "calc_sql": STAGES + (
                "SELECT d.day AS day, SUM(d.conversions) AS conversions FROM data d "
                "JOIN stages s ON s.stage = d.action GROUP BY d.day ORDER BY d.day"
            ),
            "columns": {"day": "date", "conversions": "decimal"},
            "params": PERIOD,
            "max_age_minutes": 60,
        },
    },
)
```

## Variants

- **Per campaign**: filter `WHERE campaign.id = ...` to compare funnel
  shapes between campaigns.
- **Allocated cost per stage**: join campaign/date cost to conversion rows,
  then apply an explicit allocation rule before presenting stage cost.
