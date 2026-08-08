---
name: writing
description: "Writing style library and quality gate for all prose — cold emails, ads, landing pages, memos, blog posts, docs, UI copy. Routes each deliverable to a named writing system (BLUF / Minto, PAS, AIDA, Smart Brevity, inverted pyramid, classic style, plain language, Diátaxis) with hard checkable rules, then runs a lint pass that strips AI tells. Use when the user asks to write, rewrite, edit, or tighten any copy, or when another skill produces prose."
metadata:
  version: 1.0.0
icon: hyper
short_description: Route any prose to a named writing system with checkable rules, then lint out the AI tells.
---

# Writing

Almost every skill in this collection ends in prose: an email, an ad, a post, a report. This skill is the layer that makes that prose good. It works as a router plus a quality gate. First classify the deliverable, then apply one named writing system with hard, checkable rules, then run a lint pass that removes the tells of machine writing. Never invent a style ad hoc — enforce a documented one, and tell the user which one you used.

Two principles run through everything here:

1. **"Write well" is not a rule; "no sentence over 25 words" is.** Every system in this skill is expressed as rules you can check a draft against. If you cannot point to the sentence that breaks a rule, the rule does not belong in the system.
2. **Structure and voice are separate layers.** The writing system governs structure: what comes first, how ideas are ordered, how long things run. Brand voice governs vocabulary, tone, and stance. You can write a BLUF memo in a playful voice or a formal one — the skeleton is the same.

## Requirements

- **Hyper MCP connected.** https://app.hyperfx.ai/mcp — this skill needs no specific toolkit. Drafting, editing, and linting use your file tools.
- **Recommended: a `brand-context.md`** built by the `brand-context` skill. Read it before drafting anything customer-facing. If it does not exist, ask two questions (who is the reader, what should they do after reading) rather than guessing.
- **Optional: Firecrawl**, to pull source material or examples the user points at by URL.

## Tool surface

| Job | Tools |
| --- | --- |
| Read and write drafts, read `brand-context.md` | your file tools (`read_file`, `create_file`, `edit_file`) |
| Pull source material or examples from URLs | `firecrawl_urls_scrape`, `web_scrape_page` |

## Out of scope: defer to other skills

This skill is about how to write, not what to publish or research. When the request is one of these, hand off:

| Request | Send them to |
| --- | --- |
| A full SEO blog post, topic selection, ranking strategy | `blog-generation` |
| Prospecting, sending, sequencing cold email | `cold-email-outreach` (use this skill for the copy itself) |
| Publishing to LinkedIn / Instagram / TikTok | `linkedin`, `instagram`, `tiktok` |
| Ad copy tied to creative production and campaign setup | `ad-creative-generation` |
| Building the brand voice doc itself | `brand-context` |
| Finding real customer language to write with | `customer-research` |

## The workflow

Run these steps in order for every writing or editing request.

**Step 1: Classify the deliverable.** What is it (email, memo, post, doc page), who reads it, and what should they do after reading? If the user's request answers these, do not ask. If the reader or the desired action is genuinely unknown and changes the writing, ask once.

**Step 2: Pick one system from the style map below.** One deliverable, one system. Name it to the user in one line ("Writing this as a BLUF memo"). If the user names a system themselves, use theirs.

**Step 3: Read the reference file for that system.** Each reference holds the hard rules and before/after examples. Do not draft from memory of the system's name.

**Step 4: Read `brand-context.md` if it exists.** Voice, banned words, and proof points come from there. The system's rules never override the brand's banned-word list.

**Step 5: Draft to the rules.** Apply the system's hard rules while writing, not as an afterthought.

**Step 6: Lint.** Run the full pass in [`references/lint-and-humanize.md`](references/lint-and-humanize.md) — the universal rules plus the AI-tell ban list. Fix every violation before showing the draft. This step is not skippable, including for "quick" edits.

**Step 7: Deliver.** Show the draft. State in one line which system you used. If the user asked for a rewrite, show what changed and why in two or three bullets, not a lecture.

When the request is **edit / tighten / "make this sound human"** rather than write-from-scratch: go to Step 6 and run the editing passes in the lint reference against the user's text — but still identify which system the text wants to be (Step 2). A limp cold email usually fails as PAS, not as prose in general.

## The style map

| Deliverable | System | Reference |
| --- | --- | --- |
| Cold email, outreach message | PAS | [`copywriting.md`](references/copywriting.md) |
| Landing page hero + sections | PAS or BAB | [`copywriting.md`](references/copywriting.md) |
| Ad copy (search, social, display) | AIDA + direct-response rules | [`copywriting.md`](references/copywriting.md) |
| Product / feature announcement | Smart Brevity | [`business-writing.md`](references/business-writing.md) |
| Press release | Inverted pyramid | [`business-writing.md`](references/business-writing.md) |
| Exec memo, status update, report | BLUF / Minto pyramid | [`business-writing.md`](references/business-writing.md) |
| Proposal, pitch, one-pager | SCQA | [`business-writing.md`](references/business-writing.md) |
| Case study | SCQA opening + BAB body | [`business-writing.md`](references/business-writing.md) |
| Newsletter | Smart Brevity | [`business-writing.md`](references/business-writing.md) |
| Blog post, essay, thought leadership | Classic style | [`prose-style.md`](references/prose-style.md) |
| Founder / personal social post | Classic style, compressed | [`prose-style.md`](references/prose-style.md) |
| Docs: tutorial, how-to, reference, explanation | Diátaxis + plain language | [`technical-writing.md`](references/technical-writing.md) |
| UI copy, error messages, empty states | UX microcopy | [`technical-writing.md`](references/technical-writing.md) |
| Spec, requirements, API contract | RFC requirement keywords | [`technical-writing.md`](references/technical-writing.md) |
| Operator instructions, step-by-step procedures | Controlled technical English | [`technical-writing.md`](references/technical-writing.md) |

Two systems can share one piece (a case study opens SCQA and closes with a CTA written to direct-response rules). Never more than two, and say which governs which section.

## The universal lint pass (summary)

The full pass with examples and the editing sweeps is in [`references/lint-and-humanize.md`](references/lint-and-humanize.md). The ten rules every draft must survive, regardless of system:

1. The point of the piece appears in the first two sentences.
2. No sentence over 25 words unless it earns it; never two in a row.
3. Active voice unless the actor is truly unknown or irrelevant.
4. Every claim is concrete: a number, a name, an example — or it goes.
5. Cut hedges (`quite`, `fairly`, `somewhat`, `arguably`) unless the hedge is the point.
6. Verbs over nominalizations: "we decided," not "a decision was made."
7. One idea per paragraph; the first sentence of each paragraph states it.
8. No filler openers: "It's worth noting," "In today's world," "As we all know."
9. The last line tells the reader what to do or what happens next.
10. Zero entries from the AI-tell ban list (see the reference).

## Working with brand voice

- The system decides structure. `brand-context.md` decides words, tone, and proof.
- On conflict, brand voice wins on word choice; the system wins on ordering and length.
- If the brand's own voice examples violate the lint pass (marketing sludge in, marketing sludge out), flag it once and follow the lint pass — the user can overrule.
