---
name: documents
description: Generate professional PDF documents in the sandbox — reports, factsheets, invoices, proposals — and convert Markdown to styled PDFs. Use when the user wants a PDF report, invoice, proposal, factsheet, a markdown-to-PDF conversion, or a PDF deck for a LinkedIn document post.
use_cases:
  - Generate a PDF report from data
  - Create a finance report with charts and tables
  - Build a marketing performance report
  - Generate a client proposal document
  - Create an invoice with line items and payment details
  - Generate a formal project proposal or RFP response
  - Create a fund factsheet or KIID
  - Produce a PDF with two-column layout
  - Make a PDF with pie charts and bar charts
  - Generate a PDF dashboard with KPI cards
  - Create a professional document with cover page
  - Convert structured data into a formatted PDF
  - Convert a markdown file or string to a styled PDF
  - Generate a PDF deck for a LinkedIn document or carousel post
triggers:
  - pdf
  - markdown to pdf
  - md to pdf
  - report
  - generate pdf
  - pdf report
  - document generation
  - factsheet
  - proposal
  - invoice
  - finance report
  - marketing report
  - reportlab
  - linkedin carousel
  - linkedin pdf
requires_toolkits:
  - sandbox
suggested_toolkits:
  - file_manager
  - image_gen
---

# Documents

Generate professional, well-designed PDF documents using ReportLab in the E2B sandbox.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Sandbox toolkit** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## ALWAYS Read First

Before writing any PDF generation code, read `references/design-principles.md`. It defines the color palettes, typography scale, spacing system, and composition rules that separate professional output from generic slop. Every report you generate must follow these principles.

## Routing Table

Read the focused reference based on the task:

| Need | Reference |
|------|-----------|
| Design rules, color palettes, typography, anti-patterns | `references/design-principles.md` |
| ReportLab imports, page setup, styles, flowables | `references/reportlab-fundamentals.md` |
| Two-column and multi-column page layouts | `references/two-column-layouts.md` |
| Charts: pie, bar, line, heatmap, donut, KPI cards (matplotlib/seaborn preferred) | `references/charts-and-visualizations.md` |
| Finance reports (P&L, revenue, expenses) | `references/finance-reports.md` |
| Marketing reports (campaigns, funnel, ROI) | `references/marketing-reports.md` |
| Client proposals (scope, pricing, timeline) | `references/client-proposals.md` |
| Invoices (line items, tax, payment details) | `references/invoices.md` |
| Document proposals (RFP, methodology, team, risk) | `references/document-proposals.md` |
| Fund factsheets / KIID documents | `references/fund-factsheets.md` |
| Editorial/guide documents (themes, logo, chapter graphics) | `references/editorial-documents.md` |
| Markdown → PDF conversion (weasyprint or ReportLab pipeline) | `references/markdown-to-pdf.md` |

When a request spans multiple areas, read references in this order:
1. `references/design-principles.md` (always first)
2. `references/reportlab-fundamentals.md` (if unfamiliar with ReportLab)
3. The domain-specific reference (finance, marketing, proposal, or factsheet)
4. `references/two-column-layouts.md` or `references/charts-and-visualizations.md` as needed

## Ready-to-Run Scripts

This skill includes complete, working scripts in `scripts/`. Use these as starting points — upload to the sandbox, edit the `DATA` dict, and run. **You can also edit or improve the scripts directly** when the DATA dict is not enough (e.g. add sections, change layout, extend themes).

| Script | What it generates | Output path |
|--------|-------------------|-------------|
| `generate_invoice.py` | Professional invoice (Cool Slate palette) — line items, tax, payment details | `/home/user/invoice.pdf` |
| `generate_finance_report.py` | Multi-page finance report (Corporate Navy) — KPIs, revenue chart, expense pie | `/home/user/finance_report.pdf` |
| `generate_proposal.py` | Formal project proposal (Corporate Navy) — methodology, team, timeline, risk, budget | `/home/user/proposal.pdf` |
| `generate_editorial.py` | Themable editorial PDF (12 themes, logo, chapter graphics) — landscape, two-column | `/home/user/editorial.pdf` |
| `pdf_to_images.py` | Convert PDF pages to PNG images for preview/visibility | `/home/user/pdf_preview/` |

### How to use a script

1. Install dependencies:
```python
shell(command="pip install reportlab matplotlib seaborn")
```

2. Upload the script to the sandbox. The script content is available in the skill's `scripts` list — write it to a file:
```python
sandbox_write_file(path="/home/user/generate_invoice.py", content=SCRIPT_CONTENT)
```

3. Run the script:
```python
shell(command="cd /home/user && python generate_invoice.py")
```

4. Download the PDF:
```python
sandbox_download_file(path="/home/user/invoice.pdf")
```

### Customizing script data

Each script has a `DATA` dict at the bottom with sample values. To customize:
- Read the script content from the skill
- Modify the `DATA` dict with the user's actual data (company name, line items, amounts, etc.)
- Write the modified script to the sandbox and run it

If the user needs a report type not covered by existing scripts, use the reference files to build a custom script following the same patterns.

### Editorial PDF with logo and preview

1. **Logo**: Use `nano_banana_image_generation` (model `nano_banana2`) with a prompt like: "Minimal logo for [org name], clean geometric design, white on transparent background, square format." Download the image and write it to the sandbox (e.g. `/home/user/logo.png`).

2. **Generate**: Edit `generate_editorial.py` DATA — set `theme` (e.g. `ocean`, `corporate_navy`, `warm_editorial`), `title`, `subtitle`, `org_name`, `logo_path`. Run in sandbox.

3. **Preview**: Run `pdf_to_images.py /home/user/editorial.pdf -o /home/user/pdf_preview` to convert pages to PNGs. Requires `pdf2image` and poppler (`apt-get install -y poppler-utils` in sandbox). Download the images for full visibility.

## Core Workflow (From Scratch)

When building a custom report (no matching script):

1. Install dependencies:
```python
shell(command="pip install reportlab matplotlib seaborn")
```

2. Write the generation script — read `references/design-principles.md` first, then the domain-specific reference:
```python
python(code=script_content)
```

3. Download the PDF:
```python
sandbox_download_file(path="/home/user/report.pdf")
```

## LinkedIn Document and Carousel Use

Use this skill when a LinkedIn workflow needs a PDF artifact, especially for document posts and PDF-backed carousels.

Recommended routing:
- If the user already has a finished PDF, post it with `linkedin_create_document_post`.
- If the user wants a carousel generated from text, prefer `linkedin_create_carousel_from_text`.
- If the user needs a custom-designed PDF deck first, generate it here, then hand the result to the LinkedIn posting flow.

For the full LinkedIn posting workflow, also read the `linkedin` skill.

## Sandbox Toolkit Reference

| Tool | Use |
|------|-----|
| `shell(command)` | Install reportlab, run shell commands |
| `python(code)` | Execute inline PDF generation code |
| `sandbox_write_file(path, content)` | Write script files to sandbox filesystem |
| `sandbox_download_file(path)` | Download generated PDF to permanent storage |

## Best Practices

1. Always define a color palette with semantic roles before writing any layout code.
2. Use two-column Table layouts for professional documents — never stack everything single-column.
3. Wrap all Table cell content in `Paragraph` with a defined style — never use raw strings.
4. Use separate legend tables for pie charts — never put labels directly on small slices.
5. Follow the 4pt spacing system: 4, 8, 16, 24, 32pt for consistent visual rhythm.
6. Maximum 4 KPI cards per row, maximum 4 series per grouped bar chart.
7. Use **matplotlib + seaborn** for data-heavy charts (bar, line, pie, heatmap, donut). Use ReportLab native drawings only for lightweight inline elements (KPI cards, sparklines, progress bars).
8. Download the PDF with `sandbox_download_file` after generation.

## Troubleshooting

### ReportLab or matplotlib not installed
If you see `ModuleNotFoundError`:
```python
shell(command="pip install reportlab matplotlib seaborn")
```

### Table cell content overflows
Wrap all cell text in `Paragraph` objects with a style that sets `fontSize` and `leading`. Raw strings in tables do not wrap and will overflow the column width.

### Pie chart labels overlap
Never put labels directly on pie slices. Use a separate two-column legend table next to the pie chart (see `references/charts-and-visualizations.md`).

### PDF is blank or has only one page
Ensure `doc.build(elements)` is called with the full `elements` list. Check that `PageBreak()` is used between sections for multi-page reports.
