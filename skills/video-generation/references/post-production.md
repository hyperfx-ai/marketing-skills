# Video Post-Production

Set `source_video_file_id` to the stored file ID of an uploaded video or the `video_file_id` of a completed generation or edit. For each edit, confirm success and use its completed `video_file_id` as input to the next step.

The six editing tools labeled **Hyper Chat only** require an active conversation thread. On headless MCP or CLI, download the source, subtitle, and narration files you need and edit them with local FFmpeg or a video editor. Use those same editing steps on local files when working without Hyper.

## Subtitles

`videos_transcribe` returns transcript text. On MCP or CLI, extract the text string from the response and pass it as `transcript` to `videos_subtitles_generate`. The defaults are `format="srt"` and `max_chars_per_line=42`. Use `format="vtt"` for VTT output.

```python
transcript_text = videos_transcribe(file_id=source_video_file_id)
subs = videos_subtitles_generate(
    file_id=source_video_file_id,
    transcript=transcript_text,
    format="srt",
    max_chars_per_line=42,
)
```

`videos_subtitles_burn` (**Hyper Chat only**) takes the source `video_file_id` and `subtitle_file_id=subs.file_id`. It also accepts raw SRT or VTT via `subtitle_text`. Its defaults are `style="bold_outline"`, `position="bottom"`, `font_size=24`, and `font_color="white"`. Other positions are `"top"` and `"center"`.

```python
subtitled = videos_subtitles_burn(
    video_file_id=source_video_file_id,
    subtitle_file_id=subs.file_id,
    style="bold_outline",
    position="bottom",
)
```

| Style | Effect |
| --- | --- |
| `default` | Plain white text |
| `bold_outline` | Bold white with a black outline |
| `shadow` | White text with a drop shadow |
| `box` | White text on a semi-transparent black box |

## Voiceover and narration

`audio_speech_generate` defaults to `voice="nova"`, `model="tts-1"`, and `speed=1.0`. Available voices are `alloy`, `ash`, `coral`, `echo`, `fable`, `nova`, `onyx`, `sage`, and `shimmer`.

`videos_audio_add` (**Hyper Chat only**) defaults to `mode="replace"` and `audio_volume=1.0`. Set `mode="mix"` explicitly to retain the original audio. Use `audio_volume` to adjust the added track when mixing.

```python
audio = audio_speech_generate(
    text="Snap the lid shut before you head out.",
    voice="nova",
    model="tts-1",
    speed=1.0,
)
narrated = videos_audio_add(
    video_file_id=source_video_file_id,
    audio_file_id=audio.file_id,
    mode="mix",
    audio_volume=0.8,
)
```

## Highlighted captions

`videos_captions_burn_highlighted` (**Hyper Chat only**) transcribes the video audio with word timings. Defaults are `style="tiktok"`, `position="bottom"`, and `words_per_group=4`. The `"tiktok"` style places a colored box around the active word. The `"karaoke"` style changes the active word's color and accepts a `background` behind the caption. Customize with `highlight_color`, `base_color`, `font_size`, or a `language` hint. Positions are `"bottom"`, `"top"`, and `"center"`.

```python
captioned = videos_captions_burn_highlighted(
    video_file_id=narrated.video_file_id,
    style="tiktok",
    highlight_color="#3B82F6",
    base_color="white",
    words_per_group=4,
    position="bottom",
)
```

## Text overlays

`videos_text_overlays_add` (**Hyper Chat only**) adds titles, lower thirds, or calls to action at specified times. Positions are `top`, `bottom`, `center`, `top-left`, `top-right`, `bottom-left`, and `bottom-right`.

```python
titled = videos_text_overlays_add(
    video_file_id=captioned.video_file_id,
    overlays=[
        {
            "text": "Ready for the commute",
            "start_time": 0.0,
            "end_time": 3.0,
            "position": "top",
            "font_size": 48,
            "color": "white",
            "background": "black@0.5",
        }
    ],
)
```

## Extract clips

`videos_clips_extract` (**Hyper Chat only**) takes timestamps in seconds. Set `end_time` after `start_time`.

```python
clip = videos_clips_extract(
    video_file_id=source_video_file_id,
    start_time=45.0,
    end_time=60.0,
)
```

## Stitch clips

`videos_stitch` (**Hyper Chat only**) requires at least two completed `video_file_ids` in playback order. `transition="none"` is the default. Set `transition="crossfade"` for fades, with `crossfade_duration=0.5` seconds by default.
