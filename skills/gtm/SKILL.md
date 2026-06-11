---
name: gtm
description: GTM operating system for a brand — decide where to focus (content, community, or ads), write and maintain the marketing plan, run the chosen workflows, and set up recurring monitoring. Delegates channel execution to the dedicated skills. Use when the user asks what to do next, wants a marketing plan, GTM or growth strategy, a full brand audit, or the weekly content/community/ads cadence run.
use_cases:
  - Write the first marketing plan after onboarding
  - Recommend where the brand should focus next
  - Choose between content, community, and ads
  - Run a Full Brand Audit (brand profile, tracking audit, competitors, SEO/AI visibility, social intel)
  - Audit SEO keywords and AI search visibility
  - Research a SERP and write an SEO blog post
  - Generate a social content package distilled from a blog post
  - Publish approved content to Webflow
  - Find high-engagement Reddit threads and draft community replies
  - Launch paid campaigns through the meta-ads / google-ads skills
  - Set up recurring monitoring tasks (daily campaign report, weekly intel)
  - Explain what to measure and which tools are missing
triggers:
  - gtm
  - go to market
  - marketing plan
  - marketing strategy
  - growth strategy
  - what should we do
  - where should i focus
  - next steps
  - pick a channel
  - channel strategy
  - brand audit
  - run brand audit
  - audit seo keywords
  - check ai visibility
  - write blog post
  - generate social posts
  - publish to webflow
  - find reddit threads
  - draft reddit replies
  - daily campaign report
  - cmo task
requires_toolkits:
  - cmo
  - sandbox
  - firecrawl_toolkit
  - hyperseo
suggested_toolkits:
  - files
  - hyper_database
  - image_gen
  - meta_ads_library
  - meta_business
  - google_ads
  - webflow_toolkit
  - reddit_scraper
  - google_search_console_toolkit
  - google_analytics_toolkit
  - website_analyzer_toolkit
---

# GTM

Help a brand decide what to do next, write the plan, and run it.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **CMO toolkit** plus the baseline execution set (sandbox, Firecrawl, HyperSEO) enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations). Channel workflows need their own integrations (Meta Business, Google Ads, Webflow, Reddit scraper) — inspect what is connected before running a step.

This skill has two layers:

- **Decision layer** — read the brand state, choose one focus, write `/files/cmo/{domain}/plan.md`, keep `status.md` current, propose scheduled tasks. This layer decides; nothing else does.
- **Execution layer** — run the workflow the plan chose. Research and audit steps live in this skill's references; channel execution (paid campaigns, ad creative, competitor ad scans) is delegated to the dedicated channel skills.

Keep the writing plain. The user should be able to read the answer quickly and understand the point without learning internal labels.

## When to use which layer

Decision layer:

- onboarding is done and the brand needs its first plan
- the user asks what to do next, or where to focus
- the user wants to change the plan
- the user asks for a marketing strategy or GTM plan

Execution layer:

- the plan exists and a specific step should run ("write the blog post", "scan competitor ads", "draft Reddit replies")
- the user explicitly asks for an execution-side outcome and the channel is already settled
- a Full Brand Audit needs the research foundation before the decision layer can synthesize a plan

# Decision layer

The job is simple:

1. Read the brand files.
2. Ask only the questions that are still missing.
3. Choose one main focus.
4. Write `/files/cmo/{domain}/plan.md`.
5. Update `/files/cmo/{domain}/status.md`.
6. Ask in chat before adding scheduled tasks.

## How to think

Use normal language. Do not write internal labels or process notes into chat or `plan.md`.

- "The offer is not clear enough yet."
- "Focus on content first."
- "Search Console is missing, so we do not have a real organic baseline."
- "I can add a weekly SEO task, but it needs HyperSEO first."

## What the agent can choose

Choose one main focus unless the user clearly asks for more.

The normal choices are:

- Content: blog posts, search, social posts, and visibility in AI answers.
- Community: Reddit, forums, or similar places where the audience already talks.
- Ads: Meta or Google Ads, only when the right ad tools and measurement are connected.

Warm outreach, cold outreach, affiliates, and referrals are not started from this skill. Mention them only if the user says they already run them and the detail matters. (For dedicated outbound work, the `cold-email-outreach` skill exists — but it is not part of the default focus choice.)

## Read the current state

Read these files first:

- `/files/cmo/{domain}/business_context.md`
- `/files/cmo/{domain}/status.md`
- `/files/cmo/{domain}/plan.md`, if it exists

Use `cmo_get_brand_data` when you need the current structured brand data.

Do not recollect brand data unless it is missing, stale, or the user asks for a refresh. If you call `cmo_collect_brand_data`, pass the brand URL.

Use `cmo_collect_ad_performance` only when connected ad accounts are available.

## Ask only useful questions

Use `ask_user` when the answer changes the plan.

Ask as few questions as possible. One batch is preferred. Do not ask what tools are connected; inspect that yourself.

Useful questions:

- What should this brand win in the next 90 days?
- Which audience should we focus on first?
- Are content, ads, or community off-limits?
- Are warm outreach, cold outreach, affiliates, or referrals already running?
- If the user wants ads and ad tools are missing: what budget range are they considering?

Skip questions that the brand files already answer.

If a question is still unanswered, ask it in chat. Do not put unanswered questions into `plan.md`.

## Choose the focus

Use the references when deciding:

- `references/strategy/offer-first.md`: use when the offer is unclear.
- `references/strategy/channels.md`: use when choosing content, community, or ads.
- `references/strategy/channel-fit-diagnostic.md`: use when the best focus is not obvious.
- `references/strategy/concentration.md`: use when the plan is spreading effort too widely.
- `references/strategy/always-on-content.md`: use for the weekly baseline.
- `references/strategy/recurring-schedules.md`: use only after the plan is written, when proposing scheduled tasks.

Choose content when:

- people already search for the problem or category
- competitors rank and the brand does not
- the brand needs useful public pages before ads can work well
- measurement tools are missing and content is the safest useful start

Choose community when:

- the audience is clearly active in one place
- people discuss the exact problem there
- the brand can join without sounding forced

Choose ads when:

- Meta or Google Ads is connected
- tracking is good enough to measure results
- the offer is clear enough to spend against
- there is evidence that ads can work for the brand or category

If the offer is unclear, say that plainly. Recommend fixing the offer before spending on more traffic.

## Evidence rules

Do not invent measurements.

If a tool or file did not measure something, say it is missing.

Examples:

- Do not say the brand has "0 AI citations" unless a file or tool actually checked AI answers.
- Do not say search traffic is growing unless Search Console or another real source shows it.
- Do not invent a baseline for traffic, leads, revenue, ROAS, rankings, or AI answer visibility.
- If a source is missing, name the missing source and explain what it would measure.

Every recommendation should cite the files or dashboard panels that support it.

## Write `plan.md`

Write or revise exactly this file:

`/files/cmo/{domain}/plan.md`

Use this shape:

```md
# Marketing plan

## Diagnosis

What is happening, why it matters, and which files or dashboard panels support it.

## Focus

The one place to focus first, why it is the right next move, and which workflow should run.

## Measurement

The weekly goal, the main number to watch, the source of truth, the current baseline if known, and missing tools.

## Weekly cadence

The basic weekly work that should keep happening.

## Not doing now

Only include this when leaving something out matters.
```

Do not put these in `plan.md`:

- unanswered questions
- task ideas waiting for approval
- scheduled tasks
- approval text
- schedule record IDs
- copied task lists
- internal tool-call notes

`plan.md` is the permanent marketing plan. It is not a task manager.

## Update `status.md`

After writing the plan, update:

`/files/cmo/{domain}/status.md`

Update only the parts that matter:

- mark the initial plan as written
- note the current goal
- note the latest decision
- note the next action
- note missing measurement tools
- record approved scheduled tasks after they are actually created

Keep task state in `status.md`, the task sidebar, and chat. Do not copy it into `plan.md`.

## Ask before scheduling tasks

After the plan is written, suggest useful scheduled tasks in chat.

Keep it short:

```text
I suggest adding a weekly SEO scan and a Monday blog draft task. The blog draft needs HyperSEO and Firecrawl. Approve these, or tell me what to change.
```

Before scheduling a task:

1. Check which tools the task needs.
2. Check which tools are connected.
3. Ask the user to approve the task.
4. If needed tools are missing, create the task inactive or ask the user to connect the tools first.

When calling `agents_schedule`, use only supported arguments:

- `agent_id`
- `instructions`
- `cron` or `run_at`
- `timezone`
- `name`
- `active`

Do not pass fields such as `requires`, `required_providers`, or `required_toolkits`.

In the task instructions, start with a plain sentence like:

```text
Tools needed: HyperSEO and Firecrawl. If either tool is not connected, stop and tell the user what is missing.
```

After approved schedules are created, confirm in chat and update `status.md`. Do not update `plan.md` with schedule details.

## Final response to the user

After writing the plan and updating status, reply with:

- the main problem
- the focus
- the measurement source or missing source
- the weekly cadence
- any task approval question

Keep it short. Do not repeat the whole plan in chat.

# Execution layer

Run the workflow the plan chose. Research and produce artifacts; surface them as you go. This layer never picks channels or goals — the decision layer owns those.

## Routing table (workflow slug → where the steps live)

| Workflow slug | Read / delegate, in order |
|---|---|
| `research/foundation` | `references/playbooks/research/00-client-intake.md` → `01-scrape-brand-profile.md` → `02-audit-website-tracking.md` → `03-research-competitors.md` |
| `organic-content/seo-blog` | `references/playbooks/organic-content/04-audit-seo-keywords.md` → `08-research-serp.md` → `11-write-blog-post.md` → `16-publish-to-webflow.md` |
| `organic-content/ai-visibility` | `references/playbooks/organic-content/05-check-ai-visibility.md` → `04-audit-seo-keywords.md` |
| `organic-content/social-cadence` | `references/playbooks/organic-content/12-generate-social-posts.md`; for posting, hand off to the [`linkedin`](../linkedin), [`instagram`](../instagram), and [`tiktok`](../tiktok) skills |
| `community/reddit` | `references/playbooks/community/07-find-reddit-threads.md` → `13-draft-reddit-replies.md`; for deeper mining, the [`reddit`](../reddit) skill |
| `paid-ads/meta` | Delegate: [`meta-ads-library`](../meta-ads-library) (competitor scan) → [`ad-creative-generation`](../ad-creative-generation) (copy + images) → [`meta-ads`](../meta-ads) (build the paused campaign) |
| `paid-ads/google` | `references/playbooks/organic-content/04-audit-seo-keywords.md` → [`ad-creative-generation`](../ad-creative-generation) → [`google-ads`](../google-ads) (build the paused campaign) |
| `monitoring/recurring-tasks` | `references/playbooks/monitoring/tasks.md` |

Deeper channel research also delegates: [`seo-research`](../seo-research) for keyword/SERP depth beyond the audit docs, [`competitor-intel`](../competitor-intel) for full competitor monitoring, [`customer-research`](../customer-research) for voice-of-customer mining, [`analytics-insights`](../analytics-insights) for GA4/GSC/GTM work, [`email-lifecycle`](../email-lifecycle) for lifecycle email.

## How to execute a slug

1. Look up the slug in the routing table. Read the listed reference docs in order — each has a "When to use" block at the top so you can confirm fit before running. Where a step delegates to a channel skill, load that skill and follow it; the CMO file conventions in this skill still apply to the artifacts.
2. Run the steps in sequence. Where one step's output becomes another's input (SERP brief → blog post, copy variants + images → Meta campaign), respect the order.
3. Surface artifacts to the user as you go. Do not wait until the end of the workflow to attach files or report findings.
4. If a required integration is missing (Meta Business not connected for `paid-ads/meta`, Webflow not connected for the publish step, etc.), stop the workflow at the gating step and surface the gap. Do not skip steps that depend on the missing integration.

## Composed workflow: Full Brand Audit

Run before the decision layer synthesises a plan:

1. `research/foundation` → starts from `cmo_get_brand_data` for the current CMO brand; if the brand is missing or stale, run `cmo_collect_brand_data({"url": "https://..."})` before producing the foundation files (`product-brief.md`, `brand-identity.md`, `competitors.md`, plus tracking notes)
2. `references/playbooks/organic-content/04-audit-seo-keywords.md` + `05-check-ai-visibility.md` → produces `seo-geo-audit.md`
3. `references/playbooks/community/07-find-reddit-threads.md` (read-only — no replies yet) → contributes to `social-intel.md`
4. Competitor ad scan via the [`meta-ads-library`](../meta-ads-library) skill (read-only — no campaign yet) → contributes to `social-intel.md` and the ads section of `competitors.md`

After step 4, return to the decision layer to write `/files/cmo/{domain}/plan.md`. The execution layer does not emit a plan.

## Self-Update Checklist (after research)

Mandatory after running `research/foundation` plus the audit-side organic and paid steps. Do not just present findings in chat — create the files, attach them to the agent, and confirm each one.

| File | Contents | Source steps |
|------|----------|--------------|
| `product-brief.md` | Product name, tagline, summary, features, ICP, brand voice, value props, CTA patterns, proof points | `research/01-scrape-brand-profile.md` |
| `brand-identity.md` | Colors, typography, logo, brand personality, visual asset quality, consistency, positioning vs competitors | `research/01-scrape-brand-profile.md` + `research/03-research-competitors.md` |
| `competitors.md` | Direct/adjacent/aspirational competitors with domains, traffic, keywords, messaging themes, gaps, ad strategies, market segments, differentiation | `research/03-research-competitors.md` + the `meta-ads-library` skill |
| `seo-geo-audit.md` | Current rankings, keyword opportunities by cluster, competitive gap keywords, difficulty distribution, AI search volume, SEO health, recommendations | `organic-content/04-audit-seo-keywords.md` + `05-check-ai-visibility.md` |
| `social-intel.md` | Reddit sentiment, pain points, high-engagement threads, community language, AI visibility scores, competitor ad activity, creative patterns, opportunities | `community/07-find-reddit-threads.md` + `organic-content/05-check-ai-visibility.md` + the `meta-ads-library` skill |
| `marketing-dashboard` *(conditional)* | Live performance dashboard with panels for each connected integration (GSC queries/rankings, GA4 traffic/conversions, Meta/Google Ads spend+ROAS) | Built only if at least one of GSC / GA4 / Meta / Google Ads is connected. |

Each file should contain real data, real URLs, real numbers — never placeholder text or invented metrics.

Use the CMO brand store before running one-off collectors. First call `cmo_get_brand_data` with no arguments to get the current agent's brand, business context, competitors, socials, search visibility, and context files. Do not re-derive what is already in the business context. Run `cmo_collect_brand_data` only when that data is missing/stale or the user asks for a refresh. The SEO, community, and ad-library steps are execution-specific enrichment, not replacements for the CMO brand store.

After the files are created, attach them in one call:

```
agents_update_context(
  agent_id=YOUR_AGENT_ID,
  resource_type="file",
  op="add",
  ids=[product_brief_id, brand_identity_id, competitors_id, seo_geo_audit_id, social_intel_id]
)
```

Brand assets should come from `cmo_get_brand_data` when available. If creative-quality logo/screenshot references are missing, use the Firecrawl fallback in `references/playbooks/research/01-scrape-brand-profile.md` and attach the resulting assets in the same `agents_update_context` call.

## Tools and integrations

The execution layer expects a baseline toolkit set: `sandbox` (file ops), `firecrawl_toolkit` (scraping), `hyperseo` (keyword + SERP data). The other suggested toolkits matter per workflow — `meta_business` / `meta_ads_library` for `paid-ads/meta`, `google_ads` for `paid-ads/google`, `webflow_toolkit` for the publish step, `reddit_scraper` for community work, etc.

Inspect available tools at the start of a workflow. If a step's required toolkit is not connected, stop at the gating step and surface the gap rather than hallucinating. Don't ask the user "what's connected" — check yourself.

## Important

- Honest scope: the execution layer researches and executes. It does not derive ICP, pick goals, or pick channels. Those belong to the decision layer.
- Paid campaigns are always built **paused**. The user reviews and launches manually. The `meta-ads` and `google-ads` skills enforce this too.
- Reddit replies are always drafted, never auto-posted. The user posts manually.
- Every artifact gets attached to the agent — chat-only output is not enough.
