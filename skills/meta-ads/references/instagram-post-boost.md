# Boost the brand's own Instagram post

Use this workflow for a post published by the advertiser's own Instagram account. For a creator's sponsored post or Partnership Ad code, inspect the connected Partnership Ads tools and follow that workflow. Do not send a creator's post through the own-post boost.

## Availability and identity

Inspect the live descriptors for `meta_ads_instagram_accounts_list`, `meta_ads_instagram_media_list` and `meta_ads_instagram_post_boost`. The media-list and boost tools are conditional. If either is missing, report that the connected environment cannot complete this workflow. Tool names and input schemas from the live catalog take precedence over this reference.

1. Choose the advertiser's ad account. Use `meta_ads_instagram_accounts_list(account_id=...)` to discover its Instagram identities and associated `page_id` values.
2. Match the requested brand to the returned identity. Prefer an actual Instagram account over a Page-backed identity (`source="pbia"`). Keep the Instagram user ID and Facebook Page ID distinct. If there are multiple plausible identities, ask which brand to use.
3. Read that identity's posts with `meta_ads_instagram_media_list(ig_user_id=..., limit=10)`. Use the returned `media_product_type`, timestamp, permalink and caption to select the latest requested reel or named post. An Instagram user ID identifies the account; a media ID identifies one post.
4. Inspect `boost_eligibility_info` when returned. A missing eligibility result is unknown; do not claim eligibility from media type alone. Stories are absent from the media-list edge. Do not invent an ID when the requested post is missing.

A permission error can require reconnecting the Meta Business integration with Instagram access. Report the exact error and affected identity before retrying; do not assume an empty successful list means a permission failure.

## Prepare and create

Use an existing ad set in the selected ad account. Review its objective, budget, schedule and destination requirements before creating the ad. This workflow creates one creative and one paused ad; it does not create or activate the campaign or ad set.

Present the selected post's permalink, Instagram identity, Page, ad account, ad set and proposed name. Apply the user's existing authorization and the tool's write-approval requirement. For an objective that requires a destination button, supply the supported `post.call_to_action` type and link; inspect the live schema for accepted values.

Call `meta_ads_instagram_post_boost` with:

| Input | Source |
| --- | --- |
| `adset_id` | The reviewed existing ad set |
| `name` | The reviewed name for both creative and ad |
| `post.ig_media_id` | The selected media-list result |
| `post.ig_user_id` | The discovered Instagram identity |
| `post.page_id` | That identity's returned Facebook Page |
| `post.call_to_action` | Optional supported button and destination |
| `ad_account_id` | Selected ad account; omit only when the connection has one account |

Record the returned `creative_id`, `ad_id`, `status` and any `error`. A successful boost returns `status="PAUSED"`. Show an ad preview before a separately authorized activation. Do not activate merely because the user asked to prepare a boost.

## Partial or uncertain results

A missing ID does not prove Meta created nothing. A timeout can occur after Meta accepted the request. Check Meta's current objects before retrying so the same post does not receive duplicate creatives or ads.

If `creative_id` is confirmed but `ad_id` is absent, preserve the creative ID and inspect the ad set for an existing ad. Only after establishing that an ad is absent should an authorized `meta_ads_ad_create` reuse that creative. Do not call the boost tool again to recreate it. If neither ID is confirmed, inspect both creatives and ads before another write. Report the uncertainty and confirmed state exactly.
