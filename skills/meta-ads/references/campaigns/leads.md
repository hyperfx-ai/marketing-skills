# Leads Campaign Workflow (OUTCOME_LEADS)

## When to use

Use for campaigns optimized for lead generation: native Meta lead forms, website form submissions, or any event where a user provides contact information.

## Before starting

Re-read [../constraints.md](../constraints.md). Every rule there applies here. Most relevant:
- Budget in cents (×100)
- `promoted_object` required for OUTCOME_LEADS — missing it, or missing any required field within it, causes a validation error
- `targeting_automation` inside `targeting`
- Budget at campaign level for Advantage+
- `meta_ads_adset_create` takes `ad_account_id` (numeric, no `act_` prefix) + a `body` dict — all ad set fields inside `body`
- `meta_ads_ad_create` takes `ad_account_id` + a `body` dict — no separate top-level args
- Activation: section 3
- Ad status: section 4
- **"Bid amount required" errors MUST be surfaced to the user — do NOT change optimization_goal as a workaround**

---

## Required inputs

| Input | How to get it |
|---|---|
| Ad account ID | Discovery step 1 |
| Facebook Page ID | Discovery step 2 — see fallback note below |
| Lead capture method | Ask: native lead form OR website pixel? |
| Pixel ID (if website leads) | `meta_ads_ad_pixels_list` |
| Landing page URL (if website leads) | Ask the user |
| Budget amount + currency | Ask the user |
| Daily or lifetime | Ask; lifetime needs start + end dates |
| Ad creative (image_hash or creative_id) | Upload via `meta_ads_ad_images_upload`, or list existing via `meta_ads_creative_list` |

**Never proceed to campaign creation without all required inputs confirmed.**

---

## Decision point: lead form vs website pixel

```
User wants leads
  ├── Native Meta Lead Form
  │     Users fill form directly on Facebook/Instagram
  │     optimization_goal: LEAD_GENERATION, destination_type: ON_AD
  │     promoted_object: {"page_id": "<page_id>"}
  │
  └── Website pixel (landing page)
        Users click through to your website and submit a form
        optimization_goal: OFFSITE_CONVERSIONS, destination_type: WEBSITE
        promoted_object: {
          "pixel_id": "<pixel_id>",
          "custom_event_type": "LEAD"
        }
```

If the user hasn't specified, ask:
> "Do you want users to fill out a form directly within Facebook/Instagram, or drive them to a landing page on your website?"

---

## Step-by-step creation (default)

### Pre-build checklist

- [ ] Lead capture method confirmed (form or website)
- [ ] Budget confirmed and converted to cents
- [ ] Page ID captured — see note below if `meta_ads_owned_pages_list` fails
- [ ] Pixel ID captured (if website leads)
- [ ] Destination URL confirmed (if website leads)
- [ ] Creative ready: image_hash from upload, or existing creative_id confirmed with correct destination URL
- [ ] Health check run: `meta_ads_health_check` — **required before first campaign on any account**

### 1. Run health check

```python
meta_ads_health_check()
```

Surface any non-PASS items before continuing. A failing pixel health check means the website path (`OFFSITE_CONVERSIONS` on `LEAD` events) cannot optimize yet.

### 2. Create campaign

```python
meta_ads_campaign_create(
    ad_account_id="123456789",
    body={
        "name": "Leads - [Business] - [Date]",
        "objective": "OUTCOME_LEADS",
        "status": "PAUSED",
        "daily_budget": 2000    # $20/day in cents — Advantage+ only; omit for manual
    }
)
```

→ Capture `campaign_id` from the response.

### 3. Look up pixel ID (website leads only)

```python
meta_ads_ad_pixels_list(account_id="act_123456789")
```

→ Capture `pixel_id`. Required for `promoted_object`.

Skip if using the native lead form path — `promoted_object` uses only `page_id` there.

### 4. Create ad set

> `meta_ads_adset_create` takes `ad_account_id` (numeric, no `act_` prefix) plus a `body` dict. Every ad set field goes inside `body`.

> **Bid strategy warning**: If the account has a non-default bid strategy (e.g. LOWEST_COST_WITH_BID_CAP), ad set creation will fail with "Bid Amount Required." If you see this error, **stop immediately and surface it to the user** — do NOT add `bid_amount` or change `optimization_goal` as workarounds. See constraints.md section 14.

**Advantage+ — website pixel path:**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "US Broad - Demo Requests",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "OFFSITE_CONVERSIONS",
    "destination_type": "WEBSITE",
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
      "custom_event_type": "LEAD"
    }
  }
}
```

> **CRITICAL**: Website leads: `promoted_object` = `{"pixel_id": ..., "custom_event_type": "LEAD"}`. Native form: `promoted_object` = `{"page_id": ...}`. Meta, not a local check, refuses a missing field.

**Advantage+ — native lead form path:**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "US Broad - Lead Form",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "LEAD_GENERATION",
    "destination_type": "ON_AD",
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
      "page_id": "<page_id>"
    }
  }
}
```

> **CRITICAL**: `targeting_automation` is inside `targeting`, not at the ad set top level.

> **CRITICAL**: No `daily_budget` on the ad set for Advantage+ — campaign controls budget.

**Manual (only when user explicitly requests):**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "UK Decision Makers 30-55",
    "campaign_id": "<campaign_id>",
    "optimization_goal": "OFFSITE_CONVERSIONS",
    "destination_type": "WEBSITE",
    "billing_event": "IMPRESSIONS",
    "daily_budget": 3000,
    "targeting": {
      "geo_locations": {
        "countries": [
          "GB"
        ]
      },
      "age_min": 30,
      "age_max": 55
    },
    "promoted_object": {
      "pixel_id": "<pixel_id>",
      "custom_event_type": "LEAD"
    }
  }
}
```

→ Capture `adset_id` from the response.

#### If the optimization goal is rejected (error 2490408)

See section 14 of [../constraints.md](../constraints.md).

1. Read `meta_ads_campaign_get(campaign_id=..., fields="objective,bid_strategy")`.
2. Fix the goal and the destination of the ad set for the lead capture method the user chose.
3. **Do not substitute `LINK_CLICKS` or change the objective to `OUTCOME_TRAFFIC`** without the user. That silently creates a traffic campaign, not a leads campaign.

### 5. (Native lead form path only) List lead forms

If using a native lead form, you need a `lead_gen_form_id` from the page:

```python
meta_ads_lead_forms_list(page_id="<page_id>")
```

> **Warning**: This tool requires a **Page Access Token** and will fail with error 190 ("This method must be called with a Page Access Token") when using a User Access Token. If this happens:
> - Ask the user to supply the form ID manually from their Facebook Page → Publishing Tools → Forms Library
> - With no form id, stop and ask the user: a native lead ad needs `lead_gen_form_id`
> - Do not proceed silently without informing the user of this limitation

### 5. Upload image or prepare creative

```python
meta_ads_ad_images_upload(
    account_id="act_123456789",
    image_url="<public_image_url>"    # or file_id if from Hyper file storage
)
```

→ Capture the image hash (section 7 of [../constraints.md](../constraints.md)).

#### Creating a creative from scratch with `meta_ads_creative_create`

Use this when you need full control over the creative spec (e.g., native lead form ads). `name` is required inside `body`. A native lead form creative also sets `call_to_action: {"type": "SIGN_UP", "value": {"lead_gen_form_id": "<id>"}}`.

```python
meta_ads_creative_create(
    ad_account_id="123456789",
    body={
        "name": "Creative Name",        # REQUIRED — not optional
        "object_story_spec": {
            "page_id": "<page_id>", # REQUIRED at top level — never inside link_data
            "link_data": {
                "message": "<primary ad copy>",
                "link": "<destination_url>",
                "description": "<secondary copy or headline>",
                "picture": "<image_url>",
                "call_to_action": {"type": "SIGN_UP", "value": {"lead_gen_form_id": "<lead_gen_form_id>"}}
            }
        }
    }
)
```

**Valid `link_data` fields:**

| Field | Purpose | Notes |
|---|---|---|
| `message` | Primary ad copy | Required |
| `link` | Destination URL | Required |
| `description` | Secondary copy / headline text | Use this for headline-style text |
| `picture` | Image URL | Use image_hash instead if available |
| `call_to_action` | CTA button | `{"type": "SIGN_UP"}` or similar |
| `caption` | Display URL shown under ad | **Must be a URL** (e.g. `"hyperfx.ai"`), NOT copy text |

**Fields that do NOT work in `link_data`:**
- `headline` — not a valid field; causes "unsupported field" API error. Use `description` instead.
- `page_id` — must be at the **top level** of `object_story_spec`, not inside `link_data`.

→ Capture `creative_id` from the response.

If the user has provided or selected an **existing creative** (`creative_id`), skip the upload — but verify the destination URL first.

Check the destination first (section 15 of [../constraints.md](../constraints.md)):

```python
meta_ads_creative_get(creative_id="33892633203717215", fields="link_url,object_story_spec,url_tags")
# Check the returned link_url matches the user's intended landing page
```

If the destination doesn't match, tell the user and either select a different creative or create a new inline one.

**Selecting among multiple existing creatives:** When `meta_ads_creative_list` returns several options, choose based on:
1. Body copy alignment with campaign goal (lead-focused language > viral/social tone)
2. Headline relevance to the offer or CTA
3. Destination URL (section 15 of [../constraints.md](../constraints.md))

If you're unsure, show the user the top 2–3 options (name + body copy) and let them choose.

### 6. Create ad

> **CRITICAL**: `meta_ads_ad_create` takes `ad_account_id` plus a single `body` dict. No separate top-level args.

**With new inline creative (image_hash):**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "Lead Ad - [Creative Name]",
    "adset_id": "<adset_id>",
    "status": "PAUSED",
    "creative": {
      "object_story_spec": {
        "page_id": "<page_id>",
        "link_data": {
          "link": "https://example.com/contact",
          "image_hash": "<image_hash>",
          "call_to_action": {
            "type": "LEARN_MORE"
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

**With existing creative (creative_id):**

```json
{
  "ad_account_id": "123456789",
  "body": {
    "name": "Lead Ad - [Creative Name]",
    "adset_id": "<adset_id>",
    "status": "PAUSED",
    "creative": {
      "creative_id": "<creative_id>"
    }
  }
}
```

→ Capture `ad_id` from the response.

### 7. Preview and activate

```python
# creative_id: section 13 of ../constraints.md
# ad_id is NOT a valid parameter — creative_ids (list) is always required
meta_ads_ad_previews_get(creative_ids=["<creative_id>"])
```

Summarize preview formats to user — never render iframe inline.
Wait for explicit user approval before activating.

```python
meta_ads_campaigns_activate(campaign_id="<campaign_id>")
# Activates campaign + ad sets + ads together
# NOT: meta_ads_campaign_update(status="ACTIVE") — that leaves ad sets PAUSED
```

---

## Page ID fallback

`meta_ads_owned_pages_list` can fail with "No business ID found for this ad account" when the account is not connected to a Business Manager with a recognized business ID.

**If this happens**, call `meta_accounts_list` as a fallback:

```python
meta_accounts_list()
```

[../discovery.md](../discovery.md) says what it returns. Capture `page_id` from the response.

---

## Common failure points

| Symptom | Cause | Fix |
|---|---|---|
| "No business ID found" from `meta_ads_owned_pages_list` | Account not linked to a Business Manager | Use `meta_accounts_list` as fallback |
| "Bid amount required" | Account-level bid strategy requires explicit bid | **Stop. Surface to user. Do NOT add bid_amount or change optimization_goal.** |
| "Performance goal isn't available" (subcode 2490408) | The goal does not fit the objective or the destination | See section 14 of [../constraints.md](../constraints.md). Do NOT substitute LINK_CLICKS. |
| Cryptic API error on ad set | Missing `promoted_object` entirely | Add promoted_object with all required fields |
| Budget at wrong level | Set budget on ad set for Advantage+ | Move to campaign level; remove from ad set |
| Nothing serves after activation | Used `meta_ads_campaign_update(campaign_id, body={"status": "ACTIVE"})` | See section 3 of [../constraints.md](../constraints.md) |
| Creative destination URL wrong | Existing creative linked to different URL | Verify creative destination before attaching |

---

## Full worked example

See [../examples/leads-form.md](../examples/leads-form.md).
