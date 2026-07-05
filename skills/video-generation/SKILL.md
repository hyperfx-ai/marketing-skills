---
name: video-generation
description: End-to-end AI video production through the Hyper MCP — text-to-video and image-to-video generation (Sora, Veo, Seedance), scene chaining, video analysis, transcription, subtitles, TikTok / karaoke captions, voiceover (TTS), audio mixing, clipping, stitching, and text overlays. Use when the user asks to generate a video, create UGC, scene-chain, add captions or subtitles, add narration, stitch clips, clip a podcast highlight, or do any AI video editing.
icon: video_generation
short_description: Generate and edit AI video end-to-end, from scene chaining to captions and voiceover.
---

# Video Generation & Editing

Guide for generating, editing, analyzing, and post-processing videos using AI models and FFmpeg-backed tools exposed through the Hyper MCP.

## Requirements

This skill assumes the [Hyper MCP](https://app.hyperfx.ai/mcp) is connected to your agent so the tools below are available. The underlying providers (OpenAI Sora, Google Veo, ByteDance Seedance, OpenAI TTS, transcription, etc.) are configured under your Hyper integrations.

## Tool surface

| Group | Tools |
|-------|-------|
| Generation | `videos_generate`, `sora_videos_remix`, `sora_videos_delete` |
| Analysis | `videos_analyze`, `videos_frames_capture`, `videos_transcribe` |
| Subtitles & captions | `videos_subtitles_generate`, `videos_subtitles_burn`, `videos_captions_burn_highlighted` |
| Audio | `audio_speech_generate`, `videos_audio_add` |
| Editing | `videos_clips_extract`, `videos_stitch`, `videos_text_overlays_add` |

## Out of scope

- Image generation, ad creative composition, brand extraction — use `image-generation` or `ad-creative-generation`.
- Posting finished videos to social platforms — use `tiktok`, `instagram`, or `linkedin`.
- Running paid video campaigns — use `google-ads`, `meta-ads`, `tiktok-ads`.

## Available Tools

| Tool | Purpose | Runs in Background |
|------|---------|-------------------|
| `videos_generate` | Generate video from text / image prompt | Yes |
| `sora_videos_remix` | Modify existing Sora video | Yes |
| `sora_videos_delete` | Delete a Sora video | No |
| `videos_frames_capture` | Extract frame as image | No |
| `videos_analyze` | Watch and understand video content | No |
| `videos_transcribe` | Extract audio transcript | No |
| `videos_subtitles_generate` | Create SRT / VTT subtitle file | No |
| `videos_subtitles_burn` | Burn subtitles onto video | Yes |
| `videos_captions_burn_highlighted` | TikTok / karaoke-style word-by-word captions | Yes |
| `audio_speech_generate` | Generate voiceover audio from text | No |
| `videos_audio_add` | Add / replace audio track on video | Yes |
| `videos_clips_extract` | Extract a time segment from video | Yes |
| `videos_stitch` | Concatenate multiple clips | Yes |
| `videos_text_overlays_add` | Add text / titles to video | Yes |

## Video Understanding

You can **watch and analyze any video** using `videos_analyze`. This sends the video to a multimodal AI that sees both visual and audio content.

### When to use `videos_analyze`

- After generating a video: check if it matches your intent
- Before stitching: verify scene consistency across clips
- Quality review: check for glitches, character drift, lighting issues
- Content understanding: "what happens in this video?"

### Analysis Types

```python
videos_analyze(file_id="...", analysis_type="general")
videos_analyze(file_id="...", analysis_type="quality_review")
videos_analyze(file_id="...", analysis_type="scene_breakdown")
videos_analyze(file_id="...", question="Does this match: [original prompt]?")
```

### Self-Review Workflow

Always review generated videos before delivering to the user:

```python
result = videos_generate(prompt="...", model="veo-3.1-generate-preview")
review = videos_analyze(file_id="video_file_id", analysis_type="quality_review")
# If issues found, regenerate with adjustments. If quality is good, proceed to editing.
```

## Routing table

> **All reference files live in `references/`.** Read them at `references/<file>` (e.g. `references/generation.md`).

| The user wants to… | Read these files first |
|---|---|
| Generate a video (any model) | [references/generation.md](references/generation.md) — model selection, parameter matrix, prompt templates |
| Build a longer multi-scene video | [references/generation.md](references/generation.md) — script planning + scene chaining |
| Add subtitles / captions / voiceover / overlays, or clip a video | [references/post-production.md](references/post-production.md) |
| Produce UGC / TikTok content end-to-end | [references/ugc-video.md](references/ugc-video.md) (`ugc_videos_create` modes) → [references/workflows.md](references/workflows.md) |
| Shape a prompt for a specific model (Sora / Veo / Seedance / Kling) | [references/video-prompting.md](references/video-prompting.md) |
| Turn a podcast / long video into short clips | [references/workflows.md](references/workflows.md) → [references/post-production.md](references/post-production.md) |
| Understand or QA an existing video | Use `videos_analyze` (see Video Understanding above) |

## Best Practices

1. **Review before delivering:** always use `videos_analyze` to check your output.
2. **Maintain visual consistency:** use the same character descriptions, lighting, and style across all scenes.
3. **Plan transitions:** design the end of each scene to flow into the next.
4. **Batch similar scenes:** generate scenes with similar settings together.
5. **Review before chaining:** check each scene before using its last frame for the next.
6. **Use single-variable iteration:** remix / regenerate by changing one variable at a time.
7. **Add captions for accessibility:** use the subtitle pipeline for all UGC content.
