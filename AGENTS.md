# Marketing Skills

A public collection of marketing-domain Agent Skills that wrap the **Hyper MCP** tool surface. Each skill in [`skills/`](./skills) teaches an agent how to drive Hyper's MCP tools (ad platforms, organic social, SEO, scrapers, image and video generation, email, analytics, and more) for one marketing job. `CLAUDE.md` imports this file.

Skills are not tools. They are markdown instructions plus optional reference files; the tool calls come from the connected Hyper MCP at [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp). The live MCP descriptor is the only source of truth for tool names, argument names and types. When a skill and the live catalog disagree, the catalog wins.

## Where to look

| Need | Read |
| --- | --- |
| Skill catalog with required integrations | [`README.md`](./README.md#skills) |
| One skill's workflow | `skills/<name>/SKILL.md`, long-form material in `skills/<name>/references/` |
| Authoring rules, validation, releasing | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| Validator and its banned-strings list | [`validate-skills.sh`](./validate-skills.sh) |

## Adding or editing a skill

1. A skill lives in `skills/<skill-name>/SKILL.md` with YAML frontmatter `name` and `description` only.
2. `name` MUST match the folder name.
3. `description` MUST contain a "Use when…" trigger phrase and be 50–500 characters.
4. `SKILL.md` MUST be at most 500 lines. Move long-form material into a sibling `references/` folder.
5. `SKILL.md` MUST contain a `## Requirements` section pointing at `https://app.hyperfx.ai/mcp`, plus a `## Tool surface` table of the tools it calls.
6. When adding, renaming or removing a skill, update the catalog in `README.md`.
7. Run `./validate-skills.sh` before opening a PR. CI runs the same check.
8. To release, bump the version in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`. A merge to `main` tags and publishes it.

## Repo conventions

- **One tool name on every surface.** A skill names a tool once, by its catalog name, for example `gmail_messages_send`. That name runs in Hyper chat as a direct call, on MCP with `call_read("<name>", {...})`, `call_write` or `call_destructive` (the one `describe` names in `call_with`), and on the CLI with `hyperai call <name> --json '{...}'`. Never write a legacy name or a CLI alias path such as `gmail messages send`. The live catalog (`search`, `describe`) wins over codebase function names, earlier skill content, or memory.
- **Allowed Hyper URLs in skill bodies:** only `app.hyperfx.ai/mcp` and `app.hyperfx.ai/apps`.
- **No internal infra references.** No `hyper_cache_*` table names and no instructions to discover one at runtime; those tables and the `*_insights_query` / `*_sync_*` tools that fed them are being removed. No removed `hyper_data_*` tools, internal filesystem paths, internal agent template names, or template ids outside the public MCP surface. No real account IDs, customer data, or tokens.
- **Live data and warehouses.** For live data, call the provider's own API tool. For a workspace's own warehouse tables, the `database` toolkit is the only database path: `database_tables_list` to discover, `database_tables_describe` for real columns, then `database_query`. Never hardcode or guess a table name.
- **Conditional integrations.** Some tools appear only when the integration is enabled in the user's Hyper workspace (the LinkedIn scraper, for example). Mark those tools conditional and skip the affected step gracefully instead of failing the whole workflow.
- **Self-contained skills.** When two skills overlap, add an `## Out of scope` section pointing at the right sibling instead of duplicating workflow.
- **Microcurrency.** Pinterest Ads budgets and bids are in microcurrency (`$1.00 = 1,000,000` microdollars). Skills that touch budget fields must convert.

## How an agent should use these skills

1. Read the matching `skills/<name>/SKILL.md`.
2. When a tool is not found, follow the skill's not-found line: in Hyper chat, find the toolkit id with `discover_toolkits` and pass it to `enable_toolkit`; on an MCP client or the CLI, tell the user which integration to connect.
3. Follow the workflow in the skill's body.
4. Use the skill's "Out of scope" section to hand off to a sibling skill.
5. When a call fails with an argument-validation error, re-read the MCP tool descriptor before retrying. Do not retry with the same arguments.
