# Meta Ads Creatives

Specs and guidelines for generating Meta (Facebook / Instagram) ad creative assets.

## Text Specs

### Primary Text

The main body text that appears above the image / video.

| Metric | Limit |
|--------|-------|
| Visible before "See more" | ~125 characters |
| Maximum length | 2,200 characters |
| Recommended | 125 characters or fewer |

The first 125 characters are critical — everything after is truncated behind "See more". Front-load the hook and value proposition.

### Headline

Appears below the image, next to the CTA button.

| Metric | Limit |
|--------|-------|
| Recommended | 40 characters |
| Maximum | 255 characters (truncated on most placements) |

Keep headlines punchy. They compete with the CTA button for attention.

### Description

Appears below the headline on some placements (not always shown).

| Metric | Limit |
|--------|-------|
| Recommended | 30 characters |
| Maximum | 125 characters |

Don't rely on the description for critical info — it's often hidden.

## Image Specs by Placement

### Feed Ads (Facebook + Instagram)

| Spec | Requirement |
|------|-------------|
| Aspect ratio | 1:1 (recommended) or 4:5 |
| Resolution | 1080x1080 (1:1) or 1080x1350 (4:5) |
| File type | JPG or PNG |
| Max file size | 30MB |
| Text overlay | Less than 20% of image area |

4:5 takes more vertical space in the feed, increasing visibility. Use 1:1 for broad compatibility.

### Story / Reel Ads (Facebook + Instagram)

| Spec | Requirement |
|------|-------------|
| Aspect ratio | 9:16 |
| Resolution | 1080x1920 |
| File type | JPG or PNG (image), MP4 or MOV (video) |
| Max file size | 30MB (image), 4GB (video) |
| Safe zone | Keep key content in center 1080x1420 area |

Leave ~250px clear at top (profile bar) and bottom (CTA bar).

### Right Column (Facebook Desktop)

| Spec | Requirement |
|------|-------------|
| Aspect ratio | 1:1 |
| Resolution | 1080x1080 |
| Note | Small placement, image must be clear at small size |

### Audience Network

| Spec | Requirement |
|------|-------------|
| Aspect ratio | 9:16 |
| Resolution | 1080x1920 |

## Carousel Ads

Carousel ads display up to 10 scrollable cards, each with its own image, headline, description, and link.

### Card Specs

| Spec | Requirement |
|------|-------------|
| Cards | 2-10 |
| Aspect ratio | 1:1 (required for carousel) |
| Resolution | 1080x1080 per card |
| Headline per card | 40 characters recommended |
| Description per card | 20 characters recommended |
| Link per card | Each card can link to a different URL |

### Carousel Strategies

- **Product showcase** — each card features a different product
- **Feature walkthrough** — each card explains one feature / benefit
- **Story arc** — cards tell a sequential story that builds to a CTA
- **Social proof series** — each card shows a different testimonial
- **Before / after** — alternate between problem and solution cards

### Generating Carousel Images

Generate all cards in a single batch. Each card should have the brand logo, a short headline for that card's feature, and a relevant product screenshot.

```python
images_generate(
    requests=[
        {"prompt": "Card 1 for [company]. Logo at top. Headline: '[feature 1]'. Below: product screenshot showing [feature 1 UI]. Match brand style.", "reference_images": [logo_id, screenshot_id]},
        {"prompt": "Card 2 for [company]. Logo at top. Headline: '[feature 2]'. Below: product screenshot showing [feature 2 UI]. Same style as card 1.", "reference_images": [logo_id, screenshot_id]},
        {"prompt": "Card 3 for [company]. Logo at top. Headline: '[feature 3]'. Below: product screenshot showing [feature 3 UI]. Same style as card 1.", "reference_images": [logo_id, screenshot_id]},
    ],
    quality="high"
)
```

## Creative Best Practices

### Image Creative

- **Show the product in use** — context beats isolation
- **One clear focal point** — don't overcrowd the image
- **Contrast with the feed** — bright images stand out against grey / white feeds
- **Brand colors in the image** — not just in copy, in the visual itself
- **Faces perform well** — human faces increase engagement
- **Avoid stock photo aesthetics** — authenticity outperforms polish

### Copy + Creative Alignment

The image and copy must tell the same story:

- If the hook mentions a number, the image should reinforce it
- If the body talks about ease, the image should feel simple and clean
- CTA in copy should match the CTA button selected

### Platform Differences

**Facebook Feed:**
- Longer primary text can work (users scroll slower)
- Link description is shown more often
- Right column placements need simple, clear images

**Instagram Feed:**
- Visual quality matters more than copy length
- 4:5 aspect ratio takes maximum screen real estate
- Hashtags in primary text can extend reach

**Instagram Stories:**
- Full-screen vertical format
- First 3 seconds determine whether users swipe past
- Swipe-up / link CTA must be visually prompted
- Keep text minimal — the visual does the work

## Generating Meta Ad Images

Every creative needs three layers: **brand** (logo), **copy** (headline + subline), and **product** (realistic screenshot of the actual app). Use `brand.screenshot.description` to understand what the product UI looks like.

### Feed Creative (1:1)

```python
images_generate(
    requests=[{
        "prompt": (
            "Social media ad creative for [company name]. "
            "Top: the [company] logo. "
            "Headline: '[headline from ad copy or site hero text]'. "
            "Below: a clean, realistic product screenshot of [describe actual UI from brand.screenshot.description]. "
            "Match the brand style from the references."
        ),
        "reference_images": [brand.logo.file_id, brand.screenshot.file_id]
    }],
    quality="high"
)
```

### Story Creative (9:16)

```python
images_generate(
    requests=[{
        "prompt": (
            "Vertical story ad creative for [company name]. "
            "Top: the [company] logo. "
            "Headline: '[headline]'. "
            "Below: a realistic product screenshot of [describe actual UI]. "
            "Match the brand style from the references."
        ),
        "reference_images": [brand.logo.file_id, brand.screenshot.file_id]
    }],
    quality="high"
)
```

### Text-Heavy Creative (headlines in image)

When the creative needs large, readable text baked into the image, use Nano Banana for better text rendering:

```python
images_generate(
    requests=[{
        "prompt": (
            "Ad creative for [company name]. "
            "Logo at top. Large headline: '[headline]'. "
            "Below: realistic product screenshot of [describe actual UI]. "
            "Match the brand style from the references."
        ),
        "reference_images": [brand.logo.file_id, brand.screenshot.file_id]
    }],
    aspect_ratio="1:1",
)
```
