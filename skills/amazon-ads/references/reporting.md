# Amazon Ads: Reporting, Bid Recommendations & Multi-Profile

## Reporting & Analysis

### Create Performance Report
```
amazon_ads_reports_create(
    profile_id=PROFILE_ID,
    report_type="spCampaigns",
    columns=["impressions", "clicks", "cost", "spend"],
    start_date="2026-02-01",
    end_date="2026-02-28",
    group_by=["campaign"],
    time_unit="SUMMARY"
)
```

### Check Report Status
```
amazon_ads_reports_status_get(profile_id=PROFILE_ID, report_id=REPORT_ID)
```

Reports are async. Status transitions: PENDING → PROCESSING → COMPLETED.

### Report Types
| Type | Description |
| --- | --- |
| `spCampaigns` | Campaign-level metrics. |
| `spAdGroups` | Ad group-level metrics. |
| `spAdvertisedProduct` | ASIN-level metrics. |
| `spTargeting` | Keyword/target metrics. |
| `spSearchTerm` | Search term report. |

### Report Configuration
- `group_by` is **required**: `campaign`, `adGroup`, or `campaignPlacement`.
- Valid columns include: `impressions`, `clicks`, `cost`, `spend`, `sales7d`, `purchases7d`, `unitsSoldClicks7d`, `clickThroughRate`, `costPerClick`.
- Columns like `campaignId` and `campaignName` are **not allowed** in the columns list.

### Key Metrics
| Metric | Formula |
| --- | --- |
| ACoS | ad spend / ad revenue × 100 |
| ROAS | ad revenue / ad spend |
| TACoS | ad spend / total revenue × 100 |
| CTR | clicks / impressions × 100 |
| CPC | cost / clicks |
| CVR | orders / clicks × 100 |

## Bid Recommendations

Get theme-based bid recommendations for an existing ad group:

```
amazon_ads_bid_recommendations_get(
    profile_id=PROFILE_ID,
    campaign_id=CAMPAIGN_ID,
    ad_group_id=AD_GROUP_ID,
    targeting_expressions=[
        {"type": "KEYWORD_BROAD_MATCH", "value": "wireless earbuds"},
        {"type": "KEYWORD_EXACT_MATCH", "value": "bluetooth headphones"},
        {"type": "CLOSE_MATCH"},
        {"type": "LOOSE_MATCH"}
    ]
)
```

Available targeting expression types:
- `CLOSE_MATCH`, `LOOSE_MATCH`, `SUBSTITUTES`, `COMPLEMENTS` (auto targeting).
- `KEYWORD_BROAD_MATCH`, `KEYWORD_EXACT_MATCH`, `KEYWORD_PHRASE_MATCH` (keyword targeting).

## Multi-Profile Management

Amazon Ads supports multiple profiles per integration:
- US (USD) — primary marketplace.
- Brazil (BRL) — regional expansion.
- Canada (CAD) — North America.
- Mexico (MXN) — regional expansion.

**Cross-Profile Strategy**:
- Create similar campaigns on high-performing profiles.
- Adjust bids by marketplace (currency and competition differ).
- Track unified ROI by aggregating per-profile reports in chat.
