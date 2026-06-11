"""Generate a formal project proposal PDF with methodology, team, timeline, and budget.

Uses the Corporate Navy palette. Produces a multi-page RFP response or project
bid with cover page, executive summary, numbered methodology phases, team bios,
Gantt timeline, risk matrix, case studies, and budget sign-off.
Outputs to /home/user/proposal.pdf.

Usage:
    python generate_proposal.py

Customization:
    Edit the DATA dict at the bottom. Supports arbitrary phases, team members,
    risks, case studies, and budget line items.
"""

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
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
SUCCESS = colors.HexColor("#27ae60")
WARNING = colors.HexColor("#f39c12")
DANGER = colors.HexColor("#c0392b")
BODY_TEXT = colors.HexColor("#2c3e50")
MUTED = colors.HexColor("#7f8c8d")
BORDER = colors.HexColor("#bdc3c7")
ROW_ALT = colors.HexColor("#f0f4f8")
LIGHT_ACCENT = colors.HexColor("#ebf5fb")

TINY, SMALL, MEDIUM, LARGE, SECTION = 4, 8, 16, 24, 32

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
    canvas.drawString(MARGIN, 1.2 * cm, "CONFIDENTIAL")
    canvas.drawRightString(WIDTH - MARGIN, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def _bar(elements, w=None, h=3, clr=None):
    w = w or CONTENT_W
    clr = clr or PRIMARY
    d = Drawing(w, h)
    d.add(Rect(0, 0, w, h, fillColor=clr, strokeColor=None))
    elements.append(d)


def _cover(elements, d):
    elements.append(Spacer(1, 60))
    elements.append(
        Paragraph(
            d["org"].upper(),
            ParagraphStyle(
                "O",
                fontSize=10,
                fontName="Helvetica-Bold",
                textColor=ACCENT,
                leading=14,
            ),
        )
    )
    elements.append(Spacer(1, MEDIUM))
    _bar(elements, h=8)
    elements.append(Spacer(1, LARGE))
    elements.append(
        Paragraph(
            d["title"],
            ParagraphStyle(
                "T",
                fontSize=28,
                fontName="Helvetica-Bold",
                textColor=PRIMARY,
                leading=34,
                spaceAfter=8,
            ),
        )
    )
    if d.get("subtitle"):
        elements.append(
            Paragraph(
                d["subtitle"],
                ParagraphStyle(
                    "ST",
                    fontSize=14,
                    fontName="Helvetica",
                    textColor=SECONDARY,
                    leading=18,
                    spaceAfter=16,
                ),
            )
        )
    _bar(elements, w=CONTENT_W * 0.4, clr=ACCENT)
    elements.append(Spacer(1, LARGE))
    m = ParagraphStyle(
        "M", fontSize=9, fontName="Helvetica", textColor=MUTED, leading=13
    )
    b = ParagraphStyle(
        "MB", fontSize=12, fontName="Helvetica-Bold", textColor=PRIMARY, leading=16
    )
    elements.append(Paragraph("Prepared for", m))
    elements.append(Paragraph(d["client"], b))
    elements.append(Spacer(1, MEDIUM))
    elements.append(Paragraph("Submitted by", m))
    elements.append(Paragraph(d["org"], b))
    elements.append(Spacer(1, SMALL))
    elements.append(Paragraph(f"Date: {d['date']}  |  Ref: {d['ref']}", m))
    elements.append(Spacer(1, LARGE))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elements.append(Spacer(1, SMALL))
    elements.append(
        Paragraph(
            "CONFIDENTIAL — Proprietary information for named recipient only.",
            ParagraphStyle(
                "CF",
                fontSize=7,
                fontName="Helvetica-Oblique",
                textColor=DANGER,
                leading=10,
            ),
        )
    )
    elements.append(PageBreak())


def _exec_summary(elements, paras, snapshot):
    elements.append(Paragraph("1. Executive Summary", S["heading"]))
    _bar(elements)
    elements.append(Spacer(1, MEDIUM))
    left = []
    for p in paras:
        left += [Paragraph(p, S["body"]), Spacer(1, SMALL)]
    snap_rows = [
        [
            Paragraph(
                "<b>PROJECT SNAPSHOT</b>",
                ParagraphStyle(
                    "SH2",
                    fontSize=7,
                    fontName="Helvetica-Bold",
                    textColor=colors.white,
                    leading=10,
                ),
            ),
            Paragraph("", S["body"]),
        ]
    ]
    for label, val in snapshot:
        snap_rows.append(
            [
                Paragraph(
                    label,
                    ParagraphStyle(
                        "SL",
                        fontSize=7,
                        fontName="Helvetica-Bold",
                        textColor=MUTED,
                        leading=10,
                    ),
                ),
                Paragraph(
                    f"<b>{val}</b>",
                    ParagraphStyle(
                        "SV",
                        fontSize=10,
                        fontName="Helvetica-Bold",
                        textColor=PRIMARY,
                        leading=14,
                    ),
                ),
            ]
        )
    st = Table(snap_rows, colWidths=[RIGHT_W * 0.45, RIGHT_W * 0.55])
    st.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("BACKGROUND", (0, 1), (-1, -1), LIGHT_ACCENT),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    t = Table([[left, [st]]], colWidths=[LEFT_W, RIGHT_W + COL_GAP])
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
    elements.append(Spacer(1, SECTION))


def _methodology(elements, phases):
    elements.append(Paragraph("2. Methodology", S["heading"]))
    _bar(elements)
    elements.append(Spacer(1, MEDIUM))
    for i, ph in enumerate(phases, 1):
        badge = Paragraph(
            f"<b>{i}</b>",
            ParagraphStyle(
                "BG",
                fontSize=12,
                fontName="Helvetica-Bold",
                textColor=colors.white,
                leading=16,
                alignment=TA_CENTER,
            ),
        )
        bc = Table([[badge]], colWidths=[28], rowHeights=[28])
        bc.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), ACCENT),
                    ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ]
            )
        )
        nm = Paragraph(
            f"<b>{ph['name']}</b>",
            ParagraphStyle(
                "PN",
                fontSize=12,
                fontName="Helvetica-Bold",
                textColor=PRIMARY,
                leading=16,
            ),
        )
        dr = Paragraph(
            ph["duration"],
            ParagraphStyle(
                "PD",
                fontSize=9,
                fontName="Helvetica",
                textColor=ACCENT,
                leading=13,
                alignment=TA_RIGHT,
            ),
        )
        hr = Table([[bc, nm, dr]], colWidths=[36, CONTENT_W - 120, 84])
        hr.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        elements.append(hr)
        elements.append(Spacer(1, TINY))
        elements.append(Paragraph(ph["description"], S["body"]))
        elements.append(Spacer(1, TINY))
        for act in ph.get("activities", []):
            elements.append(
                Paragraph(
                    f"\u2022 {act}",
                    ParagraphStyle(
                        "AC",
                        fontSize=8,
                        fontName="Helvetica",
                        textColor=BODY_TEXT,
                        leading=12,
                        leftIndent=16,
                        spaceAfter=2,
                    ),
                )
            )
        elements.append(Spacer(1, MEDIUM))


def _team(elements, members):
    elements.append(PageBreak())
    elements.append(Paragraph("3. Team", S["heading"]))
    _bar(elements)
    elements.append(Spacer(1, MEDIUM))
    cw = LEFT_W - 8

    def card(m):
        rows = [
            [
                Paragraph(
                    f"<b>{m['role']}</b>",
                    ParagraphStyle(
                        "R",
                        fontSize=7,
                        fontName="Helvetica-Bold",
                        textColor=ACCENT,
                        leading=10,
                    ),
                )
            ],
            [
                Paragraph(
                    f"<b>{m['name']}</b>",
                    ParagraphStyle(
                        "N",
                        fontSize=10,
                        fontName="Helvetica-Bold",
                        textColor=PRIMARY,
                        leading=14,
                    ),
                )
            ],
            [Spacer(1, 2)],
            [
                Paragraph(
                    m["bio"],
                    ParagraphStyle(
                        "BI",
                        fontSize=8,
                        fontName="Helvetica",
                        textColor=BODY_TEXT,
                        leading=11,
                    ),
                )
            ],
            [Spacer(1, 2)],
            [
                Paragraph(
                    f"{m['years_exp']}+ years experience",
                    ParagraphStyle(
                        "EX",
                        fontSize=7,
                        fontName="Helvetica-Oblique",
                        textColor=MUTED,
                        leading=10,
                    ),
                )
            ],
        ]
        c = Table(rows, colWidths=[cw])
        c.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_ACCENT),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return c

    pairs = [members[i : i + 2] for i in range(0, len(members), 2)]
    for pair in pairs:
        row = [card(pair[0])]
        row.append(card(pair[1]) if len(pair) == 2 else Paragraph("", S["body"]))
        g = Table([row], colWidths=[LEFT_W, RIGHT_W + COL_GAP])
        g.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(g)
        elements.append(Spacer(1, SMALL))


def _timeline(elements, phases):
    elements.append(Spacer(1, MEDIUM))
    elements.append(Paragraph("4. Timeline", S["heading"]))
    _bar(elements)
    elements.append(Spacer(1, MEDIUM))
    max_w = max(p["end_week"] for p in phases)
    cw = CONTENT_W * 0.60
    lw = CONTENT_W * 0.35
    rh = 24
    gap = 6
    th = len(phases) * (rh + gap) + 36
    d = Drawing(CONTENT_W, th)
    xo = lw + 12
    y = th - 20
    for w in range(0, max_w + 1, 2):
        x = xo + (w / max_w) * cw
        d.add(
            String(x, y + 2, f"W{w}", fontSize=6, fontName="Helvetica", fillColor=MUTED)
        )
    y -= 14
    clrs = [ACCENT, SECONDARY, PRIMARY, SUCCESS, WARNING]
    for i, p in enumerate(phases):
        c = clrs[i % len(clrs)]
        d.add(
            String(
                0,
                y + 6,
                p["name"][:30],
                fontSize=8,
                fontName="Helvetica-Bold",
                fillColor=BODY_TEXT,
            )
        )
        bx = xo + (p["start_week"] / max_w) * cw
        bw = ((p["end_week"] - p["start_week"]) / max_w) * cw
        d.add(Rect(bx, y, bw, rh - 4, fillColor=c, strokeColor=None, rx=3, ry=3))
        d.add(
            String(
                bx + 6,
                y + 6,
                f"Wk {p['start_week']}-{p['end_week']}",
                fontSize=6,
                fontName="Helvetica-Bold",
                fillColor=colors.white,
            )
        )
        y -= rh + gap
    elements.append(d)
    elements.append(Spacer(1, SECTION))


def _risks(elements, risks):
    elements.append(Paragraph("5. Risk Assessment", S["heading"]))
    _bar(elements)
    elements.append(Spacer(1, MEDIUM))
    risk_clrs = {"High": DANGER, "Med": WARNING, "Low": SUCCESS}

    def badge(lvl):
        return Paragraph(
            f"<b>{lvl}</b>",
            ParagraphStyle(
                "RB",
                fontSize=8,
                fontName="Helvetica-Bold",
                textColor=risk_clrs.get(lvl, MUTED),
                leading=11,
                alignment=TA_CENTER,
            ),
        )

    cw = [CONTENT_W * 0.26, CONTENT_W * 0.12, CONTENT_W * 0.12, CONTENT_W * 0.50]
    th2 = ParagraphStyle(
        "TH", fontSize=8, fontName="Helvetica-Bold", textColor=colors.white, leading=11
    )
    rows = [
        [
            Paragraph("<b>Risk</b>", th2),
            Paragraph(
                "<b>Likelihood</b>",
                ParagraphStyle("TH2", parent=th2, alignment=TA_CENTER),
            ),
            Paragraph(
                "<b>Impact</b>", ParagraphStyle("TH3", parent=th2, alignment=TA_CENTER)
            ),
            Paragraph("<b>Mitigation</b>", th2),
        ]
    ]
    for r in risks:
        rows.append(
            [
                Paragraph(r["risk"], S["body"]),
                badge(r["likelihood"]),
                badge(r["impact"]),
                Paragraph(
                    r["mitigation"],
                    ParagraphStyle(
                        "Mt",
                        fontSize=8,
                        fontName="Helvetica",
                        textColor=BODY_TEXT,
                        leading=11,
                    ),
                ),
            ]
        )
    t = Table(rows, colWidths=cw)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (1, 0), (2, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, SECTION))


def _budget(elements, items, tax_rate, org, client):
    elements.append(Paragraph("6. Budget", S["heading"]))
    _bar(elements)
    elements.append(Spacer(1, MEDIUM))
    cw = [CONTENT_W * 0.65, CONTENT_W * 0.35]
    th2 = ParagraphStyle(
        "BH", fontSize=8, fontName="Helvetica-Bold", textColor=colors.white, leading=11
    )
    rows = [
        [
            Paragraph("<b>Category</b>", th2),
            Paragraph(
                "<b>Amount</b>", ParagraphStyle("BH2", parent=th2, alignment=TA_RIGHT)
            ),
        ]
    ]
    sub = 0
    for it in items:
        sub += it["amount"]
        rows.append(
            [
                Paragraph(it["category"], S["body"]),
                Paragraph(f"${it['amount']:,.2f}", S["body_right"]),
            ]
        )
    br = ParagraphStyle(
        "BoldR",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=PRIMARY,
        leading=13,
        alignment=TA_RIGHT,
    )
    rows.append(
        [Paragraph("<b>Subtotal</b>", S["body_bold"]), Paragraph(f"${sub:,.2f}", br)]
    )
    tax = sub * tax_rate
    total = sub + tax
    if tax_rate:
        rows.append(
            [
                Paragraph(f"<b>Tax ({tax_rate * 100:.0f}%)</b>", S["body_bold"]),
                Paragraph(f"${tax:,.2f}", br),
            ]
        )
    rows.append(
        [
            Paragraph(
                "<b>TOTAL</b>",
                ParagraphStyle(
                    "TL",
                    fontSize=11,
                    fontName="Helvetica-Bold",
                    textColor=PRIMARY,
                    leading=15,
                ),
            ),
            Paragraph(
                f"<b>${total:,.2f}</b>",
                ParagraphStyle(
                    "TV",
                    fontSize=11,
                    fontName="Helvetica-Bold",
                    textColor=ACCENT,
                    leading=15,
                    alignment=TA_RIGHT,
                ),
            ),
        ]
    )
    ti = len(rows) - 1
    t = Table(rows, colWidths=cw)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, ti - 2), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, ti - 2), [colors.white, ROW_ALT]),
                ("LINEABOVE", (0, ti), (-1, ti), 2, PRIMARY),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(t)

    elements.append(Spacer(1, LARGE))
    elements.append(Paragraph("Acceptance", S["subheading"]))
    elements.append(
        HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=MEDIUM)
    )
    ss = ParagraphStyle(
        "Sg", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13
    )
    ls = [
        Paragraph(f"For <b>{org}</b>", ss),
        Spacer(1, 32),
        HRFlowable(width="90%", thickness=0.5, color=PRIMARY),
        Paragraph("Authorized Signature / Date", S["caption"]),
    ]
    rs = [
        Paragraph(f"For <b>{client}</b>", ss),
        Spacer(1, 32),
        HRFlowable(width="90%", thickness=0.5, color=PRIMARY),
        Paragraph("Authorized Signature / Date", S["caption"]),
    ]
    st = Table([[ls, rs]], colWidths=[LEFT_W, RIGHT_W + COL_GAP])
    st.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    elements.append(st)


def generate_proposal(data: dict, output_path: str = "/home/user/proposal.pdf") -> str:
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
    _exec_summary(elements, data["summary"], data["snapshot"])
    _methodology(elements, data["phases"])
    _team(elements, data["team"])
    _timeline(elements, data["phases"])
    _risks(elements, data["risks"])
    elements.append(PageBreak())
    _budget(
        elements, data["budget"], data.get("tax_rate", 0), data["org"], data["client"]
    )
    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    print(f"Generated: {output_path}")
    return output_path


# ── Sample data — edit this to generate your proposal ────────
DATA = {
    "title": "Cloud Infrastructure\nModernization Program",
    "subtitle": "Technical Proposal & Implementation Plan",
    "org": "Meridian Technology Partners",
    "client": "Atlas Financial Group",
    "date": "January 15, 2026",
    "ref": "PROP-2026-0012",
    "summary": [
        "Meridian Technology Partners proposes a comprehensive cloud modernization program to migrate Atlas Financial Group's legacy infrastructure to a scalable, secure, cloud-native architecture.",
        "This proposal outlines our phased methodology, dedicated team, detailed timeline, risk mitigations, and the investment required to deliver measurable results within 16 weeks.",
    ],
    "snapshot": [
        ("Duration", "16 weeks"),
        ("Team", "8 specialists"),
        ("Methodology", "Agile Sprints"),
        ("SLA", "99.9% uptime"),
    ],
    "phases": [
        {
            "name": "Assessment & Planning",
            "description": "Audit current infrastructure, identify migration candidates, define target architecture.",
            "activities": [
                "Infrastructure audit",
                "Dependency mapping",
                "Architecture design",
                "Migration roadmap",
            ],
            "duration": "3 weeks",
            "start_week": 1,
            "end_week": 3,
        },
        {
            "name": "Foundation & Security",
            "description": "Establish cloud foundations — networking, IAM, security baselines, CI/CD.",
            "activities": [
                "VPC & networking",
                "IAM & SSO",
                "Security baseline",
                "CI/CD pipeline",
            ],
            "duration": "3 weeks",
            "start_week": 3,
            "end_week": 6,
        },
        {
            "name": "Migration & Build",
            "description": "Migrate workloads in prioritized waves, refactor critical services.",
            "activities": [
                "Wave 1: Non-critical",
                "Wave 2: Core services",
                "Wave 3: Data tier",
                "Performance testing",
            ],
            "duration": "7 weeks",
            "start_week": 6,
            "end_week": 13,
        },
        {
            "name": "Optimization & Handover",
            "description": "Performance tuning, cost optimization, documentation, training.",
            "activities": [
                "Performance tuning",
                "Cost review",
                "Documentation",
                "Training",
                "Sign-off",
            ],
            "duration": "3 weeks",
            "start_week": 13,
            "end_week": 16,
        },
    ],
    "team": [
        {
            "name": "Sarah Chen",
            "role": "Program Director",
            "bio": "15 years leading enterprise cloud migrations. AWS & Azure certified.",
            "years_exp": 15,
        },
        {
            "name": "Marcus Williams",
            "role": "Lead Architect",
            "bio": "Distributed systems specialist. 30+ cloud-native transformations.",
            "years_exp": 12,
        },
        {
            "name": "Priya Patel",
            "role": "Security Lead",
            "bio": "CISSP certified. Cloud security and zero-trust expert.",
            "years_exp": 10,
        },
        {
            "name": "James O'Brien",
            "role": "DevOps Lead",
            "bio": "Kubernetes & Terraform specialist. CI/CD for 50+ teams.",
            "years_exp": 8,
        },
    ],
    "risks": [
        {
            "risk": "Legacy dependencies block migration",
            "likelihood": "Med",
            "impact": "High",
            "mitigation": "Early dependency mapping; parallel tracks.",
        },
        {
            "risk": "Data migration exceeds SLA downtime",
            "likelihood": "Low",
            "impact": "High",
            "mitigation": "Blue-green migration with rollback.",
        },
        {
            "risk": "Team cloud-native knowledge gaps",
            "likelihood": "Med",
            "impact": "Med",
            "mitigation": "Embedded training; runbooks.",
        },
        {
            "risk": "Scope expansion cost overrun",
            "likelihood": "Low",
            "impact": "Med",
            "mitigation": "Fixed-scope phases; change requests.",
        },
    ],
    "budget": [
        {"category": "Assessment & Planning", "amount": 45000},
        {"category": "Foundation & Security", "amount": 52000},
        {"category": "Migration & Build (7 weeks)", "amount": 168000},
        {"category": "Optimization & Handover", "amount": 38000},
        {"category": "Project Management", "amount": 24000},
        {"category": "Training & Documentation", "amount": 15000},
    ],
    "tax_rate": 0.0,
}

if __name__ == "__main__":
    generate_proposal(DATA)
