"""Generate 10 SEO-optimised YouTube title variants.

Each title is tagged with the persuasion style it leans on (curiosity-gap,
listicle, contrarian, big-number, transformation, how-to, news-jack,
question, before/after, bold-claim) so the user can quickly pick a tone that
fits their channel.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from seti.sandbox import call_tool

SEO_TITLES_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "titles": {
            "type": "array",
            "minItems": 10,
            "maxItems": 10,
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": (
                            "YouTube title, <=70 chars, includes the primary "
                            "keyword naturally, no clickbait that misleads."
                        ),
                    },
                    "style": {
                        "type": "string",
                        "enum": [
                            "curiosity-gap",
                            "listicle",
                            "contrarian",
                            "big-number",
                            "transformation",
                            "how-to",
                            "news-jack",
                            "question",
                            "before-after",
                            "bold-claim",
                        ],
                    },
                    "rationale": {
                        "type": "string",
                        "description": (
                            "One sentence explaining why this title works for "
                            "SEO and CTR for the given topic."
                        ),
                    },
                    "char_count": {"type": "integer"},
                },
                "required": ["title", "style", "rationale", "char_count"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["titles"],
    "additionalProperties": False,
}


SEO_TITLE_PROMPT = (
    "You are a YouTube SEO and packaging expert. Given a topic, target "
    "keyword, and audience, write 10 distinct title variants. Each must use "
    "a different persuasion style from the enum. Keep all titles under 70 "
    "characters. Include the primary keyword naturally in at least 7 of "
    "them. Avoid all-caps spam, misleading clickbait, and emojis unless the "
    "audience explicitly expects them. Set char_count to the exact length "
    "of the title string."
)


async def run(
    topic: str,
    primary_keyword: str | None = None,
    audience: str | None = None,
    transcript_summary: str | None = None,
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

    res = await call_tool(
        "ai_function",
        instructions=SEO_TITLE_PROMPT,
        input=payload,
        output_format="json",
        output_json_schema=SEO_TITLES_SCHEMA,
        performance="fast",
    )

    output_json = res["results"][0].get("output_json") or {}
    return {
        "topic": topic,
        "primary_keyword": primary_keyword,
        "titles": output_json.get("titles", []),
    }


EXAMPLE_INPUT = {
    "topic": "Building an AI customer support agent in a weekend",
    "primary_keyword": "AI customer support agent",
    "audience": "indie SaaS founders",
}


async def main() -> None:
    result = await run(**EXAMPLE_INPUT)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
