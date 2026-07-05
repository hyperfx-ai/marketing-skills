"""Research the top-performing YouTube videos for a search term.

Calls the new ``youtube_videos_search_top`` tool with ``download_thumbnails=True`` so
that every result has a ``thumbnail_file_id`` that subsequent scripts (e.g.
``clone_top_thumbnail_style``) can pass into image-edit tools as a reference.

Returns a compact, ranked JSON shape that the agent can render or hand back
to the user.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Literal

from seti.sandbox import call_tool


async def run(
    query: str,
    max_results: int = 10,
    sort_by: Literal["relevance", "views", "date"] = "views",
    region: str | None = None,
    upload_date: Literal["hour", "today", "week", "month", "year"] | None = None,
) -> dict[str, Any]:
    res = await call_tool(
        "youtube_videos_search_top",
        query=query,
        max_results=max_results,
        sort_by=sort_by,
        region=region,
        upload_date=upload_date,
        download_thumbnails=True,
    )

    items = res.get("items", []) if isinstance(res, dict) else []
    ranked: list[dict[str, Any]] = []
    for item in items:
        ranked.append(
            {
                "rank": item.get("rank"),
                "title": item.get("title"),
                "channel": item.get("channel"),
                "url": item.get("url"),
                "video_id": item.get("video_id"),
                "view_count": item.get("view_count"),
                "duration": item.get("duration"),
                "published_at": item.get("published_at"),
                "thumbnail_url": item.get("thumbnail_url"),
                "thumbnail_file_id": item.get("thumbnail_file_id"),
            }
        )

    return {
        "query": query,
        "sort_by": sort_by,
        "region": region,
        "result_count": len(ranked),
        "results": ranked,
    }


EXAMPLE_INPUT = {"query": "ai agent tutorial", "max_results": 5}


async def main() -> None:
    result = await run(**EXAMPLE_INPUT)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
