---
name: Charts and Visualizations
description: Use this reference when adding charts to PDFs. Covers matplotlib/seaborn for high-quality charts and native ReportLab graphics for inline drawings. Includes embedding, styling, legends, and axis formatting.
---

## When to Use Which

| Need | Use | Why |
|------|-----|-----|
| Bar, line, pie, heatmap, scatter, donut | **matplotlib + seaborn** | Anti-aliased rendering, rich styling, proper font handling, gradients |
| KPI cards, sparklines, progress bars, inline indicators | **ReportLab Drawing** | Vector precision, no rasterization, lightweight |
| Simple pie/bar in a lightweight report | Either | ReportLab native avoids extra dependency |

Default to matplotlib/seaborn for any data-heavy chart. Use ReportLab native for small decorative drawings.

---

## Matplotlib + Seaborn Charts

### Install in Sandbox

```python
shell(command="pip install reportlab matplotlib seaborn")
```

### Core Embedding Pattern

Render any matplotlib figure to a high-DPI PNG in memory, then embed into ReportLab as an `Image` flowable.

```python
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.platypus import Image

def fig_to_image(fig, width, dpi=200):
    """Convert a matplotlib Figure to a ReportLab Image flowable."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)

    from PIL import Image as PILImage
    img = PILImage.open(buf)
    aspect = img.height / img.width
    buf.seek(0)

    return Image(buf, width=width, height=width * aspect)
```

If PIL is not available, calculate aspect from the figure dimensions instead:

```python
def fig_to_image_nopil(fig, width, dpi=200):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    fig_w, fig_h = fig.get_size_inches()
    aspect = fig_h / fig_w
    return Image(buf, width=width, height=width * aspect)
```

### Theme Setup

Set the seaborn theme once at the top of the script. Derive the palette from the document's color constants.

```python
CHART_PALETTE = ["#1a5276", "#2980b9", "#1e8449", "#d4ac0d", "#c0392b", "#7c3aed", "#be185d"]

sns.set_theme(
    style="whitegrid",
    rc={
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "grid.color": "#f3f4f6",
        "grid.linewidth": 0.5,
        "axes.edgecolor": "#d5d8dc",
        "axes.linewidth": 0.5,
        "font.family": "sans-serif",
        "font.size": 9,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
    },
)
sns.set_palette(CHART_PALETTE)
```

### Palette Bridge

Convert the skill's hex palette constants to matplotlib/seaborn palettes:

```python
from reportlab.lib import colors as rl_colors

PRIMARY = rl_colors.HexColor("#0c2340")
SECONDARY = rl_colors.HexColor("#1a5276")
ACCENT = rl_colors.HexColor("#2980b9")
SUCCESS = rl_colors.HexColor("#1e8449")
DANGER = rl_colors.HexColor("#c0392b")
WARNING = rl_colors.HexColor("#d4ac0d")

CHART_PALETTE = [
    PRIMARY.hexval(), SECONDARY.hexval(), ACCENT.hexval(),
    SUCCESS.hexval(), WARNING.hexval(), DANGER.hexval(),
]
sns.set_palette(CHART_PALETTE)
```

### Sizing Rules

| Target area | Figure size (inches) | DPI | ReportLab width |
|-------------|---------------------|-----|-----------------|
| Full-width chart | `(7, 3.5)` | 200 | `CONTENT_W` |
| Half-width (two-col left) | `(4, 3)` | 200 | `LEFT_W` |
| Half-width (two-col right) | `(3.5, 3)` | 200 | `RIGHT_W` |
| Small inline chart | `(3, 2)` | 200 | 150-200pt |

Always use `dpi=200` for sharp output. Never go below 150.

### Bar Chart

```python
def make_bar_chart(categories, values, title="", palette=None, width=None):
    w = width or CONTENT_W
    fig, ax = plt.subplots(figsize=(7, 3.5))
    colors = palette or CHART_PALETTE
    bars = ax.bar(categories, values, color=colors[:len(categories)], edgecolor="none")
    ax.set_title(title, pad=12)
    ax.set_ylabel("")
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    sns.despine(left=True, bottom=True)
    fig.tight_layout()
    return fig_to_image(fig, w)
```

Usage:

```python
elements.append(Paragraph("Revenue by Quarter", STYLES["subheading"]))
elements.append(Spacer(1, TINY))
elements.append(make_bar_chart(
    ["Q1", "Q2", "Q3", "Q4"],
    [120000, 145000, 138000, 162000],
    title="",
    width=CONTENT_W,
))
```

### Line Chart

```python
def make_line_chart(x, y_series, labels, title="", width=None):
    """y_series: list of y-value lists. labels: series names."""
    w = width or CONTENT_W
    fig, ax = plt.subplots(figsize=(7, 3.5))
    for i, (y, label) in enumerate(zip(y_series, labels)):
        ax.plot(x, y, marker="o", markersize=4, linewidth=2, label=label)
    ax.set_title(title, pad=12)
    ax.legend(frameon=False, fontsize=8)
    ax.yaxis.grid(True)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    sns.despine(left=True, bottom=True)
    fig.tight_layout()
    return fig_to_image(fig, w)
```

### Pie Chart

Use matplotlib's `pie` with a separate `legend` outside the chart. Never put labels on slices.

```python
def make_pie_chart(names, values, title="", width=None):
    w = width or LEFT_W
    fig, ax = plt.subplots(figsize=(4, 3.5))
    wedges, _ = ax.pie(
        values,
        colors=CHART_PALETTE[:len(values)],
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    ax.legend(
        wedges, [f"{n}  ({v/sum(values)*100:.1f}%)" for n, v in zip(names, values)],
        loc="center left", bbox_to_anchor=(1, 0.5),
        frameon=False, fontsize=8,
    )
    ax.set_title(title, pad=12)
    fig.tight_layout()
    return fig_to_image(fig, w)
```

### Donut Chart

```python
def make_donut_chart(names, values, center_label="", title="", width=None):
    w = width or LEFT_W
    fig, ax = plt.subplots(figsize=(4, 3.5))
    wedges, _ = ax.pie(
        values,
        colors=CHART_PALETTE[:len(values)],
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5, "width": 0.4},
    )
    ax.text(0, 0, center_label, ha="center", va="center", fontsize=14, fontweight="bold")
    ax.legend(
        wedges, [f"{n}  ({v/sum(values)*100:.1f}%)" for n, v in zip(names, values)],
        loc="center left", bbox_to_anchor=(1, 0.5),
        frameon=False, fontsize=8,
    )
    ax.set_title(title, pad=12)
    fig.tight_layout()
    return fig_to_image(fig, w)
```

### Heatmap

```python
import numpy as np
import pandas as pd

def make_heatmap(data, row_labels, col_labels, title="", width=None, fmt=".1f"):
    w = width or CONTENT_W
    df = pd.DataFrame(data, index=row_labels, columns=col_labels)
    fig, ax = plt.subplots(figsize=(7, max(3, len(row_labels) * 0.5 + 1)))
    sns.heatmap(
        df, annot=True, fmt=fmt, cmap="YlOrRd",
        linewidths=0.5, linecolor="white",
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )
    ax.set_title(title, pad=12)
    fig.tight_layout()
    return fig_to_image(fig, w)
```

### Horizontal Bar Chart

```python
def make_horizontal_bar(categories, values, title="", width=None):
    w = width or CONTENT_W
    fig, ax = plt.subplots(figsize=(7, max(2.5, len(categories) * 0.4 + 1)))
    y_pos = range(len(categories))
    ax.barh(y_pos, values, color=CHART_PALETTE[0], edgecolor="none", height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories)
    ax.set_title(title, pad=12)
    ax.xaxis.grid(True)
    ax.yaxis.grid(False)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    sns.despine(left=True, bottom=True)
    fig.tight_layout()
    return fig_to_image(fig, w)
```

### Adding Charts to Story

Charts from matplotlib are `Image` flowables. Use them exactly like any other flowable:

```python
elements.append(Paragraph("Revenue Trend", STYLES["subheading"]))
elements.append(Spacer(1, TINY))
elements.append(make_line_chart(
    x=months,
    y_series=[revenue, costs],
    labels=["Revenue", "Costs"],
    width=LEFT_W,
))
elements.append(Spacer(1, MEDIUM))
```

For side-by-side charts, wrap two Image flowables in a Table:

```python
chart_left = make_pie_chart(names, values, width=LEFT_W)
chart_right = make_bar_chart(categories, amounts, width=RIGHT_W)

row = Table([[chart_left, chart_right]], colWidths=[LEFT_W, RIGHT_W])
row.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
]))
elements.append(row)
```

---

## ReportLab Native Charts

Use these for lightweight inline drawings (KPI cards, sparklines, progress bars) where vector precision matters and you want zero extra dependencies.

### Chart Construction Pattern

Every chart follows the same structure:

```python
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib import colors

# 1. Title as Paragraph (NOT String inside Drawing)
elements.append(Paragraph("Chart Title", STYLES["subheading"]))
elements.append(Spacer(1, TINY))

# 2. Drawing container
d = Drawing(chart_width, chart_height)

# 3. Add chart to Drawing
chart = VerticalBarChart()
chart.x = 40
chart.y = 20
chart.width = chart_width - 60
chart.height = chart_height - 40
d.add(chart)

# 4. Add Drawing to story
elements.append(d)
```

### Pie Charts

CRITICAL: Never put labels directly on pie slices. Always use a separate legend table.

#### Pie + Legend Table Pattern

```python
def pie_with_legend(data, chart_w, legend_w):
    """Returns a two-column Table with pie chart left, legend right."""
    names = [d["name"] for d in data]
    values = [d["value"] for d in data]
    pie_colors = [
        colors.HexColor("#2563eb"),
        colors.HexColor("#0891b2"),
        colors.HexColor("#059669"),
        colors.HexColor("#d97706"),
        colors.HexColor("#dc2626"),
        colors.HexColor("#7c3aed"),
        colors.HexColor("#be185d"),
    ]

    # Pie drawing
    d = Drawing(chart_w, 160)
    pie = Pie()
    pie.x = (chart_w - 130) / 2
    pie.y = 10
    pie.width = 130
    pie.height = 130
    pie.data = values
    pie.labels = None  # NO labels on pie
    pie.slices.strokeColor = colors.white
    pie.slices.strokeWidth = 1.5
    for i, clr in enumerate(pie_colors[:len(data)]):
        pie.slices[i].fillColor = clr
    d.add(pie)

    # Legend table
    total = sum(values)
    legend_rows = [
        [Paragraph("<b>Category</b>", STYLES["caption"]),
         Paragraph("<b>Share</b>", STYLES["caption"])],
    ]
    for i, item in enumerate(data):
        swatch = Drawing(8, 8)
        swatch.add(Rect(0, 0, 8, 8, fillColor=pie_colors[i], strokeColor=None))
        pct = item["value"] / total * 100 if total else 0
        legend_rows.append([
            Table([[swatch, Paragraph(item["name"], STYLES["body"])]],
                  colWidths=[14, legend_w - 14 - legend_w * 0.30],
                  style=TableStyle([
                      ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                      ("LEFTPADDING", (0, 0), (-1, -1), 0),
                      ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                  ])),
            Paragraph(f"{pct:.1f}%", STYLES["body_right"]),
        ])

    legend = Table(legend_rows, colWidths=[legend_w * 0.70, legend_w * 0.30])
    legend.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    # Combine side by side
    combined = Table([[d, legend]], colWidths=[chart_w, legend_w])
    combined.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return combined
```

### Vertical Bar Charts

#### Single Series

```python
def bar_chart(data, labels, chart_w, chart_h=180, bar_color=ACCENT):
    d = Drawing(chart_w, chart_h)
    bc = VerticalBarChart()
    bc.x = 40
    bc.y = 30
    bc.width = chart_w - 60
    bc.height = chart_h - 50
    bc.data = [data]
    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.labels.fontSize = 7
    bc.categoryAxis.labels.fontName = "Helvetica"
    bc.categoryAxis.labels.fillColor = MUTED
    bc.valueAxis.labels.fontSize = 7
    bc.valueAxis.labels.fontName = "Helvetica"
    bc.valueAxis.labels.fillColor = MUTED
    bc.valueAxis.valueMin = 0
    bc.valueAxis.gridStrokeColor = colors.HexColor("#f3f4f6")
    bc.valueAxis.gridStrokeWidth = 0.5
    bc.bars[0].fillColor = bar_color
    bc.bars[0].strokeColor = None
    bc.barWidth = min(20, (bc.width / len(data)) * 0.6)
    d.add(bc)
    return d
```

#### Grouped Bars (max 4 series)

```python
def grouped_bar_chart(series_data, labels, series_colors, chart_w, chart_h=180):
    """series_data: list of lists. Max 4 series."""
    assert len(series_data) <= 4, "Max 4 series in grouped bar charts"

    d = Drawing(chart_w, chart_h)
    bc = VerticalBarChart()
    bc.x = 40
    bc.y = 30
    bc.width = chart_w - 60
    bc.height = chart_h - 50
    bc.data = series_data
    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.labels.fontSize = 7
    bc.categoryAxis.labels.fontName = "Helvetica"
    bc.categoryAxis.labels.fillColor = MUTED
    bc.valueAxis.labels.fontSize = 7
    bc.valueAxis.labels.fillColor = MUTED
    bc.valueAxis.gridStrokeColor = colors.HexColor("#f3f4f6")
    bc.valueAxis.gridStrokeWidth = 0.5
    bc.groupSpacing = 8
    bc.barSpacing = 2
    for i, clr in enumerate(series_colors):
        bc.bars[i].fillColor = clr
        bc.bars[i].strokeColor = None
    d.add(bc)
    return d
```

### Line Charts

```python
def line_chart(series_data, x_labels, series_colors, chart_w, chart_h=180):
    """
    series_data: list of lists of (x, y) tuples.
    x_labels: labels for x-axis positions.
    """
    d = Drawing(chart_w, chart_h)
    lp = LinePlot()
    lp.x = 40
    lp.y = 30
    lp.width = chart_w - 60
    lp.height = chart_h - 50
    lp.data = series_data

    for i, clr in enumerate(series_colors):
        lp.lines[i].strokeColor = clr
        lp.lines[i].strokeWidth = 2
        lp.lines[i].symbol = makeMarker("Circle")
        lp.lines[i].symbol.size = 3
        lp.lines[i].symbol.fillColor = clr

    lp.xValueAxis.labels.fontSize = 7
    lp.xValueAxis.labels.fontName = "Helvetica"
    lp.xValueAxis.labels.fillColor = MUTED
    lp.yValueAxis.labels.fontSize = 7
    lp.yValueAxis.labels.fontName = "Helvetica"
    lp.yValueAxis.labels.fillColor = MUTED
    lp.yValueAxis.gridStrokeColor = colors.HexColor("#f3f4f6")
    lp.yValueAxis.gridStrokeWidth = 0.5
    d.add(lp)
    return d
```

### KPI Cards Using Drawing

For quick KPI indicators rendered as a single Drawing:

```python
def kpi_card_drawing(label, value, delta, card_w=110, card_h=70, accent=ACCENT):
    d = Drawing(card_w, card_h)
    # Background
    d.add(Rect(0, 0, card_w, card_h, fillColor=BACKGROUND, strokeColor=BORDER, strokeWidth=0.5))
    # Colored top strip
    d.add(Rect(0, card_h - 14, card_w, 14, fillColor=accent, strokeColor=None))
    # Label in strip
    d.add(String(card_w / 2, card_h - 11, label,
                 fontSize=7, fontName="Helvetica-Bold", fillColor=colors.white, textAnchor="middle"))
    # Value
    d.add(String(card_w / 2, card_h / 2 - 6, value,
                 fontSize=16, fontName="Helvetica-Bold", fillColor=PRIMARY, textAnchor="middle"))
    # Delta
    delta_color = SUCCESS if delta.startswith("+") else DANGER if delta.startswith("-") else MUTED
    d.add(String(card_w / 2, 8, delta,
                 fontSize=7, fontName="Helvetica", fillColor=delta_color, textAnchor="middle"))
    return d
```

### Chart Legends (Inline for Line/Bar)

When a chart has multiple series, add a simple legend row below:

```python
def chart_legend(items, chart_w):
    """items: list of (name, color) tuples."""
    cells = []
    for name, clr in items:
        swatch = Drawing(8, 8)
        swatch.add(Rect(0, 0, 8, 8, fillColor=clr, strokeColor=None))
        cells.append(Table(
            [[swatch, Paragraph(name, STYLES["caption"])]],
            colWidths=[12, None],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]),
        ))
    row = Table([cells], hAlign="CENTER")
    row.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return row
```

---

## Axis Formatting Rules

These apply to both matplotlib and ReportLab charts:

- X-axis labels: small size (7-8pt), muted color.
- Y-axis labels: small size (7-8pt), muted color.
- Grid lines: horizontal only, thin (0.5pt), very light (`#f3f4f6`).
- No vertical grid lines.
- `valueMin` / `ylim` should be 0 for bar charts (don't truncate bars).
- Format large numbers: "$1.2M" not "$1,200,000".

## Drawing / Image Size Guidelines

| Chart Type | matplotlib fig size | ReportLab Drawing | ReportLab width |
|------------|--------------------|--------------------|-----------------|
| Full-width chart | `(7, 3.5)` | `CONTENT_W x 180-220` | `CONTENT_W` |
| Half-width chart (two-col) | `(4, 3)` | `LEFT_W x 150-180` | `LEFT_W` or `RIGHT_W` |
| Pie / donut chart | `(4, 3.5)` | `130-160 x 130-160` | 160-200pt |
| KPI card | N/A | `110-120 x 65-75` | N/A |
| Sparkline | `(3, 1)` | `80-100 x 30-40` | 80-100pt |
