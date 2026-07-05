---
name: google-sheets
description: Safe workflow for reading, mapping, and writing Google Sheets without shifting columns or overwriting the wrong ranges. Use when the user wants to read, update, or append spreadsheet data, fix sheet structure, or sync data into Google Sheets.
use_cases:
  - Update a Google Sheet safely
  - Append rows to a spreadsheet
  - Map data into existing sheet columns
  - Fill CRM sheets from tool or database results
  - Verify spreadsheet headers before writing
  - Repair or avoid column misalignment in Sheets
triggers:
  - google sheets
  - spreadsheet
  - sheet mapping
  - write rows
  - append rows
  - update cells
  - map columns
  - fill sheet
requires_toolkits:
  - google_sheets
suggested_toolkits:
  - sandbox
icon: google_sheets
short_description: Write structured data to Google Sheets and keep spreadsheets up to date.
---

# Google Sheets Writing

Use this skill whenever you need to write structured data into an existing spreadsheet.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Google Sheets integration** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## Core Rule

Never write to Google Sheets from guessed column letters alone.

Always:
1. inspect the workbook and target worksheet
2. find the real header row
3. map fields by header name
4. verify the destination range
5. write
6. read back sample rows to confirm alignment

## Critical Failure Modes To Avoid

- Do not assume row 1 is the real header row.
- Do not assume column `A` is the first business/data column.
- Do not treat helper cells like `Total`, notes, formulas, merged labels, or spacer columns as real headers.
- Do not overwrite a broad range before checking existing data and layout.
- Do not claim success until you read back the written cells.

## Required Workflow

### Step 1: Inspect workbook structure

Start with:
- `google_sheets_get`
- `google_sheets_worksheets_list` if needed

Confirm:
- worksheet title
- row/column counts
- whether there are multiple candidate tabs

### Step 2: Read enough context to find the real headers

Read more than one row when structure is unknown.

Typical pattern:
- `google_sheets_values_get(..., range="Sheet1!A1:Z5")`

Look for:
- true column labels
- helper columns before the real table
- title rows, totals, formulas, blank separators

If the first row contains labels like `Total`, `Notes`, or other non-record metadata, do not anchor your write range to that row alone.

### Step 3: Build a header map

Map your source fields to actual sheet headers by name, not memory.

Example:
- source field `business_name` -> sheet header `Business Name`
- source field `contact_email` -> sheet header `Owner (s) Email`

If a required header is missing or ambiguous, stop and ask the user instead of guessing.

### Step 4: Choose the safest write strategy

Use:
- `google_sheets_values_update` for one verified contiguous range
- `google_sheets_values_batch_update` for multiple verified ranges

Prefer narrow writes over large blanket writes.

If appending records into a table that already has fixed columns, compute the exact destination columns from the header map first.

## Write Rules

- Only write columns you have positively mapped.
- Leave unrelated columns untouched.
- When a sheet contains helper columns before the table, start writing at the true mapped column, not column `A`.
- If a field is intentionally blank, write a blank value only to that verified column.
- Use `RAW` unless the user explicitly wants formulas or Sheets parsing behavior.

## Verification Is Mandatory

Immediately after writing:
1. read back the exact written range
2. inspect at least 2-3 sample rows
3. confirm each field landed under the intended header

If the read-back is misaligned, acknowledge it and correct it before reporting success.

## Recommended Tool Pattern

1. `google_sheets_get`
2. `google_sheets_values_get` on a header-discovery range such as `A1:Z5`
3. optional `google_sheets_values_batch_get` for existing data + destination area
4. `google_sheets_values_update` or `google_sheets_values_batch_update`
5. `google_sheets_values_get` on the written range for verification

## Example Mindset

Bad:
- “I saw `Business Name` near the start, so I will write `A2:F51`.”

Good:
- “The first visible row includes `Total: 7` in column `A`, while `Business Name` is actually in column `B`, so I will map the write range from `B` onward and verify it after writing.”
