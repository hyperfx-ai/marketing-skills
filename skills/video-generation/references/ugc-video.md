# UGC Video Reference

Use `ugc_videos_create` for any of: TikTok/UGC ads, continuous POV creator videos, how-to/tutorial videos, unboxings, routines, before/after demos, product showcases, product reviews, testimonials, TV spots, "wild card" scroll-stoppers, or virtual try-ons. The tool wraps prompt structure, model selection, and product/avatar reference handling.

## Modes

| Mode | Structure | Default aspect | Default duration |
|------|-----------|----------------|------------------|
| `ugc` | casual presenter-to-camera product mention | 9:16 | 8s |
| `ugc_how_to` | quick tutorial with visible steps | 9:16 | 8s |
| `ugc_unboxing` | package reveal + first impression close-ups | 9:16 | 8s |
| `product_showcase` | polished product-first highlight (cinematic) | 16:9 | 12s |
| `product_review` | presenter opinion + proof point | 9:16 | 8s |
| `tv_spot` | broadcast-style ad with cinematic polish | 16:9 | 12s |
| `wild_card` | unexpected visual hook around the product | 9:16 | 8s |
| `ugc_virtual_try_on` | organic mirror/handheld try-on | 9:16 | 8s |
| `virtual_try_on` | polished model-led try-on | 9:16 | 8s |

Each mode declares required beats and default camera + voice. Override with `aspect_ratio`, `duration_seconds`, `camera`, and `voice_style`.

## Backend selection

Default generation uses `veo-3.1-fast-generate-preview`. Pass `model` explicitly when you need a different backend:

- `model="veo-3.1-fast-generate-preview"`: default, fastest Veo route
- `model="veo-3.1-generate-preview"`: higher-quality Veo route
- `model="sora-2"` or `model="sora-2-pro"`: OpenAI Sora route
- `model="seedance-2"` or `model="seedance-2-fast"`: Seedance route

Explicit `model` selection always wins. The tool no longer switches to Sora just because voice or background sound is requested.

## Style templates

Use `style_template` for machine-friendly TikTok/social formats:

| Template | Use when |
|----------|----------|
| `tiktok_ugc` | General TikTok/Reels creator ad |
| `continuous_pov` | One continuous selfie/POV video without abrupt product-only cutaways |
| `creator_review` | Creator opinion with a proof point |
| `unboxing` | Package opening and first impression |
| `routine` | Product inside a daily routine |
| `before_after` | Before/result proof format |
| `problem_solution` | Quick problem then product solution |
| `how_to` | Short tutorial with visible steps |
| `testimonial` | Sincere creator testimonial |
| `product_demo` | Product function demo with creator context |
| `trend_remix` | Trend-inspired format anchored to the product benefit |

## Beat fields

Pass any of these to override mode defaults:

- `hook` — opening line
- `setting` — scene/setting description
- `action` — what happens / demonstration
- `emotion` — emotional tone
- `voice_style` — voiceover or presenter style
- `background_sound` — ambient sound or music
- `camera` — camera/framing notes
- `cta` — closing call-to-action

## Inputs

- `product` — `ProductContext` (product name, brand, references for image-to-video)
- `avatars` — `list[MediaInput]` of presenter references; the strongest one becomes the start frame for image-to-video
- `avatar_file_id` or `avatar_url` — direct presenter/start-frame avatar reference for CLI-friendly calls

## Example

```python
create_ugc_video(
    product=ProductContext(
        name="Ember Travel Mug",
        category="insulated travel mug",
        references=[MediaInput(file_id="file_image_gen_..._mug")],
    ),
    avatars=[MediaInput(file_id="file_image_gen_..._presenter")],
    style_template="unboxing",
    model="veo-3.1-fast-generate-preview",
    hook="I just got this mug and the packaging already feels premium",
    action="Opens the mailer, reveals the mug, shows the leakproof lid",
    emotion="Excited but natural first impression",
    voice_style="conversational, unscripted",
    background_sound="quiet kitchen ambience",
    cta="Try it for your morning commute",
    duration_seconds=8,
)
```

The result is a `UGCVideoResponse` with:
- `operation_id` (chat UI and Prefab compiler self-poll via `videos_status_check`)
- `mode`, `style_template`, `product_name`, `hook` (rendered above the video)
- `storyboard` and `compiled_prompt` (so the chat card can show the structure)
