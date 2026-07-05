# Meta Ads: Blueprint Creation (Preferred Path)

Use the blueprint system whenever possible for new campaigns. It validates locally, fills smart defaults (optimization goal, bid strategy, page/pixel IDs), and rolls back on failure.

Manual step-by-step creation is the fallback when the blueprint system is insufficient (complex creative overrides, replication workflows, or per-step debugging). See the objective files under `reference/campaigns/`.

---

## Workflow: Preview → Confirm → Create

1. Build the blueprint JSON from discovery research ([discovery.md](discovery.md)).
2. Call `meta_ads_blueprints_preview(blueprint={...})` to validate and show the user.
3. Get explicit user approval (skip when running a scheduled task with activation already specified).
4. Call `meta_ads_campaign_blueprints_create(blueprint={...})`.

---

## Blueprint structure

```json
{
  "account_id": "act_1234567890",
  "name": "Campaign Name",
  "objective": "OUTCOME_SALES",
  "campaign_type": "advantage_plus",
  "daily_budget": 2000,
  "status": "PAUSED",
  "url_tags": "utm_source=meta&utm_medium=paid",
  "ad_sets": [
    {
      "name": "US Broad Audience",
      "targeting": {
        "geo_locations": {"countries": ["US"]},
        "targeting_automation": {"advantage_audience": 1}
      },
      "pixel_id": null,
      "page_id": null,
      "custom_event_type": "PURCHASE",
      "ads": [
        {
          "name": "Single Image Ad",
          "link": "https://example.com",
          "primary_text": "Your ad copy here",
          "headline": "Headline here",
          "description": "Description here",
          "image_hash": "abc123",
          "call_to_action": "SHOP_NOW"
        }
      ]
    }
  ]
}
```

All budgets in **cents**. $20.00 = 2000.

---

## Blueprint features

| Feature | Details |
| --- | --- |
| Smart defaults | Optimization goal, billing event, destination type auto-filled from objective. |
| Auto-resolution | `page_id`, `pixel_id`, `instagram_user_id` auto-resolved when only one exists. |
| Objective validation | Per-objective rules enforce required fields, allowed values, promoted objects. |
| Budget placement | CBO (campaign level) vs ABO (ad set level) auto-detected. |
| Cleanup on failure | Reports `created`, `failed`, and `remaining` for recovery. |

---

## Creative formats in blueprints

**Single image/video** — standard `link`, `primary_text`, `headline`, `image_hash`, `call_to_action`.

**Carousel** (2–10 cards) — use `carousel_cards` array with per-card `image_hash`, `headline`, `link`.

**Dynamic creative** — use `text_variations` with arrays for `primary_texts`, `headlines`, `descriptions`, plus `image_hash`.

---

## Advantage+ vs manual in blueprints

- **Advantage+**: `campaign_type: "advantage_plus"`, budget at campaign level, broad targeting with `targeting_automation` inside `targeting`.
- **Manual**: `campaign_type: "manual"`, budget at ad set level, detailed targeting allowed.

---

## Creative asset preparation

Before building the blueprint:

1. Capture a website screenshot: `firecrawl_screenshots_create` on the landing page URL.
2. Generate an ad image using the screenshot as visual reference (see `ad-creative-generation` skill).
3. Upload: `meta_ads_ad_images_upload(account_id="<account_id>", image_url="<url>")` → `image_hash`.
4. Use `image_hash` in blueprint ad objects.

---

## Previews after blueprint creation

1. For each ad ID returned, fetch the creative ID: `meta_ads_get(ad_id="<ad_id>")` → `creative.id`.
2. Call `meta_ads_ad_previews_get(creative_ids=["<creative_id>"])`.
3. Summarize which preview formats succeeded/failed — never paste iframe/html snippets in chat.
4. Activate only after user approval: `meta_ads_campaigns_activate(campaign_id="<id>")` — **not** `meta_ads_campaigns_update(status="ACTIVE")`.
