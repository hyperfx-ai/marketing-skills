---
name: Finance Reports
description: Use this reference when generating financial reports -- P&L tables, KPI dashboards, revenue trend lines, expense breakdowns. Uses the Corporate Navy palette.
---

Complete finance report structure using the Corporate Navy palette. All patterns follow `design-principles.md`.

## Color Palette — Corporate Navy

```python
from reportlab.lib import colors

PRIMARY = colors.HexColor("#0c2340")
SECONDARY = colors.HexColor("#1a5276")
ACCENT = colors.HexColor("#2980b9")
SUCCESS = colors.HexColor("#1e8449")
DANGER = colors.HexColor("#c0392b")
WARNING = colors.HexColor("#d4ac0d")
BODY_TEXT = colors.HexColor("#2c3e50")
MUTED = colors.HexColor("#7f8c8d")
BORDER = colors.HexColor("#d5d8dc")
ROW_ALT = colors.HexColor("#f2f4f4")
BACKGROUND = colors.HexColor("#fdfefe")
```

## Report Structure

| Page | Content |
|------|---------|
| 1 | Cover page with title, subtitle, date, company name |
| 2 | KPI dashboard (4 cards) + Revenue trend line with summary sidebar |
| 3 | Profit & Loss table with grouped sections |
| 4 | Expense analysis: pie chart + legend table side by side |

## Cover Page

```python
def cover_page(elements, title, subtitle, company, period):
    elements.append(Spacer(1, 120))

    # Accent bar
    d = Drawing(CONTENT_W, 4)
    d.add(Rect(0, 0, CONTENT_W, 4, fillColor=ACCENT, strokeColor=None))
    elements.append(d)
    elements.append(Spacer(1, LARGE))

    elements.append(Paragraph(title, ParagraphStyle(
        "CoverTitle", fontSize=24, fontName="Helvetica-Bold",
        textColor=PRIMARY, leading=30,
    )))
    elements.append(Spacer(1, SMALL))
    elements.append(Paragraph(subtitle, ParagraphStyle(
        "CoverSub", fontSize=12, fontName="Helvetica",
        textColor=MUTED, leading=16,
    )))
    elements.append(Spacer(1, LARGE))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elements.append(Spacer(1, SMALL))
    elements.append(Paragraph(company, ParagraphStyle(
        "CoverCompany", fontSize=9, fontName="Helvetica-Bold",
        textColor=SECONDARY, leading=13,
    )))
    elements.append(Paragraph(period, ParagraphStyle(
        "CoverPeriod", fontSize=9, fontName="Helvetica",
        textColor=MUTED, leading=13,
    )))
    elements.append(PageBreak())
```

## KPI Dashboard (4 Cards)

```python
def kpi_dashboard(elements, metrics):
    """metrics: list of 4 dicts with keys: label, value, delta."""
    elements.append(Paragraph("Key Financial Metrics", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    kpi_gap = 8
    kpi_w = (CONTENT_W - 3 * kpi_gap) / 4
    cards = []
    for m in metrics[:4]:
        card = Table(
            [
                [Paragraph(f"<b>{m['label']}</b>", ParagraphStyle(
                    "KL", fontSize=7, fontName="Helvetica-Bold", textColor=colors.white, leading=10,
                ))],
                [Paragraph(f"<b>{m['value']}</b>", ParagraphStyle(
                    "KV", fontSize=16, fontName="Helvetica-Bold", textColor=PRIMARY, leading=22, alignment=TA_CENTER,
                ))],
                [Paragraph(m["delta"], ParagraphStyle(
                    "KD", fontSize=7, fontName="Helvetica",
                    textColor=SUCCESS if m["delta"].startswith("+") else DANGER, leading=10, alignment=TA_CENTER,
                ))],
            ],
            colWidths=[kpi_w],
        )
        card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), ACCENT),
            ("BACKGROUND", (0, 1), (0, -1), BACKGROUND),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        cards.append(card)

    row = Table([cards], colWidths=[kpi_w + kpi_gap] * 3 + [kpi_w])
    row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(row)
    elements.append(Spacer(1, LARGE))
```

## Revenue Trend + Summary Sidebar (Two-Column)

```python
def revenue_section(elements, monthly_data, summary_data):
    """
    monthly_data: list of (month_index, revenue_value) tuples.
    summary_data: list of (label, value) tuples for sidebar.
    """
    elements.append(Paragraph("Revenue Trend", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    # Line chart in left column
    chart_w = LEFT_W
    d = Drawing(chart_w, 180)
    lp = LinePlot()
    lp.x = 40
    lp.y = 30
    lp.width = chart_w - 60
    lp.height = 130
    lp.data = [monthly_data]
    lp.lines[0].strokeColor = ACCENT
    lp.lines[0].strokeWidth = 2
    lp.lines[0].symbol = makeMarker("Circle")
    lp.lines[0].symbol.size = 3
    lp.lines[0].symbol.fillColor = ACCENT
    lp.xValueAxis.labels.fontSize = 7
    lp.xValueAxis.labels.fillColor = MUTED
    lp.yValueAxis.labels.fontSize = 7
    lp.yValueAxis.labels.fillColor = MUTED
    lp.yValueAxis.gridStrokeColor = colors.HexColor("#f3f4f6")
    lp.yValueAxis.gridStrokeWidth = 0.5
    d.add(lp)

    # Summary table in right column
    summary_rows = [[
        Paragraph("<b>Metric</b>", STYLES["caption"]),
        Paragraph("<b>Value</b>", STYLES["caption"]),
    ]]
    for label, value in summary_data:
        summary_rows.append([
            Paragraph(label, STYLES["body"]),
            Paragraph(f"<b>{value}</b>", STYLES["body_right"]),
        ])
    summary_table = Table(summary_rows, colWidths=[RIGHT_W * 0.55, RIGHT_W * 0.45])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    # Combine
    two_col = Table([[d, [Paragraph("Revenue Summary", STYLES["subheading"]), Spacer(1, 4), summary_table]]],
                    colWidths=[LEFT_W, RIGHT_W])
    two_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(two_col)
```

## Profit & Loss Table

```python
def pnl_table(elements, sections):
    """
    sections: list of dicts:
      {"title": "Revenue", "rows": [("Product Sales", 500000, 450000), ...], "is_total": False}
    """
    elements.append(Paragraph("Profit & Loss Statement", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    col_widths = [CONTENT_W * 0.45, CONTENT_W * 0.22, CONTENT_W * 0.22, CONTENT_W * 0.11]

    all_rows = [[
        Paragraph("<b>Item</b>", STYLES["caption"]),
        Paragraph("<b>Current Period</b>", STYLES["caption"]),
        Paragraph("<b>Prior Period</b>", STYLES["caption"]),
        Paragraph("<b>Change</b>", STYLES["caption"]),
    ]]
    row_styles = []
    row_idx = 1

    for section in sections:
        # Section header row
        all_rows.append([
            Paragraph(f"<b>{section['title']}</b>", ParagraphStyle(
                "PLSec", fontSize=9, fontName="Helvetica-Bold", textColor=PRIMARY, leading=13,
            )),
            Paragraph("", STYLES["body"]),
            Paragraph("", STYLES["body"]),
            Paragraph("", STYLES["body"]),
        ])
        row_styles.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#eaf2f8")))
        row_idx += 1

        for label, current, prior in section["rows"]:
            change = ((current - prior) / prior * 100) if prior else 0
            change_color = SUCCESS if change >= 0 else DANGER
            style = STYLES["body"] if not section.get("is_total") else ParagraphStyle(
                "PLTotal", fontSize=9, fontName="Helvetica-Bold", textColor=PRIMARY, leading=13,
            )
            right_style = STYLES["body_right"] if not section.get("is_total") else ParagraphStyle(
                "PLTotalR", fontSize=9, fontName="Helvetica-Bold", textColor=PRIMARY, leading=13, alignment=TA_RIGHT,
            )
            all_rows.append([
                Paragraph(label, style),
                Paragraph(f"${current:,.0f}", right_style),
                Paragraph(f"${prior:,.0f}", right_style),
                Paragraph(f"{change:+.1f}%", ParagraphStyle(
                    "PLChange", fontSize=9, fontName="Helvetica", textColor=change_color, leading=13, alignment=TA_RIGHT,
                )),
            ])
            if section.get("is_total"):
                row_styles.append(("LINEABOVE", (0, row_idx), (-1, row_idx), 1, PRIMARY))
            row_idx += 1

    table = Table(all_rows, colWidths=col_widths)
    base_style = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    table.setStyle(TableStyle(base_style + row_styles))
    elements.append(table)
```

## Expense Breakdown: Pie + Legend Side by Side

```python
def expense_breakdown(elements, expenses):
    """expenses: list of dicts with keys: name, amount."""
    elements.append(Paragraph("Expense Analysis", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    total = sum(e["amount"] for e in expenses)
    pie_data = [{"name": e["name"], "value": e["amount"] / total * 100} for e in expenses]

    combined = pie_with_legend(pie_data, LEFT_W, RIGHT_W)
    elements.append(combined)
```

## Data Structure Example

```python
data = {
    "title": "Q4 2024 Financial Report",
    "subtitle": "Quarterly Performance Review",
    "company": "Acme Corporation",
    "period": "October – December 2024",
    "kpis": [
        {"label": "Total Revenue", "value": "$2.4M", "delta": "+12.3% YoY"},
        {"label": "Net Income", "value": "$480K", "delta": "+8.7% YoY"},
        {"label": "Gross Margin", "value": "62.4%", "delta": "+2.1pp"},
        {"label": "Operating Cash Flow", "value": "$320K", "delta": "-3.2% QoQ"},
    ],
    "monthly_revenue": [(0, 180), (1, 195), (2, 210), ...],
    "pnl_sections": [
        {"title": "Revenue", "rows": [("Product Sales", 1200000, 1050000), ...], "is_total": False},
        {"title": "Total Revenue", "rows": [("Total", 2400000, 2100000)], "is_total": True},
        ...
    ],
    "expenses": [
        {"name": "Personnel", "amount": 480000},
        {"name": "Marketing", "amount": 240000},
        ...
    ],
}
```
