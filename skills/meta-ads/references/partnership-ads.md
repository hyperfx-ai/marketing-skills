# Partnership Ads

Use this workflow for Meta Partnership Ads, branded-content ads, creator-post
promotion, and Instagram Partnership Ad codes. These tools use the Meta
Business connection in Hyper; they do not use the separate Instagram organic
publishing toolkit or publish an organic post to the advertiser's profile.

## Requirements and permissions

Confirm the user has selected the intended Meta ad account, Facebook Page, and
Instagram professional account. The Meta connection needs `ads_management` for
ad creation plus the relevant Partnership Ads permissions:

- `facebook_branded_content_ads_brand`
- `instagram_branded_content_ads_brand`
- `instagram_basic`
- `pages_show_list`
- `pages_read_engagement`

Reading user comments on managed Page posts additionally requires
`pages_read_user_content`.

If the tools are present but Meta returns a permission error, call
`meta_ads_health_check`, report the missing permission, and tell the user to
reconnect Meta after the permission is approved and added to the app's Facebook
Login for Business configuration. Do not switch to the Instagram toolkit.

## Pick the correct workflow

| Source | Validate | Create |
| --- | --- | --- |
| Existing Facebook creator post | `meta_ads_partnership_existing_post_validate` | `meta_ads_partnership_existing_post_create` |
| Existing Instagram creator media | `meta_ads_partnership_existing_post_validate` | `meta_ads_partnership_existing_post_create` |
| Instagram Partnership Ad code | `meta_ads_partnership_existing_post_validate` | `meta_ads_partnership_existing_post_create` |
| Newly uploaded image or video | `meta_ads_partnership_ad_validate` | `meta_ads_partnership_ad_create` |

Never send an existing post or ad code to `meta_ads_partnership_ad_validate` or
`meta_ads_partnership_ad_create`. Those tools build a new creative and require
exactly one ad-account media reference: `image_hash` or `video_id`.

## Identity invariant

The creator is the publishing identity. The advertiser is the sponsor:

```text
creator Facebook Page       -> object_story_spec.page_id
creator Instagram account   -> object_story_spec.instagram_user_id
advertiser Facebook Page    -> facebook_branded_content.sponsor_page_id
advertiser Instagram account-> instagram_branded_content.sponsor_id
```

Do not infer IDs from similar names. Resolve them from the connected brand
assets and Partnership Ads content discovery, then show both identities to the
user before creation. Stop if the discovered creator or sponsor differs from
the user's intended accounts.

## Discover partners and content

1. Resolve the brand's ad account, Page, and Instagram account with the normal
   discovery tools.
2. Optionally call `meta_ads_partnership_ad_partners_list` with the brand's
   Instagram Graph ID or username. It returns creator relationships authorized
   for that brand; it is not a directory of every creator.
3. Call `meta_ads_partnership_advertisable_content_list` with at least the
   brand Facebook Page or Instagram account. Use one exact lookup when the user
   supplies it:
   - `content_ids`
   - `permalinks`
   - `ad_codes`
4. Do not combine an exact lookup with partner filters or `after`. Do not send
   more than one exact-lookup type in the same request.
5. Display the selected content's creator, platform, content ID, permalink,
   media type, `ad_eligibility`, `permission_status`, and tagged sponsor.

An empty broad listing does not prove a known post or ad code is unusable. Retry
once with the exact content ID, permalink, or code. Do not fall back to the
deprecated `branded_content_advertisable_medias` or old
`partnership-ads-advertisable-content` Page edge; use this discovery tool.

`AD_READY` plus an authorized permission is the normal existing-post path. A
valid Instagram Partnership Ad code is post-level authorization, so lack of an
account-wide partner relationship does not by itself invalidate that code.
Meta validation remains authoritative.

## Existing post or Instagram ad-code flow

1. Discover the exact content first. Preserve the creator and sponsor IDs from
   the returned item.
2. Resolve the selected ad set and show its ad account, campaign, objective,
   destination type, and status.
3. Build the validation call:
   - Facebook: pass `platform="facebook"`, the composite post ID as
     `source_post_id`, and the creator/brand Page IDs.
   - Instagram media: pass `platform="instagram"`, its media ID as
     `source_post_id`, and the discovered Instagram identities.
   - Instagram ad code: pass `platform="instagram"`,
     `partnership_ad_code`, `creator_instagram_user_id`, `brand_page_id`, and
     `brand_instagram_user_id`.
4. For a website/Traffic ad set, pass the user-approved `destination_url` and
   `call_to_action_type` to both validation and creation. Do not invent a URL
   or silently switch ad sets to avoid this requirement.
5. Call `meta_ads_partnership_existing_post_validate`. This is read-only.
6. Show its review summary and Meta validation result. Continue only if the
   identities, content, destination, ad account, campaign, and ad set match the
   user's request.
7. Only when the user requested creation, call
   `meta_ads_partnership_existing_post_create` with the same reviewed values.
8. Report the returned ad ID, creative ID, and `PAUSED` status. Fetch a preview
   with `meta_ads_ad_previews_get` before any later activation.

The ad code authorizes paid promotion of the creator's content. Passing it does
not activate anything and does not publish the post to the advertiser's
Facebook or Instagram feed.

## New uploaded-media flow

1. Upload the approved asset to the selected ad account with
   `meta_ads_ad_images_upload` or `meta_ads_ad_videos_upload` and capture its
   `image_hash` or `video_id`.
2. Select an authorized creator relationship with
   `meta_ads_partnership_ad_partners_list`.
3. Show and verify the creator Page/Instagram identity, advertiser sponsor
   Page/Instagram identity, destination, ad account, campaign, and ad set.
4. Call `meta_ads_partnership_ad_validate` with exactly one of `image_hash` or
   `video_id`, plus the destination, copy, CTA, and verified identities.
5. Show the validation review. Only when the user requested creation, call
   `meta_ads_partnership_ad_create` with the same reviewed values.
6. Report the ad ID, creative ID, and `PAUSED` status. Fetch a preview before
   any later activation.

## Prelaunch review

Before any create call, present a compact review containing:

- source post/ad code or uploaded asset
- creator Page and Instagram IDs
- sponsor Page and Instagram IDs
- ad account, campaign, and ad set names/IDs
- objective and destination type
- destination URL, CTA, and tracking tags
- partnership permission and eligibility status

Meta's validate-only operation checks payload validity, authorization, and
account compatibility. It does not understand whether the person, league,
product, or subject shown in the creative belongs to the intended advertiser.
Inspect the creative/source content and compare it with the user's brief and
selected sponsor. If the content cannot be inspected, say so and require the
user to verify it. Stop on any content/account mismatch.

Successful create calls always return a `PAUSED` ad. Do not activate it unless
the user explicitly approves after reviewing the preview.

## Partial failures

Creation happens in two stages: creative, then ad. If the response has
`creative_created: true` and `ad_created: false`, do not call the operation a
success. Report the preserved `creative_id`. Ask for explicit approval before
deleting that orphan with `meta_ads_creative_delete` or before retrying with
changed inputs.

Common routing errors:

- `Provide exactly one of image_hash or video_id`: an existing post/ad code was
  sent to a new-media tool, or uploaded media is missing.
- `Call to Action Required`: supply the approved destination URL and CTA
  required by the selected website/Traffic ad set.
- `Unknown path components` or an endpoint-deprecation error: use
  `meta_ads_partnership_advertisable_content_list`; do not construct Graph API
  paths manually.

## Managed Page content

`meta_ads_page_posts_list` lists feed posts from a Facebook Page managed by the
connected user. After the user selects a post, `meta_ads_page_post_comments_list`
displays user-generated comments. Both are read-only. These tools support Page
management and should not be used as substitutes for Partnership Ads content
discovery.
