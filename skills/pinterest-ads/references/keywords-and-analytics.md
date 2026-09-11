# Pinterest Ads: Keywords, Analytics & Updates

## Phase 7: Keywords

> **CRITICAL**: `match_type` is REQUIRED. Without it, the Pinterest API returns a 500 error.

```python
pinterest_ads_keywords_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    parent_id="<AD_GROUP_ID>",
    value="spring fashion trends",
    match_type="BROAD",
)
```

**`match_type` values:** `BROAD`, `PHRASE`, `EXACT`, `EXACT_NEGATIVE`, `PHRASE_NEGATIVE`.

- `BROAD` — ads show for related searches.
- `PHRASE` — ads show when search contains the phrase.
- `EXACT` — ads show only for exact match.
- `EXACT_NEGATIVE` / `PHRASE_NEGATIVE` — exclude these terms.

**`bid`** (optional): Bid in microcurrency for this keyword. Overrides ad group default bid.

## Phase 8: Analytics

```python
pinterest_ads_campaign_analytics_get(
    ad_account_id="<AD_ACCOUNT_ID>",
    campaign_ids=["<CAMPAIGN_ID>"],
    start_date="2026-02-01",
    end_date="2026-03-01",
    columns=["SPEND_IN_MICRO_DOLLAR", "TOTAL_IMPRESSION", "TOTAL_CLICKTHROUGH", "CPC_IN_MICRO_DOLLAR", "CTR", "CPM_IN_MICRO_DOLLAR"],
    granularity="DAY",
)
```

**`granularity` values:** `TOTAL`, `DAY`, `HOUR`, `WEEKLY`, `MONTHLY`.

**Common analytics columns:** `SPEND_IN_MICRO_DOLLAR`, `TOTAL_IMPRESSION`, `TOTAL_CLICKTHROUGH`, `CPC_IN_MICRO_DOLLAR`, `CPM_IN_MICRO_DOLLAR`, `CTR`, `ECTR`, `TOTAL_CONVERSIONS`, `TOTAL_CONVERSIONS_VALUE_IN_MICRO_DOLLAR`.

## Update Operations

`pinterest_ads_campaigns_update`, `pinterest_ads_ad_groups_update`, and `pinterest_ads_update` all follow the same shape — pass `ad_account_id`, the entity ID (`campaign_id` / `ad_group_id` / `ad_id`), and any fields you want to change. Statuses use `ACTIVE`, `PAUSED`, or `ARCHIVED` (cannot be unarchived).

```python
pinterest_ads_campaigns_update(
    ad_account_id="<AD_ACCOUNT_ID>",
    campaign_id="<CAMPAIGN_ID>",
    name="Updated Name",
    status="PAUSED",
    daily_spend_cap=75000000,
)
```
