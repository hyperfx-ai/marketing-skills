# Tasks — built-in recurring tasks for the CMO agent

Tasks turn the agent from a one-shot research tool into a live marketing operator. They run on a schedule, pull from integrations the user has connected, and deliver results to wherever the user wants them.

> Proposed from `strategy/recurring-schedules.md` based on the primary channel in `plan.md`. That reference stores the strategy-level task tables and data-boundary rules; this file remains the monitoring task catalog of record (full schemas, setup prompts, output formats).

## When to use

Read this whenever the gtm decision layer routes to `monitoring/recurring-tasks`, or after the confirmed-brief step when the user is ready to set up scheduled work (Daily Campaign Report, weekly competitive intel, etc.). Tasks are disabled by default — offer them, don't auto-enable. Each task lists the integrations it needs; if a required integration isn't connected, surface that as an `open_question` in the strategy plan rather than enabling the task blind.

All tasks are **disabled by default**. Offer them after the confirmed-brief step. If a task requires an integration the user doesn't have, don't offer it — say what connecting it would unlock.

---

## 1. Weekly Performance Report

**Requires:** at least one of GSC / GA4 / Meta Ads / Google Ads connected.

**Default schedule:** Monday 9 AM (user's time zone)

**Data sources:** Google Search Console, Google Analytics, Meta Ads, Google Ads, HyperSEO (whatever's connected).

**Report structure:**

1. Executive summary — biggest win, biggest concern, recommended action
2. Channel performance — spend, conversions, CPA, ROAS per channel (WoW delta)
3. SEO movement — queries gained/lost, ranking changes (GSC)
4. Top-performing content — pages with highest traffic or conversions
5. Recommendations — what to do this week

**Output:** updates the persistent `marketing-dashboard` and delivers a weekly Markdown snapshot.

**Setup prompt:** "Which channels should I include — all connected, or just some? Any metrics you care about more than others (default: CPA + ROAS)? Deliver to Slack, email, or just the dashboard?"

---

## 2. Social Media + Competitor Monitoring

**Requires:** nothing (uses external scrapers).

**Default schedule:** Wednesday 9 AM (user's time zone)

**Data sources:** Reddit scraper, Twitter scraper, Meta Ads Library.

**Report structure:**

1. Hot Reddit threads — title, subreddit, upvotes, engagement opportunity
2. Twitter/X trends — keyword discussions, thought-leadership openings
3. Active competitor ads — new hooks, offers, creative patterns
4. Recommended actions — threads to reply to, content angles, hooks to test

**Output:** Markdown file + updates `social-intel.md`.

**Setup prompt:** "Which Reddit communities should I monitor? Any specific Twitter keywords or competitors to track? Any ICP-specific phrases to scan for?"

---

## 3. Daily Campaign Report

**Requires:** Meta Business or Google Ads connected, plus at least one active campaign.

**Default schedule:** 8 AM daily (option to skip weekends).

**Data sources:** Meta Ads, Google Ads, GA4 (for conversion attribution).

**Report structure:**

1. Spend yesterday vs prior day (WoW)
2. Performance by campaign — impressions, CTR, CPC, conversions, ROAS
3. Top ads by CTR and by ROAS
4. **Fatigue flags** — any ad where CTR dropped ≥ 30% over a 7-day rolling window, CPM rose ≥ 25% with impressions still growing, or frequency > 3.0 on a prospecting audience
5. Audience performance and overlap signals
6. Recommended actions — pause / scale / refresh creative

**Output:** Short Markdown digest delivered to Slack or email. Fatigue flags can also fire as real-time alerts (opt-in).

**Setup prompt:** "Want this every morning, weekdays only, or only while a campaign is live? Which campaigns — all of them, or specific ones? Should fatigue flags also trigger real-time alerts, or just appear in the daily report?"

---

## 4. SEO + AI Search

**Requires:** nothing is hard-required; GSC upgrades this significantly.

**Default schedule:** Friday 9 AM (weekly).

**What it does:**

1. **Opportunity scan** — combine GSC queries ranking 5–15 (quick wins) with HyperSEO gap keywords and AI search volume. Surface the highest-impact opportunities ordered by difficulty × relevance.
2. **AI search check** — run the brand and competitors through the AI visibility flow (per `playbooks/organic-content/05-check-ai-visibility.md`) and flag positioning gaps.
3. **Content generation** — for the top 2–3 opportunities, draft blog posts (via `playbooks/organic-content/11-write-blog-post.md`) ready for review. Optional: publish to Webflow via `playbooks/organic-content/16-publish-to-webflow.md` when the user approves.

**Output:** weekly opportunity report + draft blog posts attached to the thread.

**Setup prompt:** "Focus on quick-win SEO positions, AI visibility gaps, or both? How aggressive on content — draft 1 post a week, 2–3, or just flag opportunities without drafting? Any topics to avoid?"

---

## How to create a task

When the user opts in:

1. Run through the setup prompt one question at a time.
2. Confirm the final config back before creating.
3. Use the scheduler to register the task with the confirmed cron + parameters.
4. Tell the user where to find / modify / disable it later.

## How to retire a task

Any task must be disableable in one message. "Turn off the daily campaign report" should be enough — don't make the user hunt through settings.