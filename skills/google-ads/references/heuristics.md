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

## Optional dashboard rules

- Read `google_ads_gaql_query` through a declarative `tool` dataset, with a
  loader, an optional `calc_sql` and explicit `columns`
  ([reporting.md](reporting.md) Phase 4).
- Bind every displayed figure to a dataset through a `<hyper-*>` block. Type no
  numbers into the HTML.
- Return the dashboard as the final output only when the user asked for an
  interface or the task explicitly chose one.
- Do not describe internal interface implementation details to the user unless
  they ask.
