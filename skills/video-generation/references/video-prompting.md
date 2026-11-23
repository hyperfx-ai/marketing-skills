# Video Prompting

The `prompt` in `videos_generate` is free text. Choose the details below that help describe the shot. Set aspect ratio and duration through the tool arguments. [Model IDs, durations, and aspect ratios](generation.md)

## Gemini Omni and Veo 3.1 Fast

Describe a single scene with a clear subject and natural motion. Start with shot size and setting, then add relevant character details, action, lighting, and style. For spoken dialogue, say who speaks, what they say, and when they speak. Keep the line short enough for the shot.

## HeyGen Video 1

Write one talking-head or presenter shot. Anchor the presenter with `image_file_id`, give the exact lines, and describe delivery, gestures, and expression. The model generates spoken audio automatically.

## Runway Gen-4.5

Describe stylized motion, camera trajectory, and light. Build the shot around visual action because Runway produces silent clips. If the brief calls for narration or music, add it during [post-production](post-production.md).

## Grok Imagine Video 1.5 Lite and FLUX 3 Video

Keep the prompt focused on one subject, one camera move, and a short sequence of natural action. Add a short dialogue line or ambient sound cue if it supports the scene.

## Seedance

For product or scene shots, describe the shot type, subject, movement, setting, camera, and lighting. Use one main subject and one or two camera moves. Keep photorealistic human faces out of start frames.

## Image-to-video motion delta

When you supply `image_file_id`, describe only what changes from the start frame. Focus on camera movement, action, expression, dialogue, or movement in the surroundings. The image already establishes static details such as clothing, packaging, and background.

For scene chaining, capture the previous clip's last frame, then describe the next action as a continuation of that frame. [Scene chaining](generation.md#chain-scenes)
