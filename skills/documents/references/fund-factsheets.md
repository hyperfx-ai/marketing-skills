---
name: Fund Factsheets
description: Use this reference when generating fund factsheets, KIID documents, or investment summary sheets. Covers SRRI risk indicators, asset allocation pies, cumulative performance charts, and charges tables. Uses the Cool Slate palette.
---

Fund factsheet and KIID patterns using the Cool Slate palette. All patterns follow `design-principles.md`.

## Color Palette — Cool Slate

```python
from reportlab.lib import colors

PRIMARY = colors.HexColor("#1e293b")
SECONDARY = colors.HexColor("#334155")
ACCENT = colors.HexColor("#3b82f6")
SUCCESS = colors.HexColor("#16a34a")
DANGER = colors.HexColor("#dc2626")
WARNING = colors.HexColor("#eab308")
BODY_TEXT = colors.HexColor("#334155")
MUTED = colors.HexColor("#94a3b8")
BORDER = colors.HexColor("#cbd5e1")
ROW_ALT = colors.HexColor("#f8fafc")
BACKGROUND = colors.HexColor("#ffffff")
```

## Document Structure — Two Pages

| Page | Left Column (55%) | Right Column (40%) |
|------|------|---------|
| 1 | Fund objectives, performance chart | SRRI risk indicator, fund facts table |
| 2 | Charges table, past performance table | Asset allocation pie + legend, contact info |

Fund factsheets are dense, two-column layouts. Use a Table-based two-column approach throughout.

## SRRI Risk Indicator (1–7)

```python
def srri_indicator(risk_level, box_w=None):
    """Renders a 1–7 risk scale with the current level highlighted."""
    total_w = box_w or RIGHT_W
    cell_w = total_w / 7
    row = []
    for i in range(1, 8):
        if i == risk_level:
            bg = ACCENT
            text_clr = colors.white
            font = "Helvetica-Bold"
        elif i < risk_level:
            bg = colors.HexColor("#bfdbfe")
            text_clr = PRIMARY
            font = "Helvetica"
        else:
            bg = colors.HexColor("#f1f5f9")
            text_clr = MUTED
            font = "Helvetica"
        row.append(Paragraph(f"<b>{i}</b>" if i == risk_level else str(i), ParagraphStyle(
            f"SRRI{i}", fontSize=9, fontName=font, textColor=text_clr,
            leading=13, alignment=TA_CENTER,
        )))

    table = Table([row], colWidths=[cell_w] * 7)
    table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
    ] + [
        ("BACKGROUND", (i, 0), (i, 0),
         ACCENT if i + 1 == risk_level else
         colors.HexColor("#bfdbfe") if i + 1 < risk_level else
         colors.HexColor("#f1f5f9"))
        for i in range(7)
    ]))

    return [
        Paragraph("Risk and Reward Profile", STYLES["subheading"]),
        Spacer(1, TINY),
        # Labels
        Table(
            [[Paragraph("Lower risk", STYLES["caption"]),
              Paragraph("Higher risk", ParagraphStyle(
                  "RR", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10, alignment=TA_RIGHT,
              ))]],
            colWidths=[total_w / 2, total_w / 2],
            style=TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]),
        ),
        Spacer(1, 2),
        table,
        Spacer(1, 2),
        Table(
            [[Paragraph("Typically lower rewards", STYLES["caption"]),
              Paragraph("Typically higher rewards", ParagraphStyle(
                  "RR2", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10, alignment=TA_RIGHT,
              ))]],
            colWidths=[total_w / 2, total_w / 2],
            style=TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]),
        ),
    ]
```

## Fund Facts Table

```python
def fund_facts_table(facts, col_w=None):
    """
    facts: list of (label, value) tuples.
    E.g. [("ISIN", "NO0010123456"), ("NAV", "NOK 1,234.56"), ...]
    """
    w = col_w or RIGHT_W
    rows = []
    for label, value in facts:
        rows.append([
            Paragraph(label, ParagraphStyle(
                "FL", fontSize=7, fontName="Helvetica-Bold", textColor=SECONDARY, leading=10,
            )),
            Paragraph(str(value), ParagraphStyle(
                "FV", fontSize=7, fontName="Helvetica", textColor=BODY_TEXT, leading=10, alignment=TA_RIGHT,
            )),
        ])

    table = Table(rows, colWidths=[w * 0.45, w * 0.55])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table
```

## Asset Allocation Pie + Legend

```python
def asset_allocation(elements, assets):
    """assets: list of dicts with keys: name, weight (percentage)."""
    elements.append(Paragraph("Asset Allocation", STYLES["subheading"]))
    elements.append(Spacer(1, TINY))

    pie_data = [{"name": a["name"], "value": a["weight"]} for a in assets]
    combined = pie_with_legend(pie_data, LEFT_W, RIGHT_W)
    elements.append(combined)
```

## Cumulative Performance Chart (Fund vs Index)

```python
def performance_chart(fund_data, index_data, chart_w, chart_h=180):
    """
    fund_data: list of (year_index, cumulative_value) tuples.
    index_data: list of (year_index, cumulative_value) tuples.
    """
    d = Drawing(chart_w, chart_h)
    lp = LinePlot()
    lp.x = 40
    lp.y = 30
    lp.width = chart_w - 60
    lp.height = chart_h - 50
    lp.data = [fund_data, index_data]

    lp.lines[0].strokeColor = ACCENT
    lp.lines[0].strokeWidth = 2
    lp.lines[0].symbol = makeMarker("Circle")
    lp.lines[0].symbol.size = 3
    lp.lines[0].symbol.fillColor = ACCENT

    lp.lines[1].strokeColor = MUTED
    lp.lines[1].strokeWidth = 1.5
    lp.lines[1].symbol = makeMarker("Square")
    lp.lines[1].symbol.size = 2
    lp.lines[1].symbol.fillColor = MUTED

    lp.xValueAxis.labels.fontSize = 7
    lp.xValueAxis.labels.fillColor = MUTED
    lp.yValueAxis.labels.fontSize = 7
    lp.yValueAxis.labels.fillColor = MUTED
    lp.yValueAxis.gridStrokeColor = colors.HexColor("#f3f4f6")
    lp.yValueAxis.gridStrokeWidth = 0.5
    d.add(lp)

    legend = chart_legend([("Fund", ACCENT), ("Index", MUTED)], chart_w)
    return [d, Spacer(1, TINY), legend]
```

## Charges Table

```python
def charges_table(charges, col_w=None):
    """charges: list of (charge_type, value_string) tuples."""
    w = col_w or CONTENT_W
    header = [
        Paragraph("<b>Charge Type</b>", STYLES["caption"]),
        Paragraph("<b>Fee</b>", STYLES["caption"]),
    ]
    rows = [header]
    for charge_type, value in charges:
        rows.append([
            Paragraph(charge_type, STYLES["body"]),
            Paragraph(value, STYLES["body_right"]),
        ])

    table = Table(rows, colWidths=[w * 0.60, w * 0.40])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table
```

## Past Performance Table

```python
def performance_table(years_data, col_w=None):
    """
    years_data: list of dicts with keys: year, fund_return, index_return.
    """
    w = col_w or CONTENT_W
    header = [
        Paragraph("<b>Year</b>", STYLES["caption"]),
        Paragraph("<b>Fund</b>", STYLES["caption"]),
        Paragraph("<b>Index</b>", STYLES["caption"]),
        Paragraph("<b>Diff.</b>", STYLES["caption"]),
    ]
    rows = [header]
    for yr in years_data:
        diff = yr["fund_return"] - yr["index_return"]
        diff_color = SUCCESS if diff >= 0 else DANGER
        rows.append([
            Paragraph(str(yr["year"]), ParagraphStyle(
                "Yr", fontSize=9, fontName="Helvetica-Bold", textColor=SECONDARY, leading=13, alignment=TA_CENTER,
            )),
            Paragraph(f"{yr['fund_return']:+.1f}%", STYLES["body_right"]),
            Paragraph(f"{yr['index_return']:+.1f}%", STYLES["body_right"]),
            Paragraph(f"{diff:+.1f}pp", ParagraphStyle(
                "Diff", fontSize=9, fontName="Helvetica-Bold", textColor=diff_color, leading=13, alignment=TA_RIGHT,
            )),
        ])

    table = Table(rows, colWidths=[w * 0.20, w * 0.25, w * 0.25, w * 0.25])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table
```

## Data Structure — JSON Template

```python
data = {
    "fund_name": "NARF Global Value Fund",
    "subtitle": "Key Investor Information Document",
    "isin": "NO0010123456",
    "nav": "NOK 1,234.56",
    "aum": "NOK 2.8B",
    "inception_date": "2010-03-15",
    "currency": "NOK",
    "benchmark": "MSCI World NTR",
    "srri": 5,
    "objectives": "The fund aims to achieve long-term capital growth by investing...",
    "fund_facts": [
        ("ISIN", "NO0010123456"),
        ("Currency", "NOK"),
        ("AUM", "NOK 2.8B"),
        ("NAV", "NOK 1,234.56"),
        ("Inception", "15 Mar 2010"),
        ("Benchmark", "MSCI World NTR"),
    ],
    "assets": [
        {"name": "Equities", "weight": 62.5},
        {"name": "Fixed Income", "weight": 22.0},
        {"name": "Alternatives", "weight": 8.5},
        {"name": "Cash", "weight": 7.0},
    ],
    "performance": {
        "fund": [(2015, 100), (2016, 108), (2017, 122), (2018, 115), (2019, 138), ...],
        "index": [(2015, 100), (2016, 105), (2017, 118), (2018, 112), (2019, 130), ...],
    },
    "yearly_returns": [
        {"year": 2024, "fund_return": 14.2, "index_return": 12.8},
        {"year": 2023, "fund_return": 18.5, "index_return": 16.2},
        ...
    ],
    "charges": [
        ("Entry charge", "0.00%"),
        ("Exit charge", "0.00%"),
        ("Ongoing charge", "1.45%"),
        ("Performance fee", "10% above benchmark"),
    ],
}
```
