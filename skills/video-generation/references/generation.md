# Video Generation: Models, Prompting & Scene Chaining

## Script Planning

For longer, cohesive videos, plan the FULL SCRIPT before generating:

### 1. Scene Breakdown
- **Scenes:** break story into segments
  - Gemini Omni 1.2 (`gemini-omni-1.2-flash`, default): 3–10 seconds per scene, native audio, strong realism and real-person handling
  - Seedance (`seedance-2.5`, `seedance-2.5-flash`, `seedance-2`, `seedance-2-fast`): 4–15 seconds per scene, native audio with lip-sync
  - Other OpenRouter models: `veo-3.1-fast`, `runway-gen-4.5`, `flux-3-video`
- **Camera:** shot type (wide, close-up, tracking), max 1–2 smooth moves per clip
- **Transitions:** how each scene connects to the next
- **Consistency:** for image-to-video, describe only the motion delta — keep static product/subject appearance anchored to the start image

## Scene Chaining Technique

To create seamless multi-scene videos:

### Scene 1 (text-to-video)

```python
videos_generate(prompt="...", model="gemini-omni-1.2-flash", aspect_ratio="9:16")
```

### Scene 2+ (image-to-video)

```python
videos_frames_capture(video_file_id="scene1_file_id", frame_position="last")
videos_generate(prompt="continuation: ...", image_file_id="captured_frame_id")
```

Repeat: extract last frame → generate next scene.

### Stitching Scenes Together

After generating all scenes, combine them:

```python
videos_stitch(video_file_ids=["scene1_id", "scene2_id", "scene3_id"])

videos_stitch(
    video_file_ids=["scene1_id", "scene2_id", "scene3_id"],
    transition="crossfade",
    crossfade_duration=0.5,
)
```

## Prompt Structure

Each scene prompt should include:

- "Continuation of previous scene" (for scenes 2+)
- Consistent character / setting descriptions
- Specific action for this segment
- Camera movement direction

## Control Principles (most important)

- Treat API params as the **container** and prompt text as the **content**:
  - `model`, `aspect_ratio`, and `duration_seconds` must be set explicitly in the tool call.
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
| `videos_frames_capture` | Extract frames with `frame_position="last"` \| `"first"` \| `"middle"` |
| `aspect_ratio` | `"16:9"`, `"9:16"`, `"4:5"`, or `"1:1"` (for `4:5` and `1:1`, Hyper crops cleanly to `1080x1350` or `1080x1080` when a provider only outputs `3:4` or `9:16`) |
| `ad_placements` | Optional list of `["9:16", "4:5", "1:1"]` to emit a multi-placement ad pack in one call |
| `duration_seconds` | Gemini Omni / Veo / Runway / FLUX: 4-8 seconds. Seedance: 4-15 seconds |

## Important Input Rules

- Use exact values accepted by the tool schema. Do not send aliases like `landscape`, `portrait`, `720p`, or `1080p`.
- Use `aspect_ratio` (`"16:9"`, `"9:16"`, `"4:5"`, `"1:1"`) across all video models; pass `ad_placements` when producing a multi-size ad pack.
- For Seedance, you may also pass `resolution` (`"480p"` or `"720p"`).
- Keep the same `aspect_ratio` across chained scenes for continuity.

## Model Selection Guide

**When the user mentions a specific model name, always use that model.** Map user requests to the correct `model` parameter:

| User says | `model` parameter |
|-----------|-------------------|
| Default / best general video | `"gemini-omni-1.2-flash"` |
| "use seedance", "seedance 2.5" | `"seedance-2.5"` |
| "fast seedance", "seedance flash" | `"seedance-2.5-flash"` |
| "use veo", "fast veo" | `"veo-3.1-fast"` |
| "use runway", "runway gen 4.5" | `"runway-gen-4.5"` |
| "use flux video", "flux 3 video" | `"flux-3-video"` |

If the user asks for Sora or retired preview Veo models, route to `"gemini-omni-1.2-flash"` or `"veo-3.1-fast"` and note the retirement in one line.

## Model-Specific Parameter Matrix

- **Gemini Omni (`gemini-omni-1.2-flash`), Veo (`veo-3.1-fast`), Runway (`runway-gen-4.5`)**
  - Allowed sizing parameter: `aspect_ratio` (`"16:9"`, `"9:16"`, `"4:5"`, `"1:1"`; `4:5` and `1:1` are generated at `9:16` with safe-area framing and cropped to `1080x1350` or `1080x1080`)
  - Automatic fallback: real-person refusals retry once on `gemini-omni-1.2-flash`; audio copyright refusals retry once with `generate_audio=False`
- **Seedance (`seedance-2.5`, `seedance-2.5-flash`, legacy `seedance-2`, `seedance-2-fast`) and FLUX (`flux-3-video`)**
  - Allowed sizing parameters: `aspect_ratio` (`"16:9"`, `"9:16"`, `"4:5"`, `"1:1"`; `4:5` generates at `3:4` and center-crops to `1080x1350`) and optional `resolution` (`"480p"`, `"720p"`) on Seedance
  - Supports `generate_audio=true` for native audio with lip-sync

## Duration Limits

- **Gemini Omni, Veo, Runway, FLUX:** 4, 5, 6, 7, or 8 seconds per generation. Use scene chaining + `videos_stitch` for longer videos.
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
