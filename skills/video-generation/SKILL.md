---
name: video-generation
description: End-to-end AI video production through the Hyper MCP — text-to-video and image-to-video generation (Sora, Veo, Seedance), scene chaining, video analysis, transcription, subtitles, TikTok / karaoke captions, voiceover (TTS), audio mixing, clipping, stitching, and text overlays. Use when the user asks to generate a video, create UGC, scene-chain, add captions or subtitles, add narration, stitch clips, clip a podcast highlight, or do any AI video editing.
metadata:
  version: 1.0.0
---

# Video Generation & Editing

Guide for generating, editing, analyzing, and post-processing videos using AI models and FFmpeg-backed tools exposed through the Hyper MCP.

## Requirements

This skill assumes the [Hyper MCP](https://app.hyperfx.ai/mcp) is connected to your agent so the tools below are available. The underlying providers (OpenAI Sora, Google Veo, ByteDance Seedance, OpenAI TTS, transcription, etc.) are configured under your Hyper integrations.

## Tool surface

| Group | Tools |
|-------|-------|
| Generation | `videos_generate`, `sora_remix_video`, `sora_delete_video` |
| Analysis | `analyze_video`, `capture_video_frame`, `transcribe_video` |
| Subtitles & captions | `generate_subtitles`, `burn_subtitles`, `burn_highlighted_captions` |
| Audio | `text_to_speech`, `add_audio_to_video` |
| Editing | `clip_video`, `stitch_videos`, `overlay_text` |

## Out of scope

- Image generation, ad creative composition, brand extraction — use `image-generation` or `ad-creative-generation`.
- Posting finished videos to social platforms — use `tiktok`, `instagram`, or `linkedin`.
- Running paid video campaigns — use `google-ads`, `meta-ads`, `tiktok-ads`.

## Available Tools

| Tool | Purpose | Runs in Background |
|------|---------|-------------------|
| `videos_generate` | Generate video from text / image prompt | Yes |
| `sora_remix_video` | Modify existing Sora video | Yes |
| `sora_delete_video` | Delete a Sora video | No |
| `capture_video_frame` | Extract frame as image | No |
| `analyze_video` | Watch and understand video content | No |
| `transcribe_video` | Extract audio transcript | No |
| `generate_subtitles` | Create SRT / VTT subtitle file | No |
| `burn_subtitles` | Burn subtitles onto video | Yes |
| `burn_highlighted_captions` | TikTok / karaoke-style word-by-word captions | Yes |
| `text_to_speech` | Generate voiceover audio from text | No |
| `add_audio_to_video` | Add / replace audio track on video | Yes |
| `clip_video` | Extract a time segment from video | Yes |
| `stitch_videos` | Concatenate multiple clips | Yes |
| `overlay_text` | Add text / titles to video | Yes |

## Video Understanding

You can **watch and analyze any video** using `analyze_video`. This sends the video to a multimodal AI that sees both visual and audio content.

### When to use `analyze_video`

- After generating a video: check if it matches your intent
- Before stitching: verify scene consistency across clips
- Quality review: check for glitches, character drift, lighting issues
- Content understanding: "what happens in this video?"

### Analysis Types

```python
analyze_video(file_id="...", analysis_type="general")
analyze_video(file_id="...", analysis_type="quality_review")
analyze_video(file_id="...", analysis_type="scene_breakdown")
analyze_video(file_id="...", question="Does this match: [original prompt]?")
```

### Self-Review Workflow

Always review generated videos before delivering to the user:

```python
result = videos_generate(prompt="...", model="veo-3.1-generate-preview")
review = analyze_video(file_id="video_file_id", analysis_type="quality_review")
# If issues found, regenerate with adjustments. If quality is good, proceed to editing.
```

## Script Planning

For longer, cohesive videos, plan the FULL SCRIPT before generating:

### 1. Scene Breakdown
- **Scenes:** break story into segments
  - Sora: 4 / 8 / 12 seconds per scene
  - Veo: 4-8 seconds per scene
  - Seedance: 4-15 seconds per scene (native audio with lip-sync)
- **Camera:** shot type (wide, close-up, tracking), angles, movement
- **Transitions:** how each scene connects to the next
- **Consistency:** character descriptions, color palette, visual style

## Scene Chaining Technique

To create seamless multi-scene videos:

### Scene 1 (text-to-video)

```python
videos_generate(prompt="...", model="veo-3.1-generate-preview")
```

### Scene 2+ (image-to-video)

```python
capture_video_frame(video_file_id="scene1_file_id", frame_position="last")
videos_generate(prompt="continuation: ...", image_file_id="captured_frame_id")
```

Repeat: extract last frame → generate next scene.

### Stitching Scenes Together

After generating all scenes, combine them:

```python
stitch_videos(video_file_ids=["scene1_id", "scene2_id", "scene3_id"])

stitch_videos(
    video_file_ids=["scene1_id", "scene2_id", "scene3_id"],
    transition="crossfade",
    crossfade_duration=0.5,
)
```

## Subtitle / Caption Workflow

### Full pipeline: Video → Transcript → Subtitles → Burned Video

```python
transcript = transcribe_video(file_id="video_file_id")

subs = generate_subtitles(file_id="video_file_id", transcript=transcript, format="srt")

burn_subtitles(
    video_file_id="video_file_id",
    subtitle_file_id=subs.file_id,
    style="bold_outline",
    position="bottom",
)
```

### Subtitle Styles

| Style | Effect |
|-------|--------|
| `default` | Plain white text |
| `bold_outline` | Bold white with black outline (recommended) |
| `shadow` | White text with drop shadow |
| `box` | White text on semi-transparent black box |

## Text Overlays

Add titles, lower-thirds, CTAs, and other graphics:

```python
overlay_text(
    video_file_id="video_file_id",
    overlays=[
        {
            "text": "Episode 1: The Beginning",
            "start_time": 0.0,
            "end_time": 3.0,
            "position": "center",
            "font_size": 48,
            "color": "white",
            "background": "black@0.5",
        },
        {
            "text": "Subscribe for more!",
            "start_time": 10.0,
            "end_time": 14.0,
            "position": "bottom-right",
            "font_size": 28,
        },
    ],
)
```

### Overlay Positions

`top`, `bottom`, `center`, `top-left`, `top-right`, `bottom-left`, `bottom-right`

## Voiceover / Narration

Generate natural-sounding voiceover with TTS and add it to any video:

```python
audio = text_to_speech(
    text="Welcome to our product. Here's how it works...",
    voice="nova",
    model="tts-1",
)

add_audio_to_video(
    video_file_id="video_id",
    audio_file_id=audio.file_id,
    mode="replace",
)

add_audio_to_video(
    video_file_id="video_id",
    audio_file_id=audio.file_id,
    mode="mix",
    audio_volume=0.8,
)
```

### Available Voices

`alloy`, `ash`, `coral`, `echo`, `fable`, `nova` (recommended), `onyx`, `sage`, `shimmer`

## Highlighted Captions (TikTok / Reels Style)

Add word-by-word highlighted captions that light up as spoken:

```python
burn_highlighted_captions(
    video_file_id="video_id",
    style="tiktok",
    highlight_color="#3B82F6",
    base_color="white",
    words_per_group=3,
    position="center",
)

burn_highlighted_captions(
    video_file_id="video_id",
    style="karaoke",
    highlight_color="yellow",
    base_color="white",
    background="black@0.6",
    words_per_group=4,
    position="bottom",
)
```

## Video Clipping

Extract segments from longer videos:

```python
clip_video(
    video_file_id="long_video_id",
    start_time=45.0,
    end_time=60.0,
)
```

## UGC / TikTok Production Workflow

Complete workflow for producing UGC-style content:

1. **Script:** plan scenes, dialogue, and visual style
2. **Generate:** create each scene with `videos_generate`
3. **Review:** use `analyze_video` to check each scene for quality
4. **Chain:** extract last frames with `capture_video_frame`, generate next scenes
5. **Stitch:** combine all scenes with `stitch_videos`
6. **Narrate:** generate voiceover with `text_to_speech` + `add_audio_to_video`
7. **Caption:** add TikTok-style captions with `burn_highlighted_captions`
8. **Overlay:** add titles / CTAs with `overlay_text`
9. **Final review:** use `analyze_video` on the final video for quality check

### Example: Narrated UGC Video

```python
videos_generate(prompt="...", model="veo-3.1-generate-preview")

audio = text_to_speech(text="Your narration script here...", voice="nova")

add_audio_to_video(video_file_id="generated_video_id", audio_file_id=audio.file_id)

burn_highlighted_captions(video_file_id="narrated_video_id", style="tiktok")
```

### Example: Podcast to Short-Form Clips

```python
transcript = transcribe_video(file_id="podcast_video_id")

analysis = analyze_video(
    file_id="podcast_video_id",
    question="Identify the 3 most memorable / quotable moments with timestamps",
    analysis_type="scene_breakdown",
)

clip_video(video_file_id="podcast_video_id", start_time=120.0, end_time=150.0)
clip_video(video_file_id="podcast_video_id", start_time=340.0, end_time=365.0)

stitch_videos(video_file_ids=["clip1_id", "clip2_id"])

burn_highlighted_captions(video_file_id="stitched_id", style="tiktok")
```

## Prompt Structure

Each scene prompt should include:

- "Continuation of previous scene" (for scenes 2+)
- Consistent character / setting descriptions
- Specific action for this segment
- Camera movement direction

## Control Principles (most important)

- Treat API params as the **container** and prompt text as the **content**:
  - `model`, `size` / `aspect_ratio`, and `duration_seconds` must be set explicitly in the tool call.
  - Do not expect prose like "make it longer" or "make it vertical" to override API parameters.
- Use detail for control, brevity for exploration:
  - Short prompts give more creative variation.
  - Detailed prompts improve consistency and shot control.
- Iterate in small steps:
  - Change one major variable at a time (camera, lighting, action, or palette).
  - Keep what works fixed and only modify the target dimension.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `image_file_id` | Use for image-to-video (scene continuity) |
| `capture_video_frame` | Extract frames with `position="last"` \| `"first"` \| `"middle"` |
| `size` | For Sora only. One of: `"720x1280"`, `"1280x720"`, `"1024x1792"`, `"1792x1024"` |
| `aspect_ratio` | For Veo only. One of: `"16:9"` or `"9:16"` |
| `duration_seconds` | Sora: 4, 8, or 12 seconds only. Veo: 4-8 seconds |

## Important Input Rules

- Use exact values accepted by the tool schema. Do not send aliases like `landscape`, `portrait`, `720p`, or `1080p`.
- For Sora, prefer `size` and do not send `aspect_ratio`.
- For Veo, prefer `aspect_ratio` and do not send `size`.
- For Seedance, use `aspect_ratio` and optionally `resolution`. Do not pass `size`.
- Keep the same `size` / `aspect_ratio` across chained scenes for continuity.

## Model Selection Guide

**When the user mentions a specific model name, always use that model.** Map user requests to the correct `model` parameter:

| User says | `model` parameter |
|-----------|-------------------|
| "use seedance", "seedance video" | `"seedance-2"` |
| "fast seedance" | `"seedance-2-fast"` |
| "use sora", "sora video" | `"sora-2"` |
| "sora pro" | `"sora-2-pro"` |
| "use veo", "veo video" | `"veo-3.1-generate-preview"` |
| "fast veo" | `"veo-3.1-fast-generate-preview"` |

## Model-Specific Parameter Matrix

- **Sora models (`sora-2`, `sora-2-pro`)**
  - Allowed sizing parameter: `size`
  - Allowed `size` values: `"720x1280"`, `"1280x720"`, `"1024x1792"`, `"1792x1024"`
  - Do not pass `aspect_ratio`
  - Practical default pair: `"1280x720"` or `"720x1280"`
- **Veo models (`veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`)**
  - Allowed sizing parameter: `aspect_ratio`
  - Allowed `aspect_ratio` values: `"16:9"`, `"9:16"`
  - Do not pass `size`
- **Seedance models (`seedance-2`, `seedance-2-fast`)**
  - Allowed sizing parameters: `aspect_ratio` and `resolution`
  - Allowed `aspect_ratio` values: `"16:9"`, `"9:16"`, `"1:1"`, `"4:3"`, `"3:4"`
  - Allowed `resolution` values: `"480p"`, `"720p"`
  - Supports `generate_audio=true` for native audio with lip-sync
  - Do not pass `size`

## Duration Limits

- **Sora:** 4, 8, or 12 seconds per generation. Use scene chaining + `stitch_videos` for longer videos.
- **Veo:** 4, 5, 6, 7, or 8 seconds per generation.
- **Seedance:** 4-15 seconds per generation (most flexible). Supports `generate_audio=true` for native audio with lip-sync.

## High-Control Prompt Template

Use this structure when you want predictable output:

```text
Style/Tone: [realistic, cinematic, animation, documentary, etc.]
Subject/World: [who/what is in frame, key visual anchors]
Camera: [shot size + angle + movement]
Lighting/Palette: [light direction + 3-5 color anchors]
Action Beats:
- [beat 1 with timing/count]
- [beat 2 with timing/count]
- [beat 3 with timing/count]
Audio/Dialogue: [short lines or ambient cues]
Constraints: [no logos/brands, no text overlays, etc.]
```

## Best Practices

1. **Review before delivering:** always use `analyze_video` to check your output.
2. **Maintain visual consistency:** use the same character descriptions, lighting, and style across all scenes.
3. **Plan transitions:** design the end of each scene to flow into the next.
4. **Batch similar scenes:** generate scenes with similar settings together.
5. **Review before chaining:** check each scene before using its last frame for the next.
6. **Use single-variable iteration:** remix / regenerate by changing one variable at a time.
7. **Add captions for accessibility:** use the subtitle pipeline for all UGC content.
