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
| Aspect ratio | 1:1 or 4:5 |
| Resolution | 1080x1080 (1:1) or 1080x1350 (4:5) |
| File type | JPG or PNG |
| Max file size | 30MB |

4:5 takes more vertical space in the feed, increasing visibility. Use 1:1 for broad compatibility. Keep in-image text short and legible; the copy fields carry the detail.

### Story / Reel Ads (Facebook + Instagram)

| Spec | Requirement |
|------|-------------|
| Aspect ratio | 9:16 |
| Resolution | 1080x1920 |
| File type | JPG or PNG (image), MP4 or MOV (video) |
| Max file size | 30MB (image), 4GB (video) |
| Safe zone | Keep the top 250px (profile bar) and bottom 340px (CTA and caption area) clear of key content |

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
| Aspect ratio | 1:1 or 4:5 (keep every card the same) |
| Resolution | 1080x1080 (1:1) or 1080x1350 (4:5) per card |
| Headline per card | 40 characters recommended |
| Description per card | 20 characters recommended |
| Link per card | Each card can link to a different URL |

### Carousel Strategies

- **Product showcase** — each card features a different product
- **Feature walkthrough** — each card explains one feature / benefit
- **Story arc** — cards tell a sequential story that builds to a CTA
- **Social proof series** — each card shows a different verified testimonial
- **Before / after** — alternate between problem and solution cards

### Generating Carousel Cards

`ad_creatives_generate` has no dedicated carousel mode. Generate each card as its own `1:1` or `4:5` visual: one concept per card (or one concept with a per-card brief), all at the same placement, so the set reads as a series. Keep logo position, type, and color treatment identical across cards.

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

**Instagram Stories / Reels:**
- Full-screen vertical format
- First 3 seconds determine whether users skip
- Prompt the tap visually toward the link sticker or CTA button
- Keep text minimal — the visual does the work

## Generating Meta Ad Images

Use `creative_concepts_generate` to pick a concept, then `ad_creatives_generate` for the full Meta set. It adapts one visual across Feed (`1:1`, `4:5`) and Stories/Reels (`9:16`), places the headline and CTA inside the safe zones, and runs the quality checks:

```python
pack = ad_creatives_generate(
    concept=chosen_concept,
    placements=["9:16", "4:5", "1:1"],
    variants=2,
    references=[
        {"file_id": logo_file_id, "role": "logo"},
        {"file_id": screenshot_file_id, "role": "style"},
    ],
)
```

### Direct fallback with `images_generate`

When `ad_creatives_generate` is unavailable or the user wants a quick single pass, pass `ad_placements` so each output uses the exact Meta size. Each placement is generated independently, so framing can differ between sizes. Describe the real product from `brand.screenshot.description`.

```python
images_generate(
    requests=[{
        "prompt": (
            "Social ad for [company name]. Logo at top. "
            "Realistic shot of [actual product from brand.screenshot.description], "
            "clean space for a short headline. Match the brand style from the references."
        ),
        "reference_images": [logo_file_id, screenshot_file_id],
    }],
    ad_placements=["9:16", "4:5", "1:1"],
)
```

### Text baked into the image

When large, readable text must be part of the image itself (instead of the `ad_creatives_generate` overlay), use `model="nano-banana-pro"`:

```python
images_generate(
    requests=[{
        "prompt": (
            "Ad creative for [company name]. Logo at top. Large headline: '[headline]'. "
            "Below: realistic product shot of [actual product]. Match the brand style from the references."
        ),
        "reference_images": [logo_file_id, screenshot_file_id],
    }],
    model="nano-banana-pro",
    ad_placements=["1:1"],
)
```
