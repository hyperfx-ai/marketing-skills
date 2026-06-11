---
name: agents
description: Manage yourself and other agents — schedule tasks, update settings, create new agents, and delegate work. Use when the user wants to modify an agent's behavior or prompt, adjust toolkits, attach skills or files, create a new agent, schedule recurring tasks, or run another agent.
use_cases:
  - Modify an agent's behavior
  - Update an agent's system prompt
  - Rename or describe agents
  - Adjust agent toolkits
  - Attach or detach agent skills/files/knowledge bases
  - Create a new agent
  - Schedule tasks on yourself or another agent
  - Run agents
  - Configure agent commands
triggers:
  - update agent
  - modify system prompt
  - change agent prompt
  - edit agent settings
  - agent configuration
  - create agent
  - build agent
  - schedule task
  - agent settings
requires_toolkits:
  - agents
suggested_toolkits: []
---

# Agent Management

Use this skill to manage yourself and other agents — creating, updating, scheduling, webhook tasks, and running.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Agents toolkit** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## Task, Schedule, Trigger, Automation

In Hyper these are the same stored concept: an agent trigger with task instructions.
Users may call it a task, schedule, reminder, automation, webhook, or trigger.
Choose the matching trigger type and create/update the trigger on the current agent unless the user explicitly names another agent.

## Self-Management vs Creating New Agents

You know your own agent ID (provided in your prompt context). Use this decision tree:

| User intent | Action |
|---|---|
| "Do X every day" / "Schedule Y" / "Remind me weekly" | `agents_schedule(agent_id=YOUR_OWN_ID, ...)` |
| "Create a webhook for this" / "Call this webhook" | `agents_triggers_create(agent_id=YOUR_OWN_ID, trigger_type="webhook", ...)` |
| "Create a new agent for X" / "Build me an agent that does Y" | `agents_create(...)` |
| "Run this on agent Z" | `agents_run(agent_id="Z", ...)` or `agents_schedule(agent_id="Z", ...)` |

**Default to the current agent.** If the user says "create a task", "do this daily", "make a webhook", or "call this webhook", configure yourself — do not ask which agent or create a new agent unless explicitly asked.

## Hard Delegation Rules

- Use `agents_run` only when the user explicitly asks to run a specific agent, delegate to another agent, or approves creating a one-off dynamic agent.
- Do not use `agents_run` as a fallback because another tool is unclear or inconvenient.
- Do not use `agents_run` for normal media generation, image generation, video generation, browsing, research, or ad-creative work when direct tools already exist.
- If the user did not ask for delegation, stay in the current agent and use the direct domain tools.

## Prompt Field Rules

1. `system_prompt` is the canonical behavior field for agents.
2. `instructions` is for workflow-oriented use. Do not modify it unless the user explicitly asks.
3. If the user says "modify your system prompt", update `system_prompt` only.

## Resource Mentions

Use canonical resource references in text:
- Files: `{{$file:<file_id>}}`

When you pass a plain-text `system_prompt` via `agents_create` or `agents_update`, the backend converts it to BlockNote format automatically. Resource references like `{{$file:id}}` become rich mention nodes in the UI.

## Creating Agents

Use `agents_create` with:

**Required:** `name`, `system_prompt`, `description`

**Optional:** `model`, `model_settings`, `toolkits`, `commands`, `output_type`, `exclude_native_toolkits`, `scope`

**CRITICAL: Do NOT call `enable_toolkit` for toolkits intended for the new agent.** The `agents_create` tool accepts toolkit IDs directly via its `toolkits` parameter. Enabling toolkits in the current chat session adds them to your own session, not to the new agent. Just pass the toolkit IDs directly to `agents_create`. Use `search_toolkits` if you need to discover valid toolkit IDs.

```python
agents_create(
    name="Research Assistant",
    description="Helps with research tasks",
    system_prompt="You are a helpful research assistant.",
    toolkits=["system_web_toolkit"],
    model="hyper-claude-sonnet"
)
```

**After creation:** configure context resources with `agents_update_context`, then render a link: `agent/{agent_id}`

## Updating Agents

Use `agents_update` for core fields (name, description, system_prompt, model, toolkits, scope, etc.):

```python
agents_update(
    agent_id="agent_123",
    system_prompt="You are a concise assistant focused on actionable answers."
)
```

For context resources (skills, files, knowledge bases), use `agents_update_context`:

```python
agents_update_context(
    agent_id="agent_123",
    resource_type="skill",
    op="add",
    ids=["curated/seo-research"]
)
```

Only provided fields are changed.

## Scheduling Tasks

Use `agents_schedule` to set up recurring tasks — on yourself or another agent:

```python
agents_schedule(
    agent_id="YOUR_OWN_ID",
    instructions="Generate daily report",
    cron="0 9 * * *",
    timezone="UTC",
)
```

## Running Agents

Use `agents_run` to execute a specific agent immediately:

```python
agents_run(
    agent_id="agent_123",
    instructions="Analyze this data"
)
```

## Trigger Creation Playbook

Use this flow whenever a user asks to create or manage triggers.

1. Discover trigger types with `agents_triggers_inventory(query=..., provider=...)`. Use `query`, not `search_query`.
2. If the compact result is not enough, inspect the trigger with `agents_trigger_definition_get(trigger_type=...)`.
3. Call resolver toolkit tools to fetch valid values (for example `twilio_phone_numbers_list`).
4. Ask the user to confirm the target value when needed (for example which Twilio number to listen on).
5. Create the trigger with `agents_triggers_create(...)`.

### Native Webhook Example

Use the native `webhook` trigger for inbound HTTP POSTs. The webhook endpoint is:

```text
https://api.hyperfx.ai/api/v1/webhooks/triggers/{trigger_id}
```

Create it on the current agent:

```python
agents_triggers_create(
    agent_id="YOUR_OWN_ID",
    trigger_type="webhook",
    label="Inbound lead webhook",
    input_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "surname": {"type": "string"},
        },
    },
    input={"message": "Process the webhook body."},
    status="active",
)
```

The tool returns `webhook_url` and the token needed for the `X-Webhook-Token` header.

### Twilio SMS Example

```python
agents_triggers_inventory(query="twilio sms", provider="twilio")
```

Look for:
- `trigger_type`: `twilio_sms_received`
- required config: `phone_number_sid`
- resolver tool: `twilio_phone_numbers_list`

Then:

```python
agents_triggers_create(
    agent_id="YOUR_OWN_ID",
    trigger_type="twilio_sms_received",
    label="Inbound SMS",
    config={"phone_number_sid": "PN123"},
    input={"message": "Handle inbound SMS and reply when needed."},
    integration_auth_id="u_integration_...",
    status="active",
)
```

### Slack Trigger Example

```python
agents_triggers_inventory(query="slack message", provider="slack")
```

Pick the correct Slack trigger type, gather required config/integration values, then create:

```python
agents_triggers_create(
    agent_id="YOUR_OWN_ID",
    trigger_type="slack_message_posted",
    label="Slack mentions",
    config={"conversations": ["C123"]},
    input={"message": "Handle Slack events for configured channels."},
    integration_auth_id="u_integration_...",
    status="active",
)
```

## Trigger Listing And Search

- Use `agents_triggers_list` to inspect only the selected agent's triggers.
- Use `agents_triggers_get` for full task details, input schema, and webhook configuration.
- Use `query`, `offset`, and `limit` for paginated review.
- Keep `limit` small for iterative discovery (default is 10).

## Commands (Slash Commands)

Agents can define reusable commands that show up in the chat `/` menu.

| Field | Description |
|-------|-------------|
| `name` | Required display label |
| `description` | Optional help text |
| `shortcut` | Optional keyboard shortcut (e.g., `cmd+k`) |
| `action` | Editor content inserted into chat input when selected |

## What Not To Do

- Do not rewrite both `system_prompt` and `instructions` unless explicitly requested.
- Do not clear toolkits unless the user asks to remove them.
- Do not mutate `attached_resources` via `agents_update(field=...|path=...)`.
- Do not use `agents_update` to change skills/files/knowledge bases — use `agents_update_context`.
- Do not create a new agent when the user just wants to schedule a task on themselves.
- Do not ask which agent to use for a task/webhook unless the user explicitly references another agent.
- Do not call `agents_run` without `agent_id` unless the user explicitly approved a dynamic one-off agent.
- Do not call `enable_toolkit` for toolkits that are only intended for a new agent — pass them directly to `agents_create(toolkits=[...])`.
