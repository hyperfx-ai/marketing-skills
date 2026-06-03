---
name: hyper-cli
description: Use the Hyper CLI to run Hyper marketing skills from a terminal. Use when the user wants to use `hyperai`, inspect live tool schemas, translate MCP tool names from a skill into CLI commands, switch connected accounts, or run marketing tools outside an MCP-native agent host.
---

# Hyper CLI

Use `hyperai` to run Hyper tools from a terminal. This skill is a bridge for using the marketing skills in this repo through the CLI.

Marketing skills usually name the MCP/raw tools, such as `gmail_send_message` or `meta_business_list_ad_accounts`. The CLI also exposes friendly aliases, such as `gmail messages send` or `meta-ads ad-accounts list`. Pick one surface per call.

## Requirements

- **Hyper MCP configured for the workspace.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Required integrations connected** at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations). Use the sibling marketing skill to know which integrations are required.
- **Hyper CLI installed and authenticated.** Verify with `hyperai info`.

If `hyperai info` fails, stop and tell the user to authenticate the CLI before calling tools.

## Tool surface

| Need | Command |
| --- | --- |
| Confirm auth/workspace | `hyperai info` |
| Find tools by intent or raw MCP name | `hyperai search "<intent or raw tool name>" --json --signature` |
| Browse friendly aliases in a namespace | `hyperai describe <namespace>` |
| Inspect a friendly alias schema | `hyperai describe <alias path> --parameters` |
| Call a friendly alias | `hyperai call <alias path> --json '{...}'` |
| Inspect a raw toolkit tool | `hyperai tools describe <toolkit> <tool_name> --parameters` |
| Call a raw toolkit tool | `hyperai tools call <toolkit> <tool_name> --json '{...}'` |
| List connected accounts | `hyperai tools list --connected` or `hyperai connections list` |
| Switch active account | `hyperai connections use <toolkit> <auth-id>` |

## Critical rule: aliases vs raw tools

Friendly alias path:

```bash
hyperai describe gmail messages send --parameters
hyperai call gmail messages send --json '{"to":"person@example.com","subject":"Hello","body":"Hi"}'
```

Raw toolkit path:

```bash
hyperai tools describe gmail gmail_send_message --parameters
hyperai tools call gmail gmail_send_message --json '{"to":"person@example.com","subject":"Hello","body":"Hi"}'
```

If a marketing skill says `gmail_send_message`, that is a raw MCP/toolkit name. Either translate it with search:

```bash
hyperai search "gmail_send_message" --json --signature
```

or call it through the raw toolkit surface:

```bash
hyperai tools call gmail gmail_send_message --json '{...}'
```

Never assume `hyperai call gmail_send_message` will work.

## Describe progression

Use `describe` progressively. Start broad, then narrow to the exact alias before calling:

```bash
hyperai describe gmail
hyperai describe gmail messages send --parameters
hyperai call gmail messages send --to person@example.com --subject "Hello" --body "Hi"
```

For friendly aliases, use `hyperai describe <namespace>` and `hyperai describe <alias path> --parameters`. Do not use `hyperai tools describe gmail` for namespace browsing; `tools describe` is the raw toolkit form and needs both toolkit and raw tool name.

## Structured arguments

Flags are safest for simple scalar fields:

```bash
hyperai call gmail messages send --to person@example.com --subject "cli test" --body "this is a test"
```

Use `--json` for arrays, objects, nested schemas, and model-specific tools. Do not pass arrays or objects as string flags unless the live schema explicitly says the field is a string.

```bash
hyperai describe images generate nano-banana --parameters
hyperai call images generate nano-banana \
  --json '{"requests":[{"prompt":"a cat wearing a propeller hat"}],"model":"pro"}'
```

If validation says an object field was received as a string, retry with `--json` after re-reading `describe --parameters`.

## Workflow

1. Read the relevant marketing skill first, for example `meta-ads`, `cold-email-outreach`, `email-lifecycle`, or `analytics-insights`.
2. Use that skill for strategy, sequencing, safety rules, and required integrations.
3. For each tool named in the skill, resolve the live CLI command:
   - Try `hyperai search "<tool name or intent>" --json --signature`.
   - Prefer the returned `call_command` when available.
   - If no good alias exists, use `hyperai tools describe <toolkit> <tool_name>`.
4. Before calling, inspect the live schema:
   - Friendly alias: `hyperai describe <alias path> --parameters`.
   - Raw toolkit: `hyperai tools describe <toolkit> <tool_name> --parameters`.
5. Call with `--json` for structured inputs.
6. If validation fails, re-run the relevant `describe --parameters` command before retrying.

## Connected accounts

List available connected accounts:

```bash
hyperai tools list --connected
hyperai connections list
hyperai connections list gmail
```

Set the active connection for future CLI calls:

```bash
hyperai connections use gmail <auth-id>
hyperai connections use meta_business <auth-id>
```

Use `--auth-id <auth-id>` only for a one-off override.

## Examples

Marketing skill names raw Gmail tool:

```text
gmail_list_messages
```

Resolve and call friendly alias:

```bash
hyperai search "gmail_list_messages" --json --signature
hyperai describe gmail messages list --parameters
hyperai call gmail messages list --json '{"max_results":10}'
```

Marketing skill names raw Meta tool:

```text
meta_business_list_ad_accounts
```

Resolve and call friendly alias:

```bash
hyperai search "meta_business_list_ad_accounts" --json --signature
hyperai describe meta-ads ad-accounts list --parameters
hyperai call meta-ads ad-accounts list --json '{"detail":"id_only"}'
```

Raw fallback:

```bash
hyperai tools describe meta_business meta_business_list_ad_accounts --parameters
hyperai tools call meta_business meta_business_list_ad_accounts --json '{"detail":"id_only"}'
```

Image generation:

```bash
# Default image generation alias accepts the prompt positionally.
hyperai call images generate "a cat wearing a propeller hat" --quality draft --output json

# Model-specific image tools often need JSON because their schema is nested.
hyperai describe images generate nano-banana --parameters
hyperai call images generate nano-banana \
  --json '{"requests":[{"prompt":"a cat wearing a propeller hat"}],"model":"pro"}' \
  --output json
```

Meta ads performance:

```bash
hyperai search "meta ads insights" --json --signature
hyperai call meta-ads ad-accounts list --output json
hyperai describe meta-ads insights get --parameters
hyperai call meta-ads insights get --json '{"object_id":"act_<ad_account_id>","object_type":"account","date_range":"last_month"}'
```

Always list ad accounts first when the user asks for account-level performance and did not provide an `act_...` account id.

## Rules

- The live CLI schema wins over examples in any skill.
- Marketing skills provide workflow judgment; `hyperai describe` provides executable arguments.
- Prefer friendly aliases for normal use because they are easier for agents and humans.
- Use raw `hyperai tools ...` when a skill gives an exact MCP tool name and no alias is obvious.
- Do not invent toolkit IDs, tool names, or parameter names.
