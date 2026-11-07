# A/B tests and lift studies

Meta stores an A/B test and a conversion lift study as one object, the ad
study. An A/B test (`SPLIT_TEST`) splits the audience across cells that
hold different ad sets or campaigns. A lift study (`LIFT`) holds people
back and measures the difference against an objective such as purchases.

## Tools

| Tool | Purpose |
| --- | --- |
| `meta_ads_ad_study_list` | Studies of a business (`business_id`) |
| `meta_ads_ad_account_ad_study_list` | Studies that touch an ad account, the Ads Manager view |
| `meta_ads_ad_study_get` / `_update` / `_delete` | One study (`ad_study_id`); update and delete ask for approval |
| `meta_ads_ad_study_create` | Create a study under a business (asks for approval) |
| `meta_ads_ad_study_cell_list` | The cells (groups) of a study |
| `meta_ads_ad_study_objective_list` | The objectives, where results live (`results`, `last_updated_results`) |

## Creating an A/B test

```python
meta_ads_ad_study_create(
    business_id="5550000000001",
    body={
        "name": "Creative A vs B",
        "type": "SPLIT_TEST",
        "start_time": 1803859200,       # Unix seconds
        "end_time": 1805068800,
        "cells": [
            {"name": "A", "treatment_percentage": 50, "adsets": ["120210000000456"]},
            {"name": "B", "treatment_percentage": 50, "adsets": ["120210000000457"]},
        ],
    },
)
```

The create tool checks Meta's rules before sending and names the broken
one: every cell has at least 10 percent and at least one ad set, campaign
or ad account; the percentages sum to at most 100; a lift study has at
least one objective and at most one primary objective.

Times are Unix seconds. `cells` and `objectives` are arrays of objects.

## Reading results

Results sit on the objectives: `meta_ads_ad_study_objective_list(ad_study_id=...)`
returns each objective with `results` and `last_updated_results`. Cells
come from `meta_ads_ad_study_cell_list`.

Not available through Hyper: the eligibility check before creation,
results broken down per cell, and creative tests (`SPLIT_TEST_V2`).
