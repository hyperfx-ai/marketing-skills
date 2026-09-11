# Pinterest Ads: Discovery & Account Assessment

## Phase 1: Account Discovery

Call `pinterest_ads_ad_accounts_list()` to list accessible accounts.

- If multiple: ask the user to select one.
- If single: inform the user and proceed.
- Note the `ad_account_id` — it's required for every subsequent tool call.

## Phase 2: Account Assessment

### Existing campaign audit

Run these in parallel to understand the account state:

```python
pinterest_ads_campaigns_list(ad_account_id="<AD_ACCOUNT_ID>")
pinterest_ads_ad_groups_list(ad_account_id="<AD_ACCOUNT_ID>")
pinterest_ads_list(ad_account_id="<AD_ACCOUNT_ID>")
pinterest_ads_audiences_list(ad_account_id="<AD_ACCOUNT_ID>")
pinterest_ads_conversion_tags_list(ad_account_id="<AD_ACCOUNT_ID>")
```

### Research & confirm

- Get the destination URL and creative assets (Pin IDs).
- Understand the campaign objective (awareness, consideration, conversions).
- Confirm daily / lifetime budget.
- Confirm target audience (geo, interests, demographics).
- If WEB_CONVERSION: ensure a conversion tag exists.
