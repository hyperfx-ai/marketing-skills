"""Generate a structured, SEO-optimised YouTube description.

Produces a hook line, a 2-3 sentence summary, key takeaways, suggested
timestamps (when transcript or chapters are provided), pull-quotes, a CTA,
and a list of relevant hashtags. The output is structured so the agent can
either render it for the user or paste a flattened version into YouTube.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from seti.sandbox import call_tool

SEO_DESCRIPTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "hook": {
            "type": "string",
            "description": "First line of the description, <=120 chars, hooks the viewer.",
        },
        "summary": {
            "type": "string",
            "description": "2-3 sentence summary including the primary keyword naturally.",
        },
        "key_takeaways": {
            "type": "array",
            "minItems": 3,
            "maxItems": 7,
            "items": {"type": "string"},
        },
        "timestamps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "time": {
                        "type": "string",
                        "description": "MM:SS or HH:MM:SS",
                    },
                    "label": {"type": "string"},
                },
                "required": ["time", "label"],
                "additionalProperties": False,
            },
            "description": ("Empty array if no transcript or chapters were provided."),
        },
        "pull_quotes": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 3,
        },
        "cta": {
            "type": "string",
            "description": "Single call-to-action line, <=140 chars.",
        },
        "hashtags": {
            "type": "array",
            "minItems": 3,
            "maxItems": 8,
            "items": {
                "type": "string",
                "description": "Hashtag including the leading #.",
            },
        },
        "flattened": {
            "type": "string",
            "description": (
                "Final description ready to paste into YouTube, combining "
                "hook, summary, takeaways, timestamps, CTA, and hashtags "
                "with appropriate line breaks."
            ),
        },
    },
    "required": [
        "hook",
        "summary",
        "key_takeaways",
        "timestamps",
        "pull_quotes",
        "cta",
        "hashtags",
        "flattened",
    ],
    "additionalProperties": False,
}


SEO_DESCRIPTION_PROMPT = (
    "You are a YouTube SEO copywriter. Write a structured, high-CTR video "
    "description for the given video. Include the primary keyword naturally "
    "in the hook and summary. Generate timestamps only if a transcript or "
    "chapter list is provided. Hashtags should be lowercase, no spaces, "
    "directly relevant. The 'flattened' field must be the final string the "
    "user can paste into YouTube — assemble hook, summary, takeaways "
    "(bulleted with '•'), timestamps (one per line as 'MM:SS — Label'), "
    "the CTA, and hashtags on one line at the end. Avoid spammy emoji "
    "walls and never invent facts not supported by the inputs."
)


async def run(
    topic: str,
    primary_keyword: str | None = None,
    audience: str | None = None,
    transcript_summary: str | None = None,
    chapters: list[dict[str, str]] | None = None,
    cta_link: str | None = None,
) -> dict[str, Any]:
    if not topic or not topic.strip():
        raise ValueError("topic is required")

    payload: dict[str, Any] = {"topic": topic}
    if primary_keyword:
        payload["primary_keyword"] = primary_keyword
    if audience:
        payload["audience"] = audience
    if transcript_summary:
        payload["transcript_summary"] = transcript_summary
    if chapters:
        payload["chapters"] = chapters
    if cta_link:
        payload["cta_link"] = cta_link

    res = await call_tool(
        "ai_function",
        instructions=SEO_DESCRIPTION_PROMPT,
        input=payload,
        output_format="json",
        output_json_schema=SEO_DESCRIPTION_SCHEMA,
        performance="fast",
    )

    output_json = res["results"][0].get("output_json") or {}
    return {
        "topic": topic,
        "primary_keyword": primary_keyword,
        "description": output_json,
    }


EXAMPLE_INPUT = {
    "topic": "Building an AI customer support agent in a weekend",
    "primary_keyword": "AI customer support agent",
    "audience": "indie SaaS founders",
    "transcript_summary": (
        "We build a Claude-powered support agent over a weekend, hook it up "
        "to a knowledge base, and ship it to a real Intercom inbox."
    ),
}


async def main() -> None:
    result = await run(**EXAMPLE_INPUT)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
