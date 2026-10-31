# Signals and catalog health

Pixel (dataset) health, pixel access, and the catalog diagnostics that
explain why Advantage+ catalog ads drop products. Every tool here is a read
except the ones marked **approval**.

## Pixel event volume and match quality

| Tool | Purpose |
| --- | --- |
| `meta_ads_dataset_stats_list` | Event counts a pixel received (`dataset_id`, `start_time`, `end_time`, optional `aggregation`, `event`, `event_source`) |
| `meta_ads_dataset_quality_get` | Event Match Quality per web event, with coverage, freshness and dedupe feedback (`dataset_id`) |
| `meta_ads_dataset_da_checks_list` | Meta's dynamic-ads setup checks on the pixel |
| `meta_ads_pixel_event_rules_list`, `meta_ads_pixel_parameters_list` | The Events Manager rules and parameter extractors, read only |

To compare two periods, call `meta_ads_dataset_stats_list` once per period.
`event` applies only with `aggregation="custom_data_field"`; the default
aggregation groups by event name. EMQ covers web events only.

## Pixel access

| Tool | Purpose |
| --- | --- |
| `meta_ads_dataset_shared_account_list` / `_create` / `_delete` | The ad accounts a pixel is shared with; share or unshare (**approval**) |
| `meta_ads_dataset_assigned_user_list` | The business users assigned to a pixel (`dataset_id`, `business` required) |
| `meta_ads_dataset_assigned_user_create` | Assign a user with tasks: `ANALYZE`, `ADVERTISE`, `EDIT`, `UPLOAD`, `AA_ANALYZE` (**approval**) |

Sharing a pixel with a second ad account is `_shared_account_create` with
`body={"account_id": "<act id without act_>", "business": "<business id>"}`.
Removing a user is not available through Hyper (Business Settings).

## Catalog diagnostics

| Tool | Purpose |
| --- | --- |
| `meta_ads_catalog_health_get` | One call: issues grouped by severity, product count, connected event sources |
| `meta_ads_catalog_diagnostics_list` | Every issue with severity, type, affected items (`catalog_id`; filter by `severities`, `types`) |
| `meta_ads_catalog_data_sources_list` | The feeds, uploads and API sources that fill the catalog |
| `meta_ads_catalog_event_stats_list` | Matched and unmatched events per source |
| `meta_ads_catalog_batch_status_get` | The status of a batch upload (`catalog_id`, `handle`) |
| `meta_ads_product_item_list` with `filter` | Products matching a rule, for example `{"availability": {"eq": "in stock"}}` or `{"retailer_id": {"is_any": ["sku-1"]}}` |

Start with `meta_ads_catalog_health_get`. Read `_diagnostics_list` for the
full list when the summary shows `MUST_FIX` issues.

## Event sources (pixel to catalog)

A catalog matches signals against products only when a pixel, app or
offline set is connected to it.

| Tool | Purpose |
| --- | --- |
| `meta_ads_catalog_event_source_list` | What is connected (`catalog_id`) |
| `meta_ads_catalog_event_source_create` / `_delete` | Connect or disconnect: `body={"external_event_sources": ["<pixel id>"]}` (**approval**) |
| `meta_ads_event_source_catalogs_list` | The reverse: which catalogs use this pixel (`event_source_id`, `business_id`) |

Match-rate health and "which source to connect" suggestions are not
available through Hyper (Commerce Manager).

## Feed rules and re-fetches

| Tool | Purpose |
| --- | --- |
| `meta_ads_product_feed_rule_list` / `_create` / `_delete` | Rules Meta applies to every fetch of a feed (**approval** on create and delete) |
| `meta_ads_product_feed_upload_list` / `_create` | Past fetch sessions with their counts; start a fetch from the feed URL (**approval**) |
| `meta_ads_product_feed_upload_errors_list` | The errors of one session (`product_feed_upload_id`) |

Rule types and the `params` each needs (the create tool refuses a mismatch
and names the valid values):

| `rule_type` | `params` |
| --- | --- |
| `mapping_rule` | `{"map_from": "<source column>"}` |
| `value_mapping_rule` | 1 to 10 `{"<source value>": "<target value>"}` pairs |
| `letter_case_rule` | `{"type": "to_upper" \| "to_lower" \| "capitalize_all" \| "capitalize_first"}` |
| `fallback_rule` | `{"user_default_value": "<value>"}` |
| `regex_replace_rule` | `{"regex": "<pattern>"}` |

The loop a catalog person runs by hand: read the latest upload's errors,
add a rule, `_upload_create` with the feed's `url` to re-fetch, read the
new session's counts.
