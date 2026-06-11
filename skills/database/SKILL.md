---
name: database
description: Use the Hyper Database (PostgreSQL) for analytics, dashboards, data apps, and structured data storage. Use when the user wants to save datasets, build dashboards or data apps, run SQL queries, or move data between tools.
use_cases:
  - Save data to database for analysis
  - Build analytics dashboards and data apps
  - Query structured data with SQL
  - Cross-tool data transfers
triggers:
  - dashboard
  - data app
  - analytics
  - save to database
  - SQL query
  - data table
  - chart
  - KPI
  - metrics
requires_toolkits:
  - hyper_database
---

# Hyper Database (PostgreSQL)

Tenant-isolated database for structured data, analytics, dashboards, and data
apps.
NOTE: This is different from external databases that are connected by users.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Hyper Database toolkit** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## Database Tools

| Tool | Purpose |
|------|---------|
| `hyper_data_sql(sql, limit, confirm_mutation)` | Run SQL for exploration, aggregation, joins, and intentional mutations; `query` is accepted only as a compatibility alias |
| `hyper_data_save(table, data, mode)` | Save data to table |
| `hyper_data_sync(source_tool, dest_tool, ...)` | Tool-to-tool transfers |
| `hyper_data_list_tables()` | List available tables |
| `hyper_data_describe_tables(tables, ...)` | Describe selected tables; `table_names` is accepted only as a compatibility alias |
| `hyper_data_search_ui_components(query, kind)` | Discover valid dashboard/data app UI component and action names |
| `hyper_data_build_dashboard(...)` | Create or update a dashboard or data app |
| `hyper_data_list_dashboards()` | List existing dashboards |
| `hyper_data_publish_dashboard(name, dashboard_ids)` | Publish dashboards as a shareable interface |
| `hyper_data_update_interface(interface_id, ...)` | Edit a published interface (rename, add dashboards, set password) |

## When to Use

| Scenario | Action |
|----------|--------|
| User asks to save/store data | `hyper_data_save` |
| Data needed for reusable analysis | `hyper_data_save` then query or build dashboard |
| User asks for a visual dashboard or data app from provided/static data | Build the interface directly from the provided values; SQL is optional |
| Full website scrape (30+ pages) | Create Knowledge Base, query it |

## When NOT to Use

**DO NOT save:**
- Temporary test results or one-time tool verification outputs
- Debug outputs or diagnostic checks
- Results not explicitly requested by the user for storage
- Transient data that won't be used for downstream analysis

| Scenario | Why |
|----------|-----|
| Testing tool functionality | One-time verification, no need to persist |
| Debug outputs | Transient diagnostic data |
| Small result sets user can read | No benefit to database storage |
| Results user didn't ask to save | Respect user intent, don't auto-save |

## Safety Rules

- Use `hyper_data_sql` for exploration and aggregation queries.
- Use `hyper_data_sql` with `confirm_mutation=True` only for destructive
  operations such as `DROP`, `TRUNCATE`, or broad `DELETE`.
- ALWAYS confirm before DROP/DELETE/TRUNCATE operations
- **System tables** (`*_insights_*`): Created by syncs - extra caution

## Dashboard And Data App Work

For requests to create, edit, publish, or visually improve dashboards or data
apps, load
`references/dashboard-building.md`.

Do not load the dashboard/data app reference for normal SQL exploration, table
listing, data saving, or one-off analysis.

Dashboard/data app implementation details are internal. In user-facing
responses, say "dashboard", "data app", "report", or "interactive view"; do not
mention the underlying implementation argument unless the user asks how it is
built.

## Common Mistakes to Avoid

- Saving temporary debug output or one-off verification data without user
  intent.
- Running destructive SQL without explicit confirmation.
- Querying system tables casually; treat `*_insights_*` tables as generated
  sync artifacts.
- Using the dashboard/data app reference for normal database tasks.
