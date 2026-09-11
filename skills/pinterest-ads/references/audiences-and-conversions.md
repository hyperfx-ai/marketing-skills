# Pinterest Ads: Audiences & Conversion Tracking

## Phase 5: Audience & Targeting

### Create audience

```python
pinterest_ads_audiences_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="Website Visitors",
    audience_type="VISITOR",
    rule={"visitor_source_id": "<TAG_ID>", "type": "visitors"},
)
```

**`audience_type` values:** `CUSTOMER_LIST`, `VISITOR`, `ENGAGEMENT`, `ACTALIKE`.

**Rule structure by type:**

| Type | Rule example |
| --- | --- |
| `VISITOR` | `{"visitor_source_id": "<TAG_ID>", "type": "visitors"}` |
| `ENGAGEMENT` | `{"source": "AUDIENCE_RETENTION"}` (do NOT include `retention_days`) |
| `CUSTOMER_LIST` | `{"list_type": "EMAIL"}` |
| `ACTALIKE` | `{"source_id": "<SEED_AUDIENCE_ID>", "country": "US", "percentage": 5}` |

### Create customer list

```python
pinterest_ads_customer_lists_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="Email Subscribers",
    records="user1@example.com,user2@example.com,...",
    list_type="EMAIL",
)
```

**`list_type` values:** `EMAIL`, `IDFA`, `MAID`, `LR_ID`, `DLX_ID`, `HASHED_PINNER_ID`.

> Lists must match at least 100 Pinterest accounts after processing.

## Phase 6: Conversion Tracking

### List existing tags

```python
pinterest_ads_conversion_tags_list(ad_account_id="<AD_ACCOUNT_ID>")
```

### Create conversion tag

```python
pinterest_ads_conversion_tags_create(
    ad_account_id="<AD_ACCOUNT_ID>",
    name="Purchase Tracking",
    aem_enabled=true,
)
```

### Send conversion event

```python
pinterest_ads_conversion_events_send(
    ad_account_id="<AD_ACCOUNT_ID>",
    event_name="checkout",
    action_source="web",
    event_time=1709424000,
    event_id="unique_event_123",
    user_data={
        "em": ["5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"],
        "client_ip_address": "192.168.1.1",
        "client_user_agent": "Mozilla/5.0...",
    },
    custom_data={"currency": "USD", "value": "99.99"},
)
```

**`event_name` values:** `add_to_cart`, `checkout`, `custom`, `lead`, `page_visit`, `search`, `signup`, `view_category`, `watch_video`.

**`action_source` values:** `app_android`, `app_ios`, `web`, `offline`.

**`user_data` requirements** (at least one identifier required):

- `em` — array of SHA256-hashed email addresses (NOT plain text).
- `hashed_maids` — array of hashed mobile ad IDs.
- OR: `client_ip_address` + `client_user_agent`.
