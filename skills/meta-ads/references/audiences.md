# Custom audiences

Create, fill and inspect the audiences an ad set targets or excludes. The
`meta_ads_custom_audiences_list` and `meta_ads_lookalike_audiences_list`
reads in [discovery.md](discovery.md) still find existing audiences; this
file covers the writes and the reverse lookups.

## Tools

| Tool | Purpose |
| --- | --- |
| `meta_ads_custom_audience_create` | Create an audience (`body` with `name`, `subtype`, and the fields the subtype needs) |
| `meta_ads_custom_audience_get` / `_update` / `_delete` | Read, change or remove one audience (`custom_audience_id`) |
| `meta_ads_custom_audience_users_add` / `_remove` / `_replace` | Fill a customer-list audience from plain rows |
| `meta_ads_custom_audience_adsets_list` | The ad sets that include or exclude the audience, with the role of each |
| `meta_ads_custom_audience_ads_list` | The ads that use the audience |

Create, update, delete and the three users tools ask for approval.

## Subtypes and what each needs

The create tool refuses a body that lacks the subtype's fields and names
what is missing. The rules it checks:

| `subtype` | Required in `body` |
| --- | --- |
| `WEBSITE` | `rule` with the pixel as an event source (or `pixel_id`), and a retention window |
| `CUSTOM` (customer list) | `customer_file_source` (for example `USER_PROVIDED_ONLY`) |
| `LOOKALIKE` | `origin_audience_id` plus `lookalike_spec` (country and ratio) |
| `ENGAGEMENT` | `rule` whose `event_sources` name the Page or Instagram account |

`rule` and `lookalike_spec` are JSON strings on the wire. If a call is
refused because the value is an object, send the same value as JSON text.

Example, a 30-day website audience from a pixel:

```python
meta_ads_custom_audience_create(
    ad_account_id="1122334455",
    body={
        "name": "Site visitors 30d",
        "subtype": "WEBSITE",
        "retention_days": 30,
        "rule": '{"inclusions":{"operator":"or","rules":[{"event_sources":[{"id":"880000000000001","type":"pixel"}],"retention_seconds":2592000,"filter":{"operator":"and","filters":[{"field":"event","operator":"eq","value":"PageView"}]}}]}}',
    },
)
```

## Customer lists

Send plain rows. The tool normalises and hashes every value the way Meta
requires, so never hash them yourself.

```python
meta_ads_custom_audience_users_add(
    custom_audience_id="6200000000001",
    rows=[
        {"email": "jane@example.com", "phone": "+1 415 555 1234", "first_name": "Jane"},
        {"email": "max@example.com", "country": "US", "dob": "1990-05-17"},
    ],
)
```

Row keys: `email`, `phone` (with country code), `first_name`, `last_name`,
`first_initial`, `city`, `state`, `zip`, `country`, `dob` (YYYY-MM-DD),
`gender`, `external_id`, `madid`.

Any number of rows: the tool sends 10,000 per call under one session. The
result reports `num_received`, `num_invalid_entries` and samples of the
invalid rows. For more than a few hundred rows, build the row list in a
sandbox and call the tool from there.

**If a chunk fails mid-upload**, the result names `session_id` and
`resume_from_chunk`. Call the same tool again with the same rows and those
two values. Do not start a new upload: Meta rejects a second session while
the first is open, and after 90 minutes it commits only the chunks it
accepted. A `replace` that is left half-done shrinks the audience.

## Excluding an audience from an ad set

An ad set's targeting update replaces the whole targeting object. Read the
ad set first (`meta_ads_adset_get` with `targeting` in `fields`), add the
audience to `excluded_custom_audiences` as `{"id": "<audience id>"}`, keep
everything else, then `meta_ads_adset_update` with the whole targeting
object. Never put the audience in `custom_audiences`: that targets it.

## Before deleting or changing an audience

Call `meta_ads_custom_audience_adsets_list`. It reads every ad set of the
audience's ad account and keeps the ones whose targeting includes or
excludes the audience. When `complete` is false, call again with
`after=next_cursor`.
