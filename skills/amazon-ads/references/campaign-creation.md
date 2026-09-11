# Amazon Ads: Campaign Structure & Creation

Read [discovery.md](discovery.md) first — product research and the approved pre-creation summary are prerequisites.

## Phase 3: Campaign Structure

### Recommended Structure

```
Campaign (targeting type: MANUAL or AUTO)
└── Ad Group (default bid)
    ├── Product Ads (ASINs)
    ├── Keywords (MANUAL campaigns only)
    └── Product Targets (MANUAL campaigns only, mutually exclusive with keywords)
```

### Structure Decision Tree

```
AUTO Campaign:
  → Single campaign
  → Single ad group (broad matching)
  → Add product ads (ASINs)
  → Campaign-level negative keywords
  → Let Amazon optimize

MANUAL Campaign:
  → Separate ad groups by targeting theme
  → Each ad group: keywords OR product targets (not both)
  → Specific bids per keyword/target
  → Campaign and ad-group level negatives
```

### Best Practices
- Separate auto and manual campaigns.
- Group related ASINs in the same ad group.
- Use EXACT match for high-intent keywords.
- Add negatives at campaign level for broad exclusions.
- Start with conservative bids and increase based on ACoS data.

## Phase 4: Pre-Creation Summary (Must Be Approved)

```
Campaign Strategy for [Product/Brand]

Profile: [profileId] ([marketplace])
Account Type: [seller/vendor]
ASINs: [list]
Target ACoS: [X]%
Daily Budget: $[X]
Targeting: [AUTO/MANUAL/both]
Bidding Strategy: [strategy]
Keywords: [count] across [match types]
Negatives: [count] terms excluded

Approve to proceed?
```

Wait for explicit approval.

## Phase 5: Campaign Creation

### 1. Create Campaign
```
amazon_ads_campaigns_create(
    profile_id=PROFILE_ID,
    name="SP - Manual - [Product]",
    targeting_type="MANUAL",
    daily_budget=25,
    start_date="2026-03-01",
    state="PAUSED",
    bidding_strategy="legacy_for_sales"
)
```
Returns: `campaignId`.

### 2. Create Ad Group
```
amazon_ads_ad_groups_create(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    name="[Product] - Exact Keywords",
    default_bid=0.75,
    state="PAUSED"
)
```
Returns: `adGroupId`.

### 3. Add Product Ads
```
amazon_ads_product_ads_create(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    asin="B0XXXXXXXXX",
    state="PAUSED"
)
```

### 4. Add Keywords (MANUAL campaigns only)
```
amazon_ads_keywords_create(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    keyword_text="wireless earbuds",
    match_type="EXACT",
    bid=0.85
)
```

### 5. Add Negative Keywords (Campaign Level)
```
amazon_ads_campaign_negative_keywords_create(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    keyword_text="cheap",
    match_type="NEGATIVE_PHRASE"
)
```

### 6. Add Negative Keywords (Ad Group Level)
```
amazon_ads_negative_keywords_create(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    keyword_text="refurbished",
    match_type="NEGATIVE_EXACT"
)
```

### 7. Product Targeting (alternative to keywords — separate ad group)
```
amazon_ads_product_targets_create(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    expression=[{"type": "ASIN_SAME_AS", "value": "B0COMPETITOR"}],
    bid=0.60,
    state="PAUSED"
)
```

Available expression types:
- `ASIN_SAME_AS`: target a specific ASIN.
- `ASIN_CATEGORY_SAME_AS`: target an entire category.
- `ASIN_BRAND_SAME_AS`: target a brand (requires numeric brand ID).

### 8. Negative Product Targets (Ad Group Level)
```
amazon_ads_negative_product_targets_create(
    profile_id=PROFILE_ID,
    ad_group_id=AD_GROUP_ID,
    campaign_id=CAMPAIGN_ID,
    expression=[{"type": "ASIN_SAME_AS", "value": "B0EXCLUDE"}],
    state="ENABLED"
)
```

Only `ASIN_SAME_AS` and `ASIN_BRAND_SAME_AS` are supported for negative targets.
