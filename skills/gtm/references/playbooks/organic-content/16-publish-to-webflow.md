# Webflow Publishing

Publish approved content to a Webflow CMS collection as a draft.

## When to use

Read this only after a blog post (or other content artifact) is fully drafted and approved, and the brand uses Webflow as its CMS (check `02-audit-website-tracking.md`). Always the final step of `organic-content/seo-blog`. Skip if the brand is on Ghost, WordPress, etc., and surface that as an `open_question` in the strategy plan.

## Workflow

1. `webflow_list_sites()` — find the target site
2. `webflow_list_collections(site_id=...)` — find the blog collection
3. `webflow_get_collection_fields(site_id=..., collection_id=...)` — inspect actual field schema
4. Create draft: `webflow_create_collection_item_proxy(..., is_draft=True)`
5. Share preview with user
6. Only publish live if user confirms

## Field Mapping

Map to actual collection field names from step 3. Do not assume field names. Common fields:
- Title → name field
- Slug → slug field
- Body → rich text field
- Summary → plain text field
- Main image → image field

## Non-Negotiable

- Always create as draft first
- If the site is not on Webflow, stop and say so
- Do not guess field names — read the schema
