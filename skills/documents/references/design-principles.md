---
name: Design Principles
description: Use this reference FIRST before generating any PDF. Defines the opinionated design system -- color palettes, typography scale, spacing, composition rules, and anti-patterns -- that separates professional output from generic AI slop.
---

This reference defines the design system for all PDF generation. Read it before writing any code. Every rule here is non-negotiable.

## Design Thinking

Before coding, understand the context and commit to a design direction:

- **Purpose**: What is this document for? Who reads it? Board members need gravitas and restraint. Marketing teams need energy and data density. Finance needs precision and hierarchy. Clients need clarity and trust.
- **Tone**: Pick and commit to one: corporate/institutional, modern/clean, editorial/magazine, data-dense/dashboard, warm/approachable. Do not mix tones.
- **Differentiation**: What makes this PDF feel intentionally designed? Professional PDFs have a clear visual hierarchy, consistent rhythm, and deliberate use of whitespace. Generic PDFs stack elements top-to-bottom with no spatial relationship between them.

**CRITICAL**: Choose a clear design direction and execute it with discipline. A restrained corporate report and an energetic marketing dashboard are both excellent -- the key is consistency and intention, not decoration.

## Color Palettes

Every PDF must use a defined palette with semantic roles. Pick one of these four or derive a custom one using the same structure.

### Corporate Navy (finance, annual reports, board documents)
```python
PRIMARY = colors.HexColor("#0c2340")    # Headings, headers, rules
SECONDARY = colors.HexColor("#1a5276") # Subheadings, chart primary
ACCENT = colors.HexColor("#2980b9")    # Highlights, links, KPI values
SUCCESS = colors.HexColor("#1e8449")   # Positive values, on-track status
DANGER = colors.HexColor("#c0392b")    # Negative values, alerts
WARNING = colors.HexColor("#d4ac0d")   # At-risk, caution indicators
BODY_TEXT = colors.HexColor("#2c3e50") # Body paragraphs
MUTED = colors.HexColor("#7f8c8d")     # Captions, footnotes, axis labels
BORDER = colors.HexColor("#d5d8dc")    # Table borders, dividers
ROW_ALT = colors.HexColor("#f2f4f4")   # Alternating table rows
BACKGROUND = colors.HexColor("#fdfefe") # Card backgrounds
```

### Modern Teal (marketing, dashboards, product reports)
```python
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

### Warm Amber (proposals, client-facing, creative)
```python
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

### Cool Slate (factsheets, technical, regulatory)
```python
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

### Rules
- NEVER use random or unnamed colors. Every color must come from the palette.
- NEVER use pure black (`#000000`) for text. Use `BODY_TEXT` from the palette.
- NEVER mix warm and cool hues in the same palette unless you have a deliberate reason.
- Build custom palettes from a single brand hue by varying HSL lightness: dark (10-20%) for text, medium (40-55%) for headings, light (90-96%) for backgrounds.
- White space is a color. Use it deliberately.

## Typography Scale

Fixed semantic scale. Do not invent sizes.

| Role | Size | Font | Leading | Use |
|------|------|------|---------|-----|
| Display | 24pt | Helvetica-Bold | 30pt | Cover page titles, hero text |
| Heading | 16pt | Helvetica-Bold | 22pt | Section headings |
| Subheading | 12pt | Helvetica-Bold | 16pt | Subsection headings, card labels |
| Body | 9pt | Helvetica | 13pt | Paragraph text, table cells |
| Caption | 7pt | Helvetica | 10pt | Footnotes, chart sources, axis labels |
| Micro | 6pt | Helvetica | 8pt | Legal text, fine print, page numbers |

### Rules
- Only two font families: `Helvetica-Bold` for headings and labels, `Helvetica` for body and captions.
- Leading (line height) = fontSize * 1.4, never less.
- NEVER use more than 4 distinct font sizes on a single page.
- NEVER use font sizes between the defined steps (no 10pt, no 13pt, no 20pt).

```python
STYLES = {
    "display": ParagraphStyle("Display", fontSize=24, fontName="Helvetica-Bold", textColor=PRIMARY, leading=30, spaceAfter=16),
    "heading": ParagraphStyle("Heading", fontSize=16, fontName="Helvetica-Bold", textColor=PRIMARY, leading=22, spaceAfter=8),
    "subheading": ParagraphStyle("Subheading", fontSize=12, fontName="Helvetica-Bold", textColor=SECONDARY, leading=16, spaceAfter=4),
    "body": ParagraphStyle("Body", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13, alignment=TA_JUSTIFY),
    "caption": ParagraphStyle("Caption", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10),
    "micro": ParagraphStyle("Micro", fontSize=6, fontName="Helvetica", textColor=MUTED, leading=8),
}
```

## Spacing System

4pt base unit. Use only these values.

| Token | Value | Use |
|-------|-------|-----|
| `TINY` | 4pt | Between label and value, within a card |
| `SMALL` | 8pt | Between related elements (heading and body) |
| `MEDIUM` | 16pt | Between sections within a group |
| `LARGE` | 24pt | Between major sections |
| `SECTION` | 32pt | Before a new page-level section |

```python
TINY, SMALL, MEDIUM, LARGE, SECTION = 4, 8, 16, 24, 32

# Usage
elements.append(Spacer(1, SMALL))   # After a heading
elements.append(Spacer(1, LARGE))   # Before next section
```

### Rules
- Use the same spacing value between all instances of the same structural element.
- Section headers always get `SECTION` (32pt) spaceBefore and `SMALL` (8pt) spaceAfter.
- Charts get `MEDIUM` (16pt) above and below.
- NEVER use arbitrary values like `0.8*cm` or `1.2*cm`. Convert to the 4pt system.

## Composition & Layout

### Two-Column Default
Professional documents use two-column layouts. Single-column stacking is for letters and simple memos, not reports.

- Use `Table([[left_content, right_content]], colWidths=[...])` for two-column sections.
- Left column: 55% width. Right column: 40% width. Gap: 5%.
- Charts share horizontal space with legends, summaries, or key metrics.

### KPI Cards
- Maximum 4 cards per row on A4.
- Minimum card width: 90pt.
- Internal padding: at least 8pt on all sides.
- Structure: colored header strip (12pt tall) with label, large value centered below, subtitle/delta at bottom.

### Tables
- ALWAYS wrap cell content in `Paragraph(text, style)`. Never pass raw strings to Table cells.
- Left-align text columns. Right-align numeric columns. Center status/tag columns.
- Header row: PRIMARY background, white text, Helvetica-Bold.
- Alternating row backgrounds using `ROW_ALT`.
- Border: 0.5pt `BORDER` color. Never heavy borders.

### Pie Charts
- NEVER put labels directly on pie slices. Labels overlap on small slices and `\n` renders as literal "n" in ReportLab.
- ALWAYS use a separate legend table next to the pie chart, inside a two-column Table.
- Pie + legend side by side: pie width 40-50%, legend table 50-60%.

### Charts General
- Use **matplotlib + seaborn** for data-heavy charts (bar, line, pie, heatmap). Use ReportLab Drawings only for inline indicators (KPI cards, sparklines).
- Chart titles: use a `Paragraph` above the chart, not a `String()` inside a Drawing.
- Maximum 4 data series in grouped bar charts. More than 4 makes bars unreadably thin.
- Axis labels: use `Caption` style (7pt, muted color).
- Grid lines: very light (`#f3f4f6`) horizontal only. No vertical grid.

#### Palette Conversion for matplotlib/seaborn

Keep chart colors consistent with the document palette by converting hex constants:

```python
import seaborn as sns

CHART_PALETTE = [
    PRIMARY.hexval(), SECONDARY.hexval(), ACCENT.hexval(),
    SUCCESS.hexval(), WARNING.hexval(), DANGER.hexval(),
]
sns.set_palette(CHART_PALETTE)
```

If using raw hex strings instead of ReportLab color objects:

```python
CHART_PALETTE = ["#0c2340", "#1a5276", "#2980b9", "#1e8449", "#d4ac0d", "#c0392b"]
sns.set_palette(CHART_PALETTE)
```

### Header & Footer
- Footer on every page: thin rule line, company name left, page number right, `Micro` style.
- Use `onFirstPage` and `onLaterPages` callbacks on `doc.build()`.

## Anti-Patterns

NEVER do any of these:

1. **Single-column chart stacking** -- full-width charts stacked vertically with no spatial relationships. Use two-column layouts to pair charts with legends or summaries.
2. **Pie slice labels with `\n`** -- `pie.labels = [f"{name}\n{pct}%"]` renders the newline as literal "n". Use a separate legend table.
3. **Manual String() for chart titles** -- `d.add(String(x, y, "Title"))` with hardcoded coordinates drifts off-center. Use `Paragraph("Title", heading_style)` above the Drawing.
4. **Hardcoded Drawing dimensions** -- `Drawing(WIDTH - 4*cm, 230)` regardless of content. Size Drawings to fit their content, not the page width.
5. **6+ KPI cards in a row** -- at 6 cards the values are unreadable. Maximum 4.
6. **5+ bar series in grouped charts** -- bars become 6-8pt wide and indistinguishable. Maximum 4 series.
7. **Raw strings in Table cells** -- `rows.append(["text", "123"])` uses default font. Always use `Paragraph("text", style)`.
8. **Random Spacer values** -- `Spacer(1, 0.7*cm)` has no relationship to other spacing. Use the 4pt system.
9. **Misleading axis labels** -- cumulative index values (350) formatted as "350%" looks like 350 percent. Label axes accurately.
10. **Tables wider than content width** -- column widths that sum to more than `WIDTH - leftMargin - rightMargin` cause overflow. Always calculate from `CONTENT_W = WIDTH - 2 * MARGIN`.
