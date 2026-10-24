# Automated Rules (Ad Rules Engine)

Meta-native automation: rules live on the ad account and run **inside Meta's
infrastructure** — once created they keep working with no agent involved. Use
them for standing guards (auto-pause on bad CPA, budget caps, alerts), not for
one-off actions you can do directly with the update tools.

## Tools

| Tool | Purpose |
| --- | --- |
| `meta_ads_adrule_create` | Create a rule (`ad_account_id` + `body`) |
| `meta_ads_adrule_list` | List rules on the account: `meta_ads_adrule_list(ad_account_id=..., fields="id,name,status,evaluation_spec,execution_spec,schedule_spec")` |
| `meta_ads_adrule_get` | Read one rule (`adrule_id`, `fields`) |
| `meta_ads_adrule_update` | Change a rule (e.g. `body={"status": "DISABLED"}`) |
| `meta_ads_adrule_delete` | Permanently remove a rule |
| `meta_ads_adrule_history_list` | Audit log: what rules changed/paused/notified, and when: `meta_ads_adrule_history_list(ad_account_id=..., fields="timestamp,evaluation_spec,execution_spec,results,exception_message")` |

## Rule anatomy

A rule = **evaluation_spec** (what to watch) + **execution_spec** (what to do)
+ optional **schedule_spec**. Two evaluation types:

- `TRIGGER` — evaluated in real time when metadata or Insights change (the
  `trigger` object is required inside `evaluation_spec`).
- `SCHEDULE` — evaluated on an interval (pair with `schedule_spec`).

`evaluation_spec.filters` select which objects the rule inspects — always
include an entity filter (e.g. `entity_type` or an id list) so the rule
doesn't scan the whole account.

Common `execution_spec.execution_type` values: `PAUSE`, `UNPAUSE`,
`CHANGE_BUDGET`, `CHANGE_BID`, `NOTIFICATION`, `REBALANCE_BUDGET`, `ROTATE`.
`status` on the rule itself: `ENABLED` / `DISABLED` (the create tool's schema
carries the full enum).

## Example — pause ad sets whose 3-day CPA exceeds $30

```python
meta_ads_adrule_create(
    ad_account_id="1122334455",
    body={
        "name": "Guard: pause ad sets with CPA > $30 (3d)",
        "status": "ENABLED",
        "evaluation_spec": {
            "evaluation_type": "SCHEDULE",
            "filters": [
                {"field": "entity_type", "value": "ADSET", "operator": "EQUAL"},
                {"field": "time_preset", "value": "LAST_3_DAYS", "operator": "EQUAL"},
                {"field": "cost_per", "value": 3000, "operator": "GREATER_THAN"}
            ]
        },
        "execution_spec": {
            "execution_type": "PAUSE",
            "execution_options": [
                {"field": "user_ids", "value": [], "operator": "EQUAL"}
            ]
        },
        "schedule_spec": {"schedule_type": "SEMI_HOURLY"}
    }
)
```

> Money fields inside rule filters are in **cents**, same as budgets
> ($30 = 3000). Verify filter field names against the account's metrics —
> `meta_ads_adrule_history_list` shows whether a rule is actually firing.

## Rules of thumb

- **Prefer a rule over polling**: if the user wants "pause X when Y happens",
  create a rule instead of a scheduled agent that polls insights.
- **Surface every rule you create** — name rules descriptively (prefix with the
  user's intent) and report the rule id; they are standing automations the
  user must be able to find and disable.
- **Check history before debugging delivery**: an ad set that "randomly
  paused" is often a rule firing — `meta_ads_adrule_history_list` answers it
  in one call.
- Disabling (`status: "DISABLED"`) is reversible; delete only on explicit
  request.
