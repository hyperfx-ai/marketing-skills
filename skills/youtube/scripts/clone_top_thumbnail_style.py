"""Clone the style of one of the top-performing thumbnails for a search term.

Two-phase script:

* Phase 1 (no ``chosen_rank``): runs ``research_top_thumbnails`` and returns
  the top ``top_k`` candidates so the agent can present them to the user and
  ask which rank to clone.

* Phase 2 (``chosen_rank`` set): looks up the chosen thumbnail's
  ``thumbnail_file_id`` and runs ``images_edit_nano_banana`` with that file as
  the style reference. If a ``face_file_id`` is provided, the prompt is
  augmented to composite the user's face into the cloned style.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from seti.sandbox import call_tool


async def _research(query: str, top_k: int) -> list[dict[str, Any]]:
    res = await call_tool(
        "youtube_videos_search_top",
        query=query,
        max_results=top_k,
        sort_by="views",
        download_thumbnails=True,
    )
    items = res.get("items", []) if isinstance(res, dict) else []
    return items


def _build_clone_prompt(my_topic: str, has_face: bool, source_title: str | None) -> str:
    base = (
        f"Recreate this exact thumbnail style and composition, but for a video "
        f"about: {my_topic.strip()}. Match the color palette, lighting, "
        f"text-overlay style, character pose, and emotional tone of the "
        f"reference image. Keep the 16:9 framing and a single dominant focal "
        f"point. Replace any subject-specific imagery so it clearly relates "
        f"to '{my_topic.strip()}'."
    )
    if source_title:
        base += f" The reference is from a video titled '{source_title}'."
    if has_face:
        base += (
            " Replace the main person in the thumbnail with the person from "
            "the supplied face reference, preserving their identity, "
            "expression style, and approximate pose. Composite cleanly with "
            "matched lighting."
        )
    return base


async def run(
    query: str,
    my_topic: str,
    face_file_id: str | None = None,
    top_k: int = 5,
    chosen_rank: int | None = None,
) -> dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("query is required")
    if not my_topic or not my_topic.strip():
        raise ValueError("my_topic is required")

    items = await _research(query, top_k)

    if chosen_rank is None:
        return {
            "phase": "research",
            "query": query,
            "my_topic": my_topic,
            "candidates": [
                {
                    "rank": item.get("rank"),
                    "title": item.get("title"),
                    "channel": item.get("channel"),
                    "url": item.get("url"),
                    "view_count": item.get("view_count"),
                    "thumbnail_url": item.get("thumbnail_url"),
                    "thumbnail_file_id": item.get("thumbnail_file_id"),
                }
                for item in items
            ],
            "next_step": (
                "Show these candidates to the user. Then re-run this script "
                "with chosen_rank=<n> to clone that thumbnail's style for "
                f"'{my_topic}'."
            ),
        }

    chosen = next((it for it in items if it.get("rank") == chosen_rank), None)
    if chosen is None:
        raise ValueError(
            f"chosen_rank={chosen_rank} not found in top {top_k} results "
            f"for query '{query}'"
        )

    style_file_id = chosen.get("thumbnail_file_id")
    if not style_file_id:
        raise RuntimeError(
            f"No thumbnail_file_id available for rank {chosen_rank}. "
            "The thumbnail download likely failed; try a different rank."
        )

    prompt = _build_clone_prompt(
        my_topic=my_topic,
        has_face=bool(face_file_id),
        source_title=chosen.get("title"),
    )

    if face_file_id:
        # OpenAI edit composes multiple references better than nano-banana edit
        # when we need to preserve a person's identity.
        result = await call_tool(
            "images_edit_openai",
            requests=[
                {
                    "prompt": prompt,
                    "reference_images": [style_file_id, face_file_id],
                }
            ],
            size="1536x1024",
            quality="high",
        )
        used_tool = "images_edit_openai"
    else:
        result = await call_tool(
            "images_edit_nano_banana",
            file_id=style_file_id,
            prompt=prompt,
            n=1,
            model="pro",
            aspect_ratio="16:9",
            image_size="2K",
        )
        used_tool = "images_edit_nano_banana"

    images = result.get("images", []) if isinstance(result, dict) else []
    if not images:
        raise RuntimeError(f"{used_tool} returned no images: {result}")
    primary = images[0]

    return {
        "phase": "generated",
        "query": query,
        "my_topic": my_topic,
        "source": {
            "rank": chosen.get("rank"),
            "title": chosen.get("title"),
            "channel": chosen.get("channel"),
            "url": chosen.get("url"),
            "thumbnail_file_id": style_file_id,
        },
        "tool_used": used_tool,
        "prompt": prompt,
        "primary": {
            "file_id": primary.get("file_id"),
            "url": primary.get("url"),
        },
    }


EXAMPLE_INPUT = {
    "query": "ai agent tutorial",
    "my_topic": "Building a customer support agent with Claude",
    "top_k": 5,
}


async def main() -> None:
    result = await run(**EXAMPLE_INPUT)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
