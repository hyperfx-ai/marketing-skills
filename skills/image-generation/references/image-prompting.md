# Image Prompting

State the objective, define the subject and composition, and specify the details that must stay fixed. Put exact copy in quotes and identify where it should sit. For an edit, say which reference provides the product, layout, or visual style. [Image Generation](../SKILL.md)

## GPT Image 2.6 Sunburst and Flare

- Start with the objective, then give the composition, style, and brand constraints. For an edit, identify the change and name the elements to preserve.
- Use Sunburst for layered compositions and precise edits. Use Flare to test a concept quickly.
- Supported ratios are `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, and `21:9`. For longer ad copy that needs crisp rendering, use `ad_creatives_generate` for HTML overlays.

## Nano Banana 2.1 and Nano Banana

- Describe the subject, composition, visual style, and lighting. When combining references, assign each one a clear role. For example, keep the packaging from the first image and use the lighting from the second.
- Specify what to preserve and remove conflicting instructions. Use the extreme ratios when the placement needs them (`1:4`, `1:8`, `4:1`, `8:1`).

## Nano Banana Pro

- Give exact text, layout, visual hierarchy, and style. Keep independent text blocks short and make their relative placement explicit.
- For search grounding, name the real product, place, or subject and set `use_search=true` in the call.

## FLUX 3 Image

- For candid photography, describe who or what is in frame, the natural light, the lens or framing, and details of a believable setting. A concrete detail such as uneven phone-camera framing is more actionable than “make it authentic.”
- Use a text-only prompt. `flux-3-image` ignores `quality`.

## Seedream 4.5

- Describe product identity, material and fabric finish, lighting, camera angle, and environment. Specify packaging geometry, color, and any short label that needs to stay legible.
- Use a text-only prompt. When reference fidelity matters, choose a model that accepts product images.

## Output controls

Set framing with `aspect_ratio` or `ad_placements`. The `quality` values `"draft"`, `"standard"`, and `"high"` map differently by model. GPT Image maps them to quality settings, Nano Banana to image sizes, and Seedream to size presets for the selected ratio.
