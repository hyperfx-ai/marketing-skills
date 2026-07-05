# Video Prompting (per backend)

Each video backend rewards a different prompt structure. When calling `videos_generate` directly (not via `ugc_videos_create`), shape the prompt to the model you're using.

## Sora (`sora-2`, `sora-2-pro`)
- Shape: storyboard scene with action beats.
- Required sections: subject/scene → action beats → camera/framing → lighting/palette → audio/dialogue.
- Avoid: vague style stacks, asking for duration/aspect in prose, more than ~2 scene changes in one clip.

## Veo (`veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`)
- Shape: a single clear scene.
- Required sections: shot → scene → character details → action → lighting → style (+ optional dialogue).
- Avoid: ambiguous subjects, multiple unrelated events, quoted dialogue syntax (just write what's said).

## Seedance (`seedance-2`, `seedance-2-fast`)
- Shape: shot type, subject, what moves, environment, camera, lighting/style.
- Required sections: shot_type → subject → motion → environment → camera → lighting_style.
- Cap camera moves at 2 per clip. One strong subject per clip.
- Avoid: rewriting everything during iteration — change one variable at a time.

## Kling (image-to-video)
- Shape: motion only.
- Required sections: camera_move → action_beats → ambient_motion.
- Do not redescribe what's in the input image — clothing, appearance, product details. The image already carries that.
- Avoid: complex cinematic jargon, competing visual instructions.

## Universal rules

- Keep model-specific sizing parameters consistent: Sora uses `size` (e.g. `1280x720`), Veo and Seedance use `aspect_ratio` (e.g. `16:9`).
- Don't pass `aspect_ratio` to Sora or `size` to Veo/Seedance.
- For chained scenes, capture the last frame and pass it as `image_file_id` in the next call.
