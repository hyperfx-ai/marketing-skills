# Meta Ads account audit

Comprehensive audit of a Meta Ads account: structure, performance, and optimization opportunities. This is a read-only workflow — it produces findings and recommendations, never applies changes. If the user approves a recommendation, route the change through the normal update tools with per-change approval.

## Step 1: Account overview

1. Read the ad accounts as [discovery.md](discovery.md) Step 1 says. For the audit fields, call `meta_ads_adaccount_list(fields="id,name,account_status,currency,timezone_name,spend_cap,amount_spent")`.
2. For each account in scope, note spend limits, timezone, and currency (`currency` of `meta_ads_adaccount_list`).
3. Check account status and any restrictions. If accounts are missing or errors look like permission problems, run `meta_ads_health_check()` and surface the diagnostics.

Confirm with the user which account(s) to audit if more than one is available.

## Step 2: Campaign structure review

For each account:

1. `meta_ads_campaigns_search(account_id="act_<id>", status_filter=["ACTIVE"])` lists the active campaigns. For a full audit, pass `status_filter=["ACTIVE", "PAUSED"]`.
2. Group campaigns by objective (awareness, traffic, conversions/sales, leads, app promotion).
3. Note naming conventions, duplicates, and organization — inconsistent naming and overlapping objectives are audit findings in themselves.

## Step 3: Performance analysis

Pull performance for the audit window (default: last 30 days — confirm with the user):

1. `meta_ads_insights_get(object_id="act_<id>", object_type="account", level="campaign", date_preset="last_30d", include_actions=true)`. For a window that no preset covers, pass `time_range={"since": "YYYY-MM-DD", "until": "YYYY-MM-DD"}` in place of `date_preset`. Name the date range in the report.
2. Key metrics to capture:
   - Total spend
   - Impressions and reach
   - Click-through rate (CTR)
   - Cost per result (CPR)
   - Return on ad spend (ROAS) — only when conversion tracking is verified
3. Identify top and bottom performers by cost per result.
4. Say "no spend" only when the window's spend is zero. A paused campaign or ad set with spend in the window spent: give its status and its spend.

## Step 4: Ad set analysis

For top-spending campaigns:

1. `meta_ads_ad_sets_list(campaign_id=...)` for one campaign. For its fields, use `meta_ads_adset_list` (section 15 of [constraints.md](constraints.md)).
2. Review targeting settings:
   - Audience sizes (too narrow → high CPM; overlapping → auction competition)
   - Age/gender targeting
   - Interest and behavior targeting
   - Lookalike audiences
3. Check budget distribution — many small ad-set budgets under one campaign usually underperform consolidated budgets (CBO/Advantage+).
4. Check attribution windows are consistent across ad sets you compare (see the `attribution_spec` section in [constraints.md](constraints.md)).

## Step 5: Creative review

For top ad sets:

1. `meta_ads_list(ad_set_id=...)` — list the ads of one ad set; `meta_ads_ad_get(ad_id=..., fields="id,name,status,effective_status,creative")` for details.
2. Review creative types in use: static images, videos, carousels, dynamic creative.
3. Check ad fatigue: frequency > 3 over the window is a refresh signal.
4. Check UTM coverage with `meta_ads_creative_list(fields="id,name,url_tags,object_story_spec")`: creatives driving to a destination without `url_tags` are unmeasurable downstream — flag them.

## Step 6: Recommendations

Based on findings, provide:

1. **Quick wins** — changes that can be made immediately (pause zero-conversion spenders, fix missing UTMs, refresh fatigued creatives).
2. **Structural changes** — longer-term improvements (consolidation, objective realignment, budget rebalancing).
3. **Testing opportunities** — new approaches to try (audiences, creative formats, placements).

Do not apply any change without explicit per-change user approval.

## Output format

Create a summary report with:

- Executive summary
- Key metrics table (spend, CTR, CPR, ROAS by campaign)
- Top/bottom performing campaigns
- Prioritized recommendations (quick wins → structural → tests)

If the user wants an interactive view, build a dashboard via [dashboards.md](dashboards.md).
