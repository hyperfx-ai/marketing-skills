# Video Generation and Scene Chaining

## Plan the clip

For a multi-scene video, plan the full sequence before generating. Give each clip one main action and at most two camera moves. Choose a shot size and a clear ending pose or composition so the next scene can continue from it. For image-to-video, describe how the scene moves from the first frame. [Video prompting](video-prompting.md)

## Choose a model

Use the user's requested model when it supports the brief. Otherwise, start with the default and use the alternatives in the order below as the task requires.

| Preference | Model | Supported duration in seconds | Audio and best fit |
| --- | --- | --- | --- |
| 1 (default) | `gemini-omni-1.2-flash` | 4–8, default 8 | Native audio, `720p`, realistic human and UGC clips |
| 2 | `veo-3.1-fast` | 4, 6, 8 | Native audio, human and UGC clips |
| 3 | `heygen-video-1` | 5, 6, 7, 8, 12, 15, 30 | One native talking-head or UGC shot with automatic spoken audio. Uses `480p` or `768p` and ignores `generate_audio`. |
| 4 | `runway-gen-4.5` | 4–8 | Stylized motion, silent output. Ignores `generate_audio`. |
| 5 | `grok-imagine-video-1.5-lite` | 4, 5, 6, 7, 8, 12, 15 | Fast human and UGC clips with native audio |
| 6 | `flux-3-video` | 4–8 | Native audio |
| Product or scene only | `seedance-2.5` (quality), `seedance-2.5-flash` (faster); legacy `seedance-2`, `seedance-2-fast` | 4, 5, 6, 7, 8, 12, 15 | Native audio (set `generate_audio=false` for silent shots). Use product or scene shots without human faces. Keep photorealistic human faces out of start frames. |

## Set tool parameters

`model`, `aspect_ratio`, and `duration_seconds` are optional. The default model, `gemini-omni-1.2-flash`, generates an 8-second clip at `720p` by default. Set the model, ratio, and duration explicitly when the brief requires specific settings.

| Argument | Values and behavior |
| --- | --- |
| `prompt` | Free text describing the subject, movement, style, and any audio cues |
| `image_file_id` | Stored start-frame image for image-to-video or continuity |
| `duration_seconds` | Shared enum of `4`, `5`, `6`, `7`, `8`, `12`, `15`, and `30`. The value goes to the selected model, so choose a duration from its row above. |
| `aspect_ratio` | `"16:9"`, `"9:16"`, `"4:5"`, or `"1:1"` |
| `ad_placements` | Optional list drawn from `["9:16", "4:5", "1:1"]`. Generates one clip. Applies placement-safe framing. When `aspect_ratio` is omitted, the first placement sets the ratio. |
| `resolution` | `"480p"`, `"720p"`, or `"768p"`. HeyGen maps `"720p"` to `"768p"`. Other models map `"768p"` to `"720p"`. Omni generation uses `720p`. |
| `generate_audio` | Optional boolean (`true` by default on Veo, Grok, FLUX, and Seedance; set `false` for silent output). Omni always generates native audio, HeyGen generates speech automatically, and Runway outputs silent clips; those three ignore `generate_audio`. |

For `4:5`, Hyper crops from `9:16` or `3:4`, depending on the model. Some models output `1:1` natively and others crop from `9:16`. If the crop fails, the original framing may be kept. For a multi-placement pack with overlays, use `ad_creatives_generate(kind="video")`. [Ad creative generation](../../ad-creative-generation/SKILL.md)

## Wait for completion

Use the same completion flow for `videos_generate` and `ugc_videos_create`.

1. If the tool returns a `background_job.job_id`, poll `tool_job_read(job_id=...)` until the job finishes, then read the tool result.
2. If the result has a pending `operation_id`, poll `videos_status_check(operation_id=...)` until it finishes. If the tool already returned a completed `video_file_id`, use it immediately.
3. Pass the completed `video_file_id` to the next step. On failure, read the returned message and any `next_step` before retrying.

## Chain scenes

Generate the first clip.

```python
scene1 = videos_generate(
    prompt="A travel mug sits beside a kitchen window. A hand reaches into frame and lifts it.",
    model="gemini-omni-1.2-flash",
    aspect_ratio="9:16",
    duration_seconds=8,
)
```

Wait for `scene1` to hold the completed result. Review it, then capture its last frame. The capture tool also accepts `"first"` and `"middle"`.

```python
review = videos_analyze(file_id=scene1.video_file_id, analysis_type="quality_review")
frame = videos_frames_capture(video_file_id=scene1.video_file_id, frame_position="last")
scene2 = videos_generate(
    prompt="Continue the lift into a close-up as the thumb snaps the lid shut. The camera tracks upward.",
    image_file_id=frame.image.file_id,
    model="gemini-omni-1.2-flash",
    aspect_ratio="9:16",
    duration_seconds=8,
)
```

Repeat with the same model and aspect ratio as needed. Once each clip is complete and reviewed, pass two or more completed `video_file_ids` in order to `videos_stitch`. The default `transition="none"` makes hard cuts. For crossfading, set `transition="crossfade"` and use `crossfade_duration=0.5` seconds or specify another duration. Stitch in Hyper Chat or use local FFmpeg or a video editor. [Post-production](post-production.md#stitch-clips)

## Handle refusals

- Real-person start-frame refusals leave the selected model in place. Follow any `next_step` hint to use a product-only start frame or select a human-capable model (`gemini-omni-1.2-flash`, `veo-3.1-fast`, `heygen-video-1`, or `grok-imagine-video-1.5-lite`).
- Eligible audio or music refusals at generation start trigger one retry with `generate_audio=false`. HeyGen and Runway skip that retry. If needed, add narration or music in post-production.
