# Marketplace Cards Reference

Use `images_marketplace_cards_create` for the standard image set retailers expect on a listing — Amazon main image + secondary images + A+ modules, Shopify product images, Etsy product photos.

## Scopes

Pick a scope and the tool expands it to the deterministic asset set:

| Scope | Assets |
|-------|--------|
| `main` | `main_image` |
| `product_images` | `main_image`, `infographic`, `multi_angle`, `detail_shot`, `lifestyle`, `whats_in_box` |
| `aplus` | `aplus_hero_banner`, `aplus_pain_points`, `aplus_features`, `aplus_ingredients`, `aplus_efficacy`, `aplus_how_to_use` |
| `full_set` | `product_images` + selected A+ modules |

You can override the scope by passing an explicit `assets=[...]` list.

## Per-asset framing

Each asset has its own aspect ratio and prompt focus baked in:

- `main_image` — pure white background, product fills 85% of the frame, no overlays. **1:1**
- `infographic` — feature callouts with icons + short labels. **1:1**
- `multi_angle` — three-angle composite, consistent lighting. **1:1**
- `detail_shot` — extreme close-up on signature feature, shallow depth. **1:1**
- `lifestyle` — real environment of intended use. **4:5**
- `whats_in_box` — flat lay of every included item, neutral background. **1:1**
- `aplus_hero_banner` — wide hero with negative space, premium lighting. **16:9**
- `aplus_pain_points` — before/after split or icon grid. **16:9**
- `aplus_features` — three to four feature tiles. **16:9**
- `aplus_ingredients` — ingredient hero shots with sourcing notes. **16:9**
- `aplus_efficacy` — results-led visual with supporting metric. **16:9**
- `aplus_how_to_use` — numbered usage steps with hands-on shots. **16:9**

## Marketplace targeting

`marketplace="amazon" | "shopify" | "etsy" | "generic"` adds a per-target compliance hint to every prompt — e.g. Amazon enforces white background on the main image and no logos/watermarks. Use `generic` when the listing isn't tied to a specific marketplace.

## Identity preservation

Every asset prompt includes preservation clauses (logo/text exact, geometry, colorway, material, scale). Pass product references via `product.references` so the underlying image-to-image backend has them.

## Example

```python
create_marketplace_cards(
    product=ProductContext(
        name="Glow Vitamin C Serum",
        brand_name="Glow Lab",
        selling_points=[
            "20% L-ascorbic acid",
            "vegan",
            "results in 4 weeks",
        ],
        references=[MediaInput(file_id="file_image_gen_..._serum")],
    ),
    scope="product_images",
    marketplace="amazon",
    quality="high",
)
```
