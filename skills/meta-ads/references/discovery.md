# Meta Ads: Account Discovery & Research

Run this phase before any campaign creation. It establishes account context, verifies health, and gathers research needed for targeting and creative decisions.

---

## Step 1: Account selection

Call `meta_ads_ad_accounts_list` with `{"detail": "id_only"}`.

- **Multiple accounts returned**: Ask the user to select one before proceeding. Do not assume.
- **Single account returned**: Inform the user and proceed.

Capture the selected `account_id` (format: `act_XXXXXXXXX`). All subsequent tool calls require it.

---

## Step 2: Page discovery

Call `meta_ads_owned_pages_list` with `{"account_id": "<selected_act_id>", "detail": "id_only"}`.

> `account_id` is REQUIRED — never call this tool without it.

**Capture the returned `page_id` explicitly.** Pass it on every ad set. Do not rely on auto-resolution.

**If the call fails with "No business ID found for this ad account":**

First check if you've already run the health check (step 4). If so, the page_id is available in the health check response under `page_publish_access.values[].id` — use that directly, no extra API call needed.

If you haven't run the health check yet, or if it didn't return a page_id, use this fallback:

```python
meta_accounts_list(account_id="act_123456789")
```

This returns connected pages through an alternate lookup path. Capture `page_id` from the response and continue.

**If no pages are returned at all:**
1. Run `meta_ads_health_check`.
2. If "Page publish access" fails: the Page must be linked to this ad account's Business Manager in Meta Business Settings. This is a user-side fix. Surface the issue and stop.

---

## Step 3: Pixel discovery (for Sales and Leads campaigns)

If the user intends to track website conversions or leads, call `meta_ads_ad_pixels_list` with `{"account_id": "<act_id>"}`.

Capture the `pixel_id`. It goes in `promoted_object` on the ad set.

**If no pixels are found:** Inform the user. Pixel setup is required for conversion-based campaigns. The user must install and verify the pixel before the campaign can be created.

**If multiple pixels are returned:** Do not guess. Either:
- Ask the user: "I found [N] pixels ([list names]). Which one should I use for this campaign?"
- Or call `meta_ads_ad_pixels_get(pixel_id)` on candidates to check which ones are actively receiving the relevant events (e.g. Lead, Purchase) before selecting.

---

## Step 3b: Audience discovery & validation (when using custom/lookalike audiences)

If the campaign targets a custom or lookalike audience, call `meta_ads_custom_audiences_list` and/or `meta_ads_lookalike_audiences_list`.

> `meta_ads_lookalike_audiences_list` returns **all** audiences in the account, not just lookalikes. Filter by `subtype` / name yourself.

**Validate any audience before using it.** A discovered audience is not necessarily usable. Check before building the ad set:

- `operation_status.code` must be `200` (Normal). Code `433` means the audience is broken ("couldn't create, delete and retry").
- `delivery_status.code` must be `200` (ready). Code `300` means too small to deliver.
- `approximate_count` should be comfortably above ~1000 for reliable delivery.

If a selected audience fails validation, **do not silently substitute a different one.** Surface it to the user:
> "The lookalike audience you wanted is currently broken (status 433) / too small to deliver. Options: pick a different audience, create a new one, or proceed with [closest alternative]. How would you like to handle it?"

The same applies to **audience parameters that don't match the brief** — e.g. the user asks for a 14-day retargeting window but only a 90-day audience exists. Surface the mismatch and let the user choose; do not quietly use the closest match.

---

## Step 4: Health check (recommended)

Call `meta_ads_health_check` before a first campaign on any account.

It verifies: token permissions, ad account access, Page publish access, and pixel access.

Surface any non-PASS items to the user before continuing. Do not proceed with creation if critical items are failing.

---

## Step 5: Website research (mandatory for any campaign linking to a website)

**Never skip this phase for website-based campaigns.**

### a) Screenshot capture (required)

Call `firecrawl_screenshots_create` on the primary site URL and/or the specific landing page URL.

The screenshot is your visual grounding for creative direction — layout, hierarchy, tone, imagery style, hero content. Treat it as required input for image generation.

### b) Branding extract

Call `firecrawl_branding_extract` on the primary site URL.

This captures brand colors, fonts, tone of voice, and key messaging. Use it to ensure generated ad creatives match the brand.

### c) Strategic assessment

After scanning, identify:
- Primary conversion goal
- Main buyer persona
- Key differentiators and value proposition
- Best CTA for this objective — choose from: `LEARN_MORE`, `SHOP_NOW`, `SIGN_UP`, `DOWNLOAD`, `BOOK_NOW`, `GET_OFFER`, `CONTACT_US`, `GET_QUOTE`

Do **not** ask the user about target audiences for Advantage+ campaigns — Advantage+ uses broad targeting by default.

---

## Step 6: Budget confirmation

Confirm before building anything:

- Budget amount and currency (e.g., "$30/day USD")
- Daily or lifetime budget
- If lifetime: start date and end date

Convert to cents immediately when confirmed. Multiply by 100 — $30/day = 3000.

---

## Step 7: Goal clarification (if not already known)

If the campaign objective hasn't been stated, ask:

```
What is the primary goal for this campaign?

1. Drive website purchases or conversions → Sales (OUTCOME_SALES)
2. Generate leads or form submissions → Leads (OUTCOME_LEADS)
3. Send traffic to a website or page → Traffic (OUTCOME_TRAFFIC)
4. Build brand awareness or maximize reach → Awareness (OUTCOME_AWARENESS)
5. Drive engagement with content or the Page → Engagement (OUTCOME_ENGAGEMENT)
6. Promote a mobile app → App Promotion (OUTCOME_APP_PROMOTION)
```

The objective determines which campaign workflow to follow. Do not guess.

Once confirmed, proceed to the appropriate campaign file:
- Sales → [campaigns/sales.md](campaigns/sales.md)
- Leads → [campaigns/leads.md](campaigns/leads.md)
- Traffic → [campaigns/traffic.md](campaigns/traffic.md)
- Awareness/Engagement → [campaigns/awareness-engagement.md](campaigns/awareness-engagement.md)
- App Promotion → [campaigns/app-promotion.md](campaigns/app-promotion.md)
