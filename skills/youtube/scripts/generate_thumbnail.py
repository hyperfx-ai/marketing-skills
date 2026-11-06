"""Generate a single YouTube thumbnail.

Every call goes through ``images_generate``; the inputs pick the ``model``:

- ``style_reference_file_id`` set     -> ``nano-banana`` (``nano-banana-pro``
                                          when the prompt needs rendered text)
                                          with that file in ``reference_images``.
- ``brand_file_ids`` or
  ``face_file_ids`` set               -> ``gpt-image-2.5-sunburst`` with the
                                          combined ``reference_images`` (best
                                          at composing several references).
- otherwise                           -> ``nano-banana-pro`` if the prompt
                                          has explicit text overlay,
                                          ``nano-banana`` otherwise.

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


# images_generate takes a quality tier; map the script's resolution knob onto it.
_QUALITY_BY_SIZE = {"1K": "draft", "2K": "standard", "4K": "high"}


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
    quality = _QUALITY_BY_SIZE[image_size]

    def gemini_model() -> str:
        if model == "pro":
            return "nano-banana-pro"
        if model == "flash":
            return "nano-banana"
        return "nano-banana-pro" if _looks_text_heavy(prompt) else "nano-banana"

    request: dict[str, Any] = {"id": "thumbnail", "prompt": prompt}
    if style_reference_file_id:
        chosen_model = gemini_model()
        request["reference_images"] = [style_reference_file_id]
    elif refs:
        chosen_model = "gpt-image-2.5-sunburst"
        request["reference_images"] = refs
    else:
        chosen_model = gemini_model()

    result = await call_tool(
        "images_generate",
        requests=[request],
        n=n,
        model=chosen_model,
        aspect_ratio=aspect,
        quality=quality,
    )

    images = result.get("images", []) if isinstance(result, dict) else []
    if not images:
        raise RuntimeError(f"images_generate returned no images: {result}")

    primary = images[0]
    return {
        "tool_used": "images_generate",
        "model": chosen_model,
        "aspect_ratio": aspect,
        "image_size": image_size,
        "quality": quality,
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
