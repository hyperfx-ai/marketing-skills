# Multi-Account Workflows (MCC)

When a user provides a manager account (MCC) with multiple sub-accounts:

## Batching Rule
**Never query more than 5 sub-accounts in a single run.** Each `google_ads_gaql_query` call goes through a proxy with a timeout. Querying 10+ accounts sequentially in one loop reliably causes 504 timeouts.

Process in batches of 5 and aggregate results before proceeding:
```
Batch 1: accounts[0:5]   → collect results
Batch 2: accounts[5:10]  → collect results
Batch 3: accounts[10:15] → collect results
...merge all batches...
```

Announce progress to the user: `"Processing accounts 1-5 of 23..."`.

## 504 Timeout Recovery
If a `google_ads_gaql_query` call times out (504 / "Google Ads API timed out after retries"):
1. The tool already retries 3× internally — do not retry immediately.
2. Reduce the scope: narrow the date range, add a `LIMIT`, or split the account list further.
3. Tell the user which accounts succeeded and which failed; do not silently drop accounts.

## Cross-Account Search Term Report (Most Common Use Case)

For MCC search term reports across many sub-accounts:

```
1. Get all accounts: connections_info(toolkit_id="google_ads") in Hyper chat,
   or google_ads_accounts_list() on an MCP client or the CLI.
   Filter to sub-accounts: [a for a in result["accounts"] if "customer_id" in a and not a.get("manager")]
2. For each batch of 5 accounts:
   - Run search_term_view GAQL (using segments.keyword.info.*, NOT ad_group_criterion).
   - Collect results tagged with customer.descriptive_name.
3. Merge all batches into a single dataset.
4. Write to Google Sheets or CSV file for the user.
```

Minimum required columns for a search term report:
- Search Term, Account Name, Keyword, Match Type, Campaign, Ad Group.
- Clicks, Impressions, Conversions, Cost.
- Add Negative (Yes/No — your recommendation).

GAQL resource-compatibility rules (which fields work with `search_term_view` vs `keyword_view`) are in [reporting.md](reporting.md).
