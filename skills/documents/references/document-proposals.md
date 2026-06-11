---
name: Document Proposals
description: Use this reference when generating formal project proposals, RFP responses, or capability documents — methodology, team qualifications, project timeline, risk matrix, case studies, and acceptance criteria. Uses the Corporate Navy palette for authority.
---

Formal document proposal patterns using the Corporate Navy palette. Distinct from `client-proposals.md` (which focuses on sales/pricing). This reference targets RFP responses, project bids, and capability statements. All patterns follow `design-principles.md`.

## Color Palette — Corporate Navy

```python
from reportlab.lib import colors

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
BACKGROUND = colors.HexColor("#fafbfc")
LIGHT_ACCENT = colors.HexColor("#ebf5fb")
```

## Proposal Structure — Multi-Page

| Page | Content |
|------|---------|
| 1 | Cover page with project title, submitting org, date, confidentiality |
| 2 | Executive summary + project snapshot sidebar |
| 3 | Methodology — numbered phases with descriptions |
| 4 | Team qualifications — two-column bios with role badges |
| 5 | Project timeline — horizontal Gantt-style bar chart |
| 6 | Risk matrix table + mitigation strategies |
| 7 | Case studies — past project summaries with results |
| 8 | Budget summary + acceptance and sign-off block |

## Cover Page

```python
def proposal_cover(elements, title, subtitle, org_name, client_name, date, ref, confidential=True):
    elements.append(Spacer(1, 60))

    # Organisation name
    elements.append(Paragraph(org_name.upper(), ParagraphStyle(
        "OrgName", fontSize=10, fontName="Helvetica-Bold",
        textColor=ACCENT, leading=14, tracking=300,
    )))
    elements.append(Spacer(1, MEDIUM))

    # Thick navy bar
    bar = Drawing(CONTENT_W, 8)
    bar.add(Rect(0, 0, CONTENT_W, 8, fillColor=PRIMARY, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, LARGE))

    # Title
    elements.append(Paragraph(title, ParagraphStyle(
        "Title", fontSize=28, fontName="Helvetica-Bold",
        textColor=PRIMARY, leading=34, spaceAfter=8,
    )))

    if subtitle:
        elements.append(Paragraph(subtitle, ParagraphStyle(
            "Subtitle", fontSize=14, fontName="Helvetica",
            textColor=SECONDARY, leading=18, spaceAfter=16,
        )))

    # Thin accent bar
    bar2 = Drawing(CONTENT_W * 0.4, 3)
    bar2.add(Rect(0, 0, CONTENT_W * 0.4, 3, fillColor=ACCENT, strokeColor=None))
    elements.append(bar2)
    elements.append(Spacer(1, LARGE))

    # Prepared for / by
    meta_style = ParagraphStyle("CoverMeta", fontSize=9, fontName="Helvetica", textColor=MUTED, leading=13)
    bold_style = ParagraphStyle("CoverBold", fontSize=12, fontName="Helvetica-Bold", textColor=PRIMARY, leading=16)

    elements.append(Paragraph("Prepared for", meta_style))
    elements.append(Paragraph(client_name, bold_style))
    elements.append(Spacer(1, MEDIUM))
    elements.append(Paragraph("Submitted by", meta_style))
    elements.append(Paragraph(org_name, bold_style))
    elements.append(Spacer(1, SMALL))
    elements.append(Paragraph(f"Date: {date}  |  Ref: {ref}", meta_style))

    if confidential:
        elements.append(Spacer(1, LARGE))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
        elements.append(Spacer(1, SMALL))
        elements.append(Paragraph(
            "CONFIDENTIAL — This document contains proprietary information and is intended solely for the named recipient.",
            ParagraphStyle("Conf", fontSize=7, fontName="Helvetica-Oblique", textColor=DANGER, leading=10),
        ))

    elements.append(PageBreak())
```

## Executive Summary + Project Snapshot

```python
def executive_summary(elements, summary_paras, snapshot):
    """
    summary_paras: list of paragraph strings.
    snapshot: list of (label, value) tuples for sidebar.
    """
    elements.append(Paragraph("1. Executive Summary", STYLES["heading"]))
    bar = Drawing(CONTENT_W, 3)
    bar.add(Rect(0, 0, CONTENT_W, 3, fillColor=PRIMARY, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, MEDIUM))

    left = []
    for para in summary_paras:
        left.append(Paragraph(para, STYLES["body"]))
        left.append(Spacer(1, SMALL))

    # Snapshot sidebar
    snap_rows = [[
        Paragraph("<b>PROJECT SNAPSHOT</b>", ParagraphStyle(
            "SnapH", fontSize=7, fontName="Helvetica-Bold", textColor=colors.white, leading=10,
        )),
        Paragraph("", STYLES["body"]),
    ]]
    for label, value in snapshot:
        snap_rows.append([
            Paragraph(label, ParagraphStyle("SL", fontSize=7, fontName="Helvetica-Bold", textColor=MUTED, leading=10)),
            Paragraph(f"<b>{value}</b>", ParagraphStyle("SV", fontSize=10, fontName="Helvetica-Bold", textColor=PRIMARY, leading=14)),
        ])

    snap_table = Table(snap_rows, colWidths=[RIGHT_W * 0.45, RIGHT_W * 0.55])
    snap_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT_ACCENT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))

    right = [snap_table]

    two_col = Table([[left, right]], colWidths=[LEFT_W, RIGHT_W])
    two_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(two_col)
```

## Methodology — Numbered Phases

```python
def methodology_section(elements, phases):
    """
    phases: list of dicts with keys: name, description, activities (list of strings), duration.
    """
    elements.append(Paragraph("2. Methodology", STYLES["heading"]))
    bar = Drawing(CONTENT_W, 3)
    bar.add(Rect(0, 0, CONTENT_W, 3, fillColor=PRIMARY, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, MEDIUM))

    for i, phase in enumerate(phases, 1):
        # Phase header row: number badge + name + duration
        badge = Paragraph(
            f"<b>{i}</b>",
            ParagraphStyle("Badge", fontSize=12, fontName="Helvetica-Bold", textColor=colors.white, leading=16, alignment=TA_CENTER),
        )
        badge_cell = Table([[badge]], colWidths=[28], rowHeights=[28])
        badge_cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), ACCENT),
            ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]))

        name_para = Paragraph(
            f"<b>{phase['name']}</b>",
            ParagraphStyle("PhaseName", fontSize=12, fontName="Helvetica-Bold", textColor=PRIMARY, leading=16),
        )
        dur_para = Paragraph(
            phase["duration"],
            ParagraphStyle("PhaseDur", fontSize=9, fontName="Helvetica", textColor=ACCENT, leading=13, alignment=TA_RIGHT),
        )

        header_row = Table([[badge_cell, name_para, dur_para]], colWidths=[36, CONTENT_W - 120, 84])
        header_row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        elements.append(header_row)
        elements.append(Spacer(1, TINY))

        # Description
        elements.append(Paragraph(phase["description"], STYLES["body"]))
        elements.append(Spacer(1, TINY))

        # Activities as bullet list
        for activity in phase.get("activities", []):
            elements.append(Paragraph(f"• {activity}", ParagraphStyle(
                "Activity", fontSize=8, fontName="Helvetica", textColor=BODY_TEXT, leading=12,
                leftIndent=16, spaceAfter=2,
            )))

        elements.append(Spacer(1, MEDIUM))
```

## Team Qualifications — Two-Column Bios

```python
def team_section(elements, team_members):
    """
    team_members: list of dicts with keys: name, role, bio, years_exp.
    Renders in two-column grid, max 2 per row.
    """
    elements.append(Paragraph("3. Team Qualifications", STYLES["heading"]))
    bar = Drawing(CONTENT_W, 3)
    bar.add(Rect(0, 0, CONTENT_W, 3, fillColor=PRIMARY, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, MEDIUM))

    card_w = LEFT_W - 4

    def make_card(member):
        role_badge = Paragraph(
            f"<b>{member['role']}</b>",
            ParagraphStyle("Role", fontSize=7, fontName="Helvetica-Bold", textColor=ACCENT, leading=10),
        )
        name_para = Paragraph(
            f"<b>{member['name']}</b>",
            ParagraphStyle("Name", fontSize=10, fontName="Helvetica-Bold", textColor=PRIMARY, leading=14),
        )
        bio_para = Paragraph(member["bio"], ParagraphStyle(
            "Bio", fontSize=8, fontName="Helvetica", textColor=BODY_TEXT, leading=11,
        ))
        exp_para = Paragraph(
            f"{member['years_exp']}+ years experience",
            ParagraphStyle("Exp", fontSize=7, fontName="Helvetica-Oblique", textColor=MUTED, leading=10),
        )

        card_data = [[role_badge], [name_para], [Spacer(1, 2)], [bio_para], [Spacer(1, 2)], [exp_para]]
        card = Table(card_data, colWidths=[card_w])
        card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_ACCENT),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        return card

    # Pair members into rows of 2
    pairs = [team_members[i:i+2] for i in range(0, len(team_members), 2)]
    for pair in pairs:
        if len(pair) == 2:
            row = [[make_card(pair[0]), make_card(pair[1])]]
            cols = [LEFT_W, RIGHT_W]
        else:
            row = [[make_card(pair[0]), Paragraph("", STYLES["body"])]]
            cols = [LEFT_W, RIGHT_W]

        grid = Table(row, colWidths=cols)
        grid.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(grid)
        elements.append(Spacer(1, SMALL))
```

## Project Timeline — Horizontal Bar Chart

```python
def timeline_chart(elements, phases):
    """
    phases: list of dicts with keys: name, start_week, end_week.
    Renders a horizontal Gantt-style chart.
    """
    elements.append(Paragraph("4. Project Timeline", STYLES["heading"]))
    bar_el = Drawing(CONTENT_W, 3)
    bar_el.add(Rect(0, 0, CONTENT_W, 3, fillColor=PRIMARY, strokeColor=None))
    elements.append(bar_el)
    elements.append(Spacer(1, MEDIUM))

    max_week = max(p["end_week"] for p in phases)
    chart_w = CONTENT_W * 0.65
    label_w = CONTENT_W * 0.30
    row_h = 24
    gap = 4
    total_h = len(phases) * (row_h + gap) + 30

    d = Drawing(CONTENT_W, total_h)
    x_offset = label_w + 8
    y = total_h - 20

    # Week headers
    for w in range(0, max_week + 1, 2):
        x = x_offset + (w / max_week) * chart_w
        d.add(String(x, y + 2, f"W{w}", fontSize=6, fontName="Helvetica", fillColor=MUTED))

    y -= 10

    phase_colors = [ACCENT, SECONDARY, PRIMARY, SUCCESS, WARNING]
    for i, phase in enumerate(phases):
        color = phase_colors[i % len(phase_colors)]
        # Label
        d.add(String(0, y + 6, phase["name"], fontSize=8, fontName="Helvetica-Bold", fillColor=BODY_TEXT))
        # Bar
        bar_x = x_offset + (phase["start_week"] / max_week) * chart_w
        bar_w = ((phase["end_week"] - phase["start_week"]) / max_week) * chart_w
        d.add(Rect(bar_x, y, bar_w, row_h - 4, fillColor=color, strokeColor=None, rx=3, ry=3))
        # Duration label on bar
        d.add(String(
            bar_x + bar_w / 2 - 10, y + 6,
            f"Wk {phase['start_week']}-{phase['end_week']}",
            fontSize=6, fontName="Helvetica-Bold", fillColor=colors.white,
        ))
        y -= (row_h + gap)

    elements.append(d)
```

## Risk Matrix

```python
def risk_matrix(elements, risks):
    """
    risks: list of dicts with keys: risk, likelihood (High/Med/Low),
    impact (High/Med/Low), mitigation.
    """
    elements.append(Paragraph("5. Risk Assessment", STYLES["heading"]))
    bar = Drawing(CONTENT_W, 3)
    bar.add(Rect(0, 0, CONTENT_W, 3, fillColor=PRIMARY, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, MEDIUM))

    risk_colors = {"High": DANGER, "Med": WARNING, "Low": SUCCESS}

    def risk_badge(level):
        clr = risk_colors.get(level, MUTED)
        return Paragraph(
            f"<b>{level}</b>",
            ParagraphStyle("RiskBadge", fontSize=8, fontName="Helvetica-Bold", textColor=clr, leading=11, alignment=TA_CENTER),
        )

    col_widths = [CONTENT_W * 0.28, CONTENT_W * 0.12, CONTENT_W * 0.12, CONTENT_W * 0.48]
    header = [
        Paragraph("<b>Risk</b>", STYLES["caption_bold"]),
        Paragraph("<b>Likelihood</b>", STYLES["caption_bold_center"]),
        Paragraph("<b>Impact</b>", STYLES["caption_bold_center"]),
        Paragraph("<b>Mitigation</b>", STYLES["caption_bold"]),
    ]
    rows = [header]

    for risk in risks:
        rows.append([
            Paragraph(risk["risk"], STYLES["body"]),
            risk_badge(risk["likelihood"]),
            risk_badge(risk["impact"]),
            Paragraph(risk["mitigation"], STYLES["body"]),
        ])

    table = Table(rows, colWidths=col_widths)
    table.setStyle(TableStyle([
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
    ]))
    elements.append(table)
```

## Case Studies

```python
def case_studies(elements, cases):
    """
    cases: list of dicts with keys: title, client, industry, challenge, solution, results (list of strings).
    """
    elements.append(Paragraph("6. Relevant Experience", STYLES["heading"]))
    bar = Drawing(CONTENT_W, 3)
    bar.add(Rect(0, 0, CONTENT_W, 3, fillColor=PRIMARY, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, MEDIUM))

    for case in cases:
        # Case header
        elements.append(Paragraph(case["title"], STYLES["subheading"]))
        elements.append(Paragraph(
            f"{case['client']}  •  {case['industry']}",
            ParagraphStyle("CaseMeta", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10),
        ))
        elements.append(Spacer(1, SMALL))

        # Two-column: challenge + solution left, results right
        left = [
            Paragraph("<b>Challenge</b>", ParagraphStyle("CL", fontSize=7, fontName="Helvetica-Bold", textColor=SECONDARY, leading=10)),
            Paragraph(case["challenge"], STYLES["body"]),
            Spacer(1, SMALL),
            Paragraph("<b>Solution</b>", ParagraphStyle("SL", fontSize=7, fontName="Helvetica-Bold", textColor=SECONDARY, leading=10)),
            Paragraph(case["solution"], STYLES["body"]),
        ]

        result_rows = []
        for r in case["results"]:
            result_rows.append([Paragraph(f"✓ {r}", ParagraphStyle(
                "Res", fontSize=8, fontName="Helvetica", textColor=SUCCESS, leading=11,
            ))])
        result_table = Table(result_rows, colWidths=[RIGHT_W - 8])
        result_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_ACCENT),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))

        right = [
            Paragraph("<b>Results</b>", ParagraphStyle("RL", fontSize=7, fontName="Helvetica-Bold", textColor=SECONDARY, leading=10)),
            Spacer(1, TINY),
            result_table,
        ]

        two_col = Table([[left, right]], colWidths=[LEFT_W, RIGHT_W])
        two_col.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        elements.append(two_col)
        elements.append(Spacer(1, MEDIUM))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=MEDIUM))
```

## Budget Summary + Sign-Off

```python
def budget_and_signoff(elements, budget_items, tax_rate, org_name, client_name):
    """
    budget_items: list of dicts with keys: category, amount.
    """
    elements.append(Paragraph("7. Budget Summary", STYLES["heading"]))
    bar = Drawing(CONTENT_W, 3)
    bar.add(Rect(0, 0, CONTENT_W, 3, fillColor=PRIMARY, strokeColor=None))
    elements.append(bar)
    elements.append(Spacer(1, MEDIUM))

    col_widths = [CONTENT_W * 0.65, CONTENT_W * 0.35]
    header = [
        Paragraph("<b>Category</b>", STYLES["caption_bold"]),
        Paragraph("<b>Amount</b>", STYLES["caption_bold"]),
    ]
    rows = [header]
    subtotal = 0
    for item in budget_items:
        subtotal += item["amount"]
        rows.append([
            Paragraph(item["category"], STYLES["body"]),
            Paragraph(f"${item['amount']:,.2f}", STYLES["body_right"]),
        ])

    tax = subtotal * tax_rate
    total = subtotal + tax
    bold_r = ParagraphStyle("BR", fontSize=9, fontName="Helvetica-Bold", textColor=PRIMARY, leading=13, alignment=TA_RIGHT)

    rows.append([Paragraph("<b>Subtotal</b>", STYLES["body_bold"]), Paragraph(f"${subtotal:,.2f}", bold_r)])
    rows.append([Paragraph(f"<b>Tax ({tax_rate*100:.0f}%)</b>", STYLES["body_bold"]), Paragraph(f"${tax:,.2f}", bold_r)])
    rows.append([
        Paragraph("<b>TOTAL INVESTMENT</b>", ParagraphStyle("TL", fontSize=11, fontName="Helvetica-Bold", textColor=PRIMARY, leading=15)),
        Paragraph(f"<b>${total:,.2f}</b>", ParagraphStyle("TV", fontSize=11, fontName="Helvetica-Bold", textColor=ACCENT, leading=15, alignment=TA_RIGHT)),
    ])

    table = Table(rows, colWidths=col_widths)
    total_idx = len(rows) - 1
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, total_idx - 3), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, total_idx - 3), [colors.white, ROW_ALT]),
        ("LINEABOVE", (0, total_idx), (-1, total_idx), 2, PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    # Sign-off block
    elements.append(Spacer(1, LARGE))
    elements.append(Paragraph("Acceptance", STYLES["subheading"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=MEDIUM))

    sig_style = ParagraphStyle("Sig", fontSize=9, fontName="Helvetica", textColor=BODY_TEXT, leading=13)
    line_style = ParagraphStyle("SigLine", fontSize=9, fontName="Helvetica", textColor=BORDER, leading=13)

    left_sig = [
        Paragraph(f"For <b>{org_name}</b>", sig_style),
        Spacer(1, 32),
        HRFlowable(width="90%", thickness=0.5, color=PRIMARY),
        Paragraph("Authorized Signature / Date", ParagraphStyle(
            "SigLabel", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10,
        )),
    ]
    right_sig = [
        Paragraph(f"For <b>{client_name}</b>", sig_style),
        Spacer(1, 32),
        HRFlowable(width="90%", thickness=0.5, color=PRIMARY),
        Paragraph("Authorized Signature / Date", ParagraphStyle(
            "SigLabel2", fontSize=7, fontName="Helvetica", textColor=MUTED, leading=10,
        )),
    ]

    sig_table = Table([[left_sig, right_sig]], colWidths=[LEFT_W, RIGHT_W])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(sig_table)
```

## Data Structure Example

```python
data = {
    "title": "Cloud Infrastructure\nModernization Program",
    "subtitle": "Technical Proposal & Implementation Plan",
    "org_name": "Meridian Technology Partners",
    "client_name": "Atlas Financial Group",
    "date": "January 15, 2026",
    "ref": "PROP-2026-0012",
    "summary": [
        "Meridian Technology Partners proposes a comprehensive cloud modernization program to migrate Atlas Financial Group's legacy infrastructure to a scalable, secure, cloud-native architecture.",
        "This proposal outlines our proven methodology, the dedicated team assigned to this engagement, a detailed timeline, risk mitigations, and the investment required to deliver measurable results within 16 weeks.",
    ],
    "snapshot": [
        ("Duration", "16 weeks"),
        ("Team", "8 specialists"),
        ("Methodology", "Agile Sprints"),
        ("SLA", "99.9% uptime"),
    ],
    "phases": [
        {"name": "Assessment & Planning", "description": "Audit current infrastructure, identify migration candidates, define target architecture.", "activities": ["Infrastructure audit", "Dependency mapping", "Architecture design", "Migration roadmap"], "duration": "3 weeks", "start_week": 1, "end_week": 3},
        {"name": "Foundation & Security", "description": "Establish cloud foundations — networking, IAM, security baselines, CI/CD pipelines.", "activities": ["VPC & networking setup", "IAM policies", "Security baseline", "CI/CD pipeline"], "duration": "3 weeks", "start_week": 3, "end_week": 6},
        {"name": "Migration & Build", "description": "Migrate workloads in prioritized waves, refactor critical services for cloud-native operation.", "activities": ["Wave 1: Non-critical workloads", "Wave 2: Core services", "Wave 3: Data tier", "Performance testing"], "duration": "7 weeks", "start_week": 6, "end_week": 13},
        {"name": "Optimization & Handover", "description": "Performance tuning, cost optimization, documentation, knowledge transfer, and production sign-off.", "activities": ["Performance tuning", "Cost optimization", "Documentation", "Team training", "Production sign-off"], "duration": "3 weeks", "start_week": 13, "end_week": 16},
    ],
    "team": [
        {"name": "Sarah Chen", "role": "Program Director", "bio": "15 years leading enterprise cloud migrations for Fortune 500 clients. AWS & Azure certified architect.", "years_exp": 15},
        {"name": "Marcus Williams", "role": "Lead Architect", "bio": "Specialist in distributed systems and microservices. Led 30+ cloud-native transformations.", "years_exp": 12},
        {"name": "Priya Patel", "role": "Security Lead", "bio": "CISSP certified. Expert in cloud security posture management and zero-trust architectures.", "years_exp": 10},
        {"name": "James O'Brien", "role": "DevOps Lead", "bio": "Kubernetes and Terraform specialist. Built CI/CD platforms for 50+ engineering teams.", "years_exp": 8},
    ],
    "risks": [
        {"risk": "Legacy system dependencies block migration timeline", "likelihood": "Med", "impact": "High", "mitigation": "Early dependency mapping in Phase 1; parallel migration tracks for independent services."},
        {"risk": "Data migration causes downtime exceeding SLA", "likelihood": "Low", "impact": "High", "mitigation": "Blue-green migration strategy with automatic rollback; off-peak migration windows."},
        {"risk": "Team knowledge gaps in cloud-native patterns", "likelihood": "Med", "impact": "Med", "mitigation": "Embedded training throughout engagement; comprehensive runbooks and documentation."},
        {"risk": "Cost overrun due to scope expansion", "likelihood": "Low", "impact": "Med", "mitigation": "Fixed-scope phases with formal change request process; weekly budget reviews."},
    ],
    "cases": [
        {"title": "Global Bank Cloud Migration", "client": "Tier-1 Investment Bank", "industry": "Financial Services", "challenge": "Migrate 200+ legacy applications from on-premise data centers to AWS within 12 months while maintaining regulatory compliance.", "solution": "Phased migration using automated lift-and-shift for commodity workloads and targeted refactoring for performance-critical trading systems.", "results": ["40% reduction in infrastructure costs", "99.99% uptime achieved", "3x faster deployment cycles", "Full SOC 2 compliance maintained"]},
        {"title": "InsurTech Platform Modernization", "client": "National Insurance Provider", "industry": "Insurance", "challenge": "Decompose a monolithic policy management system into microservices to support a new digital-first customer experience.", "solution": "Domain-driven decomposition with event-sourced architecture. Strangler fig pattern for incremental migration without service disruption.", "results": ["Policy issuance time reduced from 5 days to 4 hours", "60% fewer production incidents", "Team velocity increased 2.5x"]},
    ],
    "budget": [
        {"category": "Assessment & Planning Phase", "amount": 45000},
        {"category": "Foundation & Security Setup", "amount": 52000},
        {"category": "Migration & Build (7 weeks)", "amount": 168000},
        {"category": "Optimization & Handover", "amount": 38000},
        {"category": "Project Management & Governance", "amount": 24000},
        {"category": "Training & Documentation", "amount": 15000},
    ],
    "tax_rate": 0.0,
}
```
