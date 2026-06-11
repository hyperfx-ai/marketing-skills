# Client Intake (Pipeline Kickoff)

The research-pipeline kickoff: turn a website URL into the inputs that the rest of the `research/` group needs. The *decision* layer (which integration bucket the workspace is in, which channels to recommend) is no longer here — that lives in the gtm decision layer.

## When to use

Read this whenever the agent is starting a fresh research pipeline (Full Brand Audit, or any time the cached research files are stale). Always the first step of `research/foundation`.

## What this step does

This is a thin entry point. Its only job is to:

1. Capture what the user already provided (URL, ICP hints, known competitors, channel preferences, off-platform channels they're already running, constraints).
2. Verify a usable URL.
3. Hand off to `01-scrape-brand-profile.md`, then `02-audit-website-tracking.md`, then `03-research-competitors.md` in that order.

## What this step does NOT do

- It does not classify the workspace into "Fully connected / Partially connected / Disconnected" — the gtm decision layer does that, after the research files exist, when picking a channel.
- It does not propose channels — the gtm decision layer does that.
- It does not auto-enable monitoring tasks — those are offered after the confirmed brief, see `playbooks/monitoring/tasks.md`.

## Inputs to capture from the user (or from previous turn context)

| Field | Source |
|---|---|
| `website_url` | User-provided. Required. |
| `known_competitors` | User-provided if any; otherwise leave empty and let `03-research-competitors.md` find them. |
| `existing_off_platform_channels` | User-provided list of channels the user is already running off-platform (warm/cold outreach, affiliate program, partner referrals). The strategy skill uses this to emit `advisory` plan steps. |
| `constraints` | Free-form (e.g., "no Reddit", "no paid social", regulatory category). |
| `goals` | Free-form. The strategy skill prefers to derive these from the research files, but accepts user-stated goals as truth. |

## Output

A `client_intake_brief` object passed forward into the rest of the `research/` group:

```json
{
  "website_url": "https://example.com",
  "known_competitors": ["competitor-a.com", "competitor-b.com"],
  "existing_off_platform_channels": ["affiliates_referrals"],
  "constraints": ["regulated industry: healthcare"],
  "goals": ["leads"]
}
```

That's it. The brand profile, tracking audit, and competitor research live in the next three docs in this folder.

## Important

- If the user gave a URL with no other context, that's enough — proceed to `01-scrape-brand-profile.md` immediately and do not nag for more inputs.
- If the URL is unreachable or returns a 4xx/5xx, stop and surface that to the user before wasting tool calls.
- The integration-bucket logic that used to live in this doc has moved to the gtm decision layer (SKILL.md). Don't re-introduce it here.
