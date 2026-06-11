# Meta Insights Caching and Dashboards

## Cached Insights Usage

- Use the integration-scoped table shown in toolkit context.
- Start with simple SQL slices (daily trend, campaign breakdown, ad set breakdown).
- Prefer cached analytics for reporting and dashboarding; use API endpoints when cache is missing or user needs uncached fields.

## 90-Day Ad-Level Insights

When the user needs historical ad-level performance, first query the ad account insights edge with `level: "ad"` instead of asking for a manual export or iterating every ad ID.

```json
{
  "object_id": "act_123456789",
  "object_type": "account",
  "level": "ad",
  "date_preset": "last_90d",
  "include_actions": true
}
```

- Use `time_increment: "1"` only when daily rows are needed for delivery dates or dormancy checks.
- Use `object_type: "ad"` only for a shortlisted individual ad drilldown.
- Do not claim Meta only supports 7 days unless the actual API response says so.

## Dashboard Workflow (Preset First)

When the user asks for a Meta dashboard or performance report:

1. **Use cached data context first**
   - Read the Meta context block for table name and last sync info.
   - Query cached data via `hyper_data_sql`.
   - Do not start with direct Meta API fetches when cache exists.

2. **Check dashboard templates before custom building**
   - Call `hyper_data_list_dashboard_templates`.
   - If a suitable preset exists (for example `meta_business_performance`), use it:

   `hyper_data_build_dashboard` with:
   ```json
   {
     "name": "Meta Performance Dashboard",
     "template_id": "meta_business_performance"
   }
   ```

3. **Only build custom dashboards if needed**
   - Use the Hyper Database dashboard/data app reference when the user asks for
     non-preset metrics or a special layout.
   - Pass SQL through `sql_data_sources` with explicit `scalar` or `rows`
     shapes; do not embed raw SQL placeholders in UI props.
   - Keep custom dashboards focused on the user question.

4. **Cache refresh policy**
   - Data syncs automatically every 30 minutes.
   - If data is stale or the user requests fresh data, call `meta_business_sync` with no parameters.
   - This is a background refresh. Do not wait for completion.
   - If no cached data exists yet, you may use the Meta API tools directly as a fallback.
