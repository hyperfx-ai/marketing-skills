# Product Photoshoot Reference

Use `images_product_photoshoots_create` for studio shots, lifestyle photos, hero banners, moodboards, and sets of product variants. Supply the product name and any available brand information, verified selling points, and stored references.

## Defaults

`mode="product_shot"`, `count=1` (valid range 1–10), `quality="high"`, `variant_strategy="mixed"`, and `preserve_product_identity=true`. Set `aspect_ratio` to override the mode's default.

## Modes

| Mode | What it produces | Default aspect |
| --- | --- | --- |
| `product_shot` | Clean studio catalog shot | `1:1` |
| `lifestyle_scene` | Product in use in a real environment | `4:5` |
| `closeup_product_with_person` | Tight crop with hands or partial face | `4:5` |
| `moodboard_pin` | Pinterest-style moodboard composition | `2:3` |
| `hero_banner` | Wide campaign banner with negative space | `16:9` |
| `social_carousel` | Related slides with a shared palette | `4:5` |
| `ad_creative_pack` | Paid-social variants with room for an offer or hook | `1:1` |
| `virtual_model_tryout` | Model wearing or using the product | `4:5` |
| `conceptual_product` | Surreal styling such as levitation or splashes | `1:1` |
| `restyle` | Same subject with a new mood, season, or styling | `1:1` |

## Variant strategy

`variant_strategy` controls what changes between variants.

- `angles` varies camera views such as front, three-quarter, and top-down.
- `scenes` varies settings such as kitchen, café, and studio.
- `hooks` varies concepts such as before/after, problem/solution, and social proof.
- `palette` varies the overall color treatment.
- `props` varies accessories and styling elements.
- `mixed` picks a strategy based on the mode.

## Identity preservation

With `preserve_product_identity=true`, the tool adds prompt instructions to preserve the logo, printed text, packaging geometry, proportions, colors, finish, scale, and silhouette. It also adds `product.brand_colors` and `product.constraints` to those instructions when supplied. Inspect the generated images against the product before delivery, especially the label, colors, and proportions.

Upload or store product images first and pass `product.references[].file_id`. This tool ignores URL-only references.

## Example

Pass these JSON arguments to `images_product_photoshoots_create`.

```json
{
  "product": {
    "name": "Ember Travel Mug",
    "category": "insulated travel mug",
    "brand_name": "Ember",
    "brand_colors": ["#0F172A", "#FFEED9"],
    "selling_points": ["Leakproof closure"],
    "constraints": ["Keep the lid latch visible"],
    "references": [{"file_id": "<stored mug image file ID>"}]
  },
  "mode": "lifestyle_scene",
  "prompt": "Morning commute, modern apartment kitchen, warm window light",
  "count": 4,
  "variant_strategy": "scenes",
  "quality": "high",
  "preserve_product_identity": true
}
```
