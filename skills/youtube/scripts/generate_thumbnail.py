"""Generate a single YouTube thumbnail.

Routing logic chooses the right image-gen tool based on inputs:

- ``style_reference_file_id`` set     -> ``images_edit_nano_banana`` with that
                                          file as the base image (best for
                                          cloning a single style reference).
- ``brand_file_ids`` or
  ``face_file_ids`` set               -> ``images_edit_openai`` with combined
                                          reference_images (better at composing
                                          multiple reference assets).
- otherwise                           -> ``images_generate_nano_banana``
                                          (``model='pro'`` if the prompt has
                                          explicit text overlay, ``flash``
                                          otherwise).

All tool calls go through the sandbox RPC, so generated images are persisted
as ``DBFile``s in the conversation thread and metering fires automatically.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Literal

from seti.sandbox import call_tool

# Tokens that suggest the prompt requires legible text rendering inside the
# image. Nano-banana 'pro' is materially better at text than 'flash'.
_TEXT_HEAVY_TOKENS = (
    '"',
    "“",
    "”",
    "headline",
    "headline:",
    "text overlay",
    "text:",
    "caption",
    "subtitle",
    "title text",
    "label",
    "logo text",
)


def _looks_text_heavy(prompt: str) -> bool:
    lowered = prompt.lower()
    return any(tok in lowered for tok in _TEXT_HEAVY_TOKENS)


def _normalise_aspect(aspect_ratio: str | None) -> str:
    return aspect_ratio or "16:9"


async def run(
    prompt: str,
    face_file_ids: list[str] | None = None,
    brand_file_ids: list[str] | None = None,
    style_reference_file_id: str | None = None,
    aspect_ratio: str = "16:9",
    image_size: Literal["1K", "2K", "4K"] = "2K",
    model: Literal["pro", "flash", "auto"] = "auto",
    n: int = 1,
) -> dict[str, Any]:
    if not prompt or not prompt.strip():
        raise ValueError("prompt is required")

    refs: list[str] = []
    if face_file_ids:
        refs.extend(face_file_ids)
    if brand_file_ids:
        refs.extend(brand_file_ids)

    aspect = _normalise_aspect(aspect_ratio)
    chosen_model = model
    used_tool: str
    result: dict[str, Any]

    if style_reference_file_id:
        used_tool = "images_edit_nano_banana"
        if chosen_model == "auto":
            chosen_model = "pro" if _looks_text_heavy(prompt) else "flash"
        result = await call_tool(
            used_tool,
            file_id=style_reference_file_id,
            prompt=prompt,
            n=n,
            model=chosen_model,
            aspect_ratio=aspect,
            image_size=image_size,
        )
    elif refs:
        used_tool = "images_edit_openai"
        # OpenAI image-edit only supports its native sizes.
        openai_size = "1536x1024" if aspect.startswith("16") else "1024x1024"
        result = await call_tool(
            used_tool,
            requests=[{"prompt": prompt, "reference_images": refs}],
            size=openai_size,
            quality="high",
        )
    else:
        used_tool = "images_generate_nano_banana"
        if chosen_model == "auto":
            chosen_model = "pro" if _looks_text_heavy(prompt) else "flash"
        result = await call_tool(
            used_tool,
            requests=[{"id": "thumbnail", "prompt": prompt}],
            n=n,
            model=chosen_model,
            aspect_ratio=aspect,
            image_size=image_size,
        )

    images = result.get("images", []) if isinstance(result, dict) else []
    if not images:
        raise RuntimeError(f"{used_tool} returned no images: {result}")

    primary = images[0]
    return {
        "tool_used": used_tool,
        "model": chosen_model if used_tool != "images_edit_openai" else "gpt-image-2",
        "aspect_ratio": aspect,
        "image_size": image_size,
        "primary": {
            "file_id": primary.get("file_id"),
            "url": primary.get("url"),
        },
        "all_images": [
            {"file_id": img.get("file_id"), "url": img.get("url")} for img in images
        ],
        "reference_count": len(refs) + (1 if style_reference_file_id else 0),
    }


EXAMPLE_INPUT = {
    "prompt": (
        "16:9 YouTube thumbnail, smiling young engineer pointing at a glowing "
        "AI brain hologram on the right, dark studio background with neon "
        "blue rim light, bold yellow text overlay 'AI AGENTS EXPLAINED' on "
        "the left, cinematic depth of field"
    ),
}


async def main() -> None:
    result = await run(**EXAMPLE_INPUT)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
