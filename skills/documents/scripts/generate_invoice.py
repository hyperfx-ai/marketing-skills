"""Generate a professional invoice PDF with line items, tax, and payment details.

Uses the Cool Slate palette. Produces a single-page invoice suitable for
consulting, freelance, or B2B billing. Outputs to /home/user/invoice.pdf.

Usage:
    python generate_invoice.py

Customization:
    Edit the DATA dict at the bottom to change company, client, line items,
    tax rate, discount, and payment details. All amounts are in USD.
"""

from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
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
LEFT_W = CONTENT_W * 0.48
RIGHT_W = CONTENT_W * 0.48
COL_GAP = CONTENT_W * 0.04

# ── Cool Slate palette ───────────────────────────────────────
PRIMARY = colors.HexColor("#1e293b")
SECONDARY = colors.HexColor("#334155")
ACCENT = colors.HexColor("#3b82f6")
SUCCESS = colors.HexColor("#16a34a")
DANGER = colors.HexColor("#dc2626")
BODY_TEXT = colors.HexColor("#334155")
MUTED = colors.HexColor("#94a3b8")
BORDER = colors.HexColor("#cbd5e1")
ROW_ALT = colors.HexColor("#f8fafc")

TINY, SMALL, MEDIUM, LARGE = 4, 8, 16, 24

S = {
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


def _header(elements, company, inv_number, status):
    left = [
        Paragraph(
            f"<b>{company['name']}</b>",
            ParagraphStyle(
                "CN",
                fontSize=16,
                fontName="Helvetica-Bold",
                textColor=PRIMARY,
                leading=22,
            ),
        ),
        Paragraph(
            company.get("tagline", ""),
            ParagraphStyle(
                "Tag", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10
            ),
        ),
    ]
    status_clr = {
        "paid": SUCCESS,
        "unpaid": ACCENT,
        "overdue": DANGER,
        "draft": MUTED,
    }.get(status.lower(), MUTED)
    right = [
        Paragraph(
            "INVOICE",
            ParagraphStyle(
                "IL",
                fontSize=24,
                fontName="Helvetica-Bold",
                textColor=ACCENT,
                leading=30,
                alignment=TA_RIGHT,
            ),
        ),
        Paragraph(
            f"#{inv_number}",
            ParagraphStyle(
                "IN",
                fontSize=12,
                fontName="Helvetica-Bold",
                textColor=PRIMARY,
                leading=16,
                alignment=TA_RIGHT,
            ),
        ),
        Spacer(1, TINY),
        Paragraph(
            f"<b>{status.upper()}</b>",
            ParagraphStyle(
                "St",
                fontSize=9,
                fontName="Helvetica-Bold",
                textColor=status_clr,
                leading=13,
                alignment=TA_RIGHT,
            ),
        ),
    ]
    t = Table([[left, right]], colWidths=[LEFT_W + COL_GAP / 2, RIGHT_W + COL_GAP / 2])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    elements.append(t)
    bar = Drawing(CONTENT_W, 3)
    bar.add(Rect(0, 0, CONTENT_W, 3, fillColor=ACCENT, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, MEDIUM))


def _addresses(elements, company, client, meta):
    a = ParagraphStyle(
        "A", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13
    )
    lbl = ParagraphStyle(
        "L",
        fontSize=7,
        fontName="Helvetica-Bold",
        textColor=MUTED,
        leading=10,
        spaceAfter=2,
    )

    left = [
        Paragraph("FROM", lbl),
        Paragraph(f"<b>{company['name']}</b>", S["body_bold"]),
        Paragraph(company["address"], a),
        Paragraph(company.get("email", ""), a),
        Paragraph(company.get("phone", ""), a),
    ]
    right = [
        Paragraph("BILL TO", lbl),
        Paragraph(f"<b>{client['name']}</b>", S["body_bold"]),
        Paragraph(client["address"], a),
        Paragraph(client.get("email", ""), a),
    ]

    meta_rows = [
        [
            Paragraph(
                f"<b>{k}</b>",
                ParagraphStyle(
                    "ML",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=MUTED,
                    leading=10,
                ),
            ),
            Paragraph(
                v,
                ParagraphStyle(
                    "MV",
                    fontSize=9,
                    fontName="Helvetica",
                    textColor=BODY_TEXT,
                    leading=13,
                    alignment=TA_RIGHT,
                ),
            ),
        ]
        for k, v in meta
    ]
    mt = Table(meta_rows, colWidths=[RIGHT_W * 0.45, RIGHT_W * 0.55])
    mt.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    right += [Spacer(1, SMALL), mt]

    t = Table([[left, right]], colWidths=[LEFT_W, RIGHT_W + COL_GAP])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, LARGE))


def _line_items(elements, items):
    cw = [CONTENT_W * 0.44, CONTENT_W * 0.12, CONTENT_W * 0.20, CONTENT_W * 0.24]
    th = ParagraphStyle(
        "TH", fontSize=8, fontName="Helvetica-Bold", textColor=colors.white, leading=11
    )
    rows = [
        [
            Paragraph("<b>Description</b>", th),
            Paragraph(
                "<b>Qty</b>", ParagraphStyle("TH2", parent=th, alignment=TA_CENTER)
            ),
            Paragraph(
                "<b>Unit Price</b>",
                ParagraphStyle("TH3", parent=th, alignment=TA_RIGHT),
            ),
            Paragraph(
                "<b>Amount</b>", ParagraphStyle("TH4", parent=th, alignment=TA_RIGHT)
            ),
        ]
    ]

    for item in items:
        amt = item["quantity"] * item["unit_price"]
        desc = [Paragraph(item["description"], S["body_bold"])]
        if item.get("details"):
            desc.append(
                Paragraph(
                    item["details"],
                    ParagraphStyle(
                        "D",
                        fontSize=7,
                        fontName="Helvetica",
                        textColor=MUTED,
                        leading=10,
                    ),
                )
            )
        rows.append(
            [
                desc,
                Paragraph(
                    str(item["quantity"]),
                    ParagraphStyle(
                        "Q",
                        fontSize=9,
                        fontName="Helvetica",
                        textColor=BODY_TEXT,
                        leading=13,
                        alignment=TA_CENTER,
                    ),
                ),
                Paragraph(f"${item['unit_price']:,.2f}", S["body_right"]),
                Paragraph(f"${amt:,.2f}", S["body_right"]),
            ]
        )

    t = Table(rows, colWidths=cw)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(t)


def _totals(elements, subtotal, tax_rate=0, discount=0):
    tax = subtotal * tax_rate
    disc = subtotal * discount if discount else 0
    total = subtotal + tax - disc
    tw = CONTENT_W * 0.40
    ow = CONTENT_W * 0.60

    rows = [
        [
            Paragraph("Subtotal", S["body"]),
            Paragraph(f"${subtotal:,.2f}", S["body_right"]),
        ]
    ]
    if tax_rate:
        rows.append(
            [
                Paragraph(f"Tax ({tax_rate * 100:.0f}%)", S["body"]),
                Paragraph(f"${tax:,.2f}", S["body_right"]),
            ]
        )
    if discount:
        rows.append(
            [
                Paragraph(f"Discount ({discount * 100:.0f}%)", S["body"]),
                Paragraph(
                    f"-${disc:,.2f}",
                    ParagraphStyle(
                        "Dc",
                        fontSize=9,
                        fontName="Helvetica",
                        textColor=SUCCESS,
                        leading=13,
                        alignment=TA_RIGHT,
                    ),
                ),
            ]
        )
    rows.append(
        [
            Paragraph(
                "<b>TOTAL DUE</b>",
                ParagraphStyle(
                    "TL",
                    fontSize=12,
                    fontName="Helvetica-Bold",
                    textColor=PRIMARY,
                    leading=16,
                ),
            ),
            Paragraph(
                f"<b>${total:,.2f}</b>",
                ParagraphStyle(
                    "TV",
                    fontSize=12,
                    fontName="Helvetica-Bold",
                    textColor=ACCENT,
                    leading=16,
                    alignment=TA_RIGHT,
                ),
            ),
        ]
    )

    tt = Table(rows, colWidths=[tw * 0.55, tw * 0.45])
    n = len(rows) - 1
    tt.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (0, 0), (-1, n - 1), 0.5, BORDER),
                ("LINEABOVE", (0, n), (-1, n), 2, PRIMARY),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    w = Table([[Paragraph("", S["body"]), tt]], colWidths=[ow, tw])
    w.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    elements.append(Spacer(1, SMALL))
    elements.append(w)


def _payment(elements, info):
    elements.append(Spacer(1, LARGE))
    rows = [
        [
            Paragraph(
                f"<b>{k}</b>",
                ParagraphStyle(
                    "PL",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=SECONDARY,
                    leading=10,
                ),
            ),
            Paragraph(
                v,
                ParagraphStyle(
                    "PV",
                    fontSize=9,
                    fontName="Helvetica",
                    textColor=BODY_TEXT,
                    leading=13,
                ),
            ),
        ]
        for k, v in info.items()
    ]
    pt = Table(rows, colWidths=[CONTENT_W * 0.22, CONTENT_W * 0.38])
    pt.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), ROW_ALT),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    left = [
        Paragraph("Payment Details", S["subheading"]),
        Spacer(1, TINY),
        Paragraph("Please reference the invoice number in your payment.", S["caption"]),
    ]
    t = Table([[left, pt]], colWidths=[LEFT_W * 0.5, CONTENT_W * 0.6 + COL_GAP])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    elements.append(t)


def _notes(elements, notes, terms):
    elements.append(Spacer(1, LARGE))
    elements.append(
        HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=SMALL)
    )
    if notes:
        elements.append(
            Paragraph(
                "<b>Notes</b>",
                ParagraphStyle(
                    "NL",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=SECONDARY,
                    leading=10,
                ),
            )
        )
        elements.append(Paragraph(notes, S["caption"]))
        elements.append(Spacer(1, SMALL))
    if terms:
        elements.append(
            Paragraph(
                "<b>Terms & Conditions</b>",
                ParagraphStyle(
                    "TL",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=SECONDARY,
                    leading=10,
                ),
            )
        )
        elements.append(Paragraph(terms, S["caption"]))
    elements.append(Spacer(1, MEDIUM))
    elements.append(
        Paragraph(
            "Thank you for your business.",
            ParagraphStyle(
                "Thx",
                fontSize=9,
                fontName="Helvetica-Oblique",
                textColor=MUTED,
                leading=13,
                alignment=TA_CENTER,
            ),
        )
    )


def generate_invoice(data: dict, output_path: str = "/home/user/invoice.pdf") -> str:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=2 * cm,
    )
    elements = []

    _header(
        elements, data["company"], data["invoice_number"], data.get("status", "unpaid")
    )
    _addresses(elements, data["company"], data["client"], data["meta"])
    _line_items(elements, data["items"])

    subtotal = sum(i["quantity"] * i["unit_price"] for i in data["items"])
    _totals(elements, subtotal, data.get("tax_rate", 0), data.get("discount", 0))
    _payment(elements, data["payment"])
    _notes(elements, data.get("notes", ""), data.get("terms", ""))

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    print(f"Generated: {output_path}")
    return output_path


# ── Sample data — edit this to generate your invoice ─────────
DATA = {
    "invoice_number": "INV-2025-0042",
    "status": "unpaid",
    "company": {
        "name": "Apex Consulting Group",
        "tagline": "Strategy & Technology Advisory",
        "address": "123 Innovation Drive, Suite 400<br/>San Francisco, CA 94105",
        "email": "billing@apexconsulting.com",
        "phone": "+1 (415) 555-0123",
    },
    "client": {
        "name": "GlobalTech Solutions Ltd.",
        "address": "456 Enterprise Boulevard<br/>London, EC2A 1NT, UK",
        "email": "accounts@globaltech.co.uk",
    },
    "meta": [
        ("Invoice Date", "December 1, 2025"),
        ("Due Date", "December 31, 2025"),
        ("Payment Terms", "Net 30"),
        ("PO Number", "PO-GT-2025-189"),
    ],
    "items": [
        {
            "description": "Strategy Consulting",
            "details": "Discovery phase — 40hrs @ senior rate",
            "quantity": 40,
            "unit_price": 250.00,
        },
        {
            "description": "Technical Architecture Review",
            "details": "Cloud migration assessment",
            "quantity": 1,
            "unit_price": 8500.00,
        },
        {
            "description": "Workshop Facilitation",
            "details": "2-day executive alignment workshop",
            "quantity": 2,
            "unit_price": 3500.00,
        },
        {
            "description": "Project Management",
            "details": "December 2025 — monthly retainer",
            "quantity": 1,
            "unit_price": 4000.00,
        },
    ],
    "tax_rate": 0.20,
    "discount": 0.05,
    "payment": {
        "Bank": "First National Bank",
        "Account Name": "Apex Consulting Group LLC",
        "Account Number": "12345678",
        "Routing": "021000021",
        "SWIFT": "FNBKUS33",
        "Reference": "INV-2025-0042",
    },
    "notes": "Services rendered for December 2025. All amounts in USD.",
    "terms": "Payment due within 30 days. Late payments incur 1.5% monthly interest.",
}

if __name__ == "__main__":
    generate_invoice(DATA)
