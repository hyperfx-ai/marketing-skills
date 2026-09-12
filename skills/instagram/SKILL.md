---
name: instagram
description: Manage Instagram professional accounts via the Hyper MCP — publish photos, Reels, Stories, and carousels; moderate comments and mentions; send Direct Messages; pull account and media insights. Uses the Instagram API with Instagram Login (Business Login). Use when the user mentions Instagram posts, Reels, Stories, carousels, IG DMs, Instagram comments, mentions, profile, or analytics. For paid Instagram advertising, use `meta-ads`.
requires_toolkits:
  - instagram_toolkit
icon: instagram
short_description: Publish photos, Reels, Stories, and carousels, moderate comments, send DMs, and pull insights.
---

# Instagram

Complete skill for managing Instagram professional accounts through the Instagram API with Instagram Login (Business Login). Covers content publishing, messaging, comment moderation, insights, and profile management.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Paid Instagram / Facebook ads, boosting a post, Advantage+ | `meta-ads` |
| Competitor ad research from the Meta Ad Library | `meta-ads-library` |
| TikTok publishing | `tiktok` |
| LinkedIn document or carousel posts | `linkedin` |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Instagram integration connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps) — this skill uses the **Instagram API with Instagram Login** (NOT the older Instagram Graph API via Facebook Login).
- For organization posts to a company page, the connected account must have permission to post for that organization.

If `search("instagram_current_user_get")` does not find `instagram_current_user_get`, stop and tell the user to enable Hyper MCP and connect Instagram.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call("<name>", {...})` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found, its integration is not connected or not enabled for the workspace: stop and tell the user which integration to connect.

## Tool surface

| Tool group | Tools |
| --- | --- |
| Account | `instagram_current_user_get`, `instagram_users_get` *(look up any public IG profile by username or ID — useful for researching commenters and DM contacts)* |
| Publishing | `instagram_photo_containers_create`, `instagram_reel_containers_create`, `instagram_carousel_containers_create`, `instagram_container_status_check`, `instagram_media_publish`, `instagram_publishing_limits_check` |
| Media library | `instagram_media_list`, `instagram_media_get`, `instagram_album_children_get`, `instagram_stories_list`, `instagram_tagged_media_get` |
| Comments | `instagram_comments_list`, `instagram_comments_send`, `instagram_comments_reply`, `instagram_comments_hide`, `instagram_comments_delete`, `instagram_comments_toggle` |
| Direct Messages | `instagram_conversations_list`, `instagram_conversation_messages_get`, `instagram_messages_get`, `instagram_messages_send`, `instagram_media_messages_send`, `instagram_post_messages_send`, `instagram_messages_react` |
| Insights | `instagram_account_insights_get`, `instagram_media_insights_get` |

## Critical Rules

> **CRITICAL**: This toolkit uses the **Instagram API with Instagram Login** (not the older Instagram Graph API via Facebook Login). Metric names and available fields differ from the older API. Always use the metric names documented in this skill.

> **CRITICAL**: The `engagement` metric does NOT exist in this API. Use individual metrics like `likes`, `comments`, `shares`, `total_interactions` instead.

> **CRITICAL**: The `impressions` metric is NOT valid for account-level insights. Use `reach` or `views` instead.

> **CRITICAL**: Content publishing uses a two-step container workflow: (1) create a media container, (2) publish it. For video content, poll the container status until `FINISHED` before publishing.

> **CRITICAL**: Instagram DM responses must be sent within 24 hours of the user's last message (standard messaging window). The Human Agent tag extends this to 7 days if approved.

> **IMPORTANT**: Publishing rate limit is 100 API-published posts per 24-hour rolling window. Carousels count as 1 post. Always call `instagram_publishing_limits_check` before bulk publishing.

> **CRITICAL**: Do NOT use the `location_id` parameter on photo, reel, or carousel containers unless the user explicitly provides a verified Facebook Page ID. This integration uses Instagram Business Login which cannot look up or validate location IDs. Passing an invalid or guessed ID will cause a 400 error (`Param location_id is not a valid location page ID`). If a user asks for location tagging, explain that they need to provide their Facebook Page ID with location data.

> **CRITICAL**: When passing media URLs (`image_url`, `video_url`, `cover_url`, `media_url`) to any Instagram tool, use the URL **exactly as returned** by the source tool — most commonly the `url` field from `read_file` or `display_file`. Do NOT:
> - Reconstruct or shorten the URL.
> - Drop, change, or invent any query parameters (signatures, timestamps, etc.).
> - Substitute a different host.
> - Copy a URL from memory or transcribe it character-by-character — call `read_file` again instead.
>
> Hyper-hosted CDN URLs are automatically resized and re-signed for Meta when needed, so just hand them through verbatim. A single-character corruption in a presigned signature causes Meta to return a misleading `9004 / 2207052: Only photo or video can be accepted as media type` error.

> **IMPORTANT**: Most tools act on the authenticated account automatically — you do NOT need to pass a `user_id`. The toolkit resolves it from the access token internally. Only call `instagram_current_user_get` when you actually need profile details (username, follower counts, etc.) to display to the user. Use `instagram_users_get(user_id=...)` only when looking up a *different* account.

## Phase 1: Account Lookup (optional)

### Get the connected account's profile

```python
instagram_current_user_get()
```

Returns: `user_id`, `username`, `name`, `account_type`, `profile_picture_url`, `followers_count`, `follows_count`, `media_count`, `biography`, `website`.

You do not need to thread the `user_id` into other tool calls — they resolve it automatically.

## Phase 2: Content Publishing

### Publishing workflow

1. **Create a media container** (photo, reel, story, or carousel).
2. **Check container status** (required for video / reels — poll until `FINISHED`).
3. **Publish the container.**
4. **Verify** by listing recent media.

### Single photo post

```python
instagram_photo_containers_create(
    image_url="https://example.com/photo.jpg",   # Public JPEG URL, max 8MB
    caption="Your caption here #hashtag",
    alt_text="Accessibility description",
)
# Returns container ID

instagram_media_publish(
    creation_id="<container_id>",
)
```

### Reel (short-form video)

```python
instagram_reel_containers_create(
    video_url="https://example.com/video.mp4",   # Public MP4/MOV, max 300MB, 3s-15min
    caption="Reel caption #reels",
    cover_url="https://example.com/cover.jpg",   # Optional cover image
    share_to_feed=True,
)

# MUST poll status for video content
instagram_container_status_check(container_id="<container_id>")
# Wait until status_code == "FINISHED", poll once per minute, max 5 minutes

instagram_media_publish(creation_id="<container_id>")
```

### Story (24-hour expiry)

> **Note:** Story *publishing* is not yet supported by this MCP integration. To read currently active stories use:
>
> ```python
> instagram_stories_list()
> ```
>
> If the user asks to post a story, inform them this capability is not yet available and suggest posting a Reel with `share_to_feed=True` as an alternative.

### Carousel (2-10 items)

```python
# Step 1: create child containers (each with is_carousel_item=True for photos)
instagram_photo_containers_create(
    image_url="https://example.com/photo1.jpg",
    is_carousel_item=True,
)
# Repeat for each image / video

# Step 2: create the carousel container with child IDs
instagram_carousel_containers_create(
    children=["<child_id_1>", "<child_id_2>", "<child_id_3>"],
    caption="Carousel caption",
)

# Step 3: publish
instagram_media_publish(creation_id="<carousel_container_id>")
```

### Content limits

| Type | Format | Max size | Duration |
| --- | --- | --- | --- |
| Photo | JPEG | 8MB | — |
| Reel | MP4 / MOV | 300MB | 3s – 15min |
| Story image | JPEG | 8MB | — |
| Story video | MP4 / MOV | 100MB | 3s – 60s |
| Caption | Text | 2200 chars | 30 hashtags, 20 @tags |
| Carousel | Mixed | 2 – 10 items | — |

## Phase 3: Comment Moderation

### Read comments

```python
instagram_comments_list(media_id="<media_id>")
```

### Post a comment

```python
instagram_comments_send(media_id="<media_id>", message="Great post!")
```

### Reply to a comment

```python
instagram_comments_reply(comment_id="<comment_id>", message="Thanks!")
```

### Moderate comments

```python
# Hide spam / inappropriate comments
instagram_comments_hide(comment_id="<comment_id>", hide=True)

# Delete a comment (only the media owner can delete)
instagram_comments_delete(comment_id="<comment_id>")

# Toggle comments on / off for a post
instagram_comments_toggle(media_id="<media_id>", comment_enabled=False)
```

### Respond to mentions

> **Note:** Mention-specific tools (`instagram_reply_to_mention`, `instagram_get_mentioned_media`, `instagram_get_mentioned_comment`) are not yet available in this MCP integration. Mentions appear as comments on your media — respond to them using `instagram_comments_reply` with the comment ID from `instagram_comments_list`.

## Phase 4: Direct Messages (CRM)

### List conversations

```python
instagram_conversations_list()
```

### Read messages

```python
# Get message IDs from a conversation
instagram_conversation_messages_get(conversation_id="<conversation_id>")

# Get full message details (only 20 most recent are queryable)
instagram_messages_get(message_id="<message_id>")
```

### Send messages

```python
# Text message
instagram_messages_send(
    recipient_id="<recipient_igsid>",   # From the message's 'from' field
    text="Thanks for reaching out!",
)

# Media attachment (image, video, audio, PDF)
instagram_media_messages_send(
    recipient_id="<recipient_igsid>",
    media_type="image",                 # image, video, audio, or file
    media_url="https://example.com/photo.jpg",
)

# Share a published post via DM
instagram_post_messages_send(
    recipient_id="<recipient_igsid>",
    post_id="<media_id>",               # Must be your own post
)

# React to a message
instagram_messages_react(
    recipient_id="<recipient_igsid>",
    message_id="<message_id>",
    reaction="love",
)
```

### Messaging constraints

- The recipient must have initiated the conversation first.
- 24-hour response window from the user's last message (7 days with the Human Agent tag).
- Text messages: UTF-8, max 1000 bytes.
- Media limits: images (PNG / JPEG, 8MB), videos (MP4 / OGG, 25MB), audio (AAC / WAV, 25MB), files (PDF, 25MB).

## Phase 5: Analytics & Insights

### Account-level insights

```python
instagram_account_insights_get(
    metric=["reach", "profile_views", "follower_count", "accounts_engaged", "total_interactions"],
    period="week",
)
```

> **Note:** Some metrics (`profile_views`, `total_interactions`, demographic metrics) require `instagram_business_manage_insights` permission and a **Business** account — they will be silently omitted for Creator accounts. If a metric is missing from the response, check the account type returned by `instagram_current_user_get`.

**Valid account metrics:**

| Metric | Description |
| --- | --- |
| `reach` | Unique accounts that saw any content. |
| `follower_count` | Total followers (lifetime period only). |
| `website_clicks` | Clicks on the website link in the profile. |
| `profile_views` | Profile page views. |
| `online_followers` | Followers online at a given time. |
| `accounts_engaged` | Unique accounts that interacted. |
| `total_interactions` | Total likes, comments, shares, saves, replies. |
| `likes` | Total likes across all content. |
| `comments` | Total comments across all content. |
| `shares` | Total shares across all content. |
| `saves` | Total saves across all content. |
| `replies` | Total replies (stories / messages). |
| `follows_and_unfollows` | Net follower changes. |
| `profile_links_taps` | Taps on profile links. |
| `views` | Total content views. |
| `engaged_audience_demographics` | Demographics of the engaged audience. |
| `reached_audience_demographics` | Demographics of the reached audience. |
| `follower_demographics` | Demographics of followers. |

**Invalid account metrics:** `impressions`, `email_contacts`, `phone_call_clicks`, `text_message_clicks`, `get_directions_clicks`.

### Media-level insights

```python
instagram_media_insights_get(
    media_id="<media_id>",
    metric=["reach", "likes", "comments", "saved", "shares", "total_interactions"],
)
```

- **Common metrics (all non-Story media):** `reach`, `saved`, `likes`, `comments`, `shares`, `total_interactions`, `views`.
- **Reel-only extras** (auto-stripped for non-Reels): `ig_reels_avg_watch_time`, `ig_reels_video_view_total_time`, `clips_replays_count`, `ig_reels_aggregated_all_plays_count`.
- **Story-only metrics:** `reach`, `replies`, `follows`, `navigation`, `profile_visits`, `profile_activity`, `views`.

> **Tip:** When unsure if media is a Reel, just use the common metrics. Reel-only metrics sent to non-Reel media will be auto-stripped by the server.

**Invalid media metrics:** `engagement`, `impressions`, `plays`, `saves` — for media use `saved` (not `saves`; `saves` is account-level only).

### Period values

| Period | Description |
| --- | --- |
| `day` | Daily breakdown. |
| `week` | Weekly breakdown. |
| `days_28` | 28-day breakdown. |
| `month` | Monthly breakdown. |
| `lifetime` | All time (required for `follower_count`). |

## Phase 6: Media & Story Management

### Browse media library

```python
# List recent posts (up to 10K)
instagram_media_list(limit=25)

# Get details of a specific post
instagram_media_get(media_id="<media_id>")

# Get carousel children
instagram_album_children_get(media_id="<carousel_media_id>")

# List active stories (24h window)
instagram_stories_list()

# Get tagged media
instagram_tagged_media_get()
```
