# Google Ads Creatives

Specs and guidelines for generating Google Ads creative assets.

## Responsive Search Ads (RSAs)

RSAs are Google's primary text ad format. You provide multiple headlines and descriptions; Google assembles combinations and optimizes.

### Asset Requirements

| Asset | Count | Character Limit | Notes |
|-------|-------|----------------|-------|
| Headlines | Up to 15 | 30 characters each | At least 3 required, 15 recommended |
| Descriptions | Up to 4 | 90 characters each | At least 2 required, 4 recommended |

### Headline Rules

- Max 30 characters including spaces
- No exclamation marks in headlines (Google policy)
- No excessive capitalization (e.g., "FREE SHIPPING" is rejected)
- Include the target keyword in at least 2-3 headlines
- Each headline should be able to stand alone (Google may show any combination)
- Don't repeat the same message across headlines — each should offer a different angle

### Headline Strategy (15 headlines)

Distribute across these categories:

| Category | Count | Examples |
|----------|-------|---------|
| Keyword-focused | 3-4 | Include primary and secondary keywords |
| Benefit-driven | 3-4 | "Save 10 Hours Per Week", "Reduce Costs by 40%" |
| Feature-specific | 2-3 | "AI-Powered Analytics", "Real-Time Dashboards" |
| CTA-oriented | 2-3 | "Start Free Trial Today", "Get a Demo" |
| Social proof | 1-2 | "Trusted by 5,000+ Teams", "4.8★ on G2" |
| Urgency/offer | 1-2 | "Limited Time Offer", "Free for 14 Days" |

### Description Rules

- Max 90 characters including spaces
- Expand on what headlines introduce — don't repeat them
- Include a clear value proposition
- End with a CTA when possible
- First description is shown most often — make it strongest

### Description Strategy (4 descriptions)

1. **Primary value prop** — the core reason to click (shown most often)
2. **Feature + benefit** — specific capability and its outcome
3. **Social proof / credibility** — results, ratings, customer count
4. **CTA + offer** — what they get and how to get it

### Pin Positions

You can pin specific headlines / descriptions to positions:

- **Pin sparingly** — pinning reduces Google's optimization ability
- **Pin your brand** to Headline 1 if brand recognition matters
- **Pin your CTA** to Headline 3 to ensure it always appears
- Never pin all positions — defeats the purpose of RSAs

## Display Ads

### Responsive Display Ads

Google's responsive display format assembles your assets into ads across the Display Network.

| Asset | Spec | Count |
|-------|------|-------|
| Landscape image | 1200x628 (1.91:1) | Up to 15 |
| Square image | 1200x1200 (1:1) | Up to 15 |
| Logo (landscape) | 1200x300 (4:1) | Up to 5 |
| Logo (square) | 1200x1200 (1:1) | Up to 5 |
| Short headline | 30 characters | Up to 5 |
| Long headline | 90 characters | 1 |
| Description | 90 characters | Up to 5 |
| Business name | 25 characters | 1 |

### Image Guidelines

- File size: max 5MB
- No text overlays covering more than 20% of the image
- High contrast between subject and background
- Product or service should be clearly visible
- Avoid borders or excessive whitespace

### Generating Display Ad Images

Every creative needs three layers: **brand** (logo), **copy** (headline), and **product** (realistic screenshot). Use `brand.screenshot.description` to describe the actual product UI.

Square (1:1):

```python
images_generate(
    requests=[{
        "prompt": (
            "Display ad creative for [company name]. "
            "Logo at top. Headline: '[headline]'. "
            "Below: realistic product screenshot of [describe actual UI from brand.screenshot.description]. "
            "Match the brand style from the references."
        ),
        "reference_images": [brand.logo.file_id, brand.screenshot.file_id]
    }],
    quality="high"
)
```

Landscape (1.91:1):

```python
images_generate(
    requests=[{
        "prompt": (
            "Wide display ad creative for [company name]. "
            "Logo at top left. Headline: '[headline]'. "
            "Right side: realistic product screenshot of [describe actual UI]. "
            "Match the brand style from the references."
        ),
        "reference_images": [brand.logo.file_id, brand.screenshot.file_id]
    }],
    quality="high"
)
```

## Performance Max

Performance Max campaigns use all Google surfaces. Asset requirements are a superset of RSA + Display.

### Additional Assets for PMax

| Asset | Spec |
|-------|------|
| YouTube video | Various aspect ratios, 10s-60s recommended |
| Portrait image | 960x1200 (4:5) |
| Call to action | Select from predefined list |
| Sitelinks | Up to 4 |

### Asset Group Strategy

- Each asset group should target a distinct audience theme
- Provide maximum assets per group for best optimization
- Use high-quality images that represent the product / service
- Include both lifestyle and product-focused images

## Google Ads Copy Rules

### Policies to Follow

- No misleading claims or exaggeration
- No exclamation marks in headlines
- No ALL CAPS (except standard acronyms like "AI", "CRM")
- No phone numbers in ad text
- No trademarked terms without authorization
- Prices and discounts must be accurate and current
- Landing page must match the ad's offer

### Quality Score Factors

Ad copy directly impacts Quality Score:

1. **Relevance** — copy must match the target keyword intent
2. **Expected CTR** — compelling copy improves predicted click-through
3. **Landing page experience** — ad promise must be fulfilled on the page

Write copy that closely matches what users are searching for and what the landing page delivers.
