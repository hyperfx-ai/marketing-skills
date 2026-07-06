# AGENTS.md

Guidance for AI coding agents (Codex, Cursor, Claude Code, etc.) working in this repository.

## What this repo is

A public collection of marketing-domain Agent Skills that wrap the **Hyper MCP** tool surface. Each skill in [`skills/`](./skills) teaches an agent how to drive Hyper's MCP-exposed tools (Google Ads, Meta, Amazon, TikTok, Pinterest, LinkedIn, HyperSEO, Apify scrapers, image / video generation, Gmail, Apollo, Klaviyo, Resend, Beehiiv, GA4, GTM, Search Console, BigQuery, etc.) for a specific marketing job.

Skills are NOT tools. They are markdown instructions plus optional reference files. The actual tool calls come from the connected Hyper MCP at [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp). The MCP descriptor for each tool is the only source of truth for tool names, arg names, and arg types — never trust skill content over the live MCP catalog when they disagree.

## Available skills

### Foundation

| Skill | What it does |
| --- | --- |
| [`brand-context`](./skills/brand-context) | Build and maintain one `brand-context.md` per brand — positioning, ICP, personas, verbatim customer language, voice, proof points — the hub doc every other skill reads before asking the user brand questions. Auto-drafts from the brand's site (Firecrawl) or via interview. |

### Paid ads

| Skill | What it does |
| --- | --- |
| [`google-ads`](./skills/google-ads) | Plan and create new Google Ads campaigns (Search, Display, Performance Max) using the blueprint flow, plus GAQL-backed reports and dashboards on existing accounts. |
| [`meta-ads`](./skills/meta-ads) | Plan and create Meta (Facebook/Instagram) ad campaigns with Advantage+ as the default; includes an account-audit workflow. |
| [`meta-ads-library`](./skills/meta-ads-library) | Search the Meta Ads Library for competitor ads, optionally enrich with page contact info, and surface structured ad-intelligence summaries inline in chat. |
| [`amazon-ads`](./skills/amazon-ads) | Plan and create Amazon Sponsored Products campaigns with strategic targeting and budget rules. |
| [`tiktok-ads`](./skills/tiktok-ads) | Plan and create TikTok Ads (Traffic, Reach, Conversions, App Promotion, Video View) with strict objective-specific parameter validation. |
| [`pinterest-ads`](./skills/pinterest-ads) | Plan and create Pinterest Ads with microcurrency budgeting, CBO rules, and conversion-tag handling. |
| [`reddit-ads`](./skills/reddit-ads) | Plan and create Reddit Ads campaigns — promoted posts, subreddit / interest / geo targeting, audiences, Reddit pixel conversion tracking, and reporting, with micro-currency budgets. |
| [`snapchat-ads`](./skills/snapchat-ads) | Plan and create Snapchat Ads campaigns — ad squads, media upload, creatives, Snap Pixel conversion tracking, and reporting, with micro-currency budgets and JSON-Patch updates. |
| [`openai-ads`](./skills/openai-ads) | Plan and manage OpenAI Ads (ChatGPT ads) — chat_card and product-feed creatives, geo targeting, custom audiences, conversion tracking, and insights. |

### Organic social publishing

| Skill | What it does |
| --- | --- |
| [`tiktok`](./skills/tiktok) | Publish organic TikTok videos, photos, and carousels through the compliance posting form. |
| [`instagram`](./skills/instagram) | Publish photos / Reels / Stories / carousels, moderate comments and mentions, send DMs, and pull insights from the Instagram API with Instagram Login. |
| [`linkedin`](./skills/linkedin) | Publish LinkedIn text, article, document, organization (company page), and AI text-to-carousel posts. |

### Research

| Skill | What it does |
| --- | --- |
| [`seo-research`](./skills/seo-research) | Data-driven SEO research via the HyperSEO toolkit — keyword research, SERP and AI Overview analysis, competitor benchmarking, content planning, AI search visibility tracking (ChatGPT / Claude / Perplexity), backlink trends, and full site audits. Ships with five reference workflows under `references/`. |
| [`competitor-intel`](./skills/competitor-intel) | End-to-end competitor research and monitoring — pick the set, scrape every public surface (Firecrawl for site/blog/pricing, HyperSEO for rank/backlinks/intersection, Apify scrapers for Instagram / TikTok / LinkedIn / Twitter / Reddit / Google search / Google Trends), diff against last run, and synthesize battle cards / weekly digests / comparison-page input / board-prep updates. Ships with two references under `references/` (per-source playbook, brief templates). |
| [`customer-research`](./skills/customer-research) | Mine Reddit, YouTube comments, G2/Capterra, X/Twitter, and TikTok to surface what customers actually say in their own words. Produces research synthesis reports, VOC quote banks, personas, and JTBD maps. Requires the Apify scrapers toolkit (Reddit, Twitter, YouTube, TikTok, Instagram). Ships with two references under `references/` (per-source playbooks, synthesis templates). |
| [`reddit`](./skills/reddit) | Research subreddits, threads, and sentiment — mine questions, pain points, and voice-of-customer from Reddit. |
| [`youtube`](./skills/youtube) | Fetch YouTube transcripts and AI-powered video extraction (`youtube_video_transcripts_fetch`, `youtube_videos_read`), repurpose video content, and create thumbnails with the bundled scripts and composition references. Requires the YouTube toolkit. |

### Creative output

| Skill | What it does |
| --- | --- |
| [`ad-creative-generation`](./skills/ad-creative-generation) | End-to-end ad creative pipeline — brand extraction (Firecrawl) → ad copy variants → on-brand images for Google RSAs, Display, Performance Max, Meta feed / story / carousel, and other paid placements. Ships with four reference workflows under `references/`. |
| [`image-generation`](./skills/image-generation) | Tool-selection guide for the bundled image models — OpenAI (`gpt-image-2`), Nano Banana (Gemini 3 Pro / 2.5 Flash), Seedream (ByteDance via fal.ai) — for ad creatives, branded compositions, photoreal product shots, image-to-image edits, and high-resolution output. |
| [`video-generation`](./skills/video-generation) | End-to-end AI video — text-to-video / image-to-video (Sora, Veo, Seedance), scene chaining, video analysis, transcription, subtitles, TikTok / karaoke captions, voiceover (TTS), audio mixing, clipping, stitching, and text overlays. |
| [`blog-generation`](./skills/blog-generation) | Generate one excellent, on-brand blog post per run — a stateful engine (reads a brand strategy doc, never repeats a topic) built to rank on Google and get cited by AI search. Firecrawl / HyperSEO / Search Console recommended. |

### Outbound & lifecycle

| Skill | What it does |
| --- | --- |
| [`cold-email-outreach`](./skills/cold-email-outreach) | End-to-end B2B cold outreach — Apollo prospect search and email enrichment, Firecrawl + LinkedIn-scraper personalization signals, Gmail drafting / sending / threading, multi-touch follow-up cadences, and reply routing via Gmail labels. Ships with three reference workflows under `references/` (frameworks, follow-ups, deliverability). |
| [`email-lifecycle`](./skills/email-lifecycle) | Welcome / nurture / re-engagement / win-back / abandoned-cart sequences across Klaviyo (ecom), Resend (SaaS / dev tools), Beehiiv (newsletters), and Gmail (small lists). Provider-selection guidance, audience setup, sequence build, launch, and measurement. Ships with two references under `references/` (cross-provider sequence patterns and per-provider tool-call mechanics). |

### Analytics

| Skill | What it does |
| --- | --- |
| [`analytics-insights`](./skills/analytics-insights) | Drive Google Analytics (GA4), Google Tag Manager, Google Search Console, and BigQuery from chat — tracking-plan design, key-event (conversion) management, custom dimensions / metrics, GA4 reports, GTM container audits, GSC search performance, and queries against the GA4 BigQuery export. Ships with three references under `references/` (GA4 tracking plan, GTM audit, BigQuery GA4 export). |

### Execution

| Skill | What it does |
| --- | --- |
| [`hyper-cli`](./skills/hyper-cli) | Bridge skill for running the marketing skills through `hyperai`, including how to translate raw MCP tool names into CLI aliases or raw toolkit calls. |

### Apps & channels

| Skill | What it does |
| --- | --- |
| [`gmail`](./skills/gmail) | Read, draft, send, and organize Gmail — labels, threads, drafts, and attachments. |
| [`google-sheets`](./skills/google-sheets) | Write structured data to Google Sheets and keep spreadsheets up to date. |
| [`slack`](./skills/slack) | Send Slack messages, share files and images, and work with channels and threads. |
| [`twilio`](./skills/twilio) | Send SMS and WhatsApp messages and manage Twilio messaging workflows. |

## Adding or editing a skill

1. Each skill lives in `skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`).
2. `name` MUST match the folder name.
3. `description` MUST contain a "Use when…" trigger phrase, 50–500 chars.
4. SKILL.md MUST be ≤500 lines. Move long-form material into a sibling `references/` folder.
5. SKILL.md MUST contain a `## Requirements` section pointing at `https://app.hyperfx.ai/mcp`.
6. Run `./validate-skills.sh` before opening a PR. CI runs the same check.

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for details.

## Repo conventions

- **Tool names are referenced verbatim from the Hyper MCP.** When citing or editing a tool name in a skill, verify it against the live MCP catalog (the `<tool-name>.json` schema files exposed by the connected MCP server). The MCP descriptor wins over codebase function names, prior skill content, or memory.
- **CLI aliases are a separate surface.** Marketing skills usually name raw MCP tools like `gmail_send_message`; the Hyper CLI may expose that as `gmail messages send`. Use `hyper-cli` for CLI execution guidance and always inspect the live CLI schema before calling.
- **Allowed Hyper URLs in skill bodies:** only `app.hyperfx.ai/mcp` and `app.hyperfx.ai/apps`. No other Hyper URLs.
- **No internal infra references.** No `hyper_cache_*` table names hardcoded into skills (the cache table name is workspace-specific — instruct agents to read it from the tool description or error `suggestion` field instead). No internal filesystem paths. No template ids that aren't part of the public MCP surface.
- **Conditional integrations.** Some tools only appear when the underlying integration is enabled in the user's Hyper workspace (LinkedIn scraper is the canonical example). Skills citing such tools must mark them conditional and gracefully skip the affected step rather than failing the whole workflow.
- **Self-contained skills.** If two skills overlap, add an "Out of scope" section pointing at the right sibling rather than duplicating workflow.
- **Microcurrency.** Pinterest Ads budgets and bids are in microcurrency (`$1.00 = 1,000,000` microdollars). Skills that touch budget fields must convert.

## How an agent should use these skills

1. Read the matching `SKILL.md` from `skills/<name>/SKILL.md`.
2. Confirm the Hyper MCP is connected — every skill defines a "stop and tell the user" check at the top.
3. Follow the workflow defined in the skill's body.
4. Cross-reference sibling skills via the "Out of scope" table when relevant.
5. When a tool call fails with an arg-validation error, re-read the MCP tool descriptor before retrying — don't blindly retry with the same args.
