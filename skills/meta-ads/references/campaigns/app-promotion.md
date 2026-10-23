# App Promotion Campaign Workflow (OUTCOME_APP_PROMOTION)

## When to use

Use for campaigns that drive mobile app installs, in-app events, or app re-engagement for a mobile application registered in Meta's App Dashboard.

## Before starting

Re-read [../constraints.md](../constraints.md). Most relevant:
- Budget in cents (×100)
- `promoted_object` required for OUTCOME_APP_PROMOTION — missing it causes a cryptic API error
- `targeting_automation` inside `targeting`
- Budget at campaign level for Advantage+
- `meta_ads_adset_create` takes `ad_account_id` (numeric, no `act_` prefix) + a `body` dict — all ad set fields inside `body`
- `meta_ads_ad_create` takes `ad_account_id` + a `body` dict — no separate top-level args
- Activation: section 3
- Ad status: section 4

---

## Required inputs

| Input | How to get it |
|---|---|
| Ad account ID | Discovery step 1 |
| Facebook Page ID | Discovery step 2 (`meta_ads_owned_pages_list`) |
| Mobile App ID | Ask the user — from Meta App Dashboard (not the app store ID) |
| App store URL | Ask the user — full Apple App Store or Google Play URL with https:// |
| Optimization goal | App installs (default) or specific in-app events |
| Budget amount + currency | Ask the user |
| Daily or lifetime | Ask; lifetime needs start + end dates |
| Ad creative (image_hash) | Upload via `meta_ads_ad_images_upload` |

`promoted_object` with both `application_id` **and** `object_store_url` is required. Missing either will fail at the API.

---

## Decision point: installs vs re-engagement

```
User wants app promotion
  ├── New installs (most common)
  │     optimization_goal: APP_INSTALLS
  │     call_to_action: DOWNLOAD
  │
  └── Re-engagement (existing users)
        optimization_goal: OFFSITE_CONVERSIONS with promoted_object.custom_event_type
        (or IN_APP_VALUE for value; confirm the event with the user)
```

Default to APP_INSTALLS unless re-engagement is specified.

---

## Step-by-step creation (default)

### Pre-build checklist

- [ ] App ID confirmed (from Meta App Dashboard — NOT the app store numeric ID)
- [ ] App store URL confirmed (full URL with https://) — this exact URL becomes both the ad set's `object_store_url` AND the creative's CTA `link`
- [ ] Budget confirmed and converted to cents
- [ ] Page ID captured explicitly from discovery
- [ ] Creative assets ready or will use app store screenshots
- [ ] Adding to an **existing** ad set? Call `meta_ads_adset_get(adset_id=..., fields="promoted_object")` first and copy `promoted_object.object_store_url` into the creative link verbatim

### 1. Create campaign

```python
meta_ads_campaign_create(
    ad_account_id="123456789",
    body={
        "name": "App Installs - [App Name] - [Date]",
        "objective": "OUTCOME_APP_PROMOTION",
        "status": "PAUSED",
        "daily_budget": 2000,              # $20/day in cents — Advantage+ only; omit for manual
        # iOS 14+ only (SKAdNetwork): the next three keys, campaign-level and immutable.
        # Omit them for Android. Meta refuses is_skadnetwork_attribution with smart_promotion_type SMART_APP_PROMOTION.
        "is_skadnetwork_attribution": True,
        "smart_promotion_type": "GUIDED_CREATION",
        "promoted_object": {
            "application_id": "<APP_ID>",
            "object_store_url": "https://apps.apple.com/app/example/id123456789"
        }
    }
)
```

→ Capture `campaign_id`.

### 2. Create ad set

> `meta_ads_adset_create` takes `ad_account_id` (numeric, no `act_` prefix) plus a `body` dict. Every ad set field goes inside `body`.

**Advantage+ (default):**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "US Broad - App Installs",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "APP_INSTALLS",
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
      "application_id": "<app_id>",
      "object_store_url": "https://apps.apple.com/app/example/id123456789"
    }
  }
}
```

> **CRITICAL**: `promoted_object` with both `application_id` AND `object_store_url` is required. Omitting either causes a cryptic API error.

> **CRITICAL**: `application_id` is the Meta App Dashboard ID, not the numeric App Store ID.

**Manual (only when user explicitly requests):**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "US 18-35 - App Installs",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "APP_INSTALLS",
    "billing_event": "IMPRESSIONS",
    "daily_budget": 2000,
    "targeting": {
      "geo_locations": {
        "countries": [
          "US"
        ]
      },
      "age_min": 18,
      "age_max": 35
    },
    "promoted_object": {
      "application_id": "<app_id>",
      "object_store_url": "https://apps.apple.com/app/example/id123456789"
    }
  }
}
```

→ Capture `adset_id`.

> **iOS 14+ targeting (SKAdNetwork).** To target "iOS 14 and above" set
> `targeting.user_os: ["iOS_ver_14.0_and_above"]` on the ad set **and** create the parent
> campaign with `is_skadnetwork_attribution: true`, `smart_promotion_type: "GUIDED_CREATION"` and
> `promoted_object: {"application_id": ..., "object_store_url": ...}` (**campaign-level** fields
> on `meta_ads_campaign_create`, not ad-set fields). Without it Meta silently clamps the
> target to `iOS_ver_14.0_to_14.4` and the ad set shows as **"Apple App Store (iOS 13.7 or
> earlier)"** in Ads Manager. The flag is **immutable after the campaign is created** — if
> you forgot it, delete the campaign and recreate it. Nothing checks this before the call:
> create the campaign with the iOS 14+ flags yourself. **Android is unaffected** — this is iOS-only (SKAdNetwork is Apple's
> framework).
>
> **user_os value format.** The ONLY valid values are `iOS_ver_<v>_and_above` /
> `Android_ver_<v>_and_above` (open-ended), `iOS_ver_<min>_to_<max>` (range), or bare
> `iOS` / `Android` (all versions). Do **not** use `iOS_14`, `iOS 14+`, or a
> `user_os_version` field — Meta rejects them with *"Invalid User_os Value"* / *"not a
> valid target spec field"*. Nothing normalizes a shorthand value: send the canonical `user_os` value.

### 3. Upload image

```python
meta_ads_ad_images_upload(account_id="act_123456789", image_url="<url>")
```

→ Capture the image hash (section 7 of [../constraints.md](../constraints.md)).

### 4. Create ad

> **CRITICAL**: `meta_ads_ad_create` takes `ad_account_id` plus a single `body` dict. No separate top-level args.

> **CRITICAL — the creative link MUST match the ad set's `object_store_url` exactly.** Meta rejects the ad with *"Object store URL does not match promoted object"* if the creative's CTA destination differs from the store URL on the ad set's `promoted_object`. **Never guess or hand-type the store URL.** If you did not just create the ad set yourself (e.g. you are adding creatives to an existing ad set), call `meta_ads_adset_get(adset_id=..., fields="promoted_object")` **first**, read `promoted_object.object_store_url`, and copy that exact value into:
> - `link_data.link`, and
> - `link_data.call_to_action.value.link`, which every app-install creative sets
>
> They must be character-for-character identical to the ad set's `object_store_url`.

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "App Install Ad - [Creative]",
    "adset_id": "<adset_id>",
    "status": "PAUSED",
    "creative": {
      "object_story_spec": {
        "page_id": "<page_id>",
        "link_data": {
          "link": "<EXACT object_store_url from the ad set's promoted_object>",
          "image_hash": "<image_hash>",
          "call_to_action": {
            "type": "DOWNLOAD",
            "value": {
              "link": "<the same object_store_url>"
            }
          },
          "message": "Download [App Name] and [key benefit].",
          "name": "Get the App"
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

## Common failure points

| Symptom | Cause | Fix |
|---|---|---|
| `Object store URL does not match promoted object` (code 100) | Creative CTA link ≠ ad set's `promoted_object.object_store_url` | Read `promoted_object.object_store_url` via `meta_ads_adset_get(adset_id=..., fields="promoted_object")` and copy it exactly into the creative's `link` (don't guess the URL) |
| Cryptic API error on ad set | Missing `promoted_object` | Add `application_id` + `object_store_url` |
| "App not found" error | Wrong `application_id` | Verify in Meta App Dashboard, not app store |
| `object_store_url` invalid | URL format wrong or missing https:// | Use full URL with https:// |
| Budget rejected | Passed dollars not cents | Multiply by 100 |
| Ad set error: unexpected argument | A misspelled field | See section 14 of [../constraints.md](../constraints.md) |
| Campaign ACTIVE but no installs | Used `meta_ads_campaign_update(campaign_id, body={"status": "ACTIVE"})` | See section 3 of [../constraints.md](../constraints.md) |
| Ad set shows "iOS 13.7 or earlier" / `user_os` reads `iOS_ver_14.0_to_14.4` | Parent **campaign** not created as iOS-14 SKAdNetwork, so Meta clamped the open-ended target | Recreate the campaign: in the `meta_ads_campaign_create` body set `is_skadnetwork_attribution: true`, `smart_promotion_type: "GUIDED_CREATION"` and `promoted_object: {"application_id": ..., "object_store_url": ...}` — campaign-level, immutable after creation |
