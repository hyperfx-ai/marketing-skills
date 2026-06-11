---
name: sandbox
description: Execute code, build webapps, and analyze data in the sandbox. Use when the user wants to run Python scripts, process files, scrape at scale, build and preview web apps, or produce CSV/Excel/JSON/PDF outputs.
use_cases:
  - Execute Python scripts
  - Build web applications from starter repositories
  - Create data visualizations and charts
  - Run code in a sandbox
  - Process and analyze data locally
  - Create CSV/Excel/JSON/PDF reports
  - Generate professional documents
  - Bulk web scraping and data collection
  - Multi-step tool pipelines (search → process → save to database)
  - Code-driven tool orchestration with call_tool
triggers:
  - sandbox
  - starter repo
  - git clone
  - code execution
  - python
  - webapp
  - dashboard
  - react app
  - vp
  - vite
  - data analysis
  - charts
  - pdf report
  - bulk scrape
  - call_tool
  - tool chaining
  - data pipeline
  - website building
requires_toolkits:
  - sandbox
---

# Sandbox Development

Execute code, build webapps, and analyze data in E2B with a clone-first workflow.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Sandbox toolkit** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## Core Principles

1. Sandbox is lean: no pre-baked framework apps.
2. For app work, initialize inside the sandbox active directory. The sandbox active directory is authoritative. Use `sandbox_pwd()` to inspect it and `sandbox_set_active_directory(path=...)` to change it.
3. Verify runtime/tooling availability before assuming defaults.
4. Python/data-analysis output now has a dedicated results surface in the UI; app work uses the current thread's sandbox IDE + preview surface.
5. Save user-deliverable files to `/files/` for sharing when you explicitly want to attach or share a file.
6. `/files/...` is VFS, not a sandbox-local directory. Sandbox code can only open `/home/user/...` unless you copy data in first.

## User Interaction Rules

1. **Users are non-technical.** Never ask about stack, framework, deployment, hosting, SSR, routing, or build tools. These are your decisions, not theirs.
2. **Always use the React Router + shadcn starter** (`hyper-sandbox-1`) for websites, landing pages, dashboards, and web apps. Do not offer HTML, Next.js, Astro, or other alternatives. The only exception is if the user explicitly names a different stack.
3. **Infer scope from context.** Short brief = single-page site. Detailed multi-section content = multi-page. Don't ask "full site or landing page?" -- decide based on what you're given.
4. **When given a reference URL**, perform brand research before building. See `references/frontend-design.md` for the workflow. Use normal agent tool calls for research -- not in-sandbox code.
5. The only acceptable questions to ask users are about their business, messaging, or what they want to communicate -- never about technology choices.

## Routing Table

Read the focused reference based on the task:

| Need | Reference |
|------|-----------|
| Runtime checks (Node/pnpm/uv/CLI availability) | `references/runtime-and-tooling.md` |
| Initialize project from starter repository | `references/starter-repositories.md` |
| Use `agent-browser` for snapshot/screenshot/click | `references/agent-browser.md` |
| Export artifacts, preview apps, share URLs | `references/artifacts-and-sharing.md` |
| Create frontend design and websites | `references/frontend-design.md` |
| Data analysis, charts, file processing | `references/data-analysis.md` |
| Bulk scraping, multi-step tool pipelines, code-driven tool orchestration | `references/tool-chaining.md` |

When the request spans multiple areas, follow references in this order:
1. `references/runtime-and-tooling.md`
2. `references/starter-repositories.md`
3. `references/tool-chaining.md`
4. `references/data-analysis.md`
5. `references/agent-browser.md`
6. `references/artifacts-and-sharing.md`

## Core Tools (Sandbox Toolkit)

| Tool | Use |
|------|-----|
| `sandbox_start()` | Start sandbox environment |
| `sandbox_shutdown()` | Shut down and destroy the sandbox |
| `shell(command)` | Execute commands in the sandbox with cwd auto-set to the current session working directory |
| `python(code)` | Execute Python |
| `javascript(code)` | Execute JavaScript |
| `sandbox_pwd()` | Show the current sandbox active directory |
| `sandbox_set_active_directory(path)` | Set the default directory for shell and file tools |
| `sandbox_edit_file(path, old, new)` | Edit existing files; relative paths resolve inside the active directory |
| `sandbox_write_file(path, content)` | Create or overwrite a file; relative paths resolve inside the active directory |
| `sandbox_check_running_port(port)` | Check if a port is active |
| `sandbox_health_check(port)` | Health check a running service |
| `sandbox_get_preview_url(port)` | Get public URL for running app |
| `sandbox_screenshot(url)` | Screenshot URL and return file URL |
| `display_file(path=...)` | Show file to user in chat |

## Sandbox Lifecycle

1. The default sandbox is persistent. Use it across runs unless the task is truly one-time.
2. Sandboxes auto-pause after inactivity and can be resumed later with files preserved.
3. When the user wants to stop the entire sandbox, call `sandbox_shutdown()`.
4. Stopping a process inside the sandbox is not the same as shutting down the sandbox itself.

## Best Practices

1. Treat the sandbox as a persistent owned workspace for the current agent, and treat the active directory as the default root for shell and file tools.
2. `shell(command)` already starts in the sandbox active directory. Do not begin by `cd`-ing to guessed app paths.
3. For app workflows, clone into a clear project folder under `/home/user`, then call `sandbox_set_active_directory(path=...)` for that folder.
4. Confirm tool availability (`node`, `pnpm`, `vp`, `uv`, `agent-browser`) before relying on them.
5. Use `pnpm` for package installation, `vp dev` for frontend dev servers, `uv` for Python.
6. Keep app preview and artifact export separate: preview with `sandbox_get_preview_url`, share files from `/files/`.
7. Prefer normal agent tool calls (outside sandbox Python) for most tool usage.
8. Use in-sandbox `call_tool` only for bulk/high-volume workflows (for example scraping/enrichment loops) where local Python orchestration is necessary.
9. Until fully validated, only use in-sandbox `call_tool` for tools that do **not** require approval (`requires_approval` / `sensitive_operation` should be false). For approval-sensitive tools, call them directly via normal agent tool calls.
10. For file transfers into the sandbox, use `copy_files(...)` to copy files explicitly into `/home/user/...`.
11. For Python analysis, let `python(code)` produce charts/files naturally first. If you want a chat attachment, copy the file to `/files/...` with `copy_files(...)` first, then call `display_file(path="/files/...")`.
12. `sandbox_shutdown()` permanently destroys the sandbox. Warn the user that unsaved work will be lost. If they only want to stop a specific process (e.g. a dev server), use `shell("kill ...")` instead.
13. If the user is building an app, reuse the persistent sandbox so preview URLs, files, logs, and terminal history stay attached to the same `sandbox_id`.
14. If preview fails, trust the returned status. `app_not_running` means the app is not serving yet -- start or restart the dev server.
15. **NEVER** start dev servers with shell `&` (e.g. `vp dev &`). This freezes the thread. Always use `shell(command, background=True)`.

## Critical File Boundary Rule

- Never treat `/files/...` as if it exists inside sandbox Python.
- These patterns are wrong and will fail:
  - `open("/files/data.json")`
  - `pd.read_csv("/files/data.csv")`
  - reading a tool-returned `/files/...` path from Python without copying it first
- Correct options:
  - `read_file(path="/files/data.csv")` when you only need to inspect the VFS file
  - `copy_files(sources=["/files/data.csv"], destination="/home/user/data.csv")` before opening it in Python
  - `call_tool(...)` or `call_tool_sync(...)` from Python when you truly need tool chaining rather than file handoff
