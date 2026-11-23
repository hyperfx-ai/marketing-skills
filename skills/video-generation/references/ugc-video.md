# UGC Video Reference

Use `ugc_videos_create` for creator ads, continuous POV clips, tutorials, unboxings, reviews, product demos, testimonials, TV spots, and virtual try-ons. Give the tool a short brief and the beats that need to appear in the clip (`product` is optional). For long single-shot scripts (such as a 30-second founder talking head on `heygen-video-1`) or custom shots without UGC beat structure, call `videos_generate` directly.

## Modes

| Mode | Structure | Default aspect | Mode duration before model limits |
| --- | --- | --- | --- |
| `ugc` (default) | Casual presenter-to-camera product mention | `9:16` | 8s |
| `ugc_how_to` | Quick tutorial with visible steps | `9:16` | 8s |
| `ugc_unboxing` | Package reveal and first-impression close-ups | `9:16` | 8s |
| `product_showcase` | Polished product-first highlight | `16:9` | 12s |
| `product_review` | Presenter opinion and proof point | `9:16` | 8s |
| `tv_spot` | Broadcast-style ad with cinematic polish | `16:9` | 12s |
| `wild_card` | Unexpected visual hook around the product | `9:16` | 8s |
| `ugc_virtual_try_on` | Casual mirror or handheld try-on | `9:16` | 8s |
| `virtual_try_on` | Polished model-led try-on | `9:16` | 8s |

Every mode defaults to `gemini-omni-1.2-flash`. The 12-second defaults for `product_showcase` and `tv_spot` clamp to 8 seconds on models with an 8-second default ceiling. An explicit `duration_seconds` is forwarded as requested, so choose one the model supports. If you omit `aspect_ratio` and supply `ad_placements`, the tool generates one clip framed for the first placement.

For alternatives to Omni, consider Veo 3.1 Fast, HeyGen Video 1, Runway Gen-4.5, Grok Imagine Video 1.5 Lite, and FLUX 3 Video in that order as the shot requires. Reserve Seedance for product or scene shots without human faces. [Model IDs, durations, and audio support](generation.md#choose-a-model)

## Style templates

Passing `style_template` overrides `mode` and supplies the template's defaults, including structure, camera, voice, aspect ratio, and duration. Explicit `camera`, `voice_style`, `aspect_ratio`, and `duration_seconds` values still apply.

| Template | Use when |
| --- | --- |
| `tiktok_ugc` | General TikTok or Reels creator ad |
| `continuous_pov` | Continuous selfie or POV clip without abrupt product-only cutaways |
| `creator_review` | Creator opinion with a proof point |
| `unboxing` | Package opening and first impression |
| `routine` | Product shown as part of a daily routine |
| `before_after` | Before and after comparison |
| `problem_solution` | Quick problem followed by the product solution |
| `how_to` | Short tutorial with visible steps |
| `testimonial` | Sincere creator testimonial |
| `product_demo` | Product function demo with creator context |
| `trend_remix` | Trend-inspired format anchored to the product benefit |

## Beat fields

- `hook` gives the opening line.
- `setting` describes the location and surroundings.
- `action` describes what happens or what the presenter demonstrates.
- `emotion` sets the emotional tone.
- `voice_style` describes spoken delivery.
- `background_sound` describes ambient sound or music.
- `camera` sets framing and movement.
- `cta` gives the closing call to action.

## Start-frame references

The tool selects the first usable `avatars` entry in list order, then falls back to the first usable `product.references` entry. An `avatar_file_id` or `avatar_url` goes at the front of `avatars`. Within one entry, `file_id` takes precedence over `url`.

## Example

Pass these JSON arguments to `ugc_videos_create`.

```json
{
  "product": {
    "name": "Ember Travel Mug",
    "category": "insulated travel mug",
    "references": [{"file_id": "<stored mug image file ID>"}]
  },
  "avatars": [{"file_id": "<stored presenter image file ID>"}],
  "style_template": "unboxing",
  "model": "gemini-omni-1.2-flash",
  "hook": "My commute mug just arrived. Let's open it.",
  "action": "Opens the box, lifts the mug toward the lens, and snaps the lid shut.",
  "emotion": "Pleased and curious",
  "voice_style": "Conversational",
  "background_sound": "Quiet kitchen ambience",
  "cta": "Try it on your next commute.",
  "duration_seconds": 8
}
```

If the response contains `background_job.job_id`, poll `tool_job_read` for the result. If the result contains a pending `operation_id`, poll `videos_status_check`. Use the completed `video_file_id` for review and editing. The generation result also includes `mode`, `style_template`, `product_name`, `hook`, `storyboard`, and `compiled_prompt`. [Waiting for generation](generation.md#wait-for-completion)
