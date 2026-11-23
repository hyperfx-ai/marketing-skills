# Video Production Workflows

Use the editing calls below in an active Hyper Chat conversation. On headless MCP or CLI, download the clips, narration, or subtitles you generated and do the composition in local FFmpeg or a video editor. Without Hyper, use the same sequence with your own tools. If no video generator is available, deliver a storyboard and shot list.

## Narrated UGC

1. Plan the hook, demonstration, and close. Include narration and captions when the brief calls for them.
2. Generate each scene with `videos_generate` or make a structured creator clip with `ugc_videos_create`. Wait for each completed `video_file_id`. [Waiting for generation](generation.md#wait-for-completion)
3. Check each scene with `videos_analyze`. For a continuous sequence, use the previous clip's last frame as the next start frame. Stitch multiple reviewed scenes in playback order. [Scene chaining](generation.md#chain-scenes)
4. Add narration, then captions, so the captions reflect the finished audio. Add overlays if the brief needs them, then review the finished clip. [Post-production](post-production.md)

### Example with narration and TikTok captions

```python
clip = videos_generate(
    prompt="Vertical kitchen close-up. A commuter fills a travel mug, then snaps the lid shut.",
    model="gemini-omni-1.2-flash",
    aspect_ratio="9:16",
    duration_seconds=8,
)
```

Wait until `clip` holds the completed result. For a stitched sequence, use the completed stitch result as `clip` in the narration step.

```python
review = videos_analyze(file_id=clip.video_file_id, analysis_type="quality_review")
```

Once the clip passes review, add the requested narration and captions. This example uses the voiceover as the entire soundtrack. Choose `mode="mix"` to keep the original sound.

```python
audio = audio_speech_generate(text="Fill it, snap the lid shut, and you're ready to go.")
narrated = videos_audio_add(
    video_file_id=clip.video_file_id,
    audio_file_id=audio.file_id,
    mode="replace",
)
captioned = videos_captions_burn_highlighted(
    video_file_id=narrated.video_file_id,
    style="tiktok",
)
final_review = videos_analyze(file_id=captioned.video_file_id, analysis_type="quality_review")
```

## Podcast to short-form clips

Transcribe the uploaded podcast and identify self-contained moments with timestamps. Set `podcast_file_id` to the stored source file ID.

```python
transcript = videos_transcribe(file_id=podcast_file_id)
analysis = videos_analyze(
    file_id=podcast_file_id,
    question="Find self-contained highlights with start and end timestamps. Keep enough context for each quote.",
)
```

Check the suggested cuts against the transcript. Use the verified start and end times for each extraction. The example uses two selections.

```python
first = videos_clips_extract(video_file_id=podcast_file_id, start_time=120.0, end_time=150.0)
second = videos_clips_extract(video_file_id=podcast_file_id, start_time=340.0, end_time=365.0)
first_review = videos_analyze(file_id=first.video_file_id, analysis_type="quality_review")
second_review = videos_analyze(file_id=second.video_file_id, analysis_type="quality_review")
```

Check the audio and whether each clip makes sense on its own. Deliver the clips individually if the brief calls for separate shorts. For a highlight reel, stitch the reviewed clips. Apply captions to the completed reel if requested.

```python
reel = videos_stitch(video_file_ids=[first.video_file_id, second.video_file_id])
captioned_reel = videos_captions_burn_highlighted(video_file_id=reel.video_file_id, style="tiktok")
final_review = videos_analyze(file_id=captioned_reel.video_file_id, analysis_type="quality_review")
```
