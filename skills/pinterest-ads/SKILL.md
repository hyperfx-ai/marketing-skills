---
name: pinterest-ads
description: Plan and create Pinterest Ads campaigns through the Hyper MCP — Awareness, Consideration, Video View, Web Conversion, Catalog Sales, and Web Sessions objectives — with strict microcurrency budgeting, CBO rules, audience and customer-list management, conversion tag handling, keyword targeting, and campaign analytics. Use when the user mentions Pinterest ads, Pinterest campaign, Pinterest ad group, Pinterest audience, Pinterest conversion tracking, Pinterest tag, or Pinterest customer list.
requires_toolkits:
  - pinterest_ads
icon: pinterest_ads
short_description: Plan and create Pinterest Ads with microcurrency budgets and conversion tags.
---

# Pinterest Ads

Strategic skill for managing Pinterest Ads campaigns via the Pinterest Ads API v5 surface exposed by the Hyper MCP. Ad-group creation goes through a direct REST call (bypassing SDK model conversion) so parameter types must be sent exactly as documented — strings as strings, integers as integers.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Google Ads campaign | `google-ads` |
| Meta (Facebook / Instagram) ad campaign | `meta-ads` |
| Amazon Sponsored Products | `amazon-ads` |
| TikTok ad campaign | `tiktok-ads` |
| Competitor ad research from the Meta Ads Library | `meta-ads-library` |
| Organic Pinterest pinning | not currently shipped — use the Pinterest app |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Pinterest Ads integration connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps) (Pinterest Business account with ad account access).

If `search("pinterest_ads_ad_accounts_list")` does not find `pinterest_ads_ad_accounts_list`, stop and tell the user to enable the Hyper MCP and connect Pinterest Ads.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call("<name>", {...})` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found, its integration is not connected or not enabled for the workspace: stop and tell the user which integration to connect.

## Tool surface

| Tool group | Tools |
| --- | --- |
| Accounts | `pinterest_ads_ad_accounts_list`, `pinterest_ads_ad_accounts_get` |
| Campaigns | `pinterest_ads_campaigns_list`, `pinterest_ads_campaigns_get`, `pinterest_ads_campaigns_create`, `pinterest_ads_campaigns_update` |
| Ad groups | `pinterest_ads_ad_groups_list`, `pinterest_ads_ad_groups_get`, `pinterest_ads_ad_groups_create`, `pinterest_ads_ad_groups_update` |
| Ads | `pinterest_ads_list`, `pinterest_ads_get`, `pinterest_ads_create`, `pinterest_ads_update` |
| Audiences | `pinterest_ads_audiences_list`, `pinterest_ads_audiences_create`, `pinterest_ads_customer_lists_create` |
| Conversion | `pinterest_ads_conversion_tags_list`, `pinterest_ads_conversion_tags_create`, `pinterest_ads_conversion_events_send` |
| Keywords | `pinterest_ads_keywords_create` |
| Analytics | `pinterest_ads_campaign_analytics_get` |

## Critical Rules

> **CRITICAL**: All budgets and bids are in **microcurrency**. $1.00 = 1,000,000 microdollars. $50/day = 50,000,000. Never pass dollar amounts directly.

> **CRITICAL**: When using `is_flexible_daily_budgets: true`, you MUST also set `is_campaign_budget_optimization: true`. FDB requires CBO.

> **CRITICAL**: Lifetime CBO campaigns MUST include `end_time` (Unix timestamp).

> **CRITICAL**: Create campaigns with status `PAUSED` initially. Never launch live without user review.

> **CRITICAL**: WEB_CONVERSION ad groups MUST use `billable_event="IMPRESSION"` (NOT `CLICKTHROUGH`) and MUST include `optimization_goal_metadata` with `attribution_windows`, `conversion_event`, `conversion_tag_id`, and `cpa_goal_value_in_micro_currency`.

> **CRITICAL**: Keyword creation REQUIRES `match_type`. Without it, the API returns 500 errors.

> **CRITICAL**: CBO campaigns manage budget at the campaign level. Do NOT set `budget_in_micro_currency` on ad groups under CBO campaigns.

> **IMPORTANT**: `retention_days` is **deprecated** for ENGAGEMENT audiences. Omit it from audience rules.

## Core process

Discovery → audit account → research (objectives, audience, assets) → confirm strategy → create campaign (`PAUSED`) → create ad groups → create ads → review → activate only with user approval.

> **All reference files live in `references/`.** Read them at `references/<file>` (e.g. `references/discovery.md`).

## Routing table

| The user wants to… | Read these files first |
|---|---|
| Create a campaign (any objective) | [references/discovery.md](references/discovery.md) → [references/campaigns.md](references/campaigns.md) |
| Build a WEB_CONVERSION campaign | [references/discovery.md](references/discovery.md) → [references/campaigns.md](references/campaigns.md) (use the WEB_CONVERSION template exactly) + [references/audiences-and-conversions.md](references/audiences-and-conversions.md) for the conversion tag |
| Create or manage audiences / customer lists | [references/audiences-and-conversions.md](references/audiences-and-conversions.md) |
| Set up conversion tracking / send conversion events | [references/audiences-and-conversions.md](references/audiences-and-conversions.md) |
| Add keywords to an ad group | [references/keywords-and-analytics.md](references/keywords-and-analytics.md) |
| Pull campaign analytics | [references/keywords-and-analytics.md](references/keywords-and-analytics.md) |
| Update or pause existing campaigns / ad groups / ads | [references/keywords-and-analytics.md](references/keywords-and-analytics.md) |
| Goal not yet clear | [references/discovery.md](references/discovery.md) — discovery clarifies the goal |

## Known Limitations

| Issue | Workaround |
| --- | --- |
| Keyword creation returns 500 without `match_type` | Always specify `match_type` (`BROAD`, `PHRASE`, `EXACT`). |
| `retention_days` deprecated for ENGAGEMENT audiences | Omit from rule dict. |
| WEB_CONVERSION ad groups require many parameters | Use the WEB_CONVERSION template exactly — include full `optimization_goal_metadata`. |
| WEB_CONVERSION ad groups must use `IMPRESSION` `billable_event` | Do NOT use `CLICKTHROUGH` for WEB_CONVERSION. |
| CBO campaigns reject ad group budgets | Do NOT set `budget_in_micro_currency` when parent campaign has CBO enabled. |
| `cpa_goal_value_in_micro_currency` must be a string | Pass as `"5000000"`, not `5000000`. |
| `conversion_tag_id` must be a real tag from the account | List conversion tags first, then use an existing tag ID. |

## Safety Rules

**Never:**

- Assume Pin IDs or ad account IDs — always ask or look up.
- Skip the account audit phase.
- Create campaigns without explicit approval.
- Set campaigns to `ACTIVE` without user consent.
- Pass dollar amounts instead of microcurrency.
- Use `retention_days` for ENGAGEMENT audiences.
- Create WEB_CONVERSION ad groups without `optimization_goal_metadata`.
- Use `CLICKTHROUGH` `billable_event` for WEB_CONVERSION campaigns (use `IMPRESSION`).
- Set ad group budgets on CBO campaigns.
- Create keywords without specifying `match_type`.
- Pass `cpa_goal_value_in_micro_currency` as an integer (must be a string like `"5000000"`).
- Omit `conversion_tag_id` from WEB_CONVERSION optimization metadata (list tags first, use a real ID).
