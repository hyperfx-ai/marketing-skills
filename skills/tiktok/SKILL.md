---
name: tiktok
description: Publish organic TikTok content (videos, photos, carousels) through the TikTok-compliant interactive posting form via the Hyper MCP. Use when the user wants to post a video to TikTok, share photos on TikTok, upload to TikTok, or any phrase like "post this to TikTok" / "share on TikTok" / "put this on my TikTok". For paid TikTok advertising campaigns, use the `tiktok-ads` skill instead.
icon: tiktok
short_description: Publish organic TikTok videos, photos, and carousels through the compliance posting form.
---

# TikTok

End-to-end skill for publishing organic content to TikTok through the **TikTok Content Sharing Guidelines-compliant** interactive posting form.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| TikTok ad campaign, Spark Ads, paid promotion | `tiktok-ads` |
| Instagram post / Reel / story | `instagram` |
| LinkedIn document or carousel post | `linkedin` |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **TikTok integration connected** at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations) — this skill uses the TikTok Login Kit / Content Posting API (NOT the TikTok Marketing API).

If `tiktok_open_post_form` is not in the tool list, stop and tell the user to enable Hyper MCP and connect TikTok.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `tiktok_open_post_form` | **The only entrypoint when a user wants to post.** Opens the compliance form. |
| `tiktok_post_video_from_url`, `tiktok_post_video_from_file`, `tiktok_post_photos` | Final posting tools — call ONLY after the user submits the form. |
| `tiktok_get_user_info` | Authenticated user profile (does not require the form). |
| `tiktok_query_creator_info` | Check posting capabilities and limits. |
| `tiktok_list_videos`, `tiktok_query_videos` | Browse the user's published videos. |
| `tiktok_get_post_status` | Check the status of a previously submitted post. |
| `tiktok_upload_video_from_url`, `tiktok_upload_video_from_file`, `tiktok_upload_photos` | Send to inbox as draft (user posts manually in the TikTok app — bypasses the form intentionally). |

## Critical Rules

> **CRITICAL**: ALWAYS use `tiktok_open_post_form` when a user wants to post to TikTok. NEVER call `tiktok_post_video_from_url`, `tiktok_post_photos`, or `tiktok_post_video_from_file` directly in response to a user request. The posting form is required for TikTok compliance.

> **CRITICAL**: Do NOT ask the user about privacy, policies, captions, or branded content settings before opening the form. The form handles all of this interactively.

> **CRITICAL**: Call `tiktok_open_post_form` immediately when the user wants to post. Do not gather information first.

## When the User Wants to Post

If the user says ANY of:

- "post this video/photo to TikTok"
- "share this on TikTok"
- "upload to TikTok"
- "put this on my TikTok"

**Immediately call `tiktok_open_post_form`:**

```python
tiktok_open_post_form(
    media_type="video",            # or "photo"
    media_url="<url>",             # single video / single photo URL
    media_urls=["<url>", ...]      # for photo carousels (max 35)
)
```

**DO NOT:**
- Ask about privacy settings before opening the form.
- Ask about caption / title before opening the form.
- Ask about policy acknowledgments before opening the form.
- Request any metadata — just open the form.
- Call `tiktok_post_video_from_url` or `tiktok_post_photos` directly.

## What the Form Handles

The interactive posting form is TikTok Content Sharing Guidelines compliant and handles:

- Creator identity display (username, avatar).
- Media preview (video player or photo grid).
- Caption / title entry with character limits (`#hashtags` and `@mentions`).
- Privacy level selection (filtered to account-eligible options).
- Interaction settings (comments, duet, stitch).
- AI-generated content labeling.
- Commercial content disclosure (branded / promotional).
- Music Usage Confirmation acknowledgment.
- Branded Content Policy acknowledgment.
- Posting restrictions / ban detection.
- Video duration validation.

## Pre-fill Parameters

When calling `tiktok_open_post_form`, provide what you know:

| Parameter | When to provide |
| --- | --- |
| `media_type` | Always (`"video"` or `"photo"`). |
| `media_url` | Single video or single photo. |
| `media_urls` | Photo carousel (list of URLs, max 35). |
| `video_duration_sec` | If known — enables duration validation. |
| `title` | If the user mentioned a caption. |
| `is_aigc` | If you generated the media (Sora, Veo, image gen, etc.). |

## After Form Submission

When the user fills out and submits the form, you receive a message containing all their chosen settings. At that point, call the appropriate posting tool with the exact parameters from their submission:

- **Video from URL**: `tiktok_post_video_from_url`
- **Video from file**: `tiktok_post_video_from_file`
- **Photos**: `tiktok_post_photos`

The posting tool will automatically poll status and return a completion message.

## Media Format Requirements

**Videos:**
- Format: MP4 + H.264 recommended.
- Resolution: 720p minimum, 4K maximum.
- Aspect ratio: 9:16, 16:9, or 1:1.
- Duration: 3s minimum, max varies by account (checked by the form).

**Photos:**
- Format: WebP or JPEG only (PNG is NOT supported).
- Resolution: 1080p maximum.
- Size: 20MB per photo maximum.
- Carousel: up to 35 photos.

**Domain verification:**
- All media URLs must be from verified domains in the TikTok Developer Portal.
- Unverified domains will fail with an authentication error.

## Example Flow

1. User: "Post this video to TikTok".
2. You: call `tiktok_open_post_form(media_type="video", media_url="<url>")`.
3. The posting form opens in the artifact panel.
4. User configures privacy, caption, policies, etc.
5. User clicks "Post to TikTok".
6. You receive their settings as a message.
7. You: call `tiktok_post_video_from_url(...)` with the submitted parameters.
8. Tool auto-polls and returns status (complete, failed, or timeout).

## Inbox / Draft Path (no form required)

These tools intentionally bypass the form — they send content to the user's TikTok app for manual posting:

- `tiktok_upload_video_from_url` — send video to inbox as draft.
- `tiktok_upload_video_from_file` — upload file to inbox as draft.
- `tiktok_upload_photos` — send photos to inbox as draft.

Use these only when the user explicitly asks to "send to my TikTok drafts" or "I want to post manually in the app". Otherwise, default to the form path.
