# Marketplace Cards Reference

Use `images_marketplace_cards_create` for Amazon main and secondary images and A+ modules, Shopify product images, or Etsy product photos.

## Scopes

The defaults are `scope="product_images"`, `marketplace="generic"`, and `quality="high"`. An explicit `assets` list overrides the scope. An optional `aspect_ratio` overrides the default framing for every selected asset.

| Scope | Assets |
| --- | --- |
| `main` | `main_image` |
| `product_images` | `main_image`, `infographic`, `multi_angle`, `detail_shot`, `lifestyle`, `whats_in_box` |
| `aplus` | `aplus_hero_banner`, `aplus_pain_points`, `aplus_features`, `aplus_ingredients`, `aplus_efficacy`, `aplus_how_to_use` |
| `full_set` | All `product_images` assets plus `aplus_hero_banner`, `aplus_pain_points`, `aplus_features`, and `aplus_how_to_use` |

## Per-asset framing

| Asset | Prompt focus | Default aspect |
| --- | --- | --- |
| `main_image` | Pure white background, product fills 85% of frame, no overlays | `1:1` |
| `infographic` | Feature callouts with icons and short labels | `1:1` |
| `multi_angle` | Three-angle composite with consistent lighting | `1:1` |
| `detail_shot` | Close-up of a key feature with shallow depth of field | `1:1` |
| `lifestyle` | Product in its intended environment | `4:5` |
| `whats_in_box` | Flat lay of included items on a neutral background | `1:1` |
| `aplus_hero_banner` | Wide hero with negative space and premium lighting | `16:9` |
| `aplus_pain_points` | Before/after comparison or icon grid | `16:9` |
| `aplus_features` | Three to four feature tiles | `16:9` |
| `aplus_ingredients` | Ingredient shots with sourcing notes | `16:9` |
| `aplus_efficacy` | Results-led visual with a supporting metric | `16:9` |
| `aplus_how_to_use` | Numbered steps with hands-on shots | `16:9` |

## Product and marketplace guidance

- Include verified claims in `product.selling_points`, especially ingredient, efficacy, or results claims.
- Upload or store product images and pass `product.references[].file_id`. The tool uses stored references and adds prompt instructions to preserve the logo, text, packaging, colors, material, and scale.
- Choose `"amazon"`, `"shopify"`, `"etsy"`, or `"generic"` for `marketplace`. Marketplace guidelines shape the prompt. Inspect the finished images against the listing's rules before publishing.

## Example

Pass these JSON arguments to `images_marketplace_cards_create`.

```json
{
  "product": {
    "name": "Glow Vitamin C Serum",
    "brand_name": "Glow Lab",
    "selling_points": ["20% L-ascorbic acid", "Vegan formula"],
    "references": [{"file_id": "<stored serum image file ID>"}]
  },
  "scope": "product_images",
  "marketplace": "amazon",
  "quality": "high"
}
```
