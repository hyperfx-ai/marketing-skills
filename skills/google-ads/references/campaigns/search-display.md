# Search & Display campaigns (granular build)

> **CRITICAL**: Present the full plan and get explicit user approval before the first mutate ([discovery.md](../discovery.md) must be complete and the summary approved). Create everything **PAUSED**, in dependency order. A generated body takes the full returned `resource_name`; a flat tool (`location_targets_add`, `keywords_create`) takes the bare id, the last part of that resource name. The tools validate bodies (writable fields, real enums, channel-type rules) and return corrective errors — fix and retry.

## Build order

1. **Budget** — `google_ads_campaign_budgets_create(customer_id, body={"name": "...", "amount_micros": 50000000})` ($50/day; micros!). Returns `customers/{cid}/campaignBudgets/{id}`.
2. **Campaign** — `google_ads_campaigns_create(customer_id, body={...})`:

```json
{
  "name": "Campaign Name",
  "advertising_channel_type": "SEARCH",
  "status": "PAUSED",
  "campaign_budget": "customers/1234567890/campaignBudgets/111",
  "target_spend": {},
  "contains_eu_political_advertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
  "network_settings": {"target_google_search": true, "target_search_network": true}
}
```

   Bidding is ONE scheme field on the campaign: `target_spend` (Maximize Clicks), `maximize_conversions`, `maximize_conversion_value`, `target_cpa`, `target_roas` or `manual_cpc`. Every campaign create body needs `contains_eu_political_advertising`. For Display set `"advertising_channel_type": "DISPLAY"`.
3. **Locations** — resolve names with `google_ads_locations_search(customer_id, query="...")`. Then call `google_ads_location_targets_add(customer_id, campaign_id="<numeric id>", location_id="1023191")` once for each location. Add `negative=True` to exclude a location.
4. **Ad group** — `google_ads_ad_groups_create(customer_id, body={"name": "Ad Group 1", "campaign": "customers/{cid}/campaigns/{id}", "status": "PAUSED"})`.
5. **Keywords** (Search) — `google_ads_keywords_create(customer_id, ad_group_id="<numeric id>", keyword_text="marketing software", match_type="PHRASE")`, one call for each keyword. For a negative, add `negative=True`.
6. **Ads** — `google_ads_ad_group_ads_create(customer_id, body={...})` with exactly ONE typed ad object:

```json
{
  "ad_group": "customers/1234567890/adGroups/222",
  "status": "PAUSED",
  "ad": {
    "final_urls": ["https://example.com"],
    "responsive_search_ad": {
      "headlines": [{"text": "Headline 1"}, {"text": "Headline 2"}, {"text": "Headline 3"}],
      "descriptions": [{"text": "Description 1"}, {"text": "Description 2"}]
    }
  }
}
```

   RSA minimums: 3–15 headlines (≤30 chars), 2–4 descriptions (≤90 chars).

## Display ads

Upload the three image asset types first with `google_ads_image_assets_upload` (prefer `file_id` from the workspace file manager), then create a `responsive_display_ad`:

```json
"ad": {
  "final_urls": ["https://example.com"],
  "responsive_display_ad": {
    "headlines": [{"text": "Headline 1"}],
    "long_headline": {"text": "Longer headline up to 90 characters"},
    "descriptions": [{"text": "Description 1"}],
    "business_name": "Business Name",
    "marketing_images": [{"asset": "customers/{cid}/assets/{landscape_id}"}],
    "square_marketing_images": [{"asset": "customers/{cid}/assets/{square_id}"}],
    "square_logo_images": [{"asset": "customers/{cid}/assets/{logo_id}"}]
  }
}
```

> **CRITICAL (Display)**: All three image asset types are REQUIRED:
> - marketing images — landscape 1.91:1 (e.g. 1200×628)
> - square marketing images — square 1:1 (e.g. 1200×1200)
> - logos — square 1:1 (or landscape 4:1)

## Extensions (sitelinks, callouts)

Create assets with `google_ads_assets_create` (`sitelink_asset` / `callout_asset` field on the body), then link with `google_ads_campaign_assets_link(customer_id, campaign_id, asset_id, field_type="SITELINK"|"CALLOUT")`.

## Verify, then activate

After building, confirm the tree by GAQL (campaign, ad groups, ads, keywords), present it to the user, then call `google_ads_campaigns_update(customer_id, campaign_id="<numeric id>", body={"status": "ENABLED"})` after explicit approval.

Re-check [constraints.md](../constraints.md) (bidding strategies, technical rules) at each creation step.
