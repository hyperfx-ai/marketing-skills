---
name: hyper-cli
description: Use the Hyper CLI to run Hyper marketing skills from a terminal. Use when the user wants to use `hyperai`, inspect live tool schemas, run a tool by its canonical name, switch connected accounts, or run marketing tools outside an MCP-native agent host.
icon: hyper
short_description: Call any Hyper platform tool from the terminal with the hyper CLI.
---

# Hyper CLI

Use `hyperai` to run any marketing skill from a terminal. A skill names each tool once, by its canonical name, for example `gmail_messages_send`. The CLI runs that name directly.

## Requirements

- **Hyper MCP configured for the workspace.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Required integrations connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps). The sibling marketing skill lists which integrations it needs.
- **Hyper CLI installed and authenticated.** Verify with `hyperai info`.

If `hyperai info` fails, stop and tell the user to authenticate the CLI before calling tools.

## The four commands

| Need | Command |
| --- | --- |
| Confirm auth and workspace | `hyperai info` |
| Find a tool | `hyperai search "<what you want to do>"` |
| Read a tool's input schema | `hyperai describe <name> --parameters` |
| Run a tool | `hyperai call <name> --json '{...}'` |

`<name>` is the canonical tool name from the skill, such as `meta_ads_adaccount_list`. The CLI also accepts the same name as separate words (`meta-ads adaccount list`); a skill never uses that form.

If your CLI version rejects the canonical name, run `hyperai search "<name>"`: the result prints the exact `hyperai call ...` line to use. Update the CLI with `hyperai update`.

## Connected accounts

| Need | Command |
| --- | --- |
| List the connected accounts for a toolkit | `hyperai call connections_list --json '{"toolkit_id": "gmail"}'` |
| Switch the active account for this shell | `hyperai call connections_use --json '{"toolkit_id": "gmail", "auth_id": "<auth_id>"}'` |

The active account is kept per shell session, the same way the MCP keeps it per session.

## Arguments

- Pass arguments as one JSON object with `--json`. The CLI validates them against the tool's schema before calling.
- When a call fails with an argument error, run `hyperai describe <name> --parameters` and read the schema. Do not retry the same arguments.
- Large results: add `--raw` to get the unformatted JSON.

## Example

```bash
hyperai info
hyperai search "send an email"
hyperai describe gmail_messages_send --parameters
hyperai call gmail_messages_send --json '{"to": "jane@example.com", "subject": "Hello", "body": "Hi Jane"}'
```

## Out of scope

| Need | Skill |
| --- | --- |
| What to send, to whom, in which sequence | the marketing skill that owns the job, for example `cold-email-outreach` |
| MCP client setup | the Hyper MCP page at [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp) |
