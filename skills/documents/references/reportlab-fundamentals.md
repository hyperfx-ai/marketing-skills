---
name: ReportLab Fundamentals
description: Use this reference for core ReportLab API patterns -- imports, page setup, styles, colors, flowable types, and header/footer callbacks.
---

Core ReportLab patterns for PDF generation in the E2B sandbox.

## Setup

Install in sandbox before use:
```bash
pip install reportlab
```

## Essential Imports

```python
from reportlab.platypus import (
    SimpleDocTemplate, BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, PageBreak,
    HRFlowable, KeepTogether, Image,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.widgets.markers import makeMarker
```

## Page Setup

```python
WIDTH, HEIGHT = A4  # 595.27, 841.89 points
MARGIN = 2 * cm     # 56.69 points
CONTENT_W = WIDTH - 2 * MARGIN  # Usable content width

doc = SimpleDocTemplate(
    "/home/user/report.pdf",
    pagesize=A4,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
    topMargin=MARGIN,
    bottomMargin=2.5 * cm,  # Extra room for footer
)
```

## Style Definitions

Always define all styles upfront as a dict. Never create styles inline.

```python
PRIMARY = colors.HexColor("#0c2340")
SECONDARY = colors.HexColor("#1a5276")
BODY_TEXT = colors.HexColor("#2c3e50")
MUTED = colors.HexColor("#7f8c8d")

STYLES = {
    "display": ParagraphStyle(
        "Display", fontSize=24, fontName="Helvetica-Bold",
        textColor=PRIMARY, leading=30, spaceAfter=16,
    ),
    "heading": ParagraphStyle(
        "Heading", fontSize=16, fontName="Helvetica-Bold",
        textColor=PRIMARY, leading=22, spaceBefore=32, spaceAfter=8,
    ),
    "subheading": ParagraphStyle(
        "Subheading", fontSize=12, fontName="Helvetica-Bold",
        textColor=SECONDARY, leading=16, spaceAfter=4,
    ),
    "body": ParagraphStyle(
        "Body", fontSize=9, fontName="Helvetica",
        textColor=BODY_TEXT, leading=13, alignment=TA_JUSTIFY,
    ),
    "body_right": ParagraphStyle(
        "BodyRight", fontSize=9, fontName="Helvetica",
        textColor=BODY_TEXT, leading=13, alignment=TA_RIGHT,
    ),
    "caption": ParagraphStyle(
        "Caption", fontSize=7, fontName="Helvetica",
        textColor=MUTED, leading=10,
    ),
    "micro": ParagraphStyle(
        "Micro", fontSize=6, fontName="Helvetica",
        textColor=MUTED, leading=8,
    ),
}
```

## Flowable Types

| Flowable | Use |
|----------|-----|
| `Paragraph(text, style)` | Styled text with HTML-like markup (`<b>`, `<br/>`, `<i>`) |
| `Spacer(width, height)` | Vertical spacing between elements |
| `Table(data, colWidths)` | Data tables and layout grids |
| `Drawing(width, height)` | Container for charts and shapes |
| `HRFlowable(width, thickness, color)` | Horizontal rule |
| `PageBreak()` | Force new page |
| `KeepTogether(flowables)` | Prevent page break within a group |
| `Image(path, width, height)` | Embed an image file |

## Table Construction

Always use Paragraph in cells. Never raw strings.

```python
BORDER = colors.HexColor("#d5d8dc")
ROW_ALT = colors.HexColor("#f2f4f4")

header = [
    Paragraph("<b>Name</b>", STYLES["caption"]),
    Paragraph("<b>Revenue</b>", STYLES["caption"]),
    Paragraph("<b>Growth</b>", STYLES["caption"]),
]
rows = [header]
for name, revenue, growth in data:
    rows.append([
        Paragraph(name, STYLES["body"]),
        Paragraph(f"${revenue:,.0f}", STYLES["body_right"]),
        Paragraph(f"{growth:+.1f}%", STYLES["body_right"]),
    ])

table = Table(rows, colWidths=[CONTENT_W * 0.40, CONTENT_W * 0.30, CONTENT_W * 0.25])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
]))
```

## Header & Footer Callbacks

```python
def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d5d8dc"))
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 1.5 * cm, WIDTH - MARGIN, 1.5 * cm)
    canvas.setFont("Helvetica", 6)
    canvas.setFillColor(colors.HexColor("#7f8c8d"))
    canvas.drawString(MARGIN, 1 * cm, "Company Name — Document Title")
    canvas.drawRightString(WIDTH - MARGIN, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()

doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
```

## Section Header Pattern

```python
def section_header(text):
    return KeepTogether([
        Paragraph(text, STYLES["heading"]),
        HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8),
    ])
```

## Color Definition

Always use HexColor. Never use named colors like `colors.blue`.

```python
color = colors.HexColor("#0c2340")
```

For transparency (rare):
```python
color = colors.Color(0.05, 0.14, 0.25, alpha=0.8)
```

## Output

Files are written to the sandbox filesystem. Use absolute paths:
```python
doc = SimpleDocTemplate("/home/user/report.pdf", ...)
```

After generation, download with:
```python
sandbox_download_file(path="/home/user/report.pdf")
```
