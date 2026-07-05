# Marketing Skills for AI Agents

Agent Skills for marketing — paid ads, social media, SEO, AI search, competitor research, ad creative generation, email lifecycle, analytics, operations, and more.

These skills run on the [Hyper MCP](https://www.hyperfx.ai/mcp), which gives your agent 100+ direct integrations and built-in marketing tools through one endpoint — a backpack of tools that travels with your agent across Claude Code, Cursor, Codex, OpenCode, GitHub Copilot, Gemini CLI, and 50+ other agents that support the Agent Skills spec.

---

## What is a skill?

A skill is a markdown file (`SKILL.md`) with the workflows, decision rules, and example tool calls your agent needs to run specific marketing functions end-to-end. The tools themselves come from the Hyper MCP. The skill teaches the agent how to think like an expert and ship correct work.

---

## The Hyper MCP

![Hyper MCP — 200+ integrations and built-in tools](assets/hyper-mcp.png)

Create, customize, and connect your MCP at [app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp). Choose which integrations and built-in tools to include, and configure approval rules action-by-action across every one of them.

What's in it:

- **100+ direct integrations** — ad platforms (Google Ads, Meta, TikTok, LinkedIn, Amazon, Pinterest), social (Instagram, Reddit, Twitter, YouTube), email (Gmail, Klaviyo, Resend, Beehiiv), analytics (GA4, Search Console, BigQuery), CRM (HubSpot, Apollo), commerce (Shopify), and more.
- **Built-in tools** — Meta Ads Library scraper, Reddit and Twitter scrapers, image generation (OpenAI, Nano Banana, Seedream), video generation (Sora, Veo, Seedance), browser automation, transcription.
- **Guardrails and permissions** — every action can require approval before it runs, so your agent can't delete a campaign or send a DM without your green light.
- **The Hyper platform** — build and manage Hyper agents, tasks, and skills directly.

[Walkthrough video.](https://www.youtube.com/watch?v=NZLAdOL9fP8)

---

## Install

```bash
npx skills add hyperfx-ai/marketing-skills
```

Auto-detects your agent and drops the skills in the right directory. Then ask your agent something a skill knows about:

> *"Plan a Google Ads search campaign for [example.com](http://example.com)."*

```bash
# install one
npx skills add hyperfx-ai/marketing-skills --skill google-ads

# install all 24
npx skills add hyperfx-ai/marketing-skills --all
```

[Other install options below.](#other-install-options)

---

## What it looks like

> **You:** Run a viral paid and organic campaign for [acmebakes.com](http://acmebakes.com). Find what's trending in our space on social, generate image and video creatives, and set up and launch ads + organic posts on Meta, Google, and TikTok. $100/day per ad platform.
>
> **Agent:** Learned your brand from [acmebakes.com](http://acmebakes.com) (logo, palette, voice). Scraped 412 Instagram posts, 287 TikToks, and 54 Reddit threads to see what people in artisan baking are talking about. Three trends stand out: sourdough rescue, Dubai-chocolate copycats, school-lunch baking. Two have low keyword competition and rising search volume — targeting those.
>
> Generated 6 image creatives + 2 short videos in your brand style. **Everything's set up and paused** — view each one before setting it live:
>
> - **[Meta](https://adsmanager.facebook.com)** — $100/day, Advantage+ targeting, optimized for the Purchase event on your pixel, US 25–54.
> - **[TikTok Ads](https://ads.tiktok.com)** — $100/day, Traffic objective on the same audience, video creatives.
> - **[Google Ads Search](https://ads.google.com)** — $100/day, phrase + exact match on the two trending opportunities, negative keywords, sitelinks.
> - **TikTok + Instagram organic** — 3 posts queued (also paused), captions matched to trending sounds and hashtags.
>
> Total ad spend: **$300/day** ($100 each on Meta, Google, TikTok).
>
> Tell me when to set them live, and I'll set up a task to monitor them every hour.

That's `meta-ads` + `google-ads` + `tiktok-ads` + `ad-creative-generation` + `video-generation` + `tiktok` + `instagram` composing into one job. Skills can compose like this because they all run against the same MCP — the agent picks the right one per step.

---

## Skills

| Skill | What it does | Required integrations |
|---|---|---|
| **Paid ads** | | |
| [`google-ads`](skills/google-ads) | Plan and launch Google Ads campaigns — Search, Display, and Performance Max — and build GAQL-backed reports and dashboards. | Google Ads |
| [`meta-ads`](skills/meta-ads) | Plan and launch Meta ad campaigns across Facebook and Instagram; audit existing accounts. | Meta Business, Firecrawl |
| [`meta-ads-library`](skills/meta-ads-library) | Research competitor ads in the Meta Ads Library. | Apify |
| [`amazon-ads`](skills/amazon-ads) | Plan and launch Amazon Sponsored Products campaigns. | Amazon Ads |
| [`tiktok-ads`](skills/tiktok-ads) | Plan and launch TikTok ad campaigns across all objectives. | TikTok Marketing |
| [`pinterest-ads`](skills/pinterest-ads) | Plan and launch Pinterest ad campaigns across all objectives. | Pinterest Ads |
| [`reddit-ads`](skills/reddit-ads) | Plan and launch Reddit ad campaigns — promoted posts, subreddit targeting, pixels, reporting. | Reddit Ads |
| [`snapchat-ads`](skills/snapchat-ads) | Plan and launch Snapchat ad campaigns — ad squads, creatives, Snap Pixel, reporting. | Snapchat Ads |
| [`openai-ads`](skills/openai-ads) | Plan and launch OpenAI Ads (ChatGPT ads) — chat card and product-feed creatives, audiences, insights. | OpenAI Ads (API key) |
| **Social media** | | |
| [`tiktok`](skills/tiktok) | Publish videos, photos, and carousels to TikTok. | TikTok (Login Kit) |
| [`instagram`](skills/instagram) | Publish posts, Reels, Stories, and carousels. Moderate comments, send DMs, pull insights. | Instagram (Business Login) |
| [`linkedin`](skills/linkedin) | Publish text, articles, documents, and AI-generated carousels — personal profiles and company pages. | LinkedIn |
| **Research** | | |
| [`seo-research`](skills/seo-research) | Keyword research, SERP and AI Overview analysis, competitor benchmarks, AI search visibility, backlinks, site audits. | HyperSEO toolkit |
| [`competitor-intel`](skills/competitor-intel) | Research competitors end-to-end — site, social, search rank, AI-search citations, mentions — and produce battle cards, weekly digests, or board-prep updates. | Firecrawl + at least one of HyperSEO or Apify scrapers |
| [`customer-research`](skills/customer-research) | Mine Reddit, YouTube comments, G2/Capterra, Twitter, and TikTok to surface what customers actually say — build personas, VOC quote banks, JTBD maps, and synthesis reports. | Apify scrapers toolkit (Reddit, Twitter, YouTube, TikTok, Instagram) |
| [`reddit`](skills/reddit) | Research subreddits, threads, and sentiment — mine questions, pain points, and voice-of-customer. | Reddit scraper |
| [`youtube`](skills/youtube) | Fetch YouTube transcripts, repurpose video content into posts/summaries/chapters, and create thumbnails from proven composition patterns. | YouTube toolkit |
| **Creative** | | |
| [`ad-creative-generation`](skills/ad-creative-generation) | Generate ad copy and on-brand images for Google and Meta placements. | Firecrawl + image gen toolkit |
| [`image-generation`](skills/image-generation) | Generate and edit images — picks the right model for text-heavy creatives, photoreal product shots, or high-res output. | Image gen toolkit |
| [`video-generation`](skills/video-generation) | Generate AI video and prep it for distribution — text/image-to-video, captions, voiceover, stitching, overlays. | Video gen toolkit |
| [`blog-generation`](skills/blog-generation) | Generate one excellent, on-brand blog post per run — a stateful engine that never repeats a topic, built for SEO and AI-search citations. | Firecrawl, HyperSEO, and Google Search Console recommended |
| **Outbound & lifecycle** | | |
| [`cold-email-outreach`](skills/cold-email-outreach) | Run end-to-end B2B cold outreach — prospect, enrich, personalize, send, follow up, route replies. | Gmail + Apollo (Firecrawl + LinkedIn scraper bundled) |
| [`email-lifecycle`](skills/email-lifecycle) | Build welcome, nurture, re-engagement, win-back, and abandoned-cart email programs. | At least one of Klaviyo, Resend, Beehiiv, or Gmail |
| **Analytics** | | |
| [`analytics-insights`](skills/analytics-insights) | Drive GA4, Google Tag Manager, Search Console, and BigQuery from chat — tracking plans, reports, conversions, container audits, BigQuery export queries. | At least one of GA4, GTM, GSC, or BigQuery |
| **Execution** | | |
| [`hyper-cli`](skills/hyper-cli) | Run these marketing skills through the Hyper CLI (beta), translating raw MCP tool names into CLI aliases or raw toolkit calls. | Hyper CLI + the integrations required by the sibling skill |

Invoke explicitly with `/google-ads`, `/cold-email-outreach`, `/seo-research`, etc. — the slash name matches the folder under `skills/`.

---

## Usage

Skill discovery is automatic. The transcript above shows multi-skill composition; smaller asks route to one skill at a time:

> *"Pull all the active Facebook ads for 'meal kit delivery' into a database."*
> → `meta-ads-library`

> *"Run a 50-prospect cold-email campaign to Heads of Growth at US Series A SaaS companies."*
> → `cold-email-outreach`

> *"Pull last month's GA4 traffic by channel and flag any conversion event that dropped >20%."*
> → `analytics-insights`

> *"Build a weekly competitor digest for [comp-a, comp-b, comp-c] — site changes, social, search rank, mentions."*
> → `competitor-intel`

---

## Other install options

```bash
# install globally (available across every project)
npx skills add hyperfx-ai/marketing-skills -s seo-research -g

# Claude Code plugin marketplace
/plugin marketplace add hyperfx-ai/marketing-skills
/plugin install hyper-marketing@hyperfx-marketing-skills

# manual copy
cp -r skills/google-ads ~/.claude/skills/         # Claude Code
cp -r skills/google-ads ~/.agents/skills/         # Cursor / Codex / generic

# git submodule
git submodule add https://github.com/hyperfx-ai/marketing-skills.git .agents/marketing-skills
```

---

## Repo layout

```
marketing-skills/
├── .claude-plugin/plugin.json          # Claude Code plugin manifest
├── .claude-plugin/marketplace.json    # Claude Code plugin marketplace catalog
├── .mcp.json                          # Hyper MCP server config (bundled with plugin)
├── .github/workflows/validate.yml     # CI: validate-skills.sh on PRs
├── skills/                             # one folder per skill
│   ├── <skill>/SKILL.md
│   └── <skill>/references/*.md         # progressive disclosure on larger skills
├── AGENTS.md                           # generic-agent entrypoint
├── CLAUDE.md                           # Claude Code entrypoint
├── CONTRIBUTING.md
└── validate-skills.sh                  # frontmatter + MCP-call lints
```

---

## Built-in tools

| Tool | Description |
|---|---|
| E-commerce Scraper | Scrape product listings, prices, and reviews |
| Firecrawl | Web scraping and crawling |
| Google Search Scraper | Pull Google SERP data |
| Google Trends Scraper | Pull Google Trends data |
| HyperSEO | Keyword research, SERP analysis, AI search visibility |
| Image Generation | Generate images (OpenAI, Nano Banana, Seedream) |
| Instagram Scraper | Scrape Instagram posts, profiles, and engagement |
| Knowledge Base | Query and manage the agent's knowledge base |
| Location Search | Geo and location lookup |
| Meeting Bot | Join, transcribe, and summarize meetings |
| Meta Ads Library | Search, scrape, and download live and historical Meta ads |
| Reddit Scraper | Scrape Reddit posts, threads, and comments |
| TikTok Scraper | Scrape TikTok videos, profiles, and engagement |
| Twitter Scraper | Scrape tweets, profiles, and threads |
| Video Generation | Generate AI video (Sora, Veo, Seedance) |
| Web Scraper | Search and scrape web pages |
| Website Analyzer | Analyze a website's tech stack, pixels, and more |
| YouTube | Search YouTube and fetch transcripts |

## Native Hyper platform tools

| Tool | Description |
|---|---|
| Database | Query and store data |
| Code Execution | Run Python or JavaScript in a sandbox |
| Toolkit Manager | Manage MCP toolkits and connections |
| Skills | Manage and invoke skills |
| Files | Built-in file system — read and write files |
| Planning | Multi-step task planning |
| Todo | Track tasks and progress |
| Web Search | General-purpose web search |
| Browser | Headless browser automation |
| Agents | Create and manage agents (instructions, tasks, skills, context files, Slack channels) |
| Hyper | Workspace, account, and platform-level actions |

---

## Roadmap

Near-term skills and surfaces:

- [x] `hyper-cli` (beta) — run these skills through the Hyper CLI from a terminal, cron job, or shell pipeline.
- [ ] `google-ads-operator` — production Google Ads account operation and optimization.
- [ ] `meta-account-audit` — Meta account diagnostics, spend checks, and performance recommendations.
- [ ] `social-carousel` — carousel planning, copy, and export for social channels.
- [ ] `cmo` — executive marketing reporting and cross-channel performance summaries.
- [ ] `reddit-research` — focused Reddit research workflows for VOC, market maps, and positioning.
- [ ] `slide-generation` — turn research, reports, and campaign plans into presentation decks.
- [ ] `pdf-generation` — generate polished marketing reports and briefs.
- [ ] `copywriting` — general-purpose marketing copy workflows.
- [ ] `lead-generation` — prospect sourcing, enrichment, scoring, and handoff.
- [ ] `crm-revops` — CRM hygiene, routing, attribution, and pipeline operations.
- [ ] `google-sheets-writing` — structured spreadsheet creation and reporting.
- [ ] `gmail-email-management` — inbox triage, labeling, reply drafting, and operational email workflows.
- [ ] `figma` — design workflow support for ad creative, landing pages, and campaign assets.

See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute a skill.

---

### Apps & channels

| Skill | What it does | Needs |
| --- | --- | --- |
| [`gmail`](skills/gmail) | Read, draft, send, and organize Gmail — labels, threads, drafts, attachments. | Gmail |
| [`google-sheets`](skills/google-sheets) | Write structured data to Google Sheets and keep spreadsheets up to date. | Google Sheets |
| [`slack`](skills/slack) | Send Slack messages, share files and images, and work with channels and threads. | Slack |
| [`twilio`](skills/twilio) | Send SMS and WhatsApp messages and manage Twilio messaging workflows. | Twilio |
| [`polymarket-trading`](skills/polymarket-trading) | Research Polymarket prediction markets and manage positions and orders. | Polymarket |

## Contributing

PRs welcome. Every skill must pass `./validate-skills.sh` (frontmatter + MCP-call lint). See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
