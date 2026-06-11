---
name: Client Proposals
description: Use this reference when generating client-facing proposals -- cover pages, executive summaries, scope tables, pricing, deliverable timelines. Uses the Warm Amber palette.
---

Client proposal patterns using the Warm Amber palette. All patterns follow `design-principles.md`.

## Color Palette — Warm Amber

```python
from reportlab.lib import colors

PRIMARY = colors.HexColor("#78350f")
SECONDARY = colors.HexColor("#b45309")
ACCENT = colors.HexColor("#d97706")
SUCCESS = colors.HexColor("#15803d")
DANGER = colors.HexColor("#b91c1c")
WARNING = colors.HexColor("#ca8a04")
BODY_TEXT = colors.HexColor("#292524")
MUTED = colors.HexColor("#78716c")
BORDER = colors.HexColor("#d6d3d1")
ROW_ALT = colors.HexColor("#fffbeb")
BACKGROUND = colors.HexColor("#fafaf9")
```

## Report Structure

| Page | Content |
|------|---------|
| 1 | Cover page with client name, proposal title, company branding |
| 2 | Executive summary with key metrics sidebar |
| 3 | Scope of work table + deliverables timeline |
| 4 | Pricing table with subtotals and total row + terms |

## Cover Page

```python
def proposal_cover(elements, client_name, proposal_title, company_name, date, ref_number):
    elements.append(Spacer(1, 80))

    # Company name at top
    elements.append(Paragraph(company_name.upper(), ParagraphStyle(
        "Company", fontSize=12, fontName="Helvetica-Bold",
        textColor=ACCENT, leading=16, spaceAfter=4, tracking=200,
    )))

    # Warm accent bar
    d = Drawing(CONTENT_W, 6)
    d.add(Rect(0, 0, CONTENT_W * 0.3, 6, fillColor=ACCENT, strokeColor=None))
    d.add(Rect(CONTENT_W * 0.3, 0, CONTENT_W * 0.7, 6, fillColor=PRIMARY, strokeColor=None))
    elements.append(d)
    elements.append(Spacer(1, LARGE))

    # Proposal title
    elements.append(Paragraph(proposal_title, ParagraphStyle(
        "Title", fontSize=24, fontName="Helvetica-Bold",
        textColor=PRIMARY, leading=30, spaceAfter=8,
    )))

    # "Prepared for"
    elements.append(Spacer(1, MEDIUM))
    elements.append(Paragraph("Prepared for", ParagraphStyle(
        "Prep", fontSize=9, fontName="Helvetica", textColor=MUTED, leading=13,
    )))
    elements.append(Paragraph(client_name, ParagraphStyle(
        "Client", fontSize=16, fontName="Helvetica-Bold",
        textColor=SECONDARY, leading=22, spaceAfter=16,
    )))

    # Metadata
    elements.append(HRFlowable(width="40%", thickness=0.5, color=BORDER))
    elements.append(Spacer(1, SMALL))
    meta_style = ParagraphStyle("Meta", fontSize=9, fontName="Helvetica", textColor=MUTED, leading=13)
    elements.append(Paragraph(f"Date: {date}", meta_style))
    elements.append(Paragraph(f"Reference: {ref_number}", meta_style))
    elements.append(PageBreak())
```

## Executive Summary + Metrics Sidebar

```python
def executive_summary(elements, summary_text, key_metrics):
    """
    summary_text: string with the executive summary.
    key_metrics: list of (label, value) tuples for sidebar.
    """
    elements.append(Paragraph("Executive Summary", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    # Left: summary text
    left = [Paragraph(summary_text, STYLES["body"])]

    # Right: metrics card
    metric_rows = []
    for label, value in key_metrics:
        metric_rows.append([
            Paragraph(label, ParagraphStyle(
                "ML", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10,
            )),
            Paragraph(f"<b>{value}</b>", ParagraphStyle(
                "MV", fontSize=12, fontName="Helvetica-Bold", textColor=PRIMARY, leading=16,
            )),
        ])

    metric_table = Table(metric_rows, colWidths=[RIGHT_W * 0.45, RIGHT_W * 0.55])
    metric_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), BACKGROUND),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))

    right = [
        Paragraph("Key Metrics", STYLES["subheading"]),
        Spacer(1, TINY),
        metric_table,
    ]

    two_col = Table([[left, right]], colWidths=[LEFT_W, RIGHT_W])
    two_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(two_col)
```

## Scope of Work Table

```python
def scope_table(elements, items):
    """items: list of dicts with keys: phase, description, duration, deliverables."""
    elements.append(Paragraph("Scope of Work", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    col_widths = [CONTENT_W * 0.15, CONTENT_W * 0.40, CONTENT_W * 0.15, CONTENT_W * 0.30]
    header = [
        Paragraph("<b>Phase</b>", STYLES["caption"]),
        Paragraph("<b>Description</b>", STYLES["caption"]),
        Paragraph("<b>Duration</b>", STYLES["caption"]),
        Paragraph("<b>Deliverables</b>", STYLES["caption"]),
    ]
    rows = [header]
    for item in items:
        rows.append([
            Paragraph(item["phase"], ParagraphStyle(
                "Phase", fontSize=9, fontName="Helvetica-Bold", textColor=SECONDARY, leading=13,
            )),
            Paragraph(item["description"], STYLES["body"]),
            Paragraph(item["duration"], ParagraphStyle(
                "Dur", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13, alignment=TA_CENTER,
            )),
            Paragraph(item["deliverables"], STYLES["body"]),
        ])

    table = Table(rows, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (2, 0), (2, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
```

## Pricing Table

```python
def pricing_table(elements, line_items, tax_rate=0):
    """
    line_items: list of dicts with keys: description, quantity, unit_price.
    """
    elements.append(Paragraph("Investment", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    col_widths = [CONTENT_W * 0.45, CONTENT_W * 0.15, CONTENT_W * 0.18, CONTENT_W * 0.22]
    header = [
        Paragraph("<b>Description</b>", STYLES["caption"]),
        Paragraph("<b>Qty</b>", STYLES["caption"]),
        Paragraph("<b>Unit Price</b>", STYLES["caption"]),
        Paragraph("<b>Total</b>", STYLES["caption"]),
    ]
    rows = [header]

    subtotal = 0
    for item in line_items:
        total = item["quantity"] * item["unit_price"]
        subtotal += total
        rows.append([
            Paragraph(item["description"], STYLES["body"]),
            Paragraph(str(item["quantity"]), ParagraphStyle(
                "Qty", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13, alignment=TA_CENTER,
            )),
            Paragraph(f"${item['unit_price']:,.2f}", STYLES["body_right"]),
            Paragraph(f"${total:,.2f}", STYLES["body_right"]),
        ])

    # Subtotal row
    bold_right = ParagraphStyle(
        "BR", fontSize=9, fontName="Helvetica-Bold", textColor=PRIMARY, leading=13, alignment=TA_RIGHT,
    )
    rows.append([
        Paragraph("", STYLES["body"]),
        Paragraph("", STYLES["body"]),
        Paragraph("<b>Subtotal</b>", bold_right),
        Paragraph(f"<b>${subtotal:,.2f}</b>", bold_right),
    ])

    if tax_rate:
        tax = subtotal * tax_rate
        rows.append([
            Paragraph("", STYLES["body"]),
            Paragraph("", STYLES["body"]),
            Paragraph(f"<b>Tax ({tax_rate*100:.0f}%)</b>", bold_right),
            Paragraph(f"<b>${tax:,.2f}</b>", bold_right),
        ])
        grand_total = subtotal + tax
    else:
        grand_total = subtotal

    rows.append([
        Paragraph("", STYLES["body"]),
        Paragraph("", STYLES["body"]),
        Paragraph("<b>TOTAL</b>", ParagraphStyle(
            "TotalLabel", fontSize=12, fontName="Helvetica-Bold", textColor=PRIMARY, leading=16, alignment=TA_RIGHT,
        )),
        Paragraph(f"<b>${grand_total:,.2f}</b>", ParagraphStyle(
            "TotalVal", fontSize=12, fontName="Helvetica-Bold", textColor=ACCENT, leading=16, alignment=TA_RIGHT,
        )),
    ])

    table = Table(rows, colWidths=col_widths)
    total_row_idx = len(rows) - 1
    subtotal_row_idx = total_row_idx - (2 if tax_rate else 1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, subtotal_row_idx - 1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, subtotal_row_idx - 1), [colors.white, ROW_ALT]),
        ("LINEABOVE", (2, subtotal_row_idx), (-1, subtotal_row_idx), 1, BORDER),
        ("LINEABOVE", (2, total_row_idx), (-1, total_row_idx), 2, PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
```

## Terms & Conditions

```python
def terms_section(elements, terms):
    """terms: list of strings."""
    elements.append(Spacer(1, LARGE))
    elements.append(Paragraph("Terms & Conditions", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    for i, term in enumerate(terms, 1):
        elements.append(Paragraph(f"{i}. {term}", STYLES["body"]))
        elements.append(Spacer(1, TINY))
```

## Data Structure Example

```python
data = {
    "client_name": "GlobalTech Solutions",
    "proposal_title": "Digital Transformation\nConsulting Engagement",
    "company_name": "Apex Consulting Group",
    "date": "December 15, 2024",
    "ref_number": "PRO-2024-0847",
    "summary": "We propose a comprehensive digital transformation...",
    "key_metrics": [
        ("Timeline", "12 weeks"),
        ("Team Size", "6 specialists"),
        ("ROI Target", "340%"),
        ("Risk Level", "Low"),
    ],
    "scope": [
        {"phase": "Discovery", "description": "Requirements gathering and stakeholder interviews",
         "duration": "2 weeks", "deliverables": "Requirements doc, Stakeholder map"},
        {"phase": "Design", "description": "Solution architecture and technical design",
         "duration": "3 weeks", "deliverables": "Architecture doc, Wireframes"},
        {"phase": "Build", "description": "Implementation and development",
         "duration": "5 weeks", "deliverables": "Working system, Test results"},
        {"phase": "Launch", "description": "Deployment, training, and handover",
         "duration": "2 weeks", "deliverables": "Deployed system, Training materials"},
    ],
    "pricing": [
        {"description": "Discovery & Strategy Phase", "quantity": 1, "unit_price": 15000},
        {"description": "UX/UI Design", "quantity": 1, "unit_price": 22000},
        {"description": "Development (per sprint)", "quantity": 5, "unit_price": 18000},
        {"description": "Testing & QA", "quantity": 1, "unit_price": 12000},
        {"description": "Deployment & Training", "quantity": 1, "unit_price": 8000},
    ],
    "terms": [
        "Payment terms: 50% upon signing, 25% at mid-point, 25% upon delivery.",
        "This proposal is valid for 30 days from the date of issue.",
        "All prices are exclusive of applicable taxes.",
        "Changes to scope will be handled via a change request process.",
    ],
}
```
