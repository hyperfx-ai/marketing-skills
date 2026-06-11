---
name: Marketing Reports
description: Use this reference when generating marketing performance reports -- campaign tables, funnel visualizations, channel ROI, lead source breakdowns. Uses the Modern Teal palette.
---

Marketing report patterns using the Modern Teal palette. All patterns follow `design-principles.md`.

## Color Palette — Modern Teal

```python
from reportlab.lib import colors

PRIMARY = colors.HexColor("#0e4d64")
SECONDARY = colors.HexColor("#0d9488")
ACCENT = colors.HexColor("#14b8a6")
SUCCESS = colors.HexColor("#059669")
DANGER = colors.HexColor("#dc2626")
WARNING = colors.HexColor("#f59e0b")
BODY_TEXT = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
BORDER = colors.HexColor("#d1d5db")
ROW_ALT = colors.HexColor("#f0fdfa")
BACKGROUND = colors.HexColor("#f9fafb")
```

## Report Structure

| Page | Content |
|------|---------|
| 1 | Cover page + Executive summary with 4 KPI cards |
| 2 | Campaign performance table + Channel ROI bar chart |
| 3 | Marketing funnel visualization + Conversion trend line |
| 4 | Lead source pie chart + legend table side by side |

## Campaign Performance Table

```python
def campaign_table(elements, campaigns):
    """
    campaigns: list of dicts with keys:
      name, spend, impressions, clicks, conversions, cpa, status
    """
    elements.append(Paragraph("Campaign Performance", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    col_widths = [CONTENT_W * 0.22, CONTENT_W * 0.12, CONTENT_W * 0.14,
                  CONTENT_W * 0.12, CONTENT_W * 0.12, CONTENT_W * 0.12, CONTENT_W * 0.14]

    header = [
        Paragraph("<b>Campaign</b>", STYLES["caption"]),
        Paragraph("<b>Spend</b>", STYLES["caption"]),
        Paragraph("<b>Impressions</b>", STYLES["caption"]),
        Paragraph("<b>Clicks</b>", STYLES["caption"]),
        Paragraph("<b>Conv.</b>", STYLES["caption"]),
        Paragraph("<b>CPA</b>", STYLES["caption"]),
        Paragraph("<b>Status</b>", STYLES["caption"]),
    ]
    rows = [header]

    status_colors = {"Active": SUCCESS, "Paused": WARNING, "Ended": MUTED}
    for c in campaigns:
        status_clr = status_colors.get(c["status"], MUTED)
        rows.append([
            Paragraph(c["name"], STYLES["body"]),
            Paragraph(f"${c['spend']:,.0f}", STYLES["body_right"]),
            Paragraph(f"{c['impressions']:,.0f}", STYLES["body_right"]),
            Paragraph(f"{c['clicks']:,.0f}", STYLES["body_right"]),
            Paragraph(f"{c['conversions']:,.0f}", STYLES["body_right"]),
            Paragraph(f"${c['cpa']:.2f}", STYLES["body_right"]),
            Paragraph(f"<b>{c['status']}</b>", ParagraphStyle(
                "Status", fontSize=9, fontName="Helvetica-Bold",
                textColor=status_clr, leading=13, alignment=TA_CENTER,
            )),
        ])

    table = Table(rows, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 0), (5, -1), "RIGHT"),
        ("ALIGN", (6, 0), (6, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
```

## Marketing Funnel

Graduated horizontal bars showing drop-off at each stage.

```python
def marketing_funnel(elements, stages):
    """
    stages: list of (stage_name, value) tuples, ordered top to bottom.
    E.g. [("Visitors", 50000), ("Leads", 8000), ("MQLs", 3200), ("SQLs", 1200), ("Customers", 480)]
    """
    elements.append(Paragraph("Marketing Funnel", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    max_val = stages[0][1]
    funnel_w = CONTENT_W * 0.7
    bar_h = 28

    d = Drawing(CONTENT_W, len(stages) * (bar_h + 8) + 10)
    teal_shades = [
        colors.HexColor("#0d9488"),
        colors.HexColor("#14b8a6"),
        colors.HexColor("#2dd4bf"),
        colors.HexColor("#5eead4"),
        colors.HexColor("#99f6e4"),
    ]

    for i, (name, val) in enumerate(stages):
        y = d.height - (i + 1) * (bar_h + 8)
        bar_width = (val / max_val) * funnel_w
        x_offset = (funnel_w - bar_width) / 2

        shade = teal_shades[min(i, len(teal_shades) - 1)]
        d.add(Rect(x_offset, y, bar_width, bar_h, fillColor=shade, strokeColor=None, rx=4))

        d.add(String(funnel_w / 2, y + bar_h / 2 - 4, f"{name}: {val:,}",
                      fontSize=9, fontName="Helvetica-Bold", fillColor=PRIMARY, textAnchor="middle"))

        if i > 0:
            prev_val = stages[i - 1][1]
            pct = val / prev_val * 100 if prev_val else 0
            d.add(String(funnel_w + 16, y + bar_h / 2 - 4, f"{pct:.0f}%",
                          fontSize=7, fontName="Helvetica", fillColor=MUTED, textAnchor="start"))

    elements.append(d)
```

## Channel ROI Bar Chart

```python
def channel_roi_chart(elements, channels):
    """channels: list of (channel_name, roi_pct) tuples."""
    elements.append(Paragraph("Channel ROI", STYLES["subheading"]))
    elements.append(Spacer(1, TINY))

    d = Drawing(LEFT_W, 180)
    bc = VerticalBarChart()
    bc.x = 40
    bc.y = 30
    bc.width = LEFT_W - 60
    bc.height = 130
    bc.data = [[c[1] for c in channels]]
    bc.categoryAxis.categoryNames = [c[0] for c in channels]
    bc.categoryAxis.labels.fontSize = 7
    bc.categoryAxis.labels.fillColor = MUTED
    bc.categoryAxis.labels.fontName = "Helvetica"
    bc.valueAxis.labels.fontSize = 7
    bc.valueAxis.labels.fillColor = MUTED
    bc.valueAxis.gridStrokeColor = colors.HexColor("#f3f4f6")
    bc.valueAxis.gridStrokeWidth = 0.5
    bc.bars[0].fillColor = ACCENT
    bc.bars[0].strokeColor = None
    bc.barWidth = 18
    d.add(bc)
    elements.append(d)
```

## Conversion Trend Line

```python
def conversion_trend(elements, monthly_data, chart_w=CONTENT_W):
    """monthly_data: list of (month_idx, conversion_rate) tuples."""
    elements.append(Paragraph("Monthly Conversion Rate", STYLES["subheading"]))
    elements.append(Spacer(1, TINY))

    d = Drawing(chart_w, 160)
    lp = LinePlot()
    lp.x = 40
    lp.y = 30
    lp.width = chart_w - 60
    lp.height = 110
    lp.data = [monthly_data]
    lp.lines[0].strokeColor = SECONDARY
    lp.lines[0].strokeWidth = 2
    lp.lines[0].symbol = makeMarker("Circle")
    lp.lines[0].symbol.size = 3
    lp.lines[0].symbol.fillColor = SECONDARY
    lp.xValueAxis.labels.fontSize = 7
    lp.xValueAxis.labels.fillColor = MUTED
    lp.yValueAxis.labels.fontSize = 7
    lp.yValueAxis.labels.fillColor = MUTED
    lp.yValueAxis.gridStrokeColor = colors.HexColor("#f3f4f6")
    lp.yValueAxis.gridStrokeWidth = 0.5
    d.add(lp)
    elements.append(d)
```

## Lead Source Pie + Legend

```python
def lead_sources(elements, sources):
    """sources: list of dicts with keys: name, count."""
    elements.append(Paragraph("Lead Sources", STYLES["heading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    total = sum(s["count"] for s in sources)
    pie_data = [{"name": s["name"], "value": s["count"] / total * 100} for s in sources]

    # Use pie_with_legend from charts-and-visualizations.md
    combined = pie_with_legend(pie_data, LEFT_W, RIGHT_W)
    elements.append(combined)
```

## Budget Comparison (Grouped Bars, max 2 series)

```python
def budget_vs_actual(elements, categories, budget_vals, actual_vals):
    """Compare budget vs actual spend per category."""
    elements.append(Paragraph("Budget vs Actual", STYLES["subheading"]))
    elements.append(Spacer(1, TINY))

    d = Drawing(CONTENT_W, 180)
    bc = VerticalBarChart()
    bc.x = 40
    bc.y = 30
    bc.width = CONTENT_W - 60
    bc.height = 130
    bc.data = [budget_vals, actual_vals]
    bc.categoryAxis.categoryNames = categories
    bc.categoryAxis.labels.fontSize = 7
    bc.categoryAxis.labels.fillColor = MUTED
    bc.valueAxis.labels.fontSize = 7
    bc.valueAxis.labels.fillColor = MUTED
    bc.valueAxis.gridStrokeColor = colors.HexColor("#f3f4f6")
    bc.valueAxis.gridStrokeWidth = 0.5
    bc.groupSpacing = 10
    bc.barSpacing = 2
    bc.bars[0].fillColor = SECONDARY
    bc.bars[0].strokeColor = None
    bc.bars[1].fillColor = ACCENT
    bc.bars[1].strokeColor = None
    d.add(bc)

    # Legend below chart
    legend = chart_legend([("Budget", SECONDARY), ("Actual", ACCENT)], CONTENT_W)
    elements.append(d)
    elements.append(Spacer(1, TINY))
    elements.append(legend)
```

## Data Structure Example

```python
data = {
    "title": "Q4 2024 Marketing Report",
    "subtitle": "Digital Marketing Performance Review",
    "company": "TechCorp Inc.",
    "period": "October – December 2024",
    "kpis": [
        {"label": "Total Spend", "value": "$124K", "delta": "+8.2% QoQ"},
        {"label": "Total Leads", "value": "3,842", "delta": "+22.1% QoQ"},
        {"label": "Avg. CPA", "value": "$32.28", "delta": "-5.4% QoQ"},
        {"label": "ROAS", "value": "4.2x", "delta": "+0.8x QoQ"},
    ],
    "campaigns": [
        {"name": "Brand Awareness", "spend": 35000, "impressions": 2800000,
         "clicks": 42000, "conversions": 840, "cpa": 41.67, "status": "Active"},
        ...
    ],
    "funnel": [("Visitors", 50000), ("Leads", 8000), ("MQLs", 3200),
               ("SQLs", 1200), ("Customers", 480)],
    "channel_roi": [("SEO", 380), ("PPC", 220), ("Email", 450), ("Social", 180)],
    "lead_sources": [
        {"name": "Organic Search", "count": 1400},
        {"name": "Paid Search", "count": 980},
        ...
    ],
}
```
