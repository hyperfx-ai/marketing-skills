---
name: browser
description: Control a web browser for automation tasks, including authenticated sessions. Use when the user wants to automate a website, fill forms, navigate logged-in pages, save auth state, or extract data that requires real browser interaction.
use_cases:
  - Browse websites automatically
  - Interact with web pages
  - Use authenticated browser sessions
  - Scrape web content
  - Automate browser workflows
  - LinkedIn automation
  - Web navigation tasks
triggers:
  - browser
  - web automation
  - browse
  - navigate
  - linkedin
  - authenticated browsing
requires_toolkits:
  - web_browsing_toolkit
suggested_toolkits: []
---

# Web Browser Automation

You have access to a full browser that you can control for web automation tasks.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Web browsing toolkit** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## Authenticated Sessions

When using a browser that already has an authenticated context, try to go as far as possible without user assistance. For example, when using LinkedIn, you could be redirected to select an active login - use it.

### Using Browser Contexts

Browser contexts allow you to use pre-authenticated sessions for sites like LinkedIn, Gmail, etc.

**If a browser context is selected:**
- Use `web_browser_initialize_session(browser_context_id="<id>")` to start the browser with that context

**If no context is selected but the task requires authentication:**
1. Call `web_browser_list_contexts` to see available contexts
2. If a relevant context exists, confirm with the user FIRST before using it
3. Start with `web_browser_initialize_session(browser_context_id="<id>")`
4. If no suitable context exists, ask the user to add or select one

## Key Rules

- **Only use browser contexts within the web_browsing_toolkit** - don't try to use them with other toolkits
- When working with authenticated sites, always try to proceed as far as possible automatically
- Handle login prompts and redirects automatically when using an authenticated context
- **Do NOT take screenshots after every action** - the user can see the browser via the live view. Only take screenshots when the user explicitly requests one or you need to visually analyze page content

## Common Workflows

### Basic Web Navigation
1. Initialize browser session
2. Navigate to target URL
3. Interact with page elements
4. Extract or process content

### Authenticated Site Access
1. List available browser contexts
2. Confirm context selection with user
3. Initialize session with context
4. Proceed with automated tasks

### Workflow Mode Differences
In workflow/automated environments:
- Attempt to use the browser without context first
- Only ask about browser contexts if it clearly fails

In interactive mode:
- Confirm browser context usage with the user before starting
