---
name: slack
description: Slack messaging, file sharing, Block Kit formatting, and channel management. Use when the user wants to send Slack messages, post rich Block Kit layouts, share files, react, or manage channels and members.
use_cases:
  - Send messages in Slack channels
  - Upload and share files in Slack
  - Share generated images in Slack
  - Format messages with Block Kit
  - Manage Slack channels and threads
  - Search Slack messages
triggers:
  - slack
  - channel
  - message
  - upload file
  - block kit
requires_toolkits:
  - slack_toolkit
suggested_toolkits: []
---

# Slack Messaging

This skill provides comprehensive guidance for Slack messaging, file sharing, and formatting.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Slack integration** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## When NOT to Respond

Return ONLY the text `[NO_RESPONSE]` (nothing else) in these situations:

1. **Message mentions another user, not you**: If the user mentions another person (e.g., `@John` or `@SomeOtherBot`) and the message is directed at that person, not you.
2. **User explicitly asks to be ignored**: If the user says something like "ignore this", "don't respond", or similar.
3. **Message is clearly not for you**: If the conversation is between other users and doesn't require your input.
4. **Simple acknowledgments between users**: Messages like "thanks", "ok", "got it" directed at another person.

**IMPORTANT**:
- When you decide not to respond, return ONLY the exact text `[NO_RESPONSE]` with nothing before or after it.
- When in doubt, respond. It's better to be helpful than to stay silent when someone needs you.
- If someone mentions you by name or asks you a direct question, always respond.
- In DMs (direct messages), always respond unless explicitly asked not to.

## File Sharing - Critical Rules

**CRITICAL**: Files can ONLY be shared in Slack via upload. URLs and file paths do NOT render as viewable content in Slack.

- Use `slack_upload_file` to share any file in Slack
- Always upload to both the channel AND thread you are responding in, unless requested otherwise
- The `slack_upload_file` tool accepts a `file_id` parameter for files already stored in the system

### Sharing Generated Images

When you generate an image (e.g., via `openai_image_generation` or similar tools), the result includes a `file_id`. This image is NOT automatically displayed in Slack. You MUST explicitly upload it:

1. Generate the image using the image generation tool
2. Note the `file_id` from the result
3. Call `slack_upload_file` with that `file_id`, the current `channel_id`, and `thread_ts`

**Example workflow:**
- User asks: "Generate an image of a sunset"
- You call the image generation tool, which returns `file_id: "abc123"`
- You then call `slack_upload_file(channel_id="C...", file_id="abc123", thread_ts="...")`
- Now the image appears in Slack

Do NOT just say "Here's your image" without uploading it. The user will see nothing.

### Sharing Other Files

For any file you want to share (documents, CSVs, etc.), use `slack_upload_file` with either:
- `file_id`: For files already in the system
- `file_path`: For local files
- `content`: For text content to upload as a file

## Message Formatting

### When to Use Plain Text vs Block Kit
- **Simple messages**: Use plain markdown text via `slack_post_message` or `slack_reply_to_thread`
- **Tables, lists, structured data**: Use Block Kit `rich_text` blocks via `slack_send_block_kit_message`
- **Messages over 3000 characters**: Use `slack_send_large_message`

### Slack Markdown
Slack uses a simplified markdown:
- `*bold*` (single asterisks, not double)
- `_italic_`
- `~strikethrough~`
- `` `code` `` for inline code
- ` ```code block``` ` for code blocks
- `<url|display text>` for links (NOT `[text](url)`)

### Block Kit Rich Text

Block Kit's `rich_text` block provides flexible formatting:

**Available Elements:**
- `rich_text_section`: Single line of text with inline formatting
- `rich_text_list`: Bulleted or ordered lists (`style: "bullet"` or `style: "ordered"`)
- `rich_text_quote`: Quote blocks with vertical bar styling

**Element Types Within Sections:**
- `text`: Plain or styled text (supports `bold`, `italic`, `strike`, `code`)
- `link`: Hyperlinks with optional display text
- `emoji`: Emoji by name
- `user`: User mentions
- `channel`: Channel mentions

**Bulleted List Example:**
```json
{
    "type": "rich_text",
    "elements": [
        {
            "type": "rich_text_list",
            "style": "bullet",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [{"type": "text", "text": "First item"}]
                },
                {
                    "type": "rich_text_section",
                    "elements": [{"type": "text", "text": "Second item"}]
                }
            ]
        }
    ]
}
```

**Ordered List:** Use `"style": "ordered"` instead of `"bullet"`.

**Nested Lists:** Use the `indent` property:
```json
{
    "type": "rich_text_list",
    "style": "ordered",
    "indent": 1,
    "elements": [...]
}
```

**Inline Styling:**
```json
{
    "type": "text",
    "text": "Bold text",
    "style": {"bold": true}
}
```
Available styles: `bold`, `italic`, `strike`, `code`

**Links in Text:**
```json
{
    "type": "rich_text_section",
    "elements": [
        {"type": "text", "text": "Click "},
        {"type": "link", "text": "here", "url": "https://example.com"},
        {"type": "text", "text": " to continue"}
    ]
}
```

## Messaging Tools Quick Reference

| Action | Tool |
|--------|------|
| Send a message | `slack_post_message` |
| Reply in a thread | `slack_reply_to_thread` |
| Upload/share a file | `slack_upload_file` |
| Send Block Kit message | `slack_send_block_kit_message` |
| Send long message (>3000 chars) | `slack_send_large_message` |
| Update a message | `slack_update_message` |
| Delete a message | `slack_delete_message` |
| Add a reaction | `slack_add_reaction` |
| Pin a message | `slack_pin_message` |
| Search messages | `slack_search_messages` |

## Channel Management Quick Reference

| Action | Tool |
|--------|------|
| List channels | `slack_list_channels` |
| Get channel info | `slack_get_channel_info` |
| Create a channel | `slack_create_channel` |
| Set channel topic | `slack_set_channel_topic` |
| Set channel purpose | `slack_set_channel_purpose` |
| Invite users | `slack_invite_users_to_channel` |
| Get channel members | `slack_get_channel_members` |

## User Operations Quick Reference

| Action | Tool |
|--------|------|
| List workspace users | `slack_get_users` |
| Get user profile | `slack_get_user_profile` |
| Find user by email | `slack_find_user_by_email` |
| Get user presence | `slack_get_user_presence` |
| Set your status | `slack_set_user_status` |
| Create a reminder | `slack_create_reminder` |
