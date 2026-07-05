# Example: Sales Campaign — Ecommerce (Advantage+, Step-by-Step)

This example shows the full sequence: user request → clarification → written plan → step-by-step execution.

---

## User request

> "I want to run Facebook ads for my online skincare store. I have a $30/day budget and want to drive purchases."

---

## Step 1: Clarification questions

Before touching any tools, ask:

```
Before I build this, a few quick details:

1. What's your website URL and main landing page for the ads?
2. Do you have a Meta Pixel installed and is it firing Purchase events?
3. What geography should I target? (Default: United States)
4. How long should this run — ongoing daily budget, or a fixed period?
5. Do you have existing product images or should I generate creatives from your website?
```

---

## Step 2: User answers

> "URL is skinfirst.com. Yes, pixel is installed and tracking purchases. US only. Ongoing. Generate from site."

---

## Step 3: Written plan (shown before any tool calls)

State the plan explicitly before acting. Do not start calling tools until this is visible.

```
Here's my plan:

OBJECTIVE: OUTCOME_SALES (website purchases via pixel)
CAMPAIGN TYPE: Advantage+ (default)
BUDGET: $30/day = 3000 cents at campaign level
OPTIMIZATION GOAL: OFFSITE_CONVERSIONS
PROMOTED OBJECT: pixel_id + custom_event_type: PURCHASE
TARGETING: Broad US, Advantage+ audience automation
STATUS: PAUSED until you approve

Steps:
1. Select ad account (meta_ads_ad_accounts_list)
2. Get Page ID (meta_ads_owned_pages_list)
3. Run health check (meta_ads_health_check)
4. Screenshot skinfirst.com for creative reference (firecrawl_screenshots_create)
5. Extract branding (firecrawl_branding_extract)
6. Generate ad creative from screenshot
7. Upload image → get image_hash (meta_ads_ad_images_upload)
8. Create campaign → campaign_id (meta_ads_campaigns_create)
9. Get Pixel ID → pixel_id (meta_ads_ad_pixels_list)
10. Create ad set → adset_id (meta_ads_ad_sets_create)
11. Create ad → ad_id (meta_ads_create)
12. Show ad previews — wait for your review
13. Activate only when you say to

Key constraints:
- $30/day = 3000 cents (not 30)
- promoted_object required: pixel_id + PURCHASE
- targeting_automation inside targeting object
- Budget at campaign level (ad set has no budget)
- create_ad_set uses mode + input_data
- create_ad uses single input_data dict
- Will use meta_ads_campaigns_activate(), not update(status="ACTIVE")
```

---

## Step 4: Execution

### Discovery

```python
meta_ads_ad_accounts_list({"detail": "id_only"})
# → account: act_111222333

meta_ads_owned_pages_list({"account_id": "act_111222333", "detail": "id_only"})
# → page_id: 632278516639981  ← captured explicitly

meta_ads_health_check({"account_id": "act_111222333"})
# → All checks PASS
```

### Research

```python
firecrawl_screenshots_create({"url": "https://skinfirst.com"})
# → Screenshot: clean minimal layout, soft pastel palette, hero product shot

firecrawl_branding_extract({"url": "https://skinfirst.com"})
# → Colors: #F5EDE4 (cream), #9B7D6E (warm brown)
# → Font: Playfair Display | Tone: elegant, natural
```

### Creative

```python
# Generate ad image using screenshot as visual reference
meta_ads_ad_images_upload({"account_id": "act_111222333", "image_url": "<generated_image_url>"})
# → image_hash: abc123def456
```

### Campaign creation (step-by-step)

```python
# Step 1: Campaign
meta_ads_campaigns_create(
    account_id="act_111222333",
    name="Sales - SkinFirst - TEST - 2026-06",
    objective="OUTCOME_SALES",
    status="PAUSED",
    daily_budget=3000    # $30/day in cents
)
# → campaign_id: 987654321

# Step 2: Pixel
meta_ads_ad_pixels_list(account_id="act_111222333")
# → pixel_id: 9876543210

# Step 3: Ad set
meta_ads_ad_sets_create(
    mode="advantage_plus",
    input_data={
        "account_id": "act_111222333",
        "name": "US Broad - Purchases - TEST",
        "campaign_id": "987654321",
        "optimization_goal": "OFFSITE_CONVERSIONS",
        "billing_event": "IMPRESSIONS",
        "targeting": {
            "geo_locations": {"countries": ["US"]},
            "targeting_automation": {"advantage_audience": 1}
        },
        "promoted_object": {
            "pixel_id": "9876543210",
            "custom_event_type": "PURCHASE"
        }
    }
)
# → adset_id: 223344556

# Step 4: Ad
meta_ads_create(
    input_data={
        "account_id": "act_111222333",
        "name": "SkinFirst - Shop Clean Beauty - TEST",
        "adset_id": "223344556",
        "creative": {
            "object_story_spec": {
                "page_id": "632278516639981",
                "link_data": {
                    "link": "https://skinfirst.com/shop",
                    "image_hash": "abc123def456",
                    "call_to_action": {"type": "SHOP_NOW"},
                    "message": "Your skin deserves better. Discover clean skincare that actually works.",
                    "name": "Shop SkinFirst",
                    "description": "Free shipping on orders over $40."
                }
            }
        }
        # No status field — ads default to PAUSED
    }
)
# → ad_id: 112233445
```

### Preview and summary

```python
# creative_id from ad creation response: response.creative.id
meta_ads_ad_previews_get(creative_ids=["<creative_id>"])
# Summarize preview formats to user — never render iframe inline
```

```
Campaign created and paused. Here's what was built:

Campaign: "Sales - SkinFirst - TEST - 2026-06"
Status: PAUSED
Budget: $30/day
Objective: Purchases (PURCHASE pixel event)
Optimization: OFFSITE_CONVERSIONS
Targeting: United States, Advantage+ broad audience
Ad previews: [available in the dashboard]

When you're ready to go live, reply "activate" and I'll launch it.
```

### Activation (when user approves)

```python
# RIGHT — activates campaign + ad sets + ads
meta_ads_campaigns_activate(campaign_id="987654321")

# WRONG — do not use this
# meta_ads_campaigns_update(campaign_id="987654321", status="ACTIVE")
```
