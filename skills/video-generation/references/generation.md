# Video Generation: Models, Prompting & Scene Chaining

## Script Planning

For longer, cohesive videos, plan the FULL SCRIPT before generating:

### 1. Scene Breakdown
- **Scenes:** break story into segments
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
| `aspect_ratio` | Veo and Seedance: `"16:9"` or `"9:16"` |
| `duration_seconds` | Veo: 4-8 seconds. Seedance: 4-15 seconds |

## Important Input Rules

- Use exact values accepted by the tool schema. Do not send aliases like `landscape`, `portrait`, `720p`, or `1080p`.
- For Veo, use `aspect_ratio`.
- For Seedance, use `aspect_ratio` and optionally `resolution`.
- Keep the same `aspect_ratio` across chained scenes for continuity.

## Model Selection Guide

**When the user mentions a specific model name, always use that model.** Map user requests to the correct `model` parameter:

| User says | `model` parameter |
|-----------|-------------------|
| "use seedance", "seedance video" | `"seedance-2"` |
| "fast seedance" | `"seedance-2-fast"` |
| "use veo", "veo video" | `"veo-3.1-generate-preview"` |
| "fast veo" | `"veo-3.1-fast-generate-preview"` |

If the user asks for Sora, use `"veo-3.1-fast-generate-preview"` and tell the user in one line that Sora is retired.

## Model-Specific Parameter Matrix

- **Veo models (`veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`)**
  - Allowed sizing parameter: `aspect_ratio`
  - Allowed `aspect_ratio` values: `"16:9"`, `"9:16"`
- **Seedance models (`seedance-2`, `seedance-2-fast`)**
  - Allowed sizing parameters: `aspect_ratio` and `resolution`
  - Allowed `aspect_ratio` values: `"16:9"`, `"9:16"`, `"1:1"`, `"4:3"`, `"3:4"`
  - Allowed `resolution` values: `"480p"`, `"720p"`
  - Supports `generate_audio=true` for native audio with lip-sync

## Duration Limits

- **Veo:** 4, 5, 6, 7, or 8 seconds per generation. Use scene chaining + `videos_stitch` for longer videos.
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
