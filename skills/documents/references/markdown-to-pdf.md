
# Markdown to PDF Conversion

Convert Markdown content to professional PDF documents in the E2B sandbox.

## Approach 1: HTML Pipeline (Quick, CSS-Styled)

Best for: documents where markdown formatting fidelity matters most. Preserves tables, code blocks, and nested lists faithfully.

### Install

```python
shell(command="pip install markdown weasyprint")
```

### Conversion Script

```python
python(code="""
import markdown
from weasyprint import HTML

MD_CONTENT = '''
# Report Title

## Summary

This is a **professional** document converted from Markdown.

### Key Metrics

| Metric | Value | Change |
|--------|-------|--------|
| Revenue | $2.4M | +12% |
| Users | 14,200 | +8% |

### Code Example

```python
def hello():
    print("Hello, World!")
```

> This is a blockquote with important information.
'''

CSS = '''
@page {
    size: A4;
    margin: 2cm 2cm 2.5cm 2cm;
    @bottom-left { content: "Company Name"; font-size: 6pt; color: #94a3b8; }
    @bottom-right { content: "Page " counter(page); font-size: 6pt; color: #94a3b8; }
}
body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 9pt;
    line-height: 1.4;
    color: #334155;
}
h1 {
    font-size: 24pt;
    color: #1e293b;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 8pt;
    margin-bottom: 16pt;
}
h2 {
    font-size: 16pt;
    color: #1e293b;
    margin-top: 32pt;
    margin-bottom: 8pt;
}
h3 {
    font-size: 12pt;
    color: #334155;
    margin-top: 16pt;
    margin-bottom: 4pt;
}
p { margin-bottom: 8pt; }
table {
    width: 100%;
    border-collapse: collapse;
    margin: 16pt 0;
    font-size: 9pt;
}
th {
    background-color: #1e293b;
    color: white;
    font-weight: bold;
    padding: 6pt;
    text-align: left;
}
td {
    padding: 4pt 6pt;
    border-bottom: 0.5pt solid #cbd5e1;
}
tr:nth-child(even) td { background-color: #f8fafc; }
code {
    font-family: Courier, monospace;
    font-size: 8pt;
    background-color: #f1f5f9;
    padding: 1pt 3pt;
    border-radius: 2pt;
}
pre {
    background-color: #f1f5f9;
    border: 0.5pt solid #cbd5e1;
    border-radius: 4pt;
    padding: 8pt 12pt;
    margin: 8pt 0 16pt 0;
    font-size: 8pt;
    line-height: 1.5;
    overflow-x: auto;
}
pre code { background: none; padding: 0; }
blockquote {
    border-left: 3pt solid #3b82f6;
    padding-left: 12pt;
    margin-left: 0;
    color: #64748b;
    font-style: italic;
}
'''

html_body = markdown.markdown(MD_CONTENT, extensions=["tables", "fenced_code"])
full_html = f"<html><head><style>{CSS}</style></head><body>{html_body}</body></html>"

HTML(string=full_html).write_pdf("/home/user/document.pdf")
print("Done: /home/user/document.pdf")
""")
```

## Approach 2: ReportLab Pipeline (Full Control)

Best for: documents where precise typographic control, custom headers/footers, and brand styling are needed. More work but higher quality output.

### Install

```python
shell(command="pip install reportlab markdown")
```

### Style Mapping

Map Markdown elements to the typography scale from the pdf-generation design system:

| Markdown | ReportLab Style | Size | Font |
|----------|----------------|------|------|
| `# H1` | Display | 24pt | Helvetica-Bold |
| `## H2` | Heading | 16pt | Helvetica-Bold |
| `### H3` | Subheading | 12pt | Helvetica-Bold |
| Body text | Body | 9pt | Helvetica |
| `> blockquote` | Body (italic, indented) | 9pt | Helvetica-Oblique |
| `` `code` `` | Code (inline) | 8pt | Courier |
| ```` ```code block``` ```` | Code (block) | 8pt | Courier |
| Footnotes | Caption | 7pt | Helvetica |

### Conversion Script

```python
python(code="""
import re
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Preformatted, KeepTogether,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_JUSTIFY

WIDTH, HEIGHT = A4
MARGIN = 2 * cm
CONTENT_W = WIDTH - 2 * MARGIN

PRIMARY = colors.HexColor("#1e293b")
SECONDARY = colors.HexColor("#334155")
ACCENT = colors.HexColor("#3b82f6")
BODY_TEXT = colors.HexColor("#334155")
MUTED = colors.HexColor("#94a3b8")
BORDER = colors.HexColor("#cbd5e1")
ROW_ALT = colors.HexColor("#f8fafc")
CODE_BG = colors.HexColor("#f1f5f9")

STYLES = {
    "h1": ParagraphStyle("H1", fontSize=24, fontName="Helvetica-Bold", textColor=PRIMARY, leading=30, spaceAfter=16),
    "h2": ParagraphStyle("H2", fontSize=16, fontName="Helvetica-Bold", textColor=PRIMARY, leading=22, spaceBefore=32, spaceAfter=8),
    "h3": ParagraphStyle("H3", fontSize=12, fontName="Helvetica-Bold", textColor=SECONDARY, leading=16, spaceBefore=16, spaceAfter=4),
    "body": ParagraphStyle("Body", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13, alignment=TA_JUSTIFY),
    "bold": ParagraphStyle("Bold", fontSize=9, fontName="Helvetica-Bold", textColor=BODY_TEXT, leading=13),
    "quote": ParagraphStyle("Quote", fontSize=9, fontName="Helvetica-Oblique", textColor=MUTED, leading=13, leftIndent=12, borderPadding=0),
    "code": ParagraphStyle("Code", fontSize=8, fontName="Courier", textColor=SECONDARY, leading=12, backColor=CODE_BG, borderPadding=6),
    "caption": ParagraphStyle("Caption", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10),
}

def md_to_flowables(md_text):
    elements = []
    lines = md_text.strip().split("\\n")
    in_code_block = False
    code_buffer = []
    in_table = False
    table_rows = []

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                code_text = "\\n".join(code_buffer)
                elements.append(Preformatted(code_text, STYLES["code"]))
                elements.append(Spacer(1, 8))
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        # Table rows
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(set(c) <= set("- :") for c in cells):
                continue  # separator row
            if not in_table:
                in_table = True
            table_rows.append(cells)
            continue
        elif in_table:
            # Flush table
            if table_rows:
                elements.append(build_table(table_rows))
                elements.append(Spacer(1, 8))
            table_rows = []
            in_table = False

        # Headings
        if line.startswith("### "):
            elements.append(Paragraph(line[4:], STYLES["h3"]))
        elif line.startswith("## "):
            elements.append(Paragraph(line[3:], STYLES["h2"]))
            elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
        elif line.startswith("# "):
            elements.append(Paragraph(line[2:], STYLES["h1"]))
            elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=16))
        elif line.startswith("> "):
            elements.append(Paragraph(line[2:], STYLES["quote"]))
            elements.append(Spacer(1, 4))
        elif line.strip() == "":
            elements.append(Spacer(1, 4))
        else:
            # Inline formatting
            text = line
            text = re.sub(r"\\*\\*(.+?)\\*\\*", r"<b>\\1</b>", text)
            text = re.sub(r"\\*(.+?)\\*", r"<i>\\1</i>", text)
            text = re.sub(r"`(.+?)`", r'<font face="Courier" size="8">\\1</font>', text)
            elements.append(Paragraph(text, STYLES["body"]))

    if in_table and table_rows:
        elements.append(build_table(table_rows))

    return elements

def build_table(rows):
    col_count = max(len(r) for r in rows)
    col_w = CONTENT_W / col_count
    data = []
    for i, row in enumerate(rows):
        style = STYLES["caption"] if i == 0 else STYLES["body"]
        data.append([Paragraph(cell, style) for cell in row])

    table = Table(data, colWidths=[col_w] * col_count)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table

def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 1.5 * cm, WIDTH - MARGIN, 1.5 * cm)
    canvas.setFont("Helvetica", 6)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(WIDTH - MARGIN, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()

MD_CONTENT = '''# Your Markdown Here'''

doc = SimpleDocTemplate(
    "/home/user/document.pdf", pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=2.5 * cm,
)
elements = md_to_flowables(MD_CONTENT)
doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
print("Done: /home/user/document.pdf")
""")
```

## When to Use Which

| Feature | HTML Pipeline | ReportLab Pipeline |
|---------|--------------|-------------------|
| Setup complexity | Low | Medium |
| Markdown fidelity | High | Medium |
| Custom branding | CSS only | Full control |
| Code blocks | Excellent | Good |
| Tables | Excellent | Good |
| Charts | Not supported | Supported |
| Page headers/footers | CSS `@page` | Canvas callbacks |
| Speed | Fast | Fast |

**Default recommendation**: Use the HTML pipeline for straightforward markdown documents. Switch to ReportLab when you need charts, KPI cards, or precise branded layouts that CSS alone cannot achieve.

## Workflow

1. Install dependencies: `pip install markdown weasyprint` (or `pip install reportlab markdown`)
2. Read or receive the markdown content
3. Run the conversion script
4. Download with `sandbox_download_file(path="/home/user/document.pdf")`
