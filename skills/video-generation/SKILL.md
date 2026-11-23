---
name: video-generation
description: Produce AI video from text or images with scene chaining, video analysis, transcription, subtitles, TikTok captions and karaoke captions, voiceover, audio mixing, clipping, stitching, and text overlays. Use when the user asks to generate a video, create UGC, scene-chain, add captions or subtitles, add narration, stitch clips, clip a podcast highlight, or do any AI video editing.
requires_toolkits:
  - video_generation_toolkit
icon: video_generation
short_description: Generate and edit AI video end-to-end, from scene chaining to captions and voiceover.
---

# Video Generation & Editing

Generate video from text, a start frame, or a structured UGC brief. Review clips, chain shots, and add the narration, captions, or overlays called for by the brief.

## Requirements

Connect to the [Hyper MCP](https://app.hyperfx.ai/mcp) to use these tools from an MCP client. Video generation, analysis, transcription, text-to-speech (TTS), and editing are built into Hyper and require no separate integration.

Hyper Chat, Hyper CLI, and the full Hyper MCP endpoint expose generation, analysis, frame capture, transcription, subtitle generation, and TTS. Some official directory MCP connectors exclude `video_generation_toolkit`. Check the active surface with `describe("videos_generate")` or the equivalent lookup below.

The six video editing tools marked **Hyper Chat only** require an active Hyper Chat conversation thread. On headless MCP or CLI, or without Hyper, use local FFmpeg or a video editor for those steps (or give the user the commands and SRT file when running without a local shell). If no video generator is available, deliver a scene-by-scene storyboard and shot list with prompts, timing, and framing.

| Surface | Find a tool | Run it |
| --- | --- | --- |
| Hyper Chat | `search_tools(queries=["<tool or action>"])` | `<name>(...)` |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | Use the `call_with` entry from `describe` to choose `call_read("<name>", {...})`, `call_write`, or `call_destructive` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

## Tool surface

| Tool | Purpose | Runs in Background | Surface notes |
| --- | --- | --- | --- |
| `videos_generate` | Generate video from text or a start frame | Yes | Chat, full MCP, CLI |
| `ugc_videos_create` | Generate a creator video from beats and references | Yes | Chat, full MCP, CLI |
| `videos_status_check` | Check a pending video operation by its `operation_id` | No | Chat, full MCP, CLI |
| `tool_job_read` | Poll a pending background job by its `background_job.job_id` | No | Chat, full MCP, CLI |
| `videos_frames_capture` | Save a frame as an image | No | Chat, full MCP, CLI |
| `videos_analyze` | Review visual and audio content | No | Chat, full MCP, CLI |
| `videos_transcribe` | Extract a transcript | No | Chat, full MCP, CLI |
| `videos_subtitles_generate` | Generate an SRT or VTT file | No | Chat, full MCP, CLI |
| `audio_speech_generate` | Generate speech from text | No | Chat, full MCP, CLI |
| `videos_subtitles_burn` | Burn subtitles into the video | No | **Hyper Chat only** |
| `videos_captions_burn_highlighted` | Burn TikTok or karaoke-style captions | No | **Hyper Chat only** |
| `videos_audio_add` | Replace or mix in an audio track | No | **Hyper Chat only** |
| `videos_clips_extract` | Extract a timestamped segment | No | **Hyper Chat only** |
| `videos_stitch` | Join multiple clips | No | **Hyper Chat only** |
| `videos_text_overlays_add` | Add titles, lower thirds, or calls to action | No | **Hyper Chat only** |

## Video Understanding

`videos_analyze(file_id=...)` takes an accessible, stored video file in a supported format and within the tool's size limit. Choose an `analysis_type` based on the task.

- `"general"` (default) describes visual and audio content.
- `"quality_review"` checks for glitches, character drift, or lighting issues.
- `"scene_breakdown"` returns a timestamped breakdown.
- `"comparison"` checks the video against an intended prompt or description.

Use `question` for a specific review request. It takes precedence over the preset prompt.

For a generated clip, wait for completion and take the `video_file_id` from the completed result. Pass that value as `file_id` to the review call. [Waiting for generation](references/generation.md#wait-for-completion)

```python
review = videos_analyze(file_id=completed.video_file_id, analysis_type="quality_review")
```

## Routing table

| The user wants to… | Read first |
| --- | --- |
| Generate a clip or chain several scenes | [Generation and scene chaining](references/generation.md) |
| Generate structured UGC or a creator ad | [UGC modes, templates, and beats](references/ugc-video.md) |
| Write a prompt for a specific model | [Video prompting](references/video-prompting.md) |
| Add subtitles, captions, narration, or overlays, or clip a video | [Post-production](references/post-production.md) |
| Produce narrated UGC or turn a podcast into shorts | [End-to-end workflows](references/workflows.md) |

## Best Practices

1. Plan each shot around the selected model's duration and keep the same model, framing, and visual anchors across chained shots.
2. Review generated clips with `videos_analyze` before chaining or stitching. Check the finished video for timing, continuity, and readable captions where requested.
3. Change one major element at a time when iterating, such as lighting, camera direction, or action.
4. In Hyper Chat, finished videos render automatically. On MCP or CLI, return the output URL or stored file ID so the user can open or download the clip.

## Out of scope

- For image generation or branded ad packs, use [Image Generation](../image-generation/SKILL.md) or [Ad Creative Generation](../ad-creative-generation/SKILL.md).
- For publishing finished videos, use the `tiktok`, `instagram`, or `linkedin` skill.
- For launching paid campaigns, use the `google-ads`, `meta-ads`, or `tiktok-ads` skill.
