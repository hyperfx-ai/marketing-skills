---
name: tiktok
description: Publish organic TikTok content (videos, photos, carousels) through the TikTok-compliant interactive posting form via the Hyper MCP. Use when the user wants to post a video to TikTok, share photos on TikTok, upload to TikTok, or any phrase like "post this to TikTok" / "share on TikTok" / "put this on my TikTok". For paid TikTok advertising campaigns, use the `tiktok-ads` skill instead.
requires_toolkits:
  - tiktok
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
- **TikTok integration connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps) — this skill uses the TikTok Login Kit / Content Posting API (NOT the TikTok Marketing API).

If `search("tiktok_post_form_open")` does not find `tiktok_post_form_open`, stop and tell the user to enable Hyper MCP and connect TikTok.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call("<name>", {...})` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found, its integration is not connected or not enabled for the workspace: stop and tell the user which integration to connect.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `tiktok_post_form_open` | **The only entrypoint when a user wants to post.** Opens the compliance form. |
| `tiktok_videos_send_from_url`, `tiktok_post_video_from_file`, `tiktok_photos_send` | Final posting tools — call ONLY after the user submits the form. |
| `tiktok_current_user_get` | Authenticated user profile (does not require the form). |
| `tiktok_creator_info_get` | Check posting capabilities and limits. |
| `tiktok_videos_list`, `tiktok_videos_query` | Browse the user's published videos. |
| `tiktok_posts_status_get` | Check the status of a previously submitted post. |
| `tiktok_videos_upload_from_url`, `tiktok_videos_upload_from_file`, `tiktok_photos_upload` | Send to inbox as draft (user posts manually in the TikTok app — bypasses the form intentionally). |

## Critical Rules

> **CRITICAL**: ALWAYS use `tiktok_post_form_open` when a user wants to post to TikTok. NEVER call `tiktok_videos_send_from_url`, `tiktok_photos_send`, or `tiktok_post_video_from_file` directly in response to a user request. The posting form is required for TikTok compliance.

> **CRITICAL**: Do NOT ask the user about privacy, policies, captions, or branded content settings before opening the form. The form handles all of this interactively.

> **CRITICAL**: Call `tiktok_post_form_open` immediately when the user wants to post. Do not gather information first.

## When the User Wants to Post

If the user says ANY of:

- "post this video/photo to TikTok"
- "share this on TikTok"
- "upload to TikTok"
- "put this on my TikTok"

**Immediately call `tiktok_post_form_open`:**

```python
tiktok_post_form_open(
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
- Call `tiktok_videos_send_from_url` or `tiktok_photos_send` directly.

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

When calling `tiktok_post_form_open`, provide what you know:

| Parameter | When to provide |
| --- | --- |
| `media_type` | Always (`"video"` or `"photo"`). |
| `media_url` | Single video or single photo. |
| `media_urls` | Photo carousel (list of URLs, max 35). |
| `video_duration_sec` | If known — enables duration validation. |
| `title` | If the user mentioned a caption. |
| `is_aigc` | If you generated the media (Veo, Seedance, image gen, etc.). |

## After Form Submission

When the user fills out and submits the form, you receive a message containing all their chosen settings. At that point, call the appropriate posting tool with the exact parameters from their submission:

- **Video from URL**: `tiktok_videos_send_from_url`
- **Video from file**: `tiktok_post_video_from_file`
- **Photos**: `tiktok_photos_send`

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
2. You: call `tiktok_post_form_open(media_type="video", media_url="<url>")`.
3. The posting form opens in the artifact panel.
4. User configures privacy, caption, policies, etc.
5. User clicks "Post to TikTok".
6. You receive their settings as a message.
7. You: call `tiktok_videos_send_from_url(...)` with the submitted parameters.
8. Tool auto-polls and returns status (complete, failed, or timeout).

## Inbox / Draft Path (no form required)

These tools intentionally bypass the form — they send content to the user's TikTok app for manual posting:

- `tiktok_videos_upload_from_url` — send video to inbox as draft.
- `tiktok_videos_upload_from_file` — upload file to inbox as draft.
- `tiktok_photos_upload` — send photos to inbox as draft.

Use these only when the user explicitly asks to "send to my TikTok drafts" or "I want to post manually in the app". Otherwise, default to the form path.
