# Thumbnail composition tips

Quick reference for the agent when generating or critiquing a YouTube
thumbnail concept. Use these as constraints inside the image-generation
prompt, not as suggestions appended after the fact.

## The 1-3-5 rule

A scrollable thumbnail can usually be parsed in under one second. Aim for:

- **1 dominant focal point** (a face, an object, a number)
- **≤3 visual elements** the eye needs to register
- **≤5 words of overlay text**

If the prompt has more than that, cut something before generating.

## Composition

- **Rule of thirds.** Place the focal subject on a third-line, not centred,
  unless the concept explicitly calls for symmetry.
- **Face on the left, text on the right** is the highest-CTR western default
  because viewers read left-to-right and the face commands attention first.
- **Eye contact** with the camera outperforms profile shots for human
  subjects. Pupils visible, no sunglasses, no extreme angles.
- **Negative space** behind text. Plain background or strong blur. Never put
  text over busy textures.
- **Contrast.** Foreground subject must visibly separate from background.
  Use rim light, drop shadow, or a contrasting backdrop colour.

## Colour palette

- 2-3 colours max, plus white/black for text.
- High-saturation accent colour (yellow, red, neon green, magenta, cyan)
  for the focal element or text overlay.
- Avoid YouTube-red as a dominant colour — it disappears against the UI.
- Mood-to-palette cheat sheet:
  - Curiosity / mystery → deep blue + neon accent
  - Excitement / hype → red + yellow
  - Tutorial / clean → white background + single accent
  - Drama / personal → cinematic teal-and-orange

## Text overlay

- Maximum 2-5 words. If you can't say it in 5, you don't need text.
- Sans-serif, heavy weight (Inter Black, Anton, Bebek, Impact-style).
- Stroke or drop shadow for legibility on every background.
- Capitalise content words; one ALL-CAPS power word is fine, never two.
- Place text where it does **not** overlap the YouTube duration badge
  (bottom-right corner) or the channel watermark (varies).

## Faces and emotion

- Strong, identifiable emotion: shocked, mind-blown, excited, smug,
  knowing-smile. Neutral faces underperform.
- One face per thumbnail unless the video is explicitly about contrast
  (debate, comparison, before/after).
- If using the user's uploaded face, preserve identity (no aging, no
  gender swap, no race shift) and only adjust expression and lighting.

## Mobile-first

- Most YouTube views happen on mobile. Open the generated image at
  ~280×158 px equivalent and check that:
  - The focal subject is still recognisable.
  - The text is still readable.
  - The visual hook still lands in <1 second.

If any of those fail, tell the user and offer to regenerate with a
simplified composition.

## What to avoid

- Stock-photo poses (especially handshakes, generic smiles, headsets).
- Generic AI-art tells (extra fingers, melted text, smooth plastic skin).
- Watermarks of unknown brands you can't verify.
- Misleading or fake "exclusive" badges.
- Heavy emoji walls — one emoji max if the niche expects them.
