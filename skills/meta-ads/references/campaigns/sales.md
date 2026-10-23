# Sales Campaign Workflow (OUTCOME_SALES)

## When to use

Use for campaigns optimized for website purchases, checkout completions, or any offsite conversion event tracked via Meta Pixel.

## Before starting

Re-read [../constraints.md](../constraints.md). Every rule there applies here. Most relevant:
- Budget in cents (×100)
- `promoted_object` required for OUTCOME_SALES
- `targeting_automation` inside `targeting`
- Budget at campaign level for Advantage+
- `meta_ads_adset_create` takes `ad_account_id` (numeric, no `act_` prefix) + a `body` dict — all ad set fields inside `body`
- `meta_ads_ad_create` takes `ad_account_id` + a `body` dict — no separate top-level args
- Use `meta_ads_campaigns_activate()`, not `meta_ads_campaign_update(campaign_id, body={"status": "ACTIVE"})`

---

## Required inputs

| Input | How to get it |
|---|---|
| Ad account ID | Discovery step 1 |
| Facebook Page ID | Discovery step 2 (`meta_ads_owned_pages_list`) |
| Meta Pixel ID | `meta_ads_ad_pixels_list` — step 2 of creation below |
| Conversion event type | Ask user — default is `PURCHASE` |
| Budget amount + currency | Ask the user |
| Daily or lifetime | Ask; lifetime needs start + end dates |
| Destination URL | Ask the user |
| Ad creative (image_hash) | Upload via `meta_ads_ad_images_upload` |

---

## Decision point: conversion type

```
User wants sales
  ├── Website purchases (most common)
  │     optimization_goal: OFFSITE_CONVERSIONS
  │     promoted_object: {pixel_id, custom_event_type: "PURCHASE"}
  ├── Custom conversion event (add to cart, checkout, etc.)
  │     optimization_goal: OFFSITE_CONVERSIONS
  │     promoted_object: {pixel_id, custom_event_type: "<EVENT>"}
  └── Catalog / dynamic product ads
        promoted_object: {pixel_id, product_catalog_id}  ← confirm with user first
```

Default to PURCHASE unless the user specifies otherwise.

---

## Step-by-step creation (default)

Use this for most campaigns. Each step is visible, failures are easy to diagnose and retry.

### Pre-build checklist

- [ ] Budget confirmed and converted to cents
- [ ] Page ID captured explicitly from discovery
- [ ] Destination URL confirmed
- [ ] Creative assets ready or will generate from site

### 1. Create campaign

```python
meta_ads_campaign_create(
    ad_account_id="123456789",
    body={
        "name": "Sales - [Business] - [Date]",
        "objective": "OUTCOME_SALES",
        "status": "PAUSED",
        "daily_budget": 2000    # $20/day in cents — Advantage+ only; omit for manual
    }
)
```

→ Capture `campaign_id` from the response.

### 2. Look up pixel ID

```python
meta_ads_ad_pixels_list(account_id="act_123456789")
```

→ Capture `pixel_id`. Required for `promoted_object`.

### 3. Create ad set

> `meta_ads_adset_create` takes `ad_account_id` (numeric, no `act_` prefix) plus a `body` dict. Every ad set field goes inside `body`.

**Advantage+ (default):**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "US Broad - Purchases",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "OFFSITE_CONVERSIONS",
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
    },
    "promoted_object": {
      "pixel_id": "<pixel_id>",
      "custom_event_type": "PURCHASE"
    }
  }
}
```

> **CRITICAL**: `promoted_object` is required for OUTCOME_SALES. Missing it causes a cryptic API error.

> **CRITICAL**: `targeting_automation` is inside `targeting`, not at the ad set top level.

> **CRITICAL**: No `daily_budget` on the ad set for Advantage+ — campaign controls budget.

**Manual (only when user explicitly requests):**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "US Women 25-44",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "OFFSITE_CONVERSIONS",
    "billing_event": "IMPRESSIONS",
    "daily_budget": 2000,
    "targeting": {
      "geo_locations": {
        "countries": [
          "US"
        ]
      },
      "age_min": 25,
      "age_max": 44,
      "genders": [
        2
      ]
    },
    "promoted_object": {
      "pixel_id": "<pixel_id>",
      "custom_event_type": "PURCHASE"
    }
  }
}
```

→ Capture `adset_id` from the response.

### 4. Upload image

```python
meta_ads_ad_images_upload(
    account_id="act_123456789",
    image_url="<public_image_url>"    # or file_id if from Hyper file storage
)
```

→ Capture `images[0].hash` and pass it as `image_hash`.

### 5. Create ad

> **CRITICAL**: `meta_ads_ad_create` takes `ad_account_id` plus a single `body` dict containing all ad fields. Do not pass `name` or `adset_id` as separate top-level arguments and do not pass `body` as a JSON string.

```
❌ WRONG: meta_ads_ad_create(account_id="act_...", adset_id="123", name="My Ad")
❌ WRONG: meta_ads_ad_create(ad_account_id="...", body='{"adset_id": "123"}')  # string not dict
✅ RIGHT:  meta_ads_ad_create(ad_account_id="111222333", body={"adset_id": "123", ...})
```

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "Sales Ad - [Creative Name]",
    "adset_id": "<adset_id>",
    "creative": {
      "object_story_spec": {
        "page_id": "<page_id>",
        "link_data": {
          "link": "https://example.com/shop",
          "image_hash": "<image_hash>",
          "call_to_action": {
            "type": "SHOP_NOW"
          },
          "message": "<primary_text>",
          "name": "<headline>",
          "description": "<description>"
        }
      }
    }
  }
}
```

> Pass `"status": "PAUSED"` in the body of every `meta_ads_ad_create`. Never pass ACTIVE.

→ Capture `ad_id` from the response.

### 6. Preview and activate

```python
# creative_id: meta_ads_ad_get(ad_id=..., fields="creative") (creative.id), or the id that meta_ads_creative_create returned
meta_ads_ad_previews_get(creative_ids=["<creative_id>"])
# Summarize formats to user — never render iframe inline
# Wait for explicit user approval

meta_ads_campaigns_activate(campaign_id="<campaign_id>")
# Activates campaign + ad sets + ads together
# NOT: meta_ads_campaign_update(status="ACTIVE") — that leaves ad sets PAUSED
```

---

## Other creative formats (step 5 variations)

The single-image `object_story_spec` above is the most common. `meta_ads_ad_create` also supports a carousel — just change the `creative` block. A dynamic creative takes two calls (below).

**Carousel** (2–10 cards) — use `child_attachments` inside `link_data`:

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "Sales Carousel Ad",
    "adset_id": "<adset_id>",
    "creative": {
      "object_story_spec": {
        "page_id": "<page_id>",
        "link_data": {
          "link": "https://example.com/shop",
          "message": "Browse our collection",
          "child_attachments": [
            {
              "link": "https://example.com/p1",
              "name": "Product 1",
              "description": "Desc 1",
              "image_hash": "<hash1>"
            },
            {
              "link": "https://example.com/p2",
              "name": "Product 2",
              "description": "Desc 2",
              "image_hash": "<hash2>"
            }
          ],
          "multi_share_optimized": true
        }
      }
    }
  }
}
```

**Dynamic creative** (Meta auto-optimizes combinations) — create it with `meta_ads_creative_create` (`asset_feed_spec` + `object_story_spec.page_id`), then pass `creative: {"creative_id": ...}` to `meta_ads_ad_create`:

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "Sales Dynamic Creative",
    "object_story_spec": {
      "page_id": "<page_id>"
    },
    "asset_feed_spec": {
      "images": [
        {
          "hash": "<hash1>"
        },
        {
          "hash": "<hash2>"
        }
      ],
      "titles": [
        {
          "text": "Headline A"
        },
        {
          "text": "Headline B"
        }
      ],
      "bodies": [
        {
          "text": "Copy option 1"
        },
        {
          "text": "Copy option 2"
        }
      ],
      "descriptions": [
        {
          "text": "Free shipping over $40"
        }
      ],
      "link_urls": [
        {
          "website_url": "https://example.com/shop"
        }
      ],
      "call_to_action_types": [
        "SHOP_NOW"
      ],
      "ad_formats": [
        "SINGLE_IMAGE"
      ]
    }
  }
}
```

→ Capture `creative_id`, then:

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "Sales Dynamic Ad",
    "adset_id": "<adset_id>",
    "creative": {"creative_id": "<creative_id>"},
    "status": "PAUSED"
  }
}
```

> Dynamic creative requirements:
> - `ad_formats` is **required** — use `["SINGLE_IMAGE"]` (or `["SINGLE_VIDEO"]` for video). Omitting it makes Meta default to SINGLE_IMAGE and reject a feed that carries video.
> - Keep a minimal `object_story_spec` with just `page_id` alongside `asset_feed_spec` (the page_id comes from there).
> - The ad set must be created with `is_dynamic_creative: true` — pass it to `meta_ads_adset_create`.
>
> For non-dynamic ads, `creative` uses a single `object_story_spec` (or `creative_id` to reuse an existing creative).

---

## Common failure points

| Symptom | Cause | Fix |
|---|---|---|
| Cryptic API error on ad set creation | Missing `promoted_object` | Add `pixel_id` + `custom_event_type` to ad set |
| Budget rejected | Passed dollars not cents | Multiply by 100 |
| Ad set error: unexpected argument | A misspelled field | A body property sent at the top level moves into `body` by itself. A misspelled property is refused, because the body schema allows no extra keys: use a name from the valid list in the message |
| Ad creation error | Separate top-level args used | Use `ad_account_id` + `body` |
| Campaign ACTIVE but nothing serves | Used `meta_ads_campaign_update(campaign_id, body={"status": "ACTIVE"})` | Use `meta_ads_campaigns_activate()` |
| "Bid amount required" | Optimization goal requires explicit bid | Do NOT change goal — ask user |
| `targeting_automation` error | Placed at ad set top level | Move inside `targeting` object |

---

## Full worked example

See [../examples/sales-ecommerce.md](../examples/sales-ecommerce.md).
