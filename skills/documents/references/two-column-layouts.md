---
name: Two-Column Layouts
description: Use this reference when building multi-column page layouts in ReportLab. Covers Table-based layouts (simple, predictable) and Frame-based layouts (advanced, page-aware).
---

Two-column layouts are the default for professional documents. Single-column stacking is for letters and memos, not reports.

## Approach 1: Table-Based Layout (Recommended)

Use a `Table` with two cells per row. Simpler, more predictable, works with `SimpleDocTemplate`.

### Constants

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
CONTENT_W = WIDTH - 2 * MARGIN
COL_GAP = CONTENT_W * 0.05
LEFT_W = CONTENT_W * 0.55
RIGHT_W = CONTENT_W * 0.40
```

### Two-Column Section

```python
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors

def two_col_section(left_flowables, right_flowables):
    """Pack two columns of flowables side by side."""
    left_cell = left_flowables if isinstance(left_flowables, list) else [left_flowables]
    right_cell = right_flowables if isinstance(right_flowables, list) else [right_flowables]

    table = Table(
        [[left_cell, right_cell]],
        colWidths=[LEFT_W, RIGHT_W],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table
```

### Example: Chart + Legend Side by Side

```python
# Build chart in left column
chart_drawing = Drawing(LEFT_W, 180)
# ... add chart to drawing ...

# Build legend table in right column
legend_rows = [
    [Paragraph("<b>Category</b>", STYLES["caption"]),
     Paragraph("<b>Value</b>", STYLES["caption"])],
]
for name, value, clr in legend_data:
    swatch = Drawing(8, 8)
    swatch.add(Rect(0, 0, 8, 8, fillColor=clr, strokeColor=None))
    legend_rows.append([
        [swatch, Paragraph(f"  {name}", STYLES["body"])],
        Paragraph(f"{value:.1f}%", STYLES["body_right"]),
    ])

legend_table = Table(legend_rows, colWidths=[RIGHT_W * 0.65, RIGHT_W * 0.35])
legend_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))

# Combine
elements.append(two_col_section(
    [Paragraph("Revenue by Segment", STYLES["subheading"]), chart_drawing],
    [Paragraph("Breakdown", STYLES["subheading"]), Spacer(1, 4), legend_table],
))
```

### Example: KPI Cards Row

```python
def kpi_card(label, value, delta, card_w, accent_color):
    """A single KPI card as a Table with colored header strip."""
    header_row = [Paragraph(f"<b>{label}</b>", ParagraphStyle(
        "KPILabel", fontSize=7, fontName="Helvetica-Bold",
        textColor=colors.white, leading=10,
    ))]
    value_row = [Paragraph(f"<b>{value}</b>", ParagraphStyle(
        "KPIValue", fontSize=16, fontName="Helvetica-Bold",
        textColor=PRIMARY, leading=22, alignment=TA_CENTER,
    ))]
    delta_row = [Paragraph(delta, ParagraphStyle(
        "KPIDelta", fontSize=7, fontName="Helvetica",
        textColor=MUTED, leading=10, alignment=TA_CENTER,
    ))]

    card = Table(
        [header_row, value_row, delta_row],
        colWidths=[card_w],
    )
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), accent_color),
        ("BACKGROUND", (0, 1), (0, -1), BACKGROUND),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
    ]))
    return card

# Build 4 KPI cards in a row
cards = [kpi_card("Revenue", "$2.4M", "+12.3% YoY", kw, ACCENT) for kw in [...]]
kpi_gap = 8
kpi_w = (CONTENT_W - 3 * kpi_gap) / 4

card_list = [kpi_card(lbl, val, delta, kpi_w, ACCENT) for lbl, val, delta in kpi_data]
kpi_row = Table([card_list], colWidths=[kpi_w] * 4)
kpi_row.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
]))
elements.append(kpi_row)
```

## Approach 2: Frame-Based Layout (Advanced)

Uses `BaseDocTemplate` with `PageTemplate` and multiple `Frame` objects. Useful when content must flow continuously across columns on the same page.

### Setup

```python
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

left_frame = Frame(
    MARGIN, MARGIN + 1 * cm,
    LEFT_W, HEIGHT - 2 * MARGIN - 1 * cm,
    id="left",
    leftPadding=0, rightPadding=8,
    topPadding=0, bottomPadding=0,
)
right_frame = Frame(
    MARGIN + LEFT_W + COL_GAP, MARGIN + 1 * cm,
    RIGHT_W, HEIGHT - 2 * MARGIN - 1 * cm,
    id="right",
    leftPadding=8, rightPadding=0,
    topPadding=0, bottomPadding=0,
)

doc = BaseDocTemplate(
    "/home/user/report.pdf",
    pagesize=A4,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
    topMargin=MARGIN,
    bottomMargin=2.5 * cm,
)

doc.addPageTemplates([
    PageTemplate(id="TwoCol", frames=[left_frame, right_frame], onPage=add_footer),
])
```

### When to Use Which

| Feature | Table-Based | Frame-Based |
|---------|-------------|-------------|
| Complexity | Low | High |
| DocTemplate | SimpleDocTemplate | BaseDocTemplate |
| Column independence | Content per cell | Content flows across frames |
| Per-section control | Each row is independent | All content flows |
| Best for | Most reports | Newsletter-style continuous text |

**Recommendation**: Use Table-based layouts for reports. Frame-based is for rare cases where body text needs to flow across columns like a newspaper.

## Layout Patterns

### 60/40 Split (Default)
```python
LEFT_W = CONTENT_W * 0.55
RIGHT_W = CONTENT_W * 0.40
# 5% implicit gap
```

### 50/50 Split
```python
HALF_W = (CONTENT_W - COL_GAP) / 2
```

### Three Columns
```python
COL3_GAP = 8
COL3_W = (CONTENT_W - 2 * COL3_GAP) / 3
```

### Full Width Fallback
For elements that span both columns (section headers, wide tables):
```python
elements.append(section_header("Financial Overview"))  # Full width
elements.append(two_col_section(left, right))          # Two column
elements.append(Spacer(1, LARGE))
elements.append(wide_table)                            # Full width again
```
