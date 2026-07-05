# Image Prompting (per model)

`images_generate` picks a model for you when `model="auto"`, but the prompt you
write should still play to whichever model runs. Set `model` when the task clearly
calls for a specific one; otherwise let `auto` decide.

## Choosing a model (cheat sheet)

| Need | `model` |
|------|---------|
| First-pass concepts, ad ideation, compositions with reference images | `gpt-image-2` |
| High-resolution refinement, broad aspect ratios, image-to-image with multiple references | `nano-banana` |
| Readable text inside the image (posters, labels, infographics) or search-grounded scenes | `nano-banana-pro` |
| Product photography, material/fabric fidelity, accurate spatial depth | `seedream-4.5` |
| No strong preference | `auto` (default) |

## Per-model prompt shapes

### `gpt-image-2` (OpenAI)
- Best for: first-pass concepts, ad creative ideation, compositions with references.
- Prompt sections: objective → composition → style → brand constraints.
- Avoid long blocks of literal text and aspect ratios beyond 1:1, 2:3, 3:2.

### `nano-banana` (Gemini)
- Best for: high-resolution refinements, broad aspect ratios, image-to-image with multiple references.
- Prompt sections: subject → composition → style → lighting.
- Avoid competing visual instructions in the same prompt.

### `nano-banana-pro` (Gemini Pro)
- Best for: exact readable text inside the image (posters, labels, infographics) and search-grounded scenes.
- Prompt sections: exact_text → layout → hierarchy → style → aspect_ratio.
- Avoid ambiguous copy and too many independent text blocks.

### `seedream-4.5`
- Best for: product photography, material/fabric preservation, scenes requiring accurate spatial depth.
- Prompt sections: product_identity → surface_materials → lighting → camera_angle → environment.
- Avoid changing logo/text, warping packaging geometry, and busy backgrounds.

## Parameters

`images_generate` takes: `requests` (each `{prompt, id?, reference_images?}`),
`model`, `aspect_ratio`, `quality` (`"draft" | "standard" | "high"`), `n` (1-4),
`seed`, and `use_search`. `aspect_ratio` is the single spatial control and `quality`
covers the resolution/quality tier across models — pass intent through those, not
raw pixel sizes.
