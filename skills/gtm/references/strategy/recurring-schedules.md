# Scheduled Tasks

Use scheduled tasks when the CMO should keep checking or drafting something over time.

## When to use

Read this after `plan.md` is written, or when the user asks what the CMO can keep doing.

Do not copy task proposals or schedule details into `plan.md`.

Task state belongs in:

- chat, while asking for approval
- the task sidebar, after tasks are created
- `/files/cmo/{domain}/status.md`, as a short record

## Scheduling rules

Before adding a task:

1. Decide whether the task is actually useful.
2. Check which tools the task needs.
3. Check whether those tools are connected.
4. Ask the user to approve the task.
5. If tools are missing, create the task inactive or ask the user to connect the tools first.

Use only supported `agents_schedule` arguments:

- `agent_id`
- `instructions`
- `cron` or `run_at`
- `timezone`
- `name`
- `active`

Do not pass unsupported fields.

Start the task instructions with:

```text
Tools needed: ...
```

If a needed tool is missing, the instructions must tell the scheduled run to stop and report what is missing.

## How to ask the user

Keep the message short:

```text
I suggest adding a weekly SEO scan and a Monday blog draft task. The blog draft needs HyperSEO and Firecrawl. Approve these, or tell me what to change.
```

Do not paste a long task list into chat unless the user asks for details.

## Housekeeping

Use this for every CMO brand after onboarding.

Name: Daily CMO housekeeping

When: daily at 08:30

Tools needed: agents, read_file, edit_file

What it does:

- reads `status.md`, `business_context.md`, and `plan.md`
- checks active schedules
- flags stale, duplicate, risky, or expensive tasks
- updates the operating notes in `status.md`

It must not start paid work or spend money.

## Content tasks

Use these when content is the focus or when the brand needs a basic weekly cadence.

Name: SEO keyword setup

When: once, next business morning

Tools needed: HyperSEO

What it does: creates the first keyword cluster table.

Output: `seo/keywords.md`

Workflow: `organic-content/04-audit-seo-keywords`

Name: SEO weekly scan

When: Fridays at 09:00

Tools needed: HyperSEO. Better with Search Console and Analytics.

What it does: finds the best search and content opportunities for next week.

Output: `seo/opportunities.md`

Workflow: `organic-content/04-audit-seo-keywords`

Name: Weekly blog draft

When: Mondays at 10:00

Tools needed: HyperSEO and Firecrawl

What it does: drafts one post from the best approved topic. It does not publish.

Output: draft attached for review

Workflow: `organic-content/seo-blog`

Name: AI answer check

When: monthly

Tools needed: HyperSEO or another tool that actually checks AI answers

What it does: checks whether AI answer engines mention the brand and competitors.

Output: short update in the research notes

Workflow: `organic-content/ai-visibility`

Do not claim AI answer results unless this task or another cited source actually measured them.

## Social and community tasks

Name: Weekly social post pack

When: Mondays at 09:00

Tools needed: none

What it does: drafts short posts from the weekly content or latest plan.

Output: five to seven draft posts for manual review

Workflow: `organic-content/social-cadence`

Name: Competitor and social scan

When: Wednesdays at 09:00

Tools needed: none. Better with Reddit or ad-library tools.

What it does: checks what competitors and relevant communities are talking about.

Output: update to `social-intel.md`

Name: Reddit thread scan

When: Tuesdays and Thursdays at 09:00

Tools needed: Reddit scraper

What it does: finds useful Reddit threads worth answering.

Output: ranked thread list

Workflow: `community/reddit`

Name: Reddit reply drafts

When: Tuesdays and Thursdays at 14:00

Tools needed: Reddit scraper

What it does: drafts helpful replies for selected threads. It does not post.

Output: reply drafts for review

Workflow: `community/reddit`

## Ads tasks

Use these only when ad tools and measurement are connected, or create them inactive until the tools are connected.

Name: Daily campaign check

When: weekdays at 08:00

Tools needed: Meta Ads or Google Ads

What it does: checks spend, results, and signs that ads need new creative.

Output: short campaign note

Name: Weekly performance note

When: Mondays at 09:00

Tools needed: one connected measurement source, such as Search Console, Analytics, Meta Ads, or Google Ads

What it does: summarizes what changed, what worked, what is concerning, and what to do next.

Output: weekly snapshot

Name: Competitor ad scan

When: Wednesdays at 09:00

Tools needed: Meta ad-library access

What it does: reviews competitor ads for hooks, offers, and creative ideas.

Output: update to `social-intel.md`

Name: Creative refresh draft

When: Fridays at 10:00

Tools needed: image generation. Better with ad-library access.

What it does: drafts ad copy and image ideas for review.

Output: copy and image concepts

Name: Paused Meta campaign build

When: once, next business morning

Tools needed: Meta Ads and image generation

What it does: builds a paused campaign for review. It does not launch.

Output: paused campaign

Workflow: `paid-ads/meta`

Name: Paused Google campaign build

When: once, next business morning

Tools needed: Google Ads and HyperSEO

What it does: builds a paused search campaign for review. It does not launch.

Output: paused campaign

Workflow: `paid-ads/google`

## Outreach and referral work

Do not start outreach or referral programs from this skill.

If the user says they already run warm outreach, cold outreach, affiliates, or referrals, you may suggest a light review or reminder task. Ask first and keep the task inactive if the needed tools are missing.

## Example schedule instruction

```text
Tools needed: HyperSEO and Firecrawl. If either tool is missing, stop and tell the user what is missing. Run the weekly blog draft workflow for example.com. Pick the approved topic from seo/opportunities.md, draft one post, and attach it for review. Do not publish.
```
