"""
Editorial Book-Style PDF Generator (Landscape, Themable).

Landscape A4. Color backgrounds ONLY on cover and chapter divider pages.
All text/content pages are clean white. Supports 12 themes, logo, chapter graphics.

Usage:
    python generate_editorial.py

Customization:
    Edit the DATA dict at the bottom. Set theme, title, subtitle, org_name,
    logo_path (sandbox path to image), and chapters. You can also edit the
    script directly to add sections, change layout, or extend themes.

Agent workflow:
    1. Edit DATA dict (or the script) with user content
    2. For logo: use nano_banana_image_generation, save image to sandbox, set logo_path
    3. Run in sandbox: pip install reportlab && python generate_editorial.py
    4. Download PDF, optionally run pdf_to_images for preview
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ── Page geometry (landscape A4) ──────────────────────────────
PAGE_SIZE = landscape(A4)
WIDTH, HEIGHT = PAGE_SIZE
MARGIN = 2 * cm
CONTENT_W = WIDTH - 2 * MARGIN
COL_GAP = 28
COL_W = (CONTENT_W - COL_GAP) / 2

SMALL, MEDIUM, LARGE = 8, 16, 28

# ── Theme definitions (12 distinct warm palettes) ───────────────
# Each palette uses a DIFFERENT hue family. Warm = warm undertone, not "brown."
THEMES: dict[str, dict] = {
    "terracotta": {
        "cover_bg": "#c4704b",
        "chapter_colors": ["#c4704b", "#9e5a6e", "#7a6e52", "#8c5c3e"],
        "title_color": "white",
        "code_bg": "#f5f0e8",
        "muted": "#999999",
        "rule": "#d4d4d4",
    },
    "crimson": {
        "cover_bg": "#9b1b30",
        "chapter_colors": ["#9b1b30", "#7a3b4a", "#a04050", "#6b2838"],
        "title_color": "white",
        "code_bg": "#fdf0f0",
        "muted": "#8b6f6f",
        "rule": "#d4c4c4",
    },
    "saffron": {
        "cover_bg": "#b8860b",
        "chapter_colors": ["#b8860b", "#8b6914", "#d4a017", "#7a6020"],
        "title_color": "white",
        "code_bg": "#fdf8e8",
        "muted": "#7a7060",
        "rule": "#d8d2c0",
    },
    "coral": {
        "cover_bg": "#d06050",
        "chapter_colors": ["#d06050", "#b85a58", "#c47868", "#a85048"],
        "title_color": "white",
        "code_bg": "#fef0ee",
        "muted": "#8b7070",
        "rule": "#e0d0ce",
    },
    "plum": {
        "cover_bg": "#6b2148",
        "chapter_colors": ["#6b2148", "#8b3a5a", "#5a2850", "#9e4868"],
        "title_color": "white",
        "code_bg": "#fdf4f8",
        "muted": "#8b6b7a",
        "rule": "#e0d0d8",
    },
    "olive": {
        "cover_bg": "#556b2f",
        "chapter_colors": ["#556b2f", "#6b7a3a", "#4a5e28", "#7a8a48"],
        "title_color": "white",
        "code_bg": "#f5f7ee",
        "muted": "#6b7a5a",
        "rule": "#d0d8c4",
    },
    "rose": {
        "cover_bg": "#b5617a",
        "chapter_colors": ["#b5617a", "#9a5068", "#c87a90", "#8a4860"],
        "title_color": "white",
        "code_bg": "#fdf2f5",
        "muted": "#8b7078",
        "rule": "#e0d0d5",
    },
    "espresso": {
        "cover_bg": "#3c2415",
        "chapter_colors": ["#3c2415", "#5a3a28", "#4e3020", "#6b4a35"],
        "title_color": "white",
        "code_bg": "#faf5f0",
        "muted": "#78706a",
        "rule": "#d6cec6",
    },
    "navy": {
        "cover_bg": "#2c3e6b",
        "chapter_colors": ["#2c3e6b", "#3a4f7a", "#4a3a68", "#354878"],
        "title_color": "white",
        "code_bg": "#f0f2f8",
        "muted": "#6a7090",
        "rule": "#c8cee0",
    },
    "wine": {
        "cover_bg": "#722f37",
        "chapter_colors": ["#722f37", "#5a3040", "#8b3a4a", "#683848"],
        "title_color": "white",
        "code_bg": "#faf0f0",
        "muted": "#8b6f6f",
        "rule": "#d4c4c4",
    },
    "teal": {
        "cover_bg": "#2a6b5e",
        "chapter_colors": ["#2a6b5e", "#3a7a6a", "#1e5a50", "#488a78"],
        "title_color": "white",
        "code_bg": "#f0f7f5",
        "muted": "#5a7a72",
        "rule": "#c4d8d2",
    },
    "aubergine": {
        "cover_bg": "#4a2050",
        "chapter_colors": ["#4a2050", "#5a3060", "#402848", "#6a3870"],
        "title_color": "white",
        "code_bg": "#f8f0fa",
        "muted": "#7a6a80",
        "rule": "#d4c8da",
    },
}

# Resolved at runtime from DATA["theme"]
COVER_BG: colors.HexColor = colors.HexColor("#c4704b")
CHAPTER_COLORS: list[colors.HexColor] = []
TEXT_DARK = colors.HexColor("#1a1a1a")
TEXT_WHITE = colors.HexColor("#ffffff")
MUTED = colors.HexColor("#999999")
CODE_BG = colors.HexColor("#f5f0e8")
RULE_CLR = colors.HexColor("#d4d4d4")
TITLE_COLOR: colors.HexColor = TEXT_WHITE

_chapter_color_stack: list[colors.HexColor] = []
_cover_data: dict = {}


def resolve_theme(theme_name: str) -> None:
    """Apply theme; sets module-level color variables."""
    global COVER_BG, CHAPTER_COLORS, MUTED, CODE_BG, RULE_CLR, TITLE_COLOR
    t = THEMES.get(theme_name, THEMES["terracotta"])
    COVER_BG = colors.HexColor(t["cover_bg"])
    CHAPTER_COLORS = [colors.HexColor(h) for h in t["chapter_colors"]]
    MUTED = colors.HexColor(t["muted"])
    CODE_BG = colors.HexColor(t["code_bg"])
    RULE_CLR = colors.HexColor(t["rule"])
    TITLE_COLOR = TEXT_WHITE if t["title_color"] == "white" else TEXT_DARK


def _build_styles() -> dict:
    """Build paragraph styles from current theme."""
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle",
            fontSize=48,
            fontName="Helvetica-Bold",
            textColor=TITLE_COLOR,
            leading=56,
            spaceAfter=14,
        ),
        "cover_sub": ParagraphStyle(
            "CoverSub",
            fontSize=15,
            fontName="Helvetica",
            textColor=TITLE_COLOR,
            leading=22,
        ),
        "cover_logo": ParagraphStyle(
            "CoverLogo",
            fontSize=14,
            fontName="Helvetica-Bold",
            textColor=TITLE_COLOR,
            leading=18,
        ),
        "chapter_label": ParagraphStyle(
            "ChapterLabel",
            fontSize=11,
            fontName="Helvetica",
            textColor=TITLE_COLOR,
            leading=15,
        ),
        "chapter_title": ParagraphStyle(
            "ChapterTitle",
            fontSize=42,
            fontName="Helvetica-Bold",
            textColor=TITLE_COLOR,
            leading=50,
        ),
        "toc_title": ParagraphStyle(
            "TocTitle",
            fontSize=36,
            fontName="Helvetica-Bold",
            textColor=TEXT_DARK,
            leading=44,
            spaceAfter=36,
        ),
        "toc_entry": ParagraphStyle(
            "TocEntry",
            fontSize=14,
            fontName="Helvetica",
            textColor=TEXT_DARK,
            leading=20,
        ),
        "toc_page": ParagraphStyle(
            "TocPage",
            fontSize=14,
            fontName="Helvetica-Bold",
            textColor=TEXT_DARK,
            leading=20,
            alignment=TA_RIGHT,
        ),
        "heading": ParagraphStyle(
            "Heading",
            fontSize=22,
            fontName="Helvetica-Bold",
            textColor=TEXT_DARK,
            leading=28,
            spaceAfter=10,
        ),
        "subheading": ParagraphStyle(
            "Subheading",
            fontSize=13,
            fontName="Helvetica-Bold",
            textColor=TEXT_DARK,
            leading=18,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            fontSize=11,
            fontName="Helvetica",
            textColor=TEXT_DARK,
            leading=16,
            alignment=TA_JUSTIFY,
        ),
        "code": ParagraphStyle(
            "Code",
            fontSize=9.5,
            fontName="Courier",
            textColor=TEXT_DARK,
            leading=14,
            backColor=CODE_BG,
            borderPadding=10,
            spaceBefore=6,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontSize=11,
            fontName="Helvetica",
            textColor=TEXT_DARK,
            leading=16,
            leftIndent=14,
            bulletIndent=0,
            spaceAfter=4,
        ),
    }


# ── Canvas callbacks ──────────────────────────────────────────
def _draw_chapter_graphic(canvas, bg_color: colors.HexColor) -> None:
    """Concentric quarter-circle arcs in top-right corner."""
    import colorsys

    r, g, b = bg_color.red, bg_color.green, bg_color.blue
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    tr, tg, tb = colorsys.hsv_to_rgb(h, max(s * 0.3, 0.05), min(1, v + 0.25))
    tint = colors.Color(tr, tg, tb, alpha=0.35)
    cx, cy = WIDTH, HEIGHT
    for radius in [100, 170, 240, 310]:
        canvas.setStrokeColor(tint)
        canvas.setLineWidth(3)
        canvas.arc(cx - radius, cy - radius, cx + radius, cy + radius, 180, 90)


def _draw_cover_logo(canvas) -> None:
    """Draw org logo at bottom-left of cover page via canvas."""
    logo_path = _cover_data.get("logo_path")
    org_name = _cover_data.get("org_name", "Hyper")
    x, y = MARGIN, MARGIN + 10

    if logo_path and os.path.isfile(logo_path):
        try:
            canvas.drawImage(logo_path, x, y, width=28, height=28, mask="auto")
            canvas.setFont("Helvetica-Bold", 14)
            canvas.setFillColor(TITLE_COLOR)
            canvas.drawString(x + 34, y + 8, org_name)
            return
        except Exception:
            pass

    sq = 5
    gap = 2
    canvas.setFillColor(TITLE_COLOR)
    canvas.rect(x, y + sq + gap, sq, sq, stroke=0, fill=1)
    canvas.rect(x + sq + gap, y + sq + gap, sq, sq, stroke=0, fill=1)
    canvas.rect(x, y, sq, sq, stroke=0, fill=1)
    canvas.rect(x + sq + gap, y, sq, sq, stroke=0, fill=1)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.setFillColor(TITLE_COLOR)
    canvas.drawString(x + 2 * sq + 2 * gap + 6, y + 2, org_name)


def on_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(COVER_BG)
    canvas.rect(0, 0, WIDTH, HEIGHT, stroke=0, fill=1)
    _draw_cover_logo(canvas)
    canvas.restoreState()


def on_white(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(WIDTH - MARGIN, MARGIN - 14, str(doc.page))
    canvas.restoreState()


def on_chapter(canvas, doc):
    canvas.saveState()
    bg = _chapter_color_stack[-1] if _chapter_color_stack else COVER_BG
    canvas.setFillColor(bg)
    canvas.rect(0, 0, WIDTH, HEIGHT, stroke=0, fill=1)
    _draw_chapter_graphic(canvas, bg)
    canvas.restoreState()


# ── Helpers ───────────────────────────────────────────────────
def _two_col(left_els, right_els, S):
    t = Table([[left_els, right_els]], colWidths=[COL_W, COL_W])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), COL_GAP // 2),
                ("LEFTPADDING", (1, 0), (1, -1), COL_GAP // 2),
                ("RIGHTPADDING", (1, 0), (1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return t


def _code_block(code_text, S):
    return Paragraph(
        code_text.replace("\n", "<br/>").replace("  ", "&nbsp;&nbsp;"),
        S["code"],
    )


def _bullet(text, S):
    return Paragraph(f"\u2022&nbsp;&nbsp;{text}", S["bullet"])


def _rule(S):
    return HRFlowable(width="100%", thickness=0.5, color=RULE_CLR, spaceAfter=MEDIUM)


# ── Page builders (take S and data) ─────────────────────────────
def build_cover(elements, data: dict, S: dict) -> None:
    title = data.get("title", "The Hyper<br/>Platform Guide").replace("\n", "<br/>")
    subtitle = data.get("subtitle", "Build intelligent agents...")

    cover_block = [
        Spacer(1, 80),
        Paragraph(title, S["cover_title"]),
        Spacer(1, 10),
        Paragraph(subtitle.replace("\n", "<br/>"), S["cover_sub"]),
    ]
    elements.append(KeepTogether(cover_block))

    elements.append(NextPageTemplate("white"))
    elements.append(PageBreak())


def build_toc(elements, chapters: list[tuple[str, str]], S: dict) -> None:
    elements.append(Paragraph("Contents", S["toc_title"]))
    elements.append(Spacer(1, LARGE))
    for title, page in chapters:
        row = Table(
            [[Paragraph(title, S["toc_entry"]), Paragraph(page, S["toc_page"])]],
            colWidths=[CONTENT_W * 0.82, CONTENT_W * 0.18],
        )
        row.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 16),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        elements.append(row)
    elements.append(NextPageTemplate("white"))
    elements.append(PageBreak())


def build_chapter_divider(elements, title: str, color_idx: int, S: dict) -> None:
    _chapter_color_stack.append(CHAPTER_COLORS[color_idx % len(CHAPTER_COLORS)])
    elements.append(NextPageTemplate("chapter"))
    elements.append(PageBreak())

    max_spacer = HEIGHT - 2 * MARGIN - 120
    divider_block = [
        Spacer(1, min(310, max_spacer)),
        Paragraph(f"Chapter {color_idx + 1}", S["chapter_label"]),
        Spacer(1, MEDIUM),
        Paragraph(title, S["chapter_title"]),
    ]
    elements.append(KeepTogether(divider_block))

    elements.append(NextPageTemplate("white"))
    elements.append(PageBreak())


# ── Content (hardcoded sample; agent edits DATA or script) ──────
def build_intro_content(elements, S: dict) -> None:
    left = [
        Paragraph(
            "Hyper is a platform for building, deploying, and managing intelligent AI agents. "
            "It provides a comprehensive framework that handles the complexity of agent orchestration, "
            "tool management, memory systems, and multi-step workflows — so you can focus on building "
            "applications that deliver real value.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        Paragraph(
            "Whether you're building a customer support agent, a research assistant, or a complex "
            "data pipeline, Hyper gives you the building blocks to move from prototype to production "
            "with confidence.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        Paragraph(
            "This guide covers everything you need to know — from architecture and tools to "
            "workflows and deployment. Each chapter builds on the previous one, but you can "
            "jump to any section.",
            S["body"],
        ),
        Spacer(1, LARGE),
        Paragraph("What you'll learn", S["subheading"]),
        _bullet("How agents process tasks and use tools", S),
        _bullet("Building workflows with the graph system", S),
        _bullet("Managing memory and conversation state", S),
        _bullet("Deploying and monitoring in production", S),
    ]
    right = [
        Paragraph("Two paths through this guide", S["subheading"]),
        Spacer(1, SMALL),
        Paragraph(
            "<b>Building from scratch?</b> Start with Getting Started and work through "
            "each chapter sequentially. By the end you'll have a fully functional agent "
            "deployed to production.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        Paragraph(
            "<b>Extending an existing setup?</b> Jump directly to Agents &amp; Workflows "
            "or Tools &amp; Integrations. Each chapter is self-contained.",
            S["body"],
        ),
        Spacer(1, LARGE),
        Paragraph("Who this is for", S["subheading"]),
        Spacer(1, SMALL),
        _bullet("Developers building AI-powered applications", S),
        _bullet("Teams standardizing agent workflows", S),
        _bullet("Architects designing multi-agent systems", S),
        _bullet("Product engineers adding AI capabilities", S),
    ]
    elements.append(
        KeepTogether(
            [
                Paragraph("Introduction", S["heading"]),
                _rule(S),
                _two_col(left, right, S),
            ]
        )
    )


def build_chapter1_content(elements, S: dict) -> None:
    left = [
        Paragraph(
            "Get started with the Hyper CLI in under five minutes. The CLI handles environment "
            "setup, database provisioning, and service configuration automatically.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        _code_block(
            "pip install hyper-seti\nhyper init my-project\ncd my-project\nhyper dev", S
        ),
        Spacer(1, MEDIUM),
        Paragraph(
            "This starts the development server with hot-reload, a local PostgreSQL instance "
            "with pgvector, and Redis for caching.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        Paragraph("Project structure", S["subheading"]),
        Spacer(1, SMALL),
        _code_block(
            "my-project/\n\u251c\u2500\u2500 agents/\n\u251c\u2500\u2500 tools/\n"
            "\u251c\u2500\u2500 workflows/\n\u2514\u2500\u2500 config.yml",
            S,
        ),
    ]
    right = [
        Paragraph("Your first agent", S["subheading"]),
        Spacer(1, SMALL),
        Paragraph(
            "Create an agent that can search the web and summarize results.", S["body"]
        ),
        Spacer(1, MEDIUM),
        _code_block(
            'from seti import Agent\n\nagent = Agent(name="researcher", model="claude-4", '
            'tools=["web_search"], memory="persistent")\nresult = await agent.run("Find AI news")\nprint(result.content)',
            S,
        ),
        Spacer(1, MEDIUM),
        Paragraph("Next steps", S["subheading"]),
        _bullet("Add custom tools for your domain", S),
        _bullet("Configure persistent memory", S),
        _bullet("Build multi-agent workflows", S),
    ]
    elements.append(
        KeepTogether(
            [
                Paragraph("Installation", S["heading"]),
                _rule(S),
                _two_col(left, right, S),
            ]
        )
    )

    left2 = [
        Paragraph(
            "<b>Agents</b> are intelligent entities that process user requests.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        Paragraph(
            "<b>Graphs</b> orchestrate the flow of operations across nodes.", S["body"]
        ),
        Spacer(1, MEDIUM),
        Paragraph(
            "<b>Tools</b> are capabilities agents use to interact with the world.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        Paragraph(
            "<b>Memory</b> persists information across conversations.", S["body"]
        ),
    ]
    right2 = [
        Paragraph("<b>Threads</b> represent conversation sessions.", S["body"]),
        Spacer(1, MEDIUM),
        Paragraph("<b>Skills</b> are reusable task-specific guides.", S["body"]),
        Spacer(1, MEDIUM),
        Paragraph(
            "<b>Integrations</b> connect agents to external services.", S["body"]
        ),
        Spacer(1, MEDIUM),
        Paragraph(
            "<b>Traces</b> provide full observability into execution.", S["body"]
        ),
    ]
    elements.append(
        KeepTogether(
            [
                Paragraph("Key concepts", S["heading"]),
                _rule(S),
                _two_col(left2, right2, S),
            ]
        )
    )


def build_chapter2_content(elements, S: dict) -> None:
    left = [
        Paragraph(
            "Every agent follows a structured execution loop. When a user sends a message, "
            "the agent evaluates its tools, plans an action sequence, executes tools, "
            "and formulates a response.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        Paragraph("Execution loop", S["subheading"]),
        Spacer(1, SMALL),
        _bullet("Receive user message and context", S),
        _bullet("Evaluate available tools", S),
        _bullet("Plan action sequence", S),
        _bullet("Execute each action, observe results", S),
        _bullet("Synthesize observations into response", S),
        Spacer(1, MEDIUM),
        Paragraph("Agents support delegation to specialized agents.", S["body"]),
    ]
    right = [
        Paragraph("Configuration", S["subheading"]),
        Spacer(1, SMALL),
        _code_block(
            'agent = Agent(name="analyst", model="claude-4", system_prompt="...", '
            'tools=["sql_query","chart_builder"], memory=MemoryConfig(backend="postgres"), max_turns=10)',
            S,
        ),
        Spacer(1, MEDIUM),
        Paragraph("<b>system_prompt</b> — Persona and constraints.", S["body"]),
        Spacer(1, SMALL),
        Paragraph("<b>tools</b> — List of tool IDs.", S["body"]),
        Spacer(1, SMALL),
        Paragraph("<b>memory</b> — ephemeral, persistent, or vector.", S["body"]),
    ]
    elements.append(
        KeepTogether(
            [
                Paragraph("Agent architecture", S["heading"]),
                _rule(S),
                _two_col(left, right, S),
            ]
        )
    )

    left2 = [
        Paragraph(
            "Workflows are built using the graph system. A graph defines a directed flow "
            "of operations — from input, through processing nodes, to output.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        Paragraph("Node types", S["subheading"]),
        Spacer(1, SMALL),
        Paragraph(
            "<b>AgentNode</b> — Runs an agent with a prompt and tools.", S["body"]
        ),
        Spacer(1, SMALL),
        Paragraph("<b>ToolNode</b> — Executes a single tool.", S["body"]),
        Spacer(1, SMALL),
        Paragraph("<b>ConditionNode</b> — Routes flow based on a boolean.", S["body"]),
        Spacer(1, SMALL),
        Paragraph(
            "<b>ParallelNode</b> — Runs multiple branches concurrently.", S["body"]
        ),
    ]
    right2 = [
        Paragraph("Example workflow", S["subheading"]),
        Spacer(1, SMALL),
        _code_block(
            'from seti.graph import Graph\nfrom seti.graph.nodes import *\n\ng = Graph(name="research")\n'
            'g.add_node(AgentNode(id="researcher", agent="web_researcher"))\n'
            'g.add_node(AgentNode(id="writer", agent="report_writer"))\ng.add_edge("researcher","writer")',
            S,
        ),
    ]
    elements.append(
        KeepTogether(
            [
                Paragraph("Building workflows", S["heading"]),
                _rule(S),
                _two_col(left2, right2, S),
            ]
        )
    )


def build_chapter3_content(elements, S: dict) -> None:
    left = [
        Paragraph(
            "Tools are the bridge between agents and the external world. Hyper provides "
            "centralized registration, namespace isolation, and execution tracing.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        Paragraph("Built-in tools", S["subheading"]),
        Spacer(1, SMALL),
        _tool_table(
            [
                ("Web &amp; Search", "web_search, web_scrape"),
                ("Files &amp; Storage", "file_read, file_write"),
                ("Code Execution", "python, bash, sandbox"),
                ("Data &amp; Database", "sql_query, vector_search"),
                ("Communication", "email_send, slack_post"),
                ("Image &amp; Media", "image_generate, image_analyze"),
            ],
            S,
        ),
        Spacer(1, MEDIUM),
        Paragraph("Tools are scoped per workspace for strict isolation.", S["body"]),
    ]
    right = [
        Paragraph("Creating custom tools", S["subheading"]),
        Spacer(1, SMALL),
        Paragraph(
            "Define tools as Python functions with type annotations. Hyper generates "
            "the JSON schema automatically.",
            S["body"],
        ),
        Spacer(1, MEDIUM),
        _code_block(
            'from seti.tools import tool\n\n@tool(name="get_weather")\nasync def get_weather(city: str) -> dict:\n  return (await fetch(f"/api/weather/{city}")).json()',
            S,
        ),
        Spacer(1, MEDIUM),
        Paragraph("Integration patterns", S["subheading"]),
        Spacer(1, SMALL),
        _bullet("OAuth providers for Google, Slack, GitHub", S),
        _bullet("Pipedream Connect for webhooks", S),
        _bullet("MCP protocol for external tool servers", S),
    ]
    elements.append(
        KeepTogether(
            [
                Paragraph("Tool system", S["heading"]),
                _rule(S),
                _two_col(left, right, S),
            ]
        )
    )


def _tool_table(rows: list[tuple[str, str]], S: dict) -> Table:
    data = []
    for category, tools in rows:
        data.append(
            [
                Paragraph(
                    f"<b>{category}</b>",
                    ParagraphStyle(
                        "TC",
                        fontSize=9.5,
                        fontName="Helvetica-Bold",
                        textColor=TEXT_DARK,
                        leading=13,
                    ),
                ),
                Paragraph(
                    tools,
                    ParagraphStyle(
                        "TT",
                        fontSize=9,
                        fontName="Courier",
                        textColor=MUTED,
                        leading=13,
                    ),
                ),
            ]
        )
    t = Table(data, colWidths=[COL_W * 0.40, COL_W * 0.60])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e8e8e8")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


# ── Main ──────────────────────────────────────────────────────
def generate(data: dict | None = None) -> str:
    global _cover_data
    data = data or DATA
    _cover_data = data
    resolve_theme(data.get("theme", "warm_editorial"))
    S = _build_styles()

    output_path = data.get("output_path")
    if not output_path:
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "editorial.pdf")

    cover_frame = Frame(MARGIN, MARGIN, CONTENT_W, HEIGHT - 2 * MARGIN, id="cover")
    white_frame = Frame(MARGIN, MARGIN, CONTENT_W, HEIGHT - 2 * MARGIN, id="white")
    chapter_frame = Frame(MARGIN, MARGIN, CONTENT_W, HEIGHT - 2 * MARGIN, id="chapter")

    doc = BaseDocTemplate(
        output_path,
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[cover_frame], onPage=on_cover),
            PageTemplate(id="white", frames=[white_frame], onPage=on_white),
            PageTemplate(id="chapter", frames=[chapter_frame], onPage=on_chapter),
        ]
    )

    elements = []
    build_cover(elements, data, S)
    build_toc(
        elements,
        [
            ("Introduction", "3"),
            ("Getting Started", "5"),
            ("Agents &amp; Workflows", "8"),
            ("Tools &amp; Integrations", "11"),
        ],
        S,
    )
    build_intro_content(elements, S)
    build_chapter_divider(elements, "Getting Started", 0, S)
    build_chapter1_content(elements, S)
    build_chapter_divider(elements, "Agents &amp; Workflows", 1, S)
    build_chapter2_content(elements, S)
    build_chapter_divider(elements, "Tools &amp; Integrations", 2, S)
    build_chapter3_content(elements, S)

    doc.build(elements)
    size = os.path.getsize(output_path)
    print(f"Generated: {output_path} ({size:,} bytes)")
    return output_path


# ── DATA: Edit this (or the script) to customize ────────────────
DATA = {
    "theme": "terracotta",
    "title": "The Hyper\nPlatform Guide",
    "subtitle": "Build intelligent agents, orchestrate workflows,\nand deploy AI-powered applications at scale.",
    "org_name": "Hyper",
    "logo_path": None,
    "output_path": None,
}

if __name__ == "__main__":
    generate()
