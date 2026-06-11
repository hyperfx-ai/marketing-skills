# Google Ads Reporting Notes

## When to use

Read this when explaining a Google Ads report. These notes describe how
to keep claims tied to the queried data; they are not optimization rules.

## Reporting rules

- State the customer ID and date range used.
- Name the GAQL resource queried, such as `campaign`, `ad_group`, or
  `conversion_action`.
- Treat rows as evidence, not as automatic recommendations.
- Do not infer account changes from a report unless the user explicitly
  asks for recommendations.
- If a report depends on conversion actions, use
  `segments.conversion_action` and `segments.conversion_action_name` for
  campaign-level metrics.
- If a report needs configured conversion-action metadata, query
  `FROM conversion_action` separately.

## Optional dashboard/data app rules

- Use `google_ads_execute_gaql` inside `tool_data_sources`.
- Query the saved cache table with `sql_data_sources`.
- Bind only SQL output variables inside the dashboard/data app code.
- Return the persisted dashboard artifact as the final output only when the
  user asked for an interface or the task explicitly chose one.
- Do not describe internal interface implementation details to the user unless
  they ask.
