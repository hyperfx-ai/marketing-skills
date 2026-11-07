# Account history, delivery issues, recommendations, field lookup

Four reads that answer "what happened, what is wrong, what does Meta
suggest, and what can I set", plus the one write that applies a suggestion.

## Tools

| Tool | Purpose |
| --- | --- |
| `meta_ads_activity_list` | The Ads Manager change history of an ad account |
| `meta_ads_delivery_issues_list` | Campaigns, ad sets and ads Meta flags with a delivery issue |
| `meta_ads_recommendation_list` | Meta's recommendations for one ad account |
| `meta_ads_business_recommendation_list` | The same across a business, with each account's opportunity score |
| `meta_ads_recommendation_apply` | Apply one recommendation by its signature (asks for approval) |
| `meta_ads_field_context_get` | Which fields a Meta object accepts, their allowed values, and which are read-only |

## Who changed what

```python
meta_ads_activity_list(
    ad_account_id="1122334455",
    oid="120210000000456",           # one object; omit for the whole account
    category="BUDGET",               # ACCOUNT, AD, AD_SET, AUDIENCE, BID, BUDGET, CAMPAIGN, STATUS, TARGETING, ...
    since="2026-10-03", until="2026-10-10",
)
```

Each entry has `event_type`, `event_time`, `actor_name`, `object_id`,
`object_name`, `object_type` and `extra_data` (old and new values as JSON
text). Always give a date range: the edge is heavy on large accounts.

## What blocks delivery

`meta_ads_delivery_issues_list(ad_account_id=..., levels=["campaign", "adset", "ad"])`
reads all three levels and returns only objects whose `issues_info` is
non-empty, with the error summary and message Meta attaches. On a large
account the read takes several seconds; each level reports `complete` and
a `next_cursor` when it stopped at its page cap.

## What Meta recommends

`meta_ads_recommendation_list(ad_account_id=...)` returns each
recommendation's `recommendation_name`, `recommendation_stage`, `level`,
`object_ids`, `opportunity_score_lift`, a deep-link `url`, and a
`recommendation_signature` when Meta lets the API apply it. Pass
`fields=recommendation_content` to add the lift estimate and body text.

`meta_ads_business_recommendation_list(business_id=...)` does the same for
every ad account the business owns and adds `opportunity_score` (0 to 100)
per account. Filters: `ad_account_ids`, `recommendation_stages`,
`recommendation_names`, `locale`.

`meta_ads_recommendation_apply(ad_account_id=..., recommendation_signature=...)`
changes the campaigns, ad sets or ads the recommendation covers. Show the
recommendation to the user first. A signature can expire; list again when
Graph refuses one. A recommendation without a signature applies only in
Ads Manager, at its `url`.

## Which fields a tool accepts

`meta_ads_field_context_get(object_type="campaign")` lists the writable
fields of the create and update tools with their allowed values, and the
readable fields of the node. With `field="objective"` it answers for one
field. No Meta call; the answer comes from the toolkit's own schema. Use it
before guessing a field name or enum value.
