# Amazon Ads: Profile Discovery & Account Assessment

## Phase 1: Profile Discovery

Call `amazon_ads_profiles_list()` to list advertising profiles.

- Each profile corresponds to a marketplace (US, BR, CA, MX, UK, DE, JP, etc.).
- Profiles are either **seller** or **vendor** type.
- If multiple: ask the user which marketplace to focus on.
- If single: inform the user and proceed.
- Note the `profileId` — it's required for every subsequent API call.

**Health Check**: Call `amazon_ads_health_check()` to verify OAuth tokens, profile access, and billing status.

## Phase 2: Account Assessment

### Existing Campaign Audit
```
amazon_ads_campaigns_list(profile_id=PROFILE_ID)
```
Review active campaigns, budgets, and targeting types (auto vs manual).

### Product Research
- Get the ASINs the user wants to advertise (real ASINs only — never invent them).
- Ask about product category, price point, and margins.
- Calculate target ACoS: `(ad spend / ad revenue) × 100`.
- Understand the competitive landscape.

### Keyword Research
- Review search term reports from existing campaigns.
- Identify high-performing keywords.
- Plan match types: EXACT for proven terms, PHRASE for discovery, BROAD for expansion.
- Identify negative keywords to exclude.

### Bid Strategy
Ask about budget and goals:
- `LEGACY_FOR_SALES` (default): Amazon lowers bids when less likely to convert.
- `AUTO_FOR_SALES`: Dynamic bids, up and down.
- `MANUAL`: Full control over bid amounts.

### Confirm Criticals
- Daily budget.
- Target ACoS.
- ASINs to advertise.
- Target marketplace(s).
- Auto vs manual targeting preference.
