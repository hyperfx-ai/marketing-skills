---
name: youtube-transcript
description: Fetch and work with YouTube video transcripts and content. Use when the user pastes a YouTube URL and wants a transcript, summary, blog post, social post, quote extraction, show notes, or any other text derived from a video. Also use when the user wants to repurpose video content, research competitor videos, extract key points without watching, pull timestamps, translate a video, or analyze what someone said in a YouTube video.
metadata:
  version: 1.0.0
---

# YouTube Transcript

Fetch the full transcript of any YouTube video and turn it into whatever the user needs — summaries, blog posts, social content, quotes, show notes, or raw text.

## Requirements

- **Hyper MCP installed.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **YouTube toolkit enabled** at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations) — provides `youtube_transcript` and `youtube_reader`.

If `youtube_transcript` is not in the tool list, stop and tell the user to enable the YouTube toolkit in Hyper.

## Two tools — pick the right one

| Tool | When to use | Returns |
| --- | --- | --- |
| `youtube_transcript` | You need the raw transcript text or timestamped segments. Fast, reliable, always get this first. | Full text string + segments with start/duration timestamps |
| `youtube_reader` | You need AI-powered extraction from the video — summaries, Q&A, topic segmentation, translation, visual descriptions. | Free-form answer to your instruction |

**Default: start with `youtube_transcript`.** Use `youtube_reader` when you need something the raw text can't give you (e.g. visual descriptions, translation, or a structured extraction from a very long video).

## Critical rules

1. **`youtube_transcript` takes 15–30 seconds.** It spins up an isolated sandbox. Tell the user it's running and to expect a short wait — don't make them think it's stuck.
2. **Both video IDs and full URLs are accepted.** `"NZLAdOL9fP8"` and `"https://www.youtube.com/watch?v=NZLAdOL9fP8"` both work.
3. **Don't fabricate transcript content.** Always fetch before summarizing. Never rely on training knowledge about what a specific video says.
4. **Very long videos (>2 hours):** `youtube_transcript` handles these fine. Only use `youtube_reader` on long videos if you specifically need AI-powered extraction — it can hit token limits on very long content.
5. **No transcript available:** Some videos have transcripts disabled. If `youtube_transcript` fails, try `youtube_reader` as a fallback — it uses a different extraction method.

## Fetching the transcript

```python
youtube_transcript(
    video_id_or_url="https://www.youtube.com/watch?v=NZLAdOL9fP8",
    language="en"   # optional — omit to auto-detect
)
```

**Response structure:**

```json
{
  "success": true,
  "video_id": "NZLAdOL9fP8",
  "language": "English (auto-generated)",
  "text": "Full transcript as one string...",
  "segments": [
    { "text": "This week we launched Hyper MCP.", "start": 0.0, "duration": 3.2 },
    { "text": "It brings Hyper's built-in tools...", "start": 3.2, "duration": 4.1 }
  ],
  "total_duration": 342.0
}
```

Use `text` for most tasks. Use `segments` when you need timestamps (e.g. chapters, clip references, karaoke captions).

## Using youtube_reader for AI-powered extraction

```python
youtube_reader(
    url="https://www.youtube.com/watch?v=NZLAdOL9fP8",
    instruction="Summarize the key points. Then list the main features demonstrated, with timestamps."
)
```

Good `instruction` examples:
- `"Extract every claim made about pricing or cost."`
- `"List the action items mentioned, in order."`
- `"Translate this to Spanish."`
- `"What tools or products does the speaker mention by name?"`
- `"Identify the main sections of this video and give me a timestamp for each."`

## What to do with the transcript

Once you have the text, ask the user what they need — or infer it from context:

| What the user wants | What to produce |
| --- | --- |
| Blog post | Restructure the transcript into intro → sections → CTA. Clean up filler words. Add subheadings. |
| LinkedIn / Twitter post | Extract the 1–2 sharpest insights. Rewrite in first person if it's the user's own video. |
| Summary | 3–5 bullet points of key takeaways. |
| Show notes / description | Title, 2-sentence summary, timestamped chapters, links mentioned. |
| Quote extraction | Pull verbatim quotes with `start` timestamps from the segments array. |
| Repurpose for email | Rewrite as a narrative email — opening hook, key insight, CTA. |
| Research / competitive analysis | Summarize what the speaker claims, what products they recommend, and what pain points they describe. |

## Example outputs

**Input:** `"Get the transcript of https://www.youtube.com/watch?v=NZLAdOL9fP8 and write a LinkedIn post from it"`

**Flow:**
1. Call `youtube_transcript(video_id_or_url="https://www.youtube.com/watch?v=NZLAdOL9fP8")`
2. Read the returned `text`
3. Identify the 1–2 sharpest moments — what's surprising, useful, or quotable
4. Draft a LinkedIn post in the speaker's voice (first person) with a hook and a clear point

**Input:** `"Summarize this video for me: [URL]"`

**Flow:**
1. Call `youtube_transcript(video_id_or_url="[URL]")`
2. Return 4–6 bullet points of key takeaways, without padding or filler

**Input:** `"Pull the timestamps for each section of this video"`

**Flow:**
1. Call `youtube_transcript(video_id_or_url="[URL]")`
2. Use the `segments` array to identify topic shifts
3. Return a chapter list: `00:00 — Intro`, `01:23 — Feature demo`, etc.

## Related skills

| When to hand off | Skill |
| --- | --- |
| Mining comments from YouTube videos for customer research | [`customer-research`](../customer-research) |
| Finding top YouTube videos by topic | Use `youtube_top_videos` directly |
| Generating video content | [`video-generation`](../video-generation) |
