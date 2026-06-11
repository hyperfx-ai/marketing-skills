"""Generate a professional finance report PDF with KPIs, charts, and P&L table.

Uses the Corporate Navy palette. Produces a multi-page finance report with
cover page, KPI dashboard, revenue trend chart, and profit & loss breakdown.
Outputs to /home/user/finance_report.pdf.

Usage:
    python generate_finance_report.py

Customization:
    Edit the DATA dict at the bottom. Supports monthly revenue/expense
    arrays, expense category breakdowns, and P&L line items.
"""

import calendar

from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Page setup ────────────────────────────────────────────────
WIDTH, HEIGHT = A4
MARGIN = 2 * cm
CONTENT_W = WIDTH - 2 * MARGIN
LEFT_W = CONTENT_W * 0.55
RIGHT_W = CONTENT_W * 0.40
COL_GAP = CONTENT_W * 0.05

# ── Corporate Navy palette ───────────────────────────────────
PRIMARY = colors.HexColor("#0c2340")
SECONDARY = colors.HexColor("#1a5276")
ACCENT = colors.HexColor("#2980b9")
SUCCESS = colors.HexColor("#1e8449")
DANGER = colors.HexColor("#c0392b")
BODY_TEXT = colors.HexColor("#2c3e50")
MUTED = colors.HexColor("#7f8c8d")
BORDER = colors.HexColor("#d5d8dc")
ROW_ALT = colors.HexColor("#f2f4f4")

PIE_COLORS = [
    colors.HexColor("#2563eb"),
    colors.HexColor("#0891b2"),
    colors.HexColor("#059669"),
    colors.HexColor("#d97706"),
    colors.HexColor("#dc2626"),
    colors.HexColor("#7c3aed"),
]

TINY, SMALL, MEDIUM, LARGE, SECTION = 4, 8, 16, 24, 32

S = {
    "display": ParagraphStyle(
        "D", fontSize=24, fontName="Helvetica-Bold", textColor=PRIMARY, leading=30
    ),
    "heading": ParagraphStyle(
        "H",
        fontSize=16,
        fontName="Helvetica-Bold",
        textColor=PRIMARY,
        leading=22,
        spaceAfter=8,
    ),
    "subheading": ParagraphStyle(
        "SH",
        fontSize=12,
        fontName="Helvetica-Bold",
        textColor=PRIMARY,
        leading=16,
        spaceAfter=4,
    ),
    "body": ParagraphStyle(
        "B",
        fontSize=9,
        fontName="Helvetica",
        textColor=BODY_TEXT,
        leading=13,
        alignment=TA_JUSTIFY,
    ),
    "body_bold": ParagraphStyle(
        "BB", fontSize=9, fontName="Helvetica-Bold", textColor=BODY_TEXT, leading=13
    ),
    "body_right": ParagraphStyle(
        "BR",
        fontSize=9,
        fontName="Helvetica",
        textColor=BODY_TEXT,
        leading=13,
        alignment=TA_RIGHT,
    ),
    "caption": ParagraphStyle(
        "C", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10
    ),
}


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(WIDTH - MARGIN, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def _kpi_card(label, value, change=None, w=None):
    w = w or (CONTENT_W - 3 * SMALL) / 4
    parts = [
        [
            Paragraph(
                label,
                ParagraphStyle(
                    "KL",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=MUTED,
                    leading=10,
                ),
            )
        ],
        [
            Paragraph(
                f"<b>{value}</b>",
                ParagraphStyle(
                    "KV",
                    fontSize=16,
                    fontName="Helvetica-Bold",
                    textColor=PRIMARY,
                    leading=20,
                ),
            )
        ],
    ]
    if change:
        clr = SUCCESS if change.startswith("+") else DANGER
        parts.append(
            [
                Paragraph(
                    change,
                    ParagraphStyle(
                        "KC",
                        fontSize=8,
                        fontName="Helvetica-Bold",
                        textColor=clr,
                        leading=11,
                    ),
                )
            ]
        )

    card = Table(parts, colWidths=[w - 16])
    card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), ROW_ALT),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return card


def _cover(elements, data):
    elements.append(Spacer(1, 80))
    elements.append(
        Paragraph(
            data["company"].upper(),
            ParagraphStyle(
                "CO",
                fontSize=10,
                fontName="Helvetica-Bold",
                textColor=ACCENT,
                leading=14,
            ),
        )
    )
    elements.append(Spacer(1, MEDIUM))
    bar = Drawing(CONTENT_W, 6)
    bar.add(Rect(0, 0, CONTENT_W, 6, fillColor=PRIMARY, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, LARGE))
    elements.append(Paragraph(data["title"], S["display"]))
    elements.append(Spacer(1, SMALL))
    elements.append(
        Paragraph(
            data["period"],
            ParagraphStyle(
                "P", fontSize=12, fontName="Helvetica", textColor=SECONDARY, leading=16
            ),
        )
    )
    elements.append(Spacer(1, MEDIUM))
    elements.append(HRFlowable(width="30%", thickness=0.5, color=BORDER))
    elements.append(Spacer(1, SMALL))
    elements.append(Paragraph(f"Prepared: {data['date']}", S["caption"]))
    elements.append(PageBreak())


def _kpi_dashboard(elements, kpis):
    elements.append(Paragraph("Financial Highlights", S["heading"]))
    elements.append(
        HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=MEDIUM)
    )
    cards = [_kpi_card(k["label"], k["value"], k.get("change")) for k in kpis[:4]]
    row = Table([cards], colWidths=[(CONTENT_W - 3 * SMALL) / 4] * 4)
    row.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), SMALL),
            ]
        )
    )
    elements.append(row)
    elements.append(Spacer(1, SECTION))


def _revenue_chart(elements, months, revenue, expenses):
    elements.append(Paragraph("Revenue & Expenses Trend", S["heading"]))
    elements.append(
        HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=MEDIUM)
    )

    chart_w = LEFT_W - 20
    chart_h = 160
    d = Drawing(chart_w + 20, chart_h + 30)

    lp = LinePlot()
    lp.x = 30
    lp.y = 20
    lp.width = chart_w - 40
    lp.height = chart_h - 20
    lp.data = [list(enumerate(revenue)), list(enumerate(expenses))]
    lp.lines[0].strokeColor = ACCENT
    lp.lines[0].strokeWidth = 2
    lp.lines[0].symbol = makeMarker("FilledCircle")
    lp.lines[0].symbol.fillColor = ACCENT
    lp.lines[0].symbol.size = 4
    lp.lines[1].strokeColor = DANGER
    lp.lines[1].strokeWidth = 2
    lp.lines[1].symbol = makeMarker("FilledSquare")
    lp.lines[1].symbol.fillColor = DANGER
    lp.lines[1].symbol.size = 4
    lp.xValueAxis.valueSteps = list(range(len(months)))
    lp.xValueAxis.labelTextFormat = (
        lambda x: months[int(x)][:3] if 0 <= int(x) < len(months) else ""
    )
    lp.xValueAxis.labels.fontSize = 6
    lp.yValueAxis.labelTextFormat = lambda x: f"${x / 1000:.0f}k"
    lp.yValueAxis.labels.fontSize = 6
    d.add(lp)

    # Summary sidebar
    total_rev = sum(revenue)
    total_exp = sum(expenses)
    profit = total_rev - total_exp
    margin_pct = (profit / total_rev * 100) if total_rev else 0

    summary_data = [
        ("Total Revenue", f"${total_rev:,.0f}"),
        ("Total Expenses", f"${total_exp:,.0f}"),
        ("Net Profit", f"${profit:,.0f}"),
        ("Profit Margin", f"{margin_pct:.1f}%"),
    ]
    summary_rows = [
        [
            Paragraph(
                f"<b>{label}</b>",
                ParagraphStyle(
                    "SL",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=MUTED,
                    leading=10,
                ),
            ),
            Paragraph(
                value,
                ParagraphStyle(
                    "SV",
                    fontSize=9,
                    fontName="Helvetica-Bold",
                    textColor=PRIMARY,
                    leading=13,
                    alignment=TA_RIGHT,
                ),
            ),
        ]
        for label, value in summary_data
    ]
    st = Table(summary_rows, colWidths=[RIGHT_W * 0.5, RIGHT_W * 0.5])
    st.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), ROW_ALT),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    right = [Paragraph("Summary", S["subheading"]), Spacer(1, TINY), st]

    two_col = Table([[[d], right]], colWidths=[LEFT_W, RIGHT_W + COL_GAP])
    two_col.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    elements.append(two_col)
    elements.append(Spacer(1, SECTION))


def _expense_pie(elements, categories):
    elements.append(Paragraph("Expense Breakdown", S["heading"]))
    elements.append(
        HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=MEDIUM)
    )

    total = sum(c["amount"] for c in categories)
    d = Drawing(LEFT_W - 20, 160)
    pie = Pie()
    pie.x = (LEFT_W - 20) / 2 - 60
    pie.y = 10
    pie.width = 120
    pie.height = 120
    pie.data = [c["amount"] for c in categories]
    pie.labels = None
    for i in range(len(categories)):
        pie.slices[i].fillColor = PIE_COLORS[i % len(PIE_COLORS)]
        pie.slices[i].strokeColor = colors.white
        pie.slices[i].strokeWidth = 1
    d.add(pie)

    legend_rows = [
        [
            Paragraph(
                "<b>Category</b>",
                ParagraphStyle(
                    "LH",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=MUTED,
                    leading=10,
                ),
            ),
            Paragraph(
                "<b>Amount</b>",
                ParagraphStyle(
                    "LH2",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=MUTED,
                    leading=10,
                    alignment=TA_RIGHT,
                ),
            ),
            Paragraph(
                "<b>%</b>",
                ParagraphStyle(
                    "LH3",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=MUTED,
                    leading=10,
                    alignment=TA_RIGHT,
                ),
            ),
        ]
    ]
    for i, c in enumerate(categories):
        pct = c["amount"] / total * 100 if total else 0
        clr = PIE_COLORS[i % len(PIE_COLORS)]
        swatch = Drawing(10, 10)
        swatch.add(Rect(0, 0, 10, 10, fillColor=clr, strokeColor=None))
        legend_rows.append(
            [
                Table(
                    [
                        [
                            swatch,
                            Paragraph(
                                c["name"],
                                ParagraphStyle(
                                    "LN",
                                    fontSize=8,
                                    fontName="Helvetica",
                                    textColor=BODY_TEXT,
                                    leading=11,
                                ),
                            ),
                        ]
                    ],
                    colWidths=[14, RIGHT_W * 0.55],
                ),
                Paragraph(
                    f"${c['amount']:,.0f}",
                    ParagraphStyle(
                        "LA",
                        fontSize=8,
                        fontName="Helvetica",
                        textColor=BODY_TEXT,
                        leading=11,
                        alignment=TA_RIGHT,
                    ),
                ),
                Paragraph(
                    f"{pct:.1f}%",
                    ParagraphStyle(
                        "LP",
                        fontSize=8,
                        fontName="Helvetica",
                        textColor=BODY_TEXT,
                        leading=11,
                        alignment=TA_RIGHT,
                    ),
                ),
            ]
        )

    lt = Table(legend_rows, colWidths=[RIGHT_W * 0.55, RIGHT_W * 0.25, RIGHT_W * 0.20])
    lt.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    two_col = Table(
        [[[d], [Spacer(1, TINY), lt]]], colWidths=[LEFT_W, RIGHT_W + COL_GAP]
    )
    two_col.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    elements.append(two_col)


def generate_finance_report(
    data: dict, output_path: str = "/home/user/finance_report.pdf"
) -> str:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=2 * cm,
    )
    elements = []

    _cover(elements, data)
    _kpi_dashboard(elements, data["kpis"])
    _revenue_chart(elements, data["months"], data["revenue"], data["expenses"])
    elements.append(PageBreak())
    _expense_pie(elements, data["expense_categories"])

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    print(f"Generated: {output_path}")
    return output_path


# ── Sample data — edit this to generate your report ──────────
DATA = {
    "company": "Apex Consulting Group",
    "title": "Financial Performance Report",
    "period": "Q4 2025 — October to December",
    "date": "January 10, 2026",
    "kpis": [
        {"label": "Total Revenue", "value": "$2.4M", "change": "+12.3%"},
        {"label": "Net Profit", "value": "$680K", "change": "+8.7%"},
        {"label": "Operating Margin", "value": "28.3%", "change": "+2.1pp"},
        {"label": "Cash Position", "value": "$1.8M", "change": "+15.2%"},
    ],
    "months": list(calendar.month_name[10:13]),  # Oct, Nov, Dec
    "revenue": [780000, 820000, 850000],
    "expenses": [540000, 570000, 590000],
    "expense_categories": [
        {"name": "Personnel", "amount": 980000},
        {"name": "Technology", "amount": 280000},
        {"name": "Marketing", "amount": 180000},
        {"name": "Facilities", "amount": 120000},
        {"name": "Professional Services", "amount": 95000},
        {"name": "Other", "amount": 45000},
    ],
}

if __name__ == "__main__":
    generate_finance_report(DATA)
