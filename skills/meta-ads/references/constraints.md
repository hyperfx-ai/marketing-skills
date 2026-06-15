# Meta Ads: Critical Constraints

Read this before any campaign creation step. These rules are non-negotiable and apply to every workflow.

---

## 1. Budgets: always in cents

All budget and bid values are in **cents** (hundredths of the currency unit).

| Dollar amount | Correct cents value |
|---|---|
| $5.00/day | 500 |
| $20.00/day | 2000 |
| $50.00/day | 5000 |
| $100.00/day | 10000 |
| $5.50/day | 550 |

```
# WRONG
"daily_budget": 20

# RIGHT
"daily_budget": 2000   # = $20.00/day
```

Applies to: `daily_budget`, `lifetime_budget`, `bid_amount`, and any other budget field.

**Wrong field names that will cause Pydantic errors:**
- `daily_budget_cents` → use `daily_budget`
- `budget` → use `daily_budget` or `lifetime_budget`

---

## 2. Budget placement: campaign vs ad set

| Campaign type | Budget lives at | Ad set budget |
|---|---|---|
| Advantage+ | **Campaign level** | Must be `null` / omitted |
| Manual | **Ad set level** | Required here |

Never set budget at both levels simultaneously.

If you have multiple ad sets under one Advantage+ campaign, the campaign `daily_budget` is shared across all of them — Meta distributes spend automatically based on performance. Each ad set has no budget field; only the campaign does.

### CBO lock: setting campaign budget blocks ad-set budgets

The moment a campaign is created with a `daily_budget` (or `lifetime_budget`), Meta activates **Campaign Budget Optimization (CBO)** for that campaign. Every child ad set is then **forbidden** from carrying its own `daily_budget` / `lifetime_budget`. Attempting it fails with:

```
Cannot set daily_budget/lifetime_budget on ad set when campaign has budget (CBO).
```

> The error message suggests `daily_spend_cap` / `lifetime_spend_cap`. **Do not chase that** — those fields are NOT in the `AdSetCreateInput` schema and will fail Pydantic validation. The message is misleading.

**Correct build order when you need ad-set-level budgets (manual campaigns):**

1. Create the campaign with **no budget**.
2. Create each ad set with its own `daily_budget`.

**Correct build order for Advantage+ (campaign-level budget):**

1. Create the campaign with **no budget**.
2. Create ad sets with **no budget** (just `bid_amount` if the account's bid strategy requires it).
3. Add `daily_budget` to the campaign via `meta_ads_campaigns_update` **after** the ad sets exist.

Deciding budget placement per campaign *before* creating anything avoids a delete-and-rebuild cycle. This matters most in multi-campaign builds that mix Advantage+ and manual modes — see [multi-campaign-funnel.md](multi-campaign-funnel.md).

---

## 3. Activation: use activate(), not update()

```
# WRONG — only flips the campaign flag; ad sets and ads stay PAUSED → nothing serves
meta_ads_campaigns_update(campaign_id, status="ACTIVE")

# RIGHT — activates campaign + all ad sets + all ads in one call
meta_ads_campaigns_activate(campaign_id)
```

`update_campaign(status="ACTIVE")` creates a silent non-delivery failure: the dashboard shows ACTIVE but nothing is actually serving because ad sets and ads remain PAUSED.

---

## 4. Campaign status: always start PAUSED

Always create campaigns with `status="PAUSED"`. Never launch live without user review.

Omit `status` when creating ads — ads default to PAUSED automatically. Never pass `status="ACTIVE"` on ad creation; always go through `meta_ads_campaigns_activate` as a deliberate launch step.

---

## 5. Targeting automation placement

`targeting_automation` must be **nested inside** the `targeting` object — not at the top level of the ad set.

```json
// WRONG — targeting_automation at ad set top level
{
  "targeting": {"geo_locations": {"countries": ["US"]}},
  "targeting_automation": {"advantage_audience": 1}
}

// RIGHT — targeting_automation inside targeting
{
  "targeting": {
    "geo_locations": {"countries": ["US"]},
    "targeting_automation": {"advantage_audience": 1}
  }
}
```

### Advantage+ silently overrides narrow age bands

When `advantage_audience: 1`, the tool **clamps** `age_min` to ≤25 and `age_max` to ≥65 (Meta rejects anything narrower for Advantage+). A request like "Advantage+, ages 25–54" is silently widened to **25–65** — the user does NOT get 25–54, and no error is raised.

If a strict age band matters to the user, do not use Advantage+ for that ad set. Use manual targeting (`mode="manual"`, no `advantage_audience`), where `age_min`/`age_max` are honored exactly. Surface the trade-off: Advantage+ audience expansion vs. a precise age band — you can't have both.

---

## 6. create_ad_set: mode + input_data pattern

`meta_ads_ad_sets_create` uses a different calling pattern from `meta_ads_campaigns_create`. Every ad set field goes inside `input_data`.

```
# WRONG — flat params like create_campaign
meta_ads_ad_sets_create(account_id="act_...", campaign_id="123", name="...")

# RIGHT — mode + input_data
meta_ads_ad_sets_create(
    mode="advantage_plus",
    input_data={"account_id": "act_...", "campaign_id": "123", "name": "...", ...}
)
```

> **Prefer `meta_ads_ad_sets_create` with `mode`** — it's the unified path the rest of this skill uses. The `meta_ads_advantage_plus_ad_sets_create` / `meta_ads_manual_ad_sets_create` variants do the same job but take **flat positional arguments** instead of `mode` + `input_data`. They aren't broken or deprecated, but if you reach for one and apply the `input_data` shape you learned here, it fails with "missing required positional arguments." Stick to `meta_ads_ad_sets_create` so there's only one calling convention to track.

---

## 7. create_ad: single input_data dict

`meta_ads_create` takes a **single `input_data` parameter** — a dict containing all fields. Do not pass `account_id`, `name`, `adset_id` etc. as separate top-level arguments.

```
❌ WRONG: meta_ads_create(account_id="act_...", adset_id="123", name="My Ad")
❌ WRONG: meta_ads_create(input_data='{"account_id": "act_..."}')  # string not dict
✅ RIGHT:  meta_ads_create(input_data={"account_id": "act_...", "adset_id": "123", ...})
```

### object_story_spec / link_data fields (applies to every objective)

When building an inline creative (`creative.object_story_spec`):

- `page_id` goes at the **top level** of `object_story_spec` — never inside `link_data`. Omitting it → "Facebook Page is Missing."

Valid `link_data` fields: `message`, `link`, `description`, `picture`, `image_hash`, `call_to_action`, `name`, `caption`.

Common footguns:
- `headline` is **not** a valid `link_data` field → "field headline is not supported." Put the headline text in `name` (or `description`).
- `caption` must be a **URL** (e.g. `"example.com"`), not copy text → "Link data caption is not an Url."

---

## 8. Optimization goal must match objective

`optimization_goal` in the ad set must match the campaign objective. Using the wrong goal is the most common cause of Meta API 400 rejections on ad set creation.

| Campaign Objective | optimization_goal | billing_event |
|---|---|---|
| OUTCOME_SALES | `OFFSITE_CONVERSIONS` | `IMPRESSIONS` |
| OUTCOME_TRAFFIC | `LINK_CLICKS` | `IMPRESSIONS` |
| OUTCOME_LEADS | `LEAD_GENERATION` | `IMPRESSIONS` |
| OUTCOME_ENGAGEMENT | `POST_ENGAGEMENT` | `IMPRESSIONS` |
| OUTCOME_AWARENESS | `REACH` | `IMPRESSIONS` |
| OUTCOME_APP_PROMOTION | `APP_INSTALLS` | `IMPRESSIONS` |

`billing_event` is almost always `IMPRESSIONS`. Only change it if you have a specific reason.

---

## 9. promoted_object requirements by objective

These objectives **require** `promoted_object` on the ad set. Omitting it causes a cryptic API error.

| Objective | promoted_object | Example |
|---|---|---|
| OUTCOME_LEADS (lead form) | **Required** | `{"page_id": "632278516639981"}` |
| OUTCOME_LEADS (website pixel) | **Required — 3 fields** | `{"pixel_id": "9876543210", "custom_event_type": "LEAD", "page_id": "632278516639981"}` |
| OUTCOME_APP_PROMOTION | **Required** | `{"application_id": "APP_ID", "object_store_url": "APP_STORE_URL"}` |
| OUTCOME_SALES (conversions) | **Required** | `{"pixel_id": "9876543210", "custom_event_type": "PURCHASE"}` |
| OUTCOME_TRAFFIC | Not required | — |
| OUTCOME_AWARENESS | Not required | — |
| OUTCOME_ENGAGEMENT | Optional | `{"page_id": "PAGE_ID"}` |

---

## 10. Never change campaign objective or optimization goal without explicit user approval

Once an ad set is created under a campaign, the `objective` field is immutable. If the objective is wrong, create a new campaign.

**More importantly:** never silently substitute a different objective or optimization goal at any point — not during planning, not during error recovery. Changing `OUTCOME_LEADS` to `OUTCOME_TRAFFIC` to work around an API error fundamentally alters what the campaign optimizes for. The user asked for leads; a traffic campaign does not deliver that.

If you cannot create the campaign as requested due to an API or account constraint:
1. Stop.
2. Explain what the constraint is.
3. Present options to the user.
4. Wait for explicit approval before changing anything.

---

## 11. page_id must be passed explicitly

Always populate `page_id` on each ad set from `meta_ads_owned_pages_list`. Auto-resolution only works when exactly one Page is linked to the Business Manager. Pass it explicitly.

---

## 12. Lifetime budgets require dates

```json
{
  "lifetime_budget": 50000,
  "start_time": "2026-07-01T00:00:00+0000",
  "end_time":   "2026-07-31T23:59:59+0000"
}
```

Lifetime budget without `end_time` will fail validation.

---

## 13. Ad preview handling

`meta_ads_ad_previews_get` requires `creative_ids` (a list). `ad_id` is **not** a valid parameter and will fail.

```python
# After meta_ads_create, extract creative_id from the response:
# response.creative.id

meta_ads_ad_previews_get(creative_ids=["<creative_id>"])

# When previewing an existing creative before ad creation:
meta_ads_ad_previews_get(creative_ids=["<existing_creative_id>"])
```

- Never paste or render iframe/html snippets directly in chat.
- Summarize which preview formats succeeded or failed.
- Direct the user to the UI artifact to view previews.

---

## 14. Errors that require user input — do not auto-fix

| Error | Do NOT do this | Do this instead |
|---|---|---|
| "Bid amount required" (subcode 1815857) — **and the user did NOT ask for a bid cap** | Change `optimization_goal` or invent a `bid_amount` | **Stop.** Surface to user: "This account requires an explicit bid amount due to its bid strategy. How would you like to proceed?" Do NOT change the optimization goal as a workaround — that silently misconfigures the campaign. (If the user *did* specify a bid strategy/cap, just set it — see section 16.) |
| "Performance goal isn't available" (subcode 2490408) | Substitute a different `optimization_goal` (e.g. LINK_CLICKS) | **Stop.** See note below — this is caused by an account-level bid strategy incompatibility, not a fixable parameter error. |
| "No Facebook Pages found" | Guess a page_id | Run `meta_ads_health_check`, surface results |
| "No business ID found" from `list_owned_pages` | Skip and ask user | Try `meta_accounts_list` as fallback |
| "image_hash is not valid" or "Link data image_hash" | Invalid or wrong-account hash | Call `meta_ads_ad_images_list(account_id)` to find valid hashes in this account, then re-upload if needed |
| "Cannot set daily_budget on ad set when campaign has budget (CBO)" | Campaign was created with a budget | Recreate the campaign with no budget, OR put budget at ad-set level only. Do NOT use `daily_spend_cap` — not a valid field. See section 2. |
| Pydantic error on `daily_spend_cap` / `lifetime_spend_cap` | Field not in `AdSetCreateInput` schema | These fields don't exist on the ad set tool. Use the build order in section 2 instead. |
| `list_ad_images` rejects `detail` value | Invalid enum | `detail` accepts only `"id_only"`, `"core"`, `"summary"`, `"full"`. Not `"minimal"`. |
| Pydantic "Unexpected keyword argument" | Guess a different field name | Re-read constraints and the relevant campaign workflow |

**OUTCOME_LEADS + LOWEST_COST_WITH_BID_CAP incompatibility (error 2490408):**

When an account's default bid strategy is `LOWEST_COST_WITH_BID_CAP`, the `LEAD_GENERATION` optimization goal is unavailable for `OUTCOME_LEADS` — even if you provide a valid `bid_amount`. This is a Meta platform constraint, not a parameter error. Adding `bid_amount` will not resolve it.

Resolution paths (present to user, get approval before proceeding):

1. **Preferred**: Change the account's default bid strategy to "Lowest Cost" (no cap) in Meta Business Manager → then retry with `LEAD_GENERATION`, no `bid_amount` needed.
2. **Degraded workaround**: Use `OUTCOME_TRAFFIC` with `optimization_goal: LINK_CLICKS`. This runs the campaign but optimizes for clicks to the page, not lead events. **Must disclose this to the user** — it is not a leads campaign.
3. **Alternative**: Try the native lead form path (`destination_type: ON_AD`) which may have different bid strategy requirements.

Never choose a resolution path without telling the user what the constraint is and what the tradeoff is.

---

## 15. Editing existing campaigns

When the user wants to update, pause, adjust budget, or change targeting on an existing campaign:

| What to update | Tool | Key params |
|---|---|---|
| Campaign status / budget | `meta_ads_campaigns_update` | `campaign_id`, `status`, `daily_budget` |
| Ad set status / budget / targeting | `meta_ads_ad_sets_update` | `ad_set_id`, `status`, `daily_budget`, `targeting` |
| Ad status / creative | `meta_ads_update` | `ad_id`, `status` |
| Take everything live at once | `meta_ads_campaigns_activate` | `campaign_id` |

Before updating, fetch current state with `meta_ads_campaigns_get` or `meta_ads_ad_sets_get` — do not guess at current values.

**To pause:** `meta_ads_campaigns_update(campaign_id="...", status="PAUSED")`
**To increase budget:** `meta_ads_campaigns_update(campaign_id="...", daily_budget=5000)` (in cents)
**To go live:** always `meta_ads_campaigns_activate(campaign_id)`, not `update_campaign(status="ACTIVE")`

---

## 16. Bid strategy & bid_amount

`bid_strategy` is a **top-level parameter** on `meta_ads_ad_sets_create` (and `meta_ads_campaigns_create`) — NOT a field inside `input_data`. Putting it inside `input_data` causes a Pydantic error. `bid_amount` (in cents) goes **inside** `input_data`.

**When the user explicitly asks for a bid cap, set it and proceed** — do not stop and ask (they already told you):

```python
meta_ads_ad_sets_create(
    mode="manual",
    bid_strategy="LOWEST_COST_WITH_BID_CAP",   # top-level param
    input_data={
        "account_id": "act_...",
        "campaign_id": "...",
        "name": "...",
        "optimization_goal": "LINK_CLICKS",
        "billing_event": "IMPRESSIONS",
        "daily_budget": 7500,                  # $75/day, ad-set level for manual
        "bid_amount": 250,                     # $2.50 cap, inside input_data
        "targeting": { ... }
    }
)
```

- `LOWEST_COST_WITH_BID_CAP` and `COST_CAP` require `bid_amount`.
- For Advantage+ / CBO, `bid_strategy` belongs on the **campaign** (`create_campaign`) and `bid_amount` on the **ad set**.
- The "stop and surface" rule in section 14 applies only when a bid-amount error appears that the user did **not** request (an account default strategy you didn't choose). Never invent a cap in that case.

---

## 17. Geo targeting beyond country (regions, cities, DMAs)

`geo_locations.countries` accepts ISO codes directly (`["US", "CA"]`). But regions, cities, and DMAs (`geo_markets`) require Meta's internal **numeric keys** — you **cannot guess them**. The validator rejects hand-written keys like `"US-CA-803"`.

Resolve keys first with `meta_ads_targeting_search`:

```python
meta_ads_targeting_search(
    search_type="adgeolocation",
    location_types=["region"],      # or ["city"], ["geo_market"] for DMAs
    country_code="US",
    q="California"
)
```

Then pass the returned `key` values:

```json
"geo_locations": {
  "regions":     [{"key": "<key from search>"}],
  "cities":      [{"key": "<key from search>"}],
  "geo_markets": [{"key": "<key from search>"}]
}
```

Never write geo keys by hand — always resolve them through the search tool first.

---

## 18. Audience exclusions — interest/behavior/demographic are deprecated

As of early 2024, Meta deprecated interest-based, behavior-based, and demographic-based audience **exclusions**. The `exclusions` field in targeting now only supports:

- `exclusions.custom_audiences` — exclude a custom audience by ID
- `exclusions.lookalike_audience` — exclude a lookalike audience

The following exclusion types **no longer work** and will return an API error:

```
exclusions.interests        ← REMOVED
exclusions.behaviors        ← REMOVED
exclusions.demographics     ← REMOVED
```

This is a **Meta platform policy change**, not a toolkit limitation. When a user asks to exclude interests or demographics from targeting, inform them that only custom audience exclusions are available and offer to set up a custom audience for the exclusion instead.

---

## 19. Dynamic creative (`asset_feed_spec`) requires the two-step pattern

`asset_feed_spec` (multiple text/headline/image variations for dynamic creative) **cannot be passed inline** inside the `creative` dict of `meta_ads_create`. It must be created as a standalone creative first.

**Two-step pattern (required):**

```python
# Step 1 — create the dynamic creative with asset_feed_spec
creative = meta_ads_ad_creatives_create(
    account_id="act_...",
    name="My Dynamic Creative",
    object_story_spec={
        "page_id": "<page_id>",
        "link_data": {
            "link": "https://example.com",
            "message": "Primary copy A",
        }
    },
    asset_feed_spec={
        "bodies": [{"text": "Copy A"}, {"text": "Copy B"}, {"text": "Copy C"}],
        "titles": [{"text": "Headline 1"}, {"text": "Headline 2"}],
        "images": [{"hash": "<image_hash_1>"}, {"hash": "<image_hash_2>"}],
        "link_urls": [{"website_url": "https://example.com"}],
        "call_to_action_types": [{"type": "LEARN_MORE"}]
    }
)
# → capture creative_id

# Step 2 — attach by creative_id
meta_ads_create(input_data={
    "account_id": "act_...",
    "adset_id": "<adset_id>",
    "name": "My Dynamic Ad",
    "creative": {"creative_id": "<creative_id from step 1>"},
    "status": "PAUSED"
})
```

Passing `asset_feed_spec` directly inside `meta_ads_create`'s `creative` dict is not supported — the inline creative spec only accepts `object_story_spec` or `creative_id`.
