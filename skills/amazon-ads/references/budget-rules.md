# Amazon Ads: Budget Rules & Automation

## Phase 6: Budget Rules & Automation

### Schedule-Based Rules

Auto-increase budget on specific dates:

```
amazon_ads_budget_rules_create(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    rule_type="SCHEDULE",
    name="Holiday Boost",
    budget_increase_percent=50,
    start_date="20261201",
    end_date="20261225"
)
```

### Performance-Based Rules

Auto-increase budget when metrics are met:

```
amazon_ads_budget_rules_create(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    rule_type="PERFORMANCE",
    name="High ROAS Rule",
    budget_increase_percent=25,
    performance_metric="ROAS",
    comparison_operator="GREATER_THAN_OR_EQUAL_TO",
    threshold=5.0,
    start_date="20260301"
)
```

Performance metrics: `ACOS`, `CTR`, `CVR`, `ROAS`.

> **CRITICAL**: Budget rule dates use `YYYYMMDD` format (not `YYYY-MM-DD`).
