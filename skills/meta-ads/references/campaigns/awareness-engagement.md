# Awareness & Engagement Campaign Workflow

## When to use

**OUTCOME_AWARENESS**: Maximize brand reach and impressions. No user action required.

**OUTCOME_ENGAGEMENT**: Drive interactions — post likes, shares, comments, Page follows, or video views.

These are the simplest campaign types. No pixel required. No complex `promoted_object` setup.

## Before starting

Re-read [../constraints.md](../constraints.md). Most relevant:
- Budget in cents (×100)
- `targeting_automation` inside `targeting`
- Budget at campaign level for Advantage+
- `meta_ads_adset_create` takes `ad_account_id` (numeric, no `act_` prefix) + a `body` dict — all ad set fields inside `body`
- `meta_ads_ad_create` takes `ad_account_id` + a `body` dict — no separate top-level args
- Use `meta_ads_campaigns_activate()`, not `meta_ads_campaign_update(campaign_id, body={"status": "ACTIVE"})`
- Every ad starts `PAUSED`: the body of each `meta_ads_ad_create` carries `"status": "PAUSED"` (section 4)

---

## Required inputs

| Input | How to get it |
|---|---|
| Ad account ID | Discovery step 1 |
| Facebook Page ID | Discovery step 2 (`meta_ads_owned_pages_list`) |
| Goal: awareness or engagement? | Ask the user if not stated |
| Budget amount + currency | Ask the user |
| Daily or lifetime | Ask; lifetime needs start + end dates |
| Ad creative (image_hash) | Upload via `meta_ads_ad_images_upload` |

No pixel needed. `promoted_object` is optional for engagement.

---

## Optimization goals

| Objective | optimization_goal |
|---|---|
| OUTCOME_AWARENESS | `REACH` |
| OUTCOME_ENGAGEMENT | `POST_ENGAGEMENT` |

---

## Step-by-step creation (default)

### 1. Create campaign

**Awareness:**
```python
meta_ads_campaign_create(
    ad_account_id="123456789",
    body={
        "name": "Awareness - [Brand] - [Date]",
        "objective": "OUTCOME_AWARENESS",
        "status": "PAUSED",
        "daily_budget": 2000    # $20/day in cents — Advantage+ only; omit for manual
    }
)
```

**Engagement:**
```python
meta_ads_campaign_create(
    ad_account_id="123456789",
    body={
        "name": "Engagement - [Brand] - [Date]",
        "objective": "OUTCOME_ENGAGEMENT",
        "status": "PAUSED",
        "daily_budget": 2000    # $20/day in cents — Advantage+ only; omit for manual
    }
)
```

→ Capture `campaign_id`.

### 2. Create ad set

> `meta_ads_adset_create` takes `ad_account_id` (numeric, no `act_` prefix) plus a `body` dict. Every ad set field goes inside `body`.

**Advantage+ awareness:**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "US Broad - Brand Awareness",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "REACH",
    "billing_event": "IMPRESSIONS",
    "targeting": {
      "geo_locations": {
        "countries": [
          "US"
        ]
      },
      "targeting_automation": {
        "advantage_audience": 1
      }
    }
  }
}
```

**Advantage+ engagement:**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "US Broad - Page Engagement",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "POST_ENGAGEMENT",
    "billing_event": "IMPRESSIONS",
    "targeting": {
      "geo_locations": {
        "countries": [
          "US"
        ]
      },
      "targeting_automation": {
        "advantage_audience": 1
      }
    }
  }
}
```

→ Capture `adset_id`.

### 3. Upload image

```python
meta_ads_ad_images_upload(account_id="act_123456789", image_url="<url>")
```

→ Capture the image hash (section 7 of [../constraints.md](../constraints.md)).

### 4. Create ad

> **CRITICAL**: `meta_ads_ad_create` takes `ad_account_id` plus a single `body` dict. No separate top-level args.

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "Awareness Ad - [Creative]",
    "adset_id": "<adset_id>",
    "status": "PAUSED",
    "creative": {
      "object_story_spec": {
        "page_id": "<page_id>",
        "link_data": {
          "link": "https://example.com",
          "image_hash": "<image_hash>",
          "call_to_action": {
            "type": "LEARN_MORE"
          },
          "message": "<primary_text>",
          "name": "<headline>"
        }
      }
    }
  }
}
```

→ Capture `ad_id`.

### 5. Preview and activate

```python
# creative_id: section 13 of ../constraints.md
meta_ads_ad_previews_get(creative_ids=["<creative_id>"])
meta_ads_campaigns_activate(campaign_id="<campaign_id>")  # when user approves
```

---

## Manual path (only when user explicitly requests)

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "AU 18-35 Awareness",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "REACH",
    "billing_event": "IMPRESSIONS",
    "daily_budget": 2000,
    "targeting": {
      "geo_locations": {
        "countries": [
          "AU"
        ]
      },
      "age_min": 18,
      "age_max": 35
    }
  }
}
```

Budget at **ad set level** for manual. No `targeting_automation`.
