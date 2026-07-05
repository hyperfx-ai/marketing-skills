# Product Photoshoot Reference

Use `images_product_photoshoots_create` (not generic image generation) whenever the goal is on-brand product or campaign visuals. The tool wraps prompt construction, identity preservation, and variant generation so you don't have to reinvent it per call.

## When to use

- The user asks for "product photos", "product shots", "lifestyle photos", "hero banner", "campaign image", "moodboard", "ad creative pack", "carousel", or similar.
- You have a `ProductContext` (name, brand, references, selling points) — even a partial one.
- You want multiple variants from a single call.

## Modes

| Mode | What it produces | Default aspect |
|------|------------------|----------------|
| `product_shot` | Clean studio catalog shot | 1:1 |
| `lifestyle_scene` | Real-environment in-use moment | 4:5 |
| `closeup_product_with_person` | Tight crop with hands or partial face | 4:5 |
| `moodboard_pin` | Pinterest-style moodboard composition | 2:3 |
| `hero_banner` | 16:9 campaign banner with negative space | 16:9 |
| `social_carousel` | Connected slide system with shared palette | 4:5 |
| `ad_creative_pack` | Paid social variants with offer/hook areas | 1:1 |
| `virtual_model_tryout` | Model wearing or using product | 4:5 |
| `conceptual_product` | Surreal CGI styling, levitation/splash | 1:1 |
| `restyle` | Keep subject, change mood/season/styling | mode default |

## Variant strategy

`variant_strategy` controls which dimension changes between variants:

- `angles` — front, three-quarter, top-down, low angle, side, back
- `scenes` — kitchen, café, studio, desk, soft daylight, dinner table
- `hooks` — before/after, problem/solution, scroll-stop, social proof
- `palette` — warm, cool, mono, high contrast, pastel, earthy
- `props` — minimal, matched accessories, ingredient props, lifestyle, food, outdoor
- `mixed` — automatic, picks the natural strategy for the mode

## Identity preservation

The tool always inserts these clauses (unless `preserve_product_identity=False`):

- Preserve logo and printed text exactly
- Preserve packaging geometry and proportions
- Preserve colorway and material finish
- Keep product scale and silhouette accurate

If `product.brand_colors` is set, it's also added as a respect-palette constraint. Anything in `product.constraints` is appended verbatim.

## Example

```python
create_product_photoshoot(
    product=ProductContext(
        name="Ember Travel Mug",
        category="insulated travel mug",
        brand_name="Ember",
        brand_colors=["#0F172A", "#FFEED9"],
        selling_points=[
            "leakproof closure",
            "16-hour heat retention",
        ],
        references=[MediaInput(file_id="file_image_gen_..._mug")],
    ),
    mode="lifestyle_scene",
    prompt="Morning commute, modern apartment kitchen, warm light",
    count=4,
    variant_strategy="scenes",
    quality="high",
)
```
