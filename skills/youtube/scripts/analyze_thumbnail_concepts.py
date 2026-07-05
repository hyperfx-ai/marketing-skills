"""Extract 5 ready-to-render thumbnail concepts from a YouTube video.

Pipeline:
1. ``youtube_videos_read`` summarises the video (title, hook, key visuals, mood).
2. ``ai_function`` coerces that summary into a strict 5-concept JSON schema
   where each concept includes a one-line title, the visual composition, the
   emotional hook, and a ``ready_to_use_prompt`` that can be passed straight
   into ``generate_thumbnail.py``.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from seti.sandbox import call_tool

THUMBNAIL_CONCEPTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "concepts": {
            "type": "array",
            "minItems": 5,
            "maxItems": 5,
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short label for this concept (3-6 words).",
                    },
                    "composition": {
                        "type": "string",
                        "description": (
                            "What the viewer sees: subject placement, focal "
                            "point, background, color palette, mood, lighting."
                        ),
                    },
                    "hook": {
                        "type": "string",
                        "description": (
                            "Emotional or curiosity hook the thumbnail leans on "
                            "(e.g. shock, transformation, before/after, big "
                            "number, contrarian claim)."
                        ),
                    },
                    "text_overlay": {
                        "type": "string",
                        "description": (
                            "2-5 word overlay text. Use uppercase if it should "
                            "render as such. Empty string if no text overlay."
                        ),
                    },
                    "ready_to_use_prompt": {
                        "type": "string",
                        "description": (
                            "Self-contained image-generation prompt that fully "
                            "describes the thumbnail. Includes composition, "
                            "subject(s), text overlay, color palette, lighting, "
                            "and 16:9 framing."
                        ),
                    },
                },
                "required": [
                    "title",
                    "composition",
                    "hook",
                    "text_overlay",
                    "ready_to_use_prompt",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["concepts"],
    "additionalProperties": False,
}


CONCEPT_EXTRACTION_PROMPT = (
    "You are a YouTube thumbnail strategist. Given a video summary, design 5 "
    "distinct high-CTR thumbnail concepts. Each concept should use a different "
    "hook (e.g. shock, transformation, contrarian, big-number, curiosity gap). "
    "Compositions must be optimised for 16:9 and remain readable on a small "
    "mobile thumbnail. ready_to_use_prompt must be a complete image-generation "
    "prompt with subject, composition, color palette, lighting, mood, and "
    "explicit '16:9 YouTube thumbnail' framing. Do not reference brands you "
    "are not sure about."
)


async def run(youtube_url: str) -> dict[str, Any]:
    summary = await call_tool(
        "youtube_videos_read",
        url=youtube_url,
        instruction=(
            "Describe this video for a thumbnail designer. Cover the topic, "
            "the host's appearance and emotion, the strongest visual moments, "
            "any on-screen text or charts, the overall mood, and the single "
            "biggest hook a viewer would click for. Be concise."
        ),
    )

    summary_text = summary if isinstance(summary, str) else json.dumps(summary)

    concepts_result = await call_tool(
        "ai_function",
        instructions=CONCEPT_EXTRACTION_PROMPT,
        input={"video_summary": summary_text, "youtube_url": youtube_url},
        output_format="json",
        output_json_schema=THUMBNAIL_CONCEPTS_SCHEMA,
        performance="fast",
    )

    output_json = concepts_result["results"][0].get("output_json") or {}
    concepts = output_json.get("concepts", [])

    return {
        "youtube_url": youtube_url,
        "video_summary": summary_text,
        "concepts": concepts,
    }


EXAMPLE_INPUT = {"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}


async def main() -> None:
    result = await run(**EXAMPLE_INPUT)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
