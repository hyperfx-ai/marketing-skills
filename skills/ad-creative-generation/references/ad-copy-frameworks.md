# Ad Copy Frameworks

Frameworks for writing ad copy variants and structuring A/B tests.

> **Before writing any copy:**
> - Use only verified proof points: section 10 of `brand-context.md` or facts the user confirmed. Never invent ratings, customer counts, or results. The numbers and quotes in the examples below are placeholders showing the pattern, not claims to reuse.
> - Honor the brand voice: words to use and words to ban are hard constraints.
> - Respect platform character limits in `meta-ads-creatives.md` and `google-ads-creatives.md`.

## Hook Patterns

The hook is the first line of ad copy — it determines whether someone keeps reading. Each pattern works differently depending on audience and offer.

### Number-Led Hook
Leads with a specific, concrete number. High CTR when the number is surprising or aspirational.

- "Cut your onboarding time from 3 weeks to 3 days"
- "47% of teams switch within the first month"
- "Save 12 hours per week on reporting"

### Question Hook
Opens with a question that the target audience would answer "yes" to. Creates immediate relevance.

- "Still manually reconciling invoices every month?"
- "What if your team could ship 2x faster?"
- "Tired of tools that promise AI but deliver spreadsheets?"

### Pain-Point Hook
Names a specific frustration the audience experiences. Works best for problem-aware audiences.

- "Your CRM shouldn't need a full-time admin"
- "Scattered tools. Missed deadlines. Sound familiar?"
- "Manual data entry is costing you more than you think"

### Benefit-First Hook
Leads with the outcome, not the problem. Works for solution-aware audiences.

- "Automate your entire onboarding workflow in one click"
- "Get real-time insights without writing a single query"
- "Ship landing pages in minutes, not sprints"

### Social Proof Hook
Opens with credibility — customer results, user count, or testimonials. Use this hook only when the proof is verified.

- "Join [verified customer count] teams that ditched manual reporting"
- "'[verbatim customer quote with a real result]' — [named customer]"
- "Rated [verified rating] on [review site] for ease of use"

## Body Frameworks

### Problem-Agitate-Solve (PAS)
1. State the problem
2. Amplify the pain
3. Present the solution

Best for: Cold audiences, pain-point messaging

### Feature-Advantage-Benefit (FAB)
1. Name the feature
2. Explain what it enables
3. State the outcome for the user

Best for: Product-aware audiences, feature launches

### Before-After-Bridge (BAB)
1. Describe current state (before)
2. Describe desired state (after)
3. Show how to get there (bridge = your product)

Best for: Aspirational messaging, transformation offers

## CTA Types

| CTA | Best For | Tone |
|-----|----------|------|
| Learn More | Top of funnel, awareness | Low commitment |
| Shop Now | E-commerce, product pages | Direct, transactional |
| Get Started | SaaS, free trial | Action-oriented |
| Try Free | Freemium, risk removal | Low barrier |
| Book a Demo | Enterprise, high-ticket | Consultative |
| Sign Up | Membership, newsletters | Simple commitment |
| Get Offer | Promotions, limited time | Urgency |
| Download | Lead magnets, resources | Value exchange |

Match CTA to funnel stage. Don't use "Shop Now" for awareness campaigns or "Learn More" for retargeting.

## Variant Generation Strategy

### The One-Variable Rule

Each variant should change exactly one element from the control. This lets you attribute performance differences to specific changes.

**Example from a winning control ad:**
> Hook: "Cut your onboarding time from 3 weeks to 3 days"
> Body: Customer quote about time savings
> CTA: "Get Started Free"

**Variant set (8 variants):**

Hook variants (change hook, keep body + CTA):
1. Different metric: "Reduce support tickets by 60% in 30 days"
2. Different metric: "Onboard new hires in hours, not weeks"
3. Question-based: "What if onboarding took 3 days instead of 3 weeks?"
4. Pain-point: "3-week onboarding is costing you your best hires"

Body variants (change body, keep hook + CTA):
5. Feature highlight instead of social proof
6. Stat-driven instead of quote-driven

CTA variants (change CTA, keep hook + body):
7. "Book a Demo" instead of "Get Started Free"
8. "See How It Works" instead of "Get Started Free"

### Variant Grouping

Always group and label variants by what's being tested:

```
GROUP A: Hook Testing (4 variants)
  - A1: Number-led (different metric)
  - A2: Number-led (different framing)
  - A3: Question-based hook
  - A4: Pain-point hook

GROUP B: Body Testing (2 variants)
  - B1: Feature-focused body
  - B2: Data-driven body

GROUP C: CTA Testing (2 variants)
  - C1: Higher-commitment CTA
  - C2: Curiosity-driven CTA
```

### A/B Test Pairing

Pair variants for testing so each pair isolates one variable:

| Test | Control Element | Test Element | Variable |
|------|----------------|-------------|----------|
| Test 1 | Number-led hook | Question hook | Hook type |
| Test 2 | Customer quote body | Feature body | Body approach |
| Test 3 | "Get Started Free" CTA | "Book a Demo" CTA | CTA commitment level |

### Test Priority

Prioritize testing based on which element has the most variance in existing performance data:

1. **Hooks first** — highest impact on CTR. If top ads have wildly different hook styles, test hooks.
2. **Body second** — impacts conversion rate. Test if CTR is stable but CVR varies.
3. **CTA last** — smallest effect size. Test when hook and body are optimized.

## Analyzing Existing Ad Performance

When the user provides performance data from existing ads:

1. **Correlate metrics with copy elements** — which hook types get highest CTR? Which body styles drive CVR?
2. **Identify winning patterns** — not just the best ad, but what pattern the top 3-5 ads share
3. **Find the gap** — what hasn't been tested yet? If all top ads use number-led hooks, a question hook is worth testing
4. **Preserve winners, vary strategically** — new variants should keep the winning pattern and change one thing

## Output Format

When delivering ad copy variants, always include:

1. Variants grouped by test variable (hook, body, CTA)
2. Annotation showing which winning element each variant preserves
3. Recommended test priority
4. Platform-specific formatting (character limits respected)
5. A/B test pairings showing which variants to test against each other
