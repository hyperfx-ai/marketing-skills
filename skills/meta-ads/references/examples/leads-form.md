# Example: Leads Campaign — Website Landing Page (B2B SaaS, Step-by-Step)

This example shows the full sequence: user request → clarification → written plan → step-by-step execution.

---

## User request

> "I want to run a Facebook lead gen campaign for my B2B SaaS. Budget is $50/day."

---

## Step 1: Clarification questions

Before touching any tools, ask:

```
Before I build this, a few questions:

1. Do you want users to fill out a form directly within Facebook/Instagram (native lead form),
   or drive them to a landing page on your website?
2. What's your website URL / landing page?
3. Do you have a Meta Pixel installed that's firing Lead events?
4. What geography should I target? (Default: United States)
5. How long should this run — ongoing daily budget, or a fixed period?
```

---

## Step 2: User answers

> "Landing page. URL is example.com/demo. Yes, pixel is installed tracking lead events. US only. Ongoing."

---

## Step 3: Written plan (shown before any tool calls)

State the plan explicitly before acting.

```
Here's my plan:

OBJECTIVE: OUTCOME_LEADS (website pixel path)
CAMPAIGN TYPE: Advantage+ (default)
BUDGET: $50/day = 5000 cents at campaign level
OPTIMIZATION GOAL: OFFSITE_CONVERSIONS, destination_type: WEBSITE
PROMOTED OBJECT: pixel_id + custom_event_type: LEAD
TARGETING: Broad US, Advantage+ audience automation
STATUS: PAUSED until you approve

Steps:
1. Select ad account and Page (connections_info(toolkit_id="meta_ads") in Hyper chat)
2. Get Page ID (meta_ads_owned_pages_list) when the context does not show it
3. Run health check (meta_ads_health_check)
4. Screenshot example.com/demo for creative reference (firecrawl_screenshots_create)
5. Extract branding (firecrawl_branding_extract)
6. Generate ad creative from screenshot
7. Upload image → get image_hash (meta_ads_ad_images_upload)
8. Create campaign → campaign_id (meta_ads_campaign_create)
9. Get Pixel ID → pixel_id (meta_ads_ad_pixels_list)
10. Create ad set → adset_id (meta_ads_adset_create)
11. Create ad → ad_id (meta_ads_ad_create)
12. Show ad previews — wait for your review
13. Activate only when you say to

Key constraints:
- $50/day = 5000 cents (not 50)
- promoted_object REQUIRED: pixel_id + LEAD event (website pixel path)
- targeting_automation inside targeting object
- Budget at campaign level (ad set has no budget)
- meta_ads_adset_create takes ad_account_id + body
- meta_ads_ad_create takes ad_account_id + body
- Will use meta_ads_campaigns_activate(), not meta_ads_campaign_update(campaign_id, body={"status": "ACTIVE"})
```

---

## Step 4: Execution

### Discovery

```python
connections_info(toolkit_id="meta_ads")
# → account: act_111222333, Page 632278516639981
# On MCP or the CLI: meta_ads_adaccount_list(fields="id,name,account_status,currency")

meta_ads_owned_pages_list({"account_id": "act_111222333", "detail": "id_only"})
# → page_id: 632278516639981  ← captured explicitly

meta_ads_health_check()
# → All checks PASS
```

### Research

```python
firecrawl_screenshots_create({"url": "https://example.com/demo"})
# → Screenshot: dark navy, "Book a Demo" hero CTA, B2B product screenshots

firecrawl_branding_extract({"url": "https://example.com"})
# → Colors: #0D1B2A (navy), #00C2FF (electric blue)
# → Font: Inter | Tone: professional, direct, B2B
```

### Creative

```python
meta_ads_ad_images_upload({"account_id": "act_111222333", "image_url": "<generated_image_url>"})
# → images[0].hash: xyz789abc012 (pass it as image_hash)
```

### Campaign creation (step-by-step)

```python
# Step 1: Campaign
meta_ads_campaign_create(
    ad_account_id="111222333",
    body={
        "name": "Leads - ExampleSaaS - TEST - 2026-06",
        "objective": "OUTCOME_LEADS",
        "status": "PAUSED",
        "daily_budget": 5000    # $50/day in cents
    }
)
# → campaign_id: 987654321

# Step 2: Pixel
meta_ads_ad_pixels_list(account_id="act_111222333")
# → pixel_id: 9876543210

# Step 3: Ad set
meta_ads_adset_create(
    ad_account_id="111222333",
    body={
        "name": "US Broad - Demo Requests - TEST",
        "campaign_id": "987654321",
        "optimization_goal": "OFFSITE_CONVERSIONS",
        "destination_type": "WEBSITE",
        "billing_event": "IMPRESSIONS",
        "targeting": {
            "geo_locations": {"countries": ["US"]},
            "targeting_automation": {"advantage_audience": 1}
        },
        "promoted_object": {
            "pixel_id": "9876543210",
            "custom_event_type": "LEAD"
        }
        # No daily_budget — campaign controls budget for Advantage+
    }
)
# → adset_id: 334455667

# Step 4: Ad
meta_ads_ad_create(
    ad_account_id="111222333",
    body={
        "name": "Demo Request - Image Ad - TEST",
        "adset_id": "334455667",
        "creative": {
            "object_story_spec": {
                "page_id": "632278516639981",
                "link_data": {
                    "link": "https://example.com/demo",
                    "image_hash": "xyz789abc012",
                    "call_to_action": {"type": "LEARN_MORE"},
                    "message": "See how ExampleSaaS helps B2B teams close deals faster.",
                    "name": "Book a Free Demo",
                    "description": "No commitment. 30-minute walkthrough."
                }
            }
        },
        "status": "PAUSED"
    }
)
# → ad_id: 556677889
```

### Preview and summary

```python
# creative_id: section 13 of ../constraints.md
meta_ads_ad_previews_get(creative_ids=["<creative_id>"])
# Summarize preview formats to user — never render iframe inline
```

```
Campaign created and paused. Here's what was built:

Campaign: "Leads - ExampleSaaS - TEST - 2026-06"
Status: PAUSED
Budget: $50/day
Objective: Leads (LEAD pixel event from example.com/demo)
Optimization: OFFSITE_CONVERSIONS on LEAD events
Targeting: United States, Advantage+ broad audience
Ad previews: [available in the dashboard]

When you're ready to go live, reply "activate".
```

### Activation (when user approves)

```python
# RIGHT
meta_ads_campaigns_activate(campaign_id="987654321")

# WRONG — do not use
# meta_ads_campaign_update(campaign_id="987654321", status="ACTIVE")
```

---

## What if no pixel is installed?

If `meta_ads_ad_pixels_list` returns nothing:

```
I couldn't find a Meta Pixel on your account. To track leads from your website,
you'll need a pixel installed and firing Lead events on the form confirmation.

Would you like to:
a) Set up a pixel first (I can walk you through it), or
b) Use a native Meta Lead Form instead (users fill the form within Facebook/Instagram)?
```

Do not proceed with a website-pixel OUTCOME_LEADS campaign if no pixel exists.
