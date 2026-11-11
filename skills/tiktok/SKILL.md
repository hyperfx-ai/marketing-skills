---
name: tiktok
description: Publish organic TikTok content (videos, photos, carousels) through the TikTok-compliant consent card via the Hyper MCP. Use when the user wants to post a video to TikTok, share photos on TikTok, upload to TikTok, or any phrase like "post this to TikTok" / "share on TikTok" / "put this on my TikTok". For paid TikTok advertising campaigns, use the `tiktok-ads` skill instead.
requires_toolkits:
  - tiktok
icon: tiktok
short_description: Publish organic TikTok videos, photos, and carousels through the TikTok consent card.
---

# TikTok

End-to-end skill for publishing organic content to TikTok. Each post waits for the user's Approve on a **TikTok Content Sharing Guidelines-compliant** consent card.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| TikTok ad campaign, Spark Ads, paid promotion | `tiktok-ads` |
| Instagram post / Reel / story | `instagram` |
| LinkedIn document or carousel post | `linkedin` |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **TikTok integration connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps) — this skill uses the TikTok Login Kit / Content Posting API (NOT the TikTok Marketing API).

If `tiktok_videos_send_from_url` is not found, the integration to connect is TikTok.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| Hyper chat | Call the tool by its name; `search_tools(queries=["<provider> <action>"])` shows its parameters | `<name>(...)` |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call_read("<name>", {...})`, `call_write` or `call_destructive`: the one that `describe` names in `call_with` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found: in Hyper chat, find its toolkit id with `discover_toolkits` and pass it to `enable_toolkit`. On an MCP client or the CLI, tell the user which integration to connect in Hyper.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `tiktok_videos_send_from_url`, `tiktok_post_video_from_file`, `tiktok_photos_send` | Post tools. Each call waits for the user's Approve on the consent card. |
| `tiktok_current_user_get` | Authenticated user profile. |
| `tiktok_creator_info_get` | Check posting capabilities and limits. |
| `tiktok_videos_list`, `tiktok_videos_query` | Browse the user's published videos. |
| `tiktok_posts_status_get` | Check the status of a previously submitted post. |
| `tiktok_videos_upload_from_url`, `tiktok_videos_upload_from_file`, `tiktok_photos_upload` | Send to inbox as draft (the user posts manually in the TikTok app). |

## Critical Rules

> **CRITICAL**: Call the post tool when the user wants to post to TikTok. Hyper pauses the call on a consent card in every access mode, and the user fills TikTok's form on that card. No setting turns this off.

> **CRITICAL**: Do NOT ask the user about privacy, policies, captions, or branded content settings before the call. The card asks for them.

> **CRITICAL**: Do NOT call the post tool again while its card waits, and do NOT tell the user the post went out until the tool returns.

## When the User Wants to Post

If the user says ANY of:

- "post this video/photo to TikTok"
- "share this on TikTok"
- "upload to TikTok"
- "put this on my TikTok"

**Call the post tool with what you know:**

| Media | Tool |
| --- | --- |
| Video from a URL | `tiktok_videos_send_from_url` |
| Video stored in Hyper (a `/files` path or file id) | `tiktok_post_video_from_file` |
| Photos or a carousel (max 35) | `tiktok_photos_send` |

Fill `title` when the user gave a caption. On a video tool, set `is_aigc` when you generated the media (Veo, Seedance, image gen, etc.). Send `privacy_level: "SELF_ONLY"` and both brand toggles off; the user sets the real values on the card.

## What the Consent Card Handles

The card is TikTok Content Sharing Guidelines compliant and handles:

- Creator identity display (username, avatar).
- Caption / title entry with character limits (`#hashtags` and `@mentions`).
- Privacy level selection (filtered to account-eligible options).
- Interaction settings (comments, duet, stitch).
- AI-generated content labeling.
- Commercial content disclosure (branded / promotional).
- Music Usage Confirmation and Branded Content Policy declarations.

Approve stays off until the user picks a privacy level and ticks the music declaration.

## After the Approve

The tool posts the settings the user approved on the card, not the arguments of your call. It polls the post status and returns a completion message. When the user rejects the card, the tool does not post; tell the user and stop.

## Media Format Requirements

**Videos:**
- Format: MP4 + H.264 recommended.
- Resolution: 720p minimum, 4K maximum.
- Aspect ratio: 9:16, 16:9, or 1:1.
- Duration: 3s minimum, max varies by account (`tiktok_creator_info_get` returns it).

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
2. You: call `tiktok_videos_send_from_url(video_url="<url>", privacy_level="SELF_ONLY", brand_content_toggle=false, brand_organic_toggle=false, is_aigc=false)`.
3. The consent card opens in the chat.
4. User sets privacy, caption, switches and declarations, then clicks Approve.
5. The tool posts the approved settings, polls, and returns status (complete, failed, or timeout).

## Inbox / Draft Path

These tools send content to the user's TikTok app, where the user posts it manually:

- `tiktok_videos_upload_from_url` — send video to inbox as draft.
- `tiktok_videos_upload_from_file` — upload file to inbox as draft.
- `tiktok_photos_upload` — send photos to inbox as draft.

Use these only when the user explicitly asks to "send to my TikTok drafts" or "I want to post manually in the app". Otherwise, use the post tools.
