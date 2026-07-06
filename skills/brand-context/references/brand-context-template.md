# brand-context.md — template, section guidance, and interview bank

This file has three parts: the copy-paste template, per-section guidance on what a good entry looks like, and the interview question bank for the conversational path.

Rules that apply to every section:

- **Evidence or empty.** Fill a section from the site, from the user, or from real research. If none of those cover it, write `*(unverified — needs input)*` and move on.
- **Attribute quotes.** Every verbatim customer quote carries a source in parentheses.
- **Write for a stranger.** The reader of this doc is an agent (or teammate) with zero context. No internal shorthand.

---

## Part 1: the template

```markdown
# Brand Context: [Business name]

Last updated: [YYYY-MM-DD]
Primary site: [url]

## 1. Product overview
- What it is: [one sentence, plain language]
- What it does: [the 2–4 jobs it does for the customer]
- Category: [the market category the buyer would name]
- One-liner: "[Brand] is a [category] for [audience] that [core value]."
- Business model: [SaaS / ecom / services / marketplace...; price range]

## 2. Target audience / ICP
- Ideal customer: [specific — role/segment, company size or demographic, situation]
- Buying trigger: [what is happening in their world when they start looking]
- NOT for: [who should not buy; where the product is a bad fit]

## 3. Personas
### [Persona name — role]
- Who: [role, context]
- Trigger: [what pushes them to look for a solution]
- Cares about: [their success criteria]
- Blocked by: [what stops them from buying]
[repeat for 2–4 personas; mark buyer vs. user where they differ]

## 4. Pain points (ranked)
1. [the pain that most reliably drives purchase]
2. [...]
3. [...]

## 5. Competitive landscape
| Alternative | Type | Why prospects consider it |
| --- | --- | --- |
| [Competitor A] | direct | [...] |
| [Competitor B] | direct | [...] |
| [Spreadsheets / agency / in-house / do nothing] | status quo | [...] |

## 6. Differentiation
- vs [Competitor A]: [why customers pick us]
- vs [status quo]: [why change at all]
- Only-we claim: [what only this brand can truthfully say — if nothing, say so]

## 7. Objections & switching
- Common objections: [price? trust? migration? "we already have X"?] — with the honest answer to each
- Switching cost: [what moving to us actually requires]
- Deal killers: [what makes prospects walk away]

## 8. Customer language (verbatim — do not paraphrase)
### About the problem
- "[exact quote]" (source: [G2 review / sales call / r/subreddit / support ticket], [date])
### About the product
- "[exact quote]" (source: [...])
### Words customers use that we don't
- [terms from their world that marketing copy should adopt]

## 9. Brand voice
- Tone: [e.g., plainspoken, dry, warm, technical]
- Reading level / register: [e.g., smart peer, no corporate speak]
- Point of view: [first person plural? direct address? opinionated or neutral?]
- Words we use: [...]
- Words we ban: [...]
- Reference sample: [link or paste of one on-voice paragraph the user endorses]

## 10. Proof points (verified only, dated)
- [metric or named customer or credential] (verified [YYYY-MM], source: [user / case study url])
- [...]

## 11. Goals & current focus
- This quarter: [the metric marketing is trying to move]
- Priority channels: [where effort goes now]
- Explicitly not doing: [channels/tactics deliberately parked]

## 12. Assets & channels
- Site: [url] · Blog: [url] · Docs: [url]
- Social: [handles per platform]
- Ad accounts in play: [platforms]
- Visual identity: [primary colors, typography, logo notes — from firecrawl_branding_extract if run]
- Other docs: [link to blog-strategy.md or other per-skill files if they exist]
```

---

## Part 2: what good looks like, per section

**1. Product overview.** The one-liner is the hardest and most valuable line in the doc. Test: could a stranger read only that line and correctly explain the product to someone else? "AI-powered platform that transforms your workflow" fails; "Hyper is a marketing-execution MCP that lets an AI agent run your ad accounts, SEO tools, and email from chat" passes. Category should be the words a *buyer* would type into Google, not the brand's invented category.

**2. ICP.** Specificity is the whole game. Push past the first answer: "marketers" → "the one growth person at a seed-stage B2B SaaS who runs paid, email, and content alone." The **NOT for** line is equally load-bearing — it keeps downstream skills from writing copy that attracts bad-fit leads.

**3. Personas.** 2–4, no more. Separate the economic buyer from the daily user when they differ; cold email targets the former, onboarding content the latter. Each persona needs a *trigger* — personas without triggers produce copy with no urgency.

**4. Pain points.** Ranked by what drives *purchase*, not what customers complain about most. Phrase each as the customer experiences it ("I can't tell which campaigns actually made money"), not as the product answers it ("lack of attribution").

**5. Competitive landscape.** Always include the status-quo row — for most brands the real competitor is a spreadsheet, an agency, or doing nothing. When `competitor-intel` or `seo-research` data is available, prefer it over the user's guess about who they compete with (search results reveal who prospects actually compare).

**6. Differentiation.** Per-alternative, not a generic strengths list — "why us over X" differs by X. The **only-we claim** must survive the test: could a competitor truthfully say the same sentence? If yes, it isn't differentiation. If no only-we claim exists, record that honestly; downstream copy then leads with proof and voice instead of claims.

**7. Objections & switching.** Source these from the user (sales calls, churn reasons) — the site never admits them. Each objection gets the *honest* answer, including "that's a real limitation"; downstream skills need to know what not to promise.

**8. Customer language.** The most valuable section and the one most tempting to fake. Only verbatim quotes with sources. Good sources: reviews (G2, Capterra, app stores, Amazon), Reddit threads, sales-call notes the user pastes, support tickets, social comments. If the user has none, offer to run `customer-research` to mine them. Downstream, these phrases become headlines, subject lines, and hooks — a real "I was drowning in carrier spreadsheets" beats any invented tagline.

**9. Brand voice.** Extract, don't prescribe. From the site's best pages (or the user's favorite piece of their own writing), name the tone in plain adjectives and — most enforceable — build the two word lists. "Words we ban" should include the AI-tells and corporate clichés the user hates; downstream skills treat both lists as hard constraints. Always capture one endorsed reference sample: a paragraph outranks any adjective list.

**10. Proof points.** Verified only, dated, with source. If the user says "around 2,000 customers," record "~2,000 customers (per founder, 2026-07)". A proof point that turns out false poisons every asset that cited it — when in doubt, leave it out.

**11. Goals & current focus.** Keeps downstream skills pointed at the right job (if the quarter is about activation, blog and email skills should skew toward onboarding content, not top-of-funnel). The **explicitly not doing** line prevents well-meaning suggestions the user has already ruled out.

**12. Assets & channels.** Pure logistics, but it's what lets skills act without asking: which handles to post to, which ad accounts exist, where the blog lives. Link out to per-skill files (like `blog-generation`'s `blog-strategy.md`) rather than duplicating their contents.

---

## Part 3: interview question bank (Path B)

Ask conversationally, a few at a time, in this order — each block builds on the previous. Let the user skip; record skips as `*(unverified — needs input)*`.

**Block 1 — product & customer (never skip):**
- What do you sell, in one sentence you'd say to a stranger at a party?
- Who buys it? Be specific — role, company size or life situation, what's going on for them when they come looking.
- Who is it *not* for?
- What would they do if you didn't exist?

**Block 2 — why you win:**
- Who do you lose deals to, and why? Who do you win against, and why?
- What's the one thing you can say that no competitor truthfully can?
- What's the most common reason a good-fit prospect *doesn't* buy?

**Block 3 — their words:**
- Do you have reviews, call notes, or messages where customers describe the problem in their own words? Paste a few. (If not: offer `customer-research`.)
- What's the best thing a customer ever said about you, verbatim?
- What words do customers use for what you do that you'd never put on your site?

**Block 4 — voice & proof:**
- Show me a piece of your own writing that sounds like you. What words or phrases do you never want to see in your marketing?
- What real numbers, customer names, or credentials can we use publicly? Are they current?

**Block 5 — focus & logistics:**
- What's the one marketing number you're trying to move this quarter? Which channels are you betting on — and which are you deliberately ignoring?
- Site, blog, social handles, ad accounts — what exists and where?

After each block, reflect the answers back in template form and save incrementally, so a half-finished interview still leaves a usable doc.
