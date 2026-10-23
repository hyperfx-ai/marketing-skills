# Multi-Campaign / Funnel Builds

## When to use

Use this when the user asks for **more than one campaign in a single request** — most commonly a funnel:

- TOF (top of funnel): awareness / reach to cold audiences
- MOF (middle of funnel): traffic / engagement retargeting warm audiences
- BOF (bottom of funnel): sales / conversions to lookalikes or customer lists

This file covers **orchestration** — planning, sequencing, and budget-mode decisions across campaigns. It does **not** replace the per-objective workflows. Each individual campaign is still built using its objective file:

- Awareness/Engagement tier → [campaigns/awareness-engagement.md](campaigns/awareness-engagement.md)
- Traffic tier → [campaigns/traffic.md](campaigns/traffic.md)
- Sales tier → [campaigns/sales.md](campaigns/sales.md)
- Leads tier → [campaigns/leads.md](campaigns/leads.md)

Read the relevant objective file for each tier before building it.

---

## Why this needs its own plan

Multi-campaign builds fail in ways single campaigns don't, because decisions made on campaign A constrain campaign B. The two big traps:

1. **Mixed budget modes** — a funnel often mixes Advantage+ (campaign-level budget) with manual (ad-set-level budget). Get the build order wrong and you hit the CBO lock (see [constraints.md](constraints.md) section 2) and have to delete and rebuild.
2. **Audience readiness** — each tier targets a different audience. If one is broken, too small, or doesn't match the brief, you should know *before* you've built two other campaigns around it.

---

## Plan before building (required)

Before any tool call, produce a written plan with a row per tier:

| Tier | Objective | Budget | Budget mode | Audience | Audience status |
|---|---|---|---|---|---|
| TOF | OUTCOME_AWARENESS | $30/day | Advantage+ (campaign) | Broad US 25-54 | n/a |
| MOF | OUTCOME_TRAFFIC | $30/day | Manual (ad set) | Website visitors 14d | verify |
| BOF | OUTCOME_SALES | $50/day | Manual (ad set) | Purchase lookalike | verify |

Filling this table forces the two decisions that prevent rebuilds: **budget mode per tier** and **audience validity per tier**.

---

## Step 1: Validate audiences first

For every tier that targets a custom or lookalike audience, run the audience validation from [discovery.md](discovery.md) step 3b **before creating any campaign**:

- `operation_status.code` = 200, `delivery_status.code` = 200, and `approximate_count_lower_bound` > ~1000 from `meta_ads_custom_audience_get(custom_audience_id=...)`
- Confirm the audience parameters match the brief (e.g. retention window)

If any audience is broken, too small, or mismatched, **surface it to the user and resolve it before building.** Do not build two campaigns and then silently swap in a customer list for the broken BOF lookalike — the user asked for a specific structure.

---

## Step 2: Decide budget mode per tier

| Tier intent | Recommended mode | Budget goes |
|---|---|---|
| Advantage+ broad targeting | Advantage+ | Campaign level (set when the campaign is made) |
| Manual / specific audience targeting | Manual | Ad set level |

A funnel commonly mixes both. That's fine — but it dictates the build order below.

---

## Step 3: Build in the order that avoids the CBO lock

This is the critical sequence. Setting a campaign budget activates CBO and blocks ad-set budgets, so budget timing matters.

1. **Create the manual campaigns with no budget**, and the Advantage+ campaigns WITH their `daily_budget` or `lifetime_budget` (and `bid_strategy`, if any).
2. **Create the manual ad sets** (MOF, BOF) with their `daily_budget` at the ad set level. With no campaign budget, there's no CBO lock.
3. **Create the Advantage+ ad sets** (TOF) with no budget (add `bid_amount` only if the bid strategy requires it — see below).
4. **Create the ads** for each ad set.
5. **Preview, then leave everything PAUSED** for user review.

See [constraints.md](constraints.md) section 2 for the full CBO explanation.

---

## Bid strategy applies to every tier

If the account's default bid strategy is `LOWEST_COST_WITH_BID_CAP`, **every** ad set across **every** tier will require a `bid_amount`, and the error will repeat per tier.

> **CRITICAL**: If you hit "Bid Amount Required" (subcode 1815857), do NOT auto-fix with a placeholder bid and do NOT change the optimization goal. Stop and surface it to the user once — it affects the whole build, so resolve it before continuing the remaining tiers. See [constraints.md](constraints.md) section 14.

---

## Recovering from a partial failure

Because each tier is built step by step, a mid-build failure leaves the earlier tiers already created. There is no automatic rollback — clean up manually before retrying:

1. Note which campaigns/ad sets/ads were created before the failure (the responses you captured).
2. Delete the incomplete artifacts with `meta_ads_campaign_delete` (deleting a campaign removes its ad sets and ads).
3. Fix the root cause (validate audiences, resolve the bid strategy, correct budget mode).
4. Rebuild from a clean state.

This is exactly why the plan-first + audience-validation steps above matter: resolving CBO, bid strategy, and audience issues *before* the first tool call is what prevents a half-built funnel in the first place.

---

## Common failure points

| Symptom | Cause | Fix |
|---|---|---|
| Ad set rejects `daily_budget` (CBO error) | A manual campaign was created with a budget | Follow the build order above — a manual campaign has no budget |
| "Bid Amount Required" on every tier | Account bid strategy is bid-cap | Stop, surface once, resolve before building remaining tiers |
| Built funnel doesn't match brief | Audience swapped or window mismatched silently | Validate + surface audience issues before building (step 1) |
| Had to delete and rebuild campaigns | Budget mode decided after creation | Decide budget mode per tier in the plan, before any tool call |
