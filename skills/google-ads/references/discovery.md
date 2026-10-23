# Discovery, research, and consultation

Every campaign build starts here. Do not skip any phase — the pre-creation summary at the end must be approved before anything is created.

## Phase 1: Initial Setup

In Hyper chat, read the accounts from `connections_info(toolkit_id="google_ads")`. Call `google_ads_accounts_list()` only on an MCP client or the CLI, or to refresh the list.

- If multiple: ask the user to select one.
- If single: inform the user and proceed.

**CRITICAL**: Verify account access before any operations.

## Phase 2: Discovery & Research (MANDATORY)

### Research Steps
1. Get the real domain (ask; don't infer).
2. Scan the site end-to-end: home, product/service, pricing, about, FAQs, locations, contact, landing pages.
3. Understand funnel & goals: primary conversions, CTAs, forms/checkout, thank-you pages.
4. Extract messaging: value props, differentiators, proof, offers.

### Conversion Tracking Check
Inspect conversion actions on the selected account:
```
google_ads_gaql_query(
  customer_id="<from google_ads_accounts_list or connections_info>",
  query="""
    SELECT conversion_action.id, conversion_action.name,
           conversion_action.status, conversion_action.type
    FROM conversion_action
    WHERE conversion_action.status = 'ENABLED'
  """
)
```



### Market & Keyword Research
- Inspect SERPs, competitors, and themes.
- Propose keyword candidates (intent-aligned).
- Identify initial negatives.

### Confirm Criticals
- Daily budget (+currency).
- Served geos.
- Constraints.
- Tracking status.

## Phase 3: Consultation

Act as a partner, not order-taker:
- Present findings (site + GAQL + market).
- Recommend bidding (default Smart Bidding when tracking exists) with trade-offs.
- Propose structure (campaign → themed ad groups → keywords + match types).
- Suggest locations with `google_ads_locations_search(customer_id="...", query="New York", country_code="US")`. `query` is one string: a city, state, country or postal code. The tool returns geo target IDs.
- Set budget expectations via benchmark ranges.
- Show reasoning for each choice.

## Phase 4: Pre-Creation Summary (Must Be Approved)

```
Campaign Strategy for [Business Name]

Sources: [URL], GAQL
Conversion Setup: [GAQL findings]
Primary Goal: [objective + why]
Bidding: [strategy + why]
Budget: $[X]/day (expectations)
Locations: [targets + rationale]
Keyword Themes: [themes + match types + 2-3 examples]
Messaging: [angles pulled from site]
Trade-offs/Risks: [bullets]

Approve to proceed?
```

Wait for explicit approval. No emojis. No assumptions.

Once approved, continue to the matching campaign file: [campaigns/search-display.md](campaigns/search-display.md) or [campaigns/pmax.md](campaigns/pmax.md).
