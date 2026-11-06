---
name: gmail
description: Manage Gmail end-to-end — send, reply, search, drafts, labels, attachments, and inbox organization. Use when the user wants to send or reply to email, clean up an inbox, build label systems, manage drafts, or pull attachments.
use_cases:
  - Organize my inbox with labels
  - Send emails via Gmail
  - Create and manage email drafts
  - Move emails between folders
  - Archive or trash emails
  - Search and filter Gmail messages
  - Email triage and cleanup
triggers:
  - gmail
  - email
  - inbox
  - send email
  - labels
  - drafts
requires_toolkits:
  - gmail
suggested_toolkits: []
icon: gmail
short_description: Read, draft, send, and organize Gmail, including labels and attachments.
---

# Gmail Email Management

This skill provides comprehensive guidance for managing Gmail emails, labels, and organization.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Gmail integration** enabled at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps).

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| Hyper chat | Call the tool by its name; `search_tools(queries=["<provider> <action>"])` shows its parameters | `<name>(...)` |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call_read("<name>", {...})`, `call_write` or `call_destructive`: the one that `describe` names in `call_with` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found: in Hyper chat, find its toolkit id with `discover_toolkits` and pass it to `enable_toolkit`. On an MCP client or the CLI, tell the user which integration to connect in Hyper.

## Label Operations - Critical Distinctions

### ADD LABEL (keeps email in current location + adds new label)
- Use: `gmail_labels_add`
- Use case: Adding labels WITHOUT moving the email from its current location
- Example: Email stays in INBOX and also gets labeled "Important"

### MOVE TO LABEL (removes from INBOX + adds to target label)
- Use: `gmail_messages_move_to_label`
- Use case: Moving email OUT of inbox and INTO a specific label/folder
- Example: Email is removed from INBOX and moved to "Archive" or "Work"
- This performs TWO operations: removes INBOX label + adds target label

### REMOVE LABEL (removes specific label)
- Use: `gmail_labels_remove`
- Use case: Removing labels from an email
- Can remove any label including INBOX

## Getting Label IDs

**CRITICAL**: Most Gmail label operations require label IDs, NOT label names.
- Always call `gmail_labels_list` first to get available labels and their IDs
- Label IDs look like: "Label_123", "Label_456", or system labels: "INBOX", "SENT", "TRASH"
- Never guess or make up label IDs

## Common Workflows

### Email Triage/Organization
1. Call `gmail_labels_list` to see available labels
2. Call `gmail_messages_list` to get emails
3. Use `gmail_messages_move_to_label` to move emails from INBOX to appropriate labels

### Adding Categories (keep in inbox)
1. Call `gmail_labels_list` to get label IDs
2. Use `gmail_labels_add` to categorize emails while keeping them in INBOX

### Creating New Labels
- Use `gmail_labels_create` if the desired label doesn't exist
- Returns the new label's ID for immediate use

## Searching and Listing Messages

**gmail_messages_list** supports full Gmail search query syntax:
- `query` parameter accepts the same syntax as Gmail's search box
- Examples: `"is:unread"`, `"from:user@example.com"`, `"has:attachment subject:invoice"`
- Combine operators: `"from:user@example.com is:unread has:attachment"`
- With no `query`, the tool adds `-in:draft`. When you pass a `query`, add `-in:draft` to it yourself
- The `label` parameter takes the label NAME (or INBOX, SENT, SPAM, TRASH, CATEGORY_*), not a `Label_…` ID. An ID is ignored with no error

## Drafts Workflow

### Creating and sending draft emails
1. `gmail_drafts_create` - Create initial draft
2. `gmail_drafts_update` - Edit existing draft (optional)
3. `gmail_drafts_send` - Send the draft as email

### Managing drafts
- `gmail_drafts_list` - List all draft emails
- `gmail_drafts_get` - Get a specific draft by ID
- `gmail_drafts_delete` - Delete a draft without sending

### When to use drafts vs direct send
- Use `gmail_messages_send` for immediate one-step sending
- Use the draft workflow when a person must review or edit the email before it is sent
- To send later, pass `scheduled_at="<ISO datetime>"` to `gmail_messages_send`; a draft does not schedule

### Replies
- `gmail_messages_reply(message_id=..., body=..., reply_all=False)` sends a reply at once
- `gmail_drafts_create(reply_to_message_id=..., mode="reply", body=...)` drafts a reply; `mode` is also `"reply_all"`, or `"forward"` with `to`

## Email Actions - Important Distinctions

### Archive vs Trash
- `gmail_messages_archive` - Removes from INBOX but keeps in "All Mail" (recoverable, not deleted)
- `gmail_messages_trash` - Moves to Trash folder (will be auto-deleted after 30 days)
- Archive is the preferred way to "clean up" inbox while keeping emails

### Attachments
- `gmail_attachments_get` - Download attachments from received emails
- To attach files, pass their workspace file IDs in `file_ids`, not `/files/...` paths (`files_create` returns the `file_id`). An unknown ID is skipped with no error, so check each ID before you send

## Tool Selection Quick Reference

| Action | Tool |
|--------|------|
| Add label X | `gmail_labels_add` |
| Move to label X | `gmail_messages_move_to_label` |
| Remove from inbox | `gmail_messages_move_to_label` (move to target) OR `gmail_labels_remove` (just remove INBOX) |
| Archive email | `gmail_messages_archive` (preferred for cleanup) |
| Delete/trash email | `gmail_messages_trash` |
| Send email now | `gmail_messages_send` |
| Send email later | `gmail_messages_send` with `scheduled_at="<ISO datetime>"` |
| Reply now | `gmail_messages_reply` |
| Draft a reply or forward | `gmail_drafts_create` with `reply_to_message_id` |
