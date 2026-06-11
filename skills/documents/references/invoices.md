---
name: Invoices
description: Use this reference when generating professional invoices -- company branding, client details, line items, tax calculations, payment terms, and bank details. Uses the Cool Slate palette for a clean, trustworthy look.
---

Professional invoice patterns using the Cool Slate palette. All patterns follow `design-principles.md`.

## Color Palette — Cool Slate

```python
from reportlab.lib import colors

PRIMARY = colors.HexColor("#1e293b")
SECONDARY = colors.HexColor("#334155")
ACCENT = colors.HexColor("#3b82f6")
SUCCESS = colors.HexColor("#16a34a")
DANGER = colors.HexColor("#dc2626")
BODY_TEXT = colors.HexColor("#334155")
MUTED = colors.HexColor("#94a3b8")
BORDER = colors.HexColor("#cbd5e1")
ROW_ALT = colors.HexColor("#f8fafc")
BACKGROUND = colors.HexColor("#ffffff")
```

## Invoice Structure — Single Page (Preferred)

| Section | Content |
|---------|---------|
| Header | Company logo/name (left), "INVOICE" label + number (right) |
| Addresses | From (company) left, Bill To (client) right — two-column |
| Meta | Invoice date, due date, payment terms, PO number |
| Line Items | Description, quantity, unit price, amount — full-width table |
| Totals | Subtotal, tax, discount, grand total — right-aligned block |
| Payment | Bank details or payment instructions |
| Footer | Notes, terms, thank-you message |

## Header — Company + Invoice Label

```python
def invoice_header(elements, company, invoice_number):
    """Two-column header: company name left, INVOICE label right."""
    left = [
        Paragraph(f"<b>{company['name']}</b>", ParagraphStyle(
            "CompanyName", fontSize=16, fontName="Helvetica-Bold",
            textColor=PRIMARY, leading=22,
        )),
        Paragraph(company.get("tagline", ""), ParagraphStyle(
            "Tagline", fontSize=7, fontName="Helvetica",
            textColor=MUTED, leading=10,
        )),
    ]

    right = [
        Paragraph("INVOICE", ParagraphStyle(
            "InvLabel", fontSize=24, fontName="Helvetica-Bold",
            textColor=ACCENT, leading=30, alignment=TA_RIGHT,
        )),
        Paragraph(f"#{invoice_number}", ParagraphStyle(
            "InvNum", fontSize=12, fontName="Helvetica-Bold",
            textColor=PRIMARY, leading=16, alignment=TA_RIGHT,
        )),
    ]

    header = Table([[left, right]], colWidths=[LEFT_W, RIGHT_W])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header)

    # Accent bar below header
    bar = Drawing(CONTENT_W, 3)
    bar.add(Rect(0, 0, CONTENT_W, 3, fillColor=ACCENT, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, MEDIUM))
```

## Address Block — From / Bill To

```python
def address_block(elements, company, client, invoice_meta):
    """Two-column: company address left, client + meta right."""
    addr_style = ParagraphStyle("Addr", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13)
    label_style = ParagraphStyle("AddrLabel", fontSize=7, fontName="Helvetica-Bold", textColor=MUTED, leading=10)

    left = [
        Paragraph("FROM", label_style),
        Spacer(1, TINY),
        Paragraph(company["name"], ParagraphStyle("CN", fontSize=9, fontName="Helvetica-Bold", textColor=PRIMARY, leading=13)),
        Paragraph(company["address"], addr_style),
        Paragraph(company.get("email", ""), addr_style),
        Paragraph(company.get("phone", ""), addr_style),
    ]

    right = [
        Paragraph("BILL TO", label_style),
        Spacer(1, TINY),
        Paragraph(client["name"], ParagraphStyle("BN", fontSize=9, fontName="Helvetica-Bold", textColor=PRIMARY, leading=13)),
        Paragraph(client["address"], addr_style),
        Paragraph(client.get("email", ""), addr_style),
        Spacer(1, SMALL),
    ]

    # Invoice metadata below the bill-to
    meta_rows = []
    for label, value in invoice_meta:
        meta_rows.append([
            Paragraph(f"<b>{label}</b>", ParagraphStyle("ML", fontSize=7, fontName="Helvetica-Bold", textColor=MUTED, leading=10)),
            Paragraph(value, ParagraphStyle("MV", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13, alignment=TA_RIGHT)),
        ])
    meta_table = Table(meta_rows, colWidths=[RIGHT_W * 0.45, RIGHT_W * 0.55])
    meta_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    right.append(meta_table)

    two_col = Table([[left, right]], colWidths=[LEFT_W, RIGHT_W])
    two_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(two_col)
    elements.append(Spacer(1, LARGE))
```

## Line Items Table

```python
def line_items_table(elements, items):
    """
    items: list of dicts with keys: description, quantity, unit_price.
    Optional keys: details (secondary description text).
    """
    col_widths = [CONTENT_W * 0.45, CONTENT_W * 0.12, CONTENT_W * 0.18, CONTENT_W * 0.25]
    header = [
        Paragraph("<b>Description</b>", STYLES["caption_bold"]),
        Paragraph("<b>Qty</b>", STYLES["caption_bold"]),
        Paragraph("<b>Unit Price</b>", STYLES["caption_bold"]),
        Paragraph("<b>Amount</b>", STYLES["caption_bold"]),
    ]
    rows = [header]

    for item in items:
        amount = item["quantity"] * item["unit_price"]
        desc = Paragraph(item["description"], STYLES["body"])
        if item.get("details"):
            desc = [
                Paragraph(item["description"], STYLES["body_bold"]),
                Paragraph(item["details"], ParagraphStyle(
                    "Detail", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10,
                )),
            ]
        rows.append([
            desc,
            Paragraph(str(item["quantity"]), ParagraphStyle(
                "Qty", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13, alignment=TA_CENTER,
            )),
            Paragraph(f"${item['unit_price']:,.2f}", STYLES["body_right"]),
            Paragraph(f"${amount:,.2f}", STYLES["body_right"]),
        ])

    table = Table(rows, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
```

## Totals Block (Right-Aligned)

```python
def totals_block(elements, subtotal, tax_rate=0, discount=0):
    """Right-aligned totals block beneath the line items table."""
    tax = subtotal * tax_rate
    discount_amt = subtotal * discount if discount else 0
    grand_total = subtotal + tax - discount_amt

    totals_w = CONTENT_W * 0.40
    offset_w = CONTENT_W * 0.60

    rows = [
        [Paragraph("Subtotal", STYLES["body"]), Paragraph(f"${subtotal:,.2f}", STYLES["body_right"])],
    ]
    if tax_rate:
        rows.append([
            Paragraph(f"Tax ({tax_rate * 100:.0f}%)", STYLES["body"]),
            Paragraph(f"${tax:,.2f}", STYLES["body_right"]),
        ])
    if discount:
        rows.append([
            Paragraph(f"Discount ({discount * 100:.0f}%)", STYLES["body"]),
            Paragraph(f"-${discount_amt:,.2f}", ParagraphStyle(
                "Disc", fontSize=9, fontName="Helvetica", textColor=SUCCESS, leading=13, alignment=TA_RIGHT,
            )),
        ])
    rows.append([
        Paragraph("<b>TOTAL DUE</b>", ParagraphStyle(
            "TotalLabel", fontSize=12, fontName="Helvetica-Bold", textColor=PRIMARY, leading=16,
        )),
        Paragraph(f"<b>${grand_total:,.2f}</b>", ParagraphStyle(
            "TotalVal", fontSize=12, fontName="Helvetica-Bold", textColor=ACCENT, leading=16, alignment=TA_RIGHT,
        )),
    ])

    totals_table = Table(rows, colWidths=[totals_w * 0.55, totals_w * 0.45])
    total_row_idx = len(rows) - 1
    totals_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, total_row_idx - 1), 0.5, BORDER),
        ("LINEABOVE", (0, total_row_idx), (-1, total_row_idx), 2, PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    # Wrap in outer table to push right
    wrapper = Table([[Paragraph("", STYLES["body"]), totals_table]], colWidths=[offset_w, totals_w])
    wrapper.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(Spacer(1, SMALL))
    elements.append(wrapper)
```

## Payment Details

```python
def payment_section(elements, payment_info):
    """
    payment_info: dict with keys like bank_name, account_name,
    account_number, sort_code/routing, swift, reference.
    """
    elements.append(Spacer(1, LARGE))

    # Light background card for payment details
    pay_rows = []
    for label, value in payment_info.items():
        pay_rows.append([
            Paragraph(f"<b>{label}</b>", ParagraphStyle(
                "PayL", fontSize=7, fontName="Helvetica-Bold", textColor=SECONDARY, leading=10,
            )),
            Paragraph(value, ParagraphStyle(
                "PayV", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13,
            )),
        ])

    pay_table = Table(pay_rows, colWidths=[CONTENT_W * 0.25, CONTENT_W * 0.40])
    pay_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), ROW_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))

    # Two-column: payment label left, table right
    left = [
        Paragraph("Payment Details", STYLES["subheading"]),
        Spacer(1, TINY),
        Paragraph("Please reference the invoice number in your payment.", STYLES["caption"]),
    ]

    two_col = Table([[left, pay_table]], colWidths=[LEFT_W * 0.55, CONTENT_W * 0.65])
    two_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(two_col)
```

## Invoice Footer / Notes

```python
def invoice_footer_notes(elements, notes, terms):
    """Add notes and terms below the payment section."""
    elements.append(Spacer(1, LARGE))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=SMALL))

    if notes:
        elements.append(Paragraph("<b>Notes</b>", ParagraphStyle(
            "NoteLabel", fontSize=7, fontName="Helvetica-Bold", textColor=SECONDARY, leading=10,
        )))
        elements.append(Paragraph(notes, STYLES["caption"]))
        elements.append(Spacer(1, SMALL))

    if terms:
        elements.append(Paragraph("<b>Terms & Conditions</b>", ParagraphStyle(
            "TermLabel", fontSize=7, fontName="Helvetica-Bold", textColor=SECONDARY, leading=10,
        )))
        elements.append(Paragraph(terms, STYLES["caption"]))

    elements.append(Spacer(1, MEDIUM))
    elements.append(Paragraph("Thank you for your business.", ParagraphStyle(
        "Thanks", fontSize=9, fontName="Helvetica-Oblique", textColor=MUTED, leading=13, alignment=TA_CENTER,
    )))
```

## Status Badge (Paid / Unpaid / Overdue)

```python
def status_badge(status):
    """Returns a colored Paragraph badge for invoice status."""
    status_map = {
        "paid": (SUCCESS, "PAID"),
        "unpaid": (ACCENT, "UNPAID"),
        "overdue": (DANGER, "OVERDUE"),
        "draft": (MUTED, "DRAFT"),
    }
    clr, label = status_map.get(status.lower(), (MUTED, status.upper()))
    return Paragraph(
        f"<b>{label}</b>",
        ParagraphStyle("Badge", fontSize=9, fontName="Helvetica-Bold", textColor=clr, leading=13, alignment=TA_RIGHT),
    )
```

## Data Structure Example

```python
data = {
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
        {"description": "Strategy Consulting", "details": "Discovery phase — 40hrs @ senior rate", "quantity": 40, "unit_price": 250.00},
        {"description": "Technical Architecture Review", "details": "Cloud migration assessment", "quantity": 1, "unit_price": 8500.00},
        {"description": "Workshop Facilitation", "details": "2-day executive alignment workshop", "quantity": 2, "unit_price": 3500.00},
        {"description": "Project Management", "details": "December 2025 — monthly retainer", "quantity": 1, "unit_price": 4000.00},
    ],
    "tax_rate": 0.20,
    "discount": 0,
    "payment": {
        "Bank": "First National Bank",
        "Account Name": "Apex Consulting Group LLC",
        "Account Number": "12345678",
        "Routing": "021000021",
        "SWIFT": "FNBKUS33",
        "Reference": "INV-2025-0042",
    },
    "notes": "Services rendered for the period of December 2025. All amounts in USD.",
    "terms": "Payment is due within 30 days of invoice date. Late payments may incur a 1.5% monthly interest charge.",
}
```

## Complete Invoice Assembly

```python
def generate_invoice(data, output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=2 * cm,
    )
    elements = []

    invoice_header(elements, data["company"], data["invoice_number"])
    address_block(elements, data["company"], data["client"], data["meta"])
    line_items_table(elements, data["items"])

    subtotal = sum(i["quantity"] * i["unit_price"] for i in data["items"])
    totals_block(elements, subtotal, data.get("tax_rate", 0), data.get("discount", 0))

    payment_section(elements, data["payment"])
    invoice_footer_notes(elements, data.get("notes", ""), data.get("terms", ""))

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
```
