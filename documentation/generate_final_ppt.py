"""
Builds AIE_Final_Review.pptx in the same visual template as AIE_Midterm_Review.pptx
(same geometry, colors, fonts) but with content updated for the final dissertation
review, pulled from Final_report_v1.docx (Testing & Results, Conclusions &
Recommendations, final development status).
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
import os

NAVY       = RGBColor(0x1E, 0x27, 0x61)
TEAL       = RGBColor(0x06, 0x5A, 0x82)
ORANGE     = RGBColor(0xF5, 0xA6, 0x23)
AMBER      = RGBColor(0xD9, 0x77, 0x06)
GREEN      = RGBColor(0x16, 0xA3, 0x4A)
GRAY       = RGBColor(0x94, 0xA3, 0xB8)
CARD_BG    = RGBColor(0xF4, 0xF6, 0xFB)
TEXT_DARK  = RGBColor(0x1E, 0x29, 0x3B)
TEXT_SUB   = RGBColor(0x64, 0x74, 0x8B)
TEXT_LIGHT = RGBColor(0xCA, 0xDC, 0xFC)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(5.625)
BLANK = prs.slide_layouts[6]

def add_slide():
    return prs.slides.add_slide(BLANK)

def set_slide_bg(slide, rgb):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = rgb

def add_rect(slide, l, t, w, h, fill_rgb, alpha=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_rgb
    shp.line.fill.background()
    shp.shadow.inherit = False
    if alpha is not None:
        _set_alpha(shp, alpha)
    return shp

def add_ellipse(slide, l, t, w, h, fill_rgb, alpha=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_rgb
    shp.line.fill.background()
    shp.shadow.inherit = False
    if alpha is not None:
        _set_alpha(shp, alpha)
    return shp

def _set_alpha(shape, pct):
    srgb = shape.fill.fore_color._xFill.find(qn('a:srgbClr'))
    a = srgb.makeelement(qn('a:alpha'), {'val': str(int(pct * 1000))})
    srgb.append(a)

def add_text(slide, l, t, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, word_wrap=True):
    """runs: list of (text, size_pt, bold, color_rgb) — each becomes its own paragraph
    unless a tuple item is a list itself (multiple runs on one line)."""
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = word_wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, para_runs in enumerate(runs):
        if isinstance(para_runs, tuple):
            para_runs = [para_runs]
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for text, size, bold, color in para_runs:
            r = p.add_run()
            r.text = text
            r.font.name = 'Calibri'
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = color
    return box

def header_bar(slide, title_text):
    add_rect(slide, 0, 0, 10, 0.8, NAVY)
    add_text(slide, 0.4, 0, 9.2, 0.8, [(title_text, 26, True, WHITE)], anchor=MSO_ANCHOR.MIDDLE)

def card(slide, l, t, w, h, header_text, header_h=0.4, header_color=NAVY, body_runs=None):
    add_rect(slide, l, t, w, h, CARD_BG)
    add_rect(slide, l, t, w, header_h, header_color)
    add_text(slide, l, t, w, header_h, [(header_text, 11, True, WHITE)],
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if body_runs:
        add_text(slide, l + 0.12, t + header_h + 0.1, w - 0.24, h - header_h - 0.15, body_runs)

def bullet_row(slide, l, t, w, label, desc, dot_color=NAVY, label_w=1.65):
    add_rect(slide, l, t + 0.03, 0.14, 0.14, dot_color)
    add_text(slide, l + 0.22, t - 0.03, label_w, 0.28, [(label, 10, True, NAVY)])
    add_text(slide, l + 0.22 + label_w + 0.15, t - 0.03, w - label_w - 0.37, 0.28,
              [(desc, 10, False, TEXT_DARK)])

def add_table(slide, l, t, w, h, headers, rows, col_widths, header_bg=NAVY):
    n_rows, n_cols = 1 + len(rows), len(headers)
    gframe = slide.shapes.add_table(n_rows, n_cols, Inches(l), Inches(t), Inches(w), Inches(h))
    tbl = gframe.table
    for ci, cw in enumerate(col_widths):
        tbl.columns[ci].width = Inches(cw)
    for ci, htext in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.text = htext
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_bg
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.runs[0]
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.name = 'Calibri'
        r.font.color.rgb = WHITE
    for ri, row in enumerate(rows, start=1):
        bg = CARD_BG if ri % 2 == 1 else WHITE
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            r = p.runs[0]
            r.font.size = Pt(10)
            r.font.name = 'Calibri'
            r.font.color.rgb = TEXT_DARK
    return gframe

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════════════════════════════
s1 = add_slide()
set_slide_bg(s1, NAVY)
add_ellipse(s1, 7.8, -1.2, 4.0, 4.0, WHITE, alpha=8)
add_ellipse(s1, 8.3, -0.7, 3.0, 3.0, WHITE, alpha=12)
add_text(s1, 0.6, 1.3, 8.8, 1.0, [('AIE AUTOCODE AGENT', 40, True, WHITE)])
add_text(s1, 0.6, 2.25, 8.8, 0.55, [('Final Dissertation Review', 20, False, TEXT_LIGHT)])
add_rect(s1, 0.6, 2.95, 3.5, 0.05, ORANGE)
add_text(s1, 0.6, 3.1, 8.8, 1.2, [
    [('Hariharan B  |  2024DA04024', 13, False, TEXT_LIGHT)],
    [('M.Tech in Data Science and Engineering', 13, False, TEXT_LIGHT)],
    [('O9 Solutions, Bangalore  |  August 2026', 13, False, TEXT_LIGHT)],
])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — SYSTEM OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
s2 = add_slide()
header_bar(s2, 'System Overview')
add_text(s2, 0.4, 0.92, 9.2, 0.55, [(
    'AIE Autocode Agent is a web-based AI platform that lets business analysts query '
    'structured datasets through natural language, with zero code required.', 11.5, False, TEXT_SUB)])

cards2 = [
    ('Upload & Understand',
     'Analysts upload CSV or Parquet files. A 10-step EDA pipeline automatically profiles '
     'the dataset: shape, types, missing values, statistics and duplicates. It then writes '
     'a structured Markdown report.'),
    ('Plan & Review',
     'A Phase 1 multi-agent group (Manager + Metadata Specialist) synthesises EDA metadata '
     'into an Implementation Plan. The user reviews, annotates, and approves it before any '
     'code runs.'),
    ('Generate & Validate',
     'Phase 2 agents (Coder, Executor, FeedbackAgent) generate Python code, execute it, and '
     'validate the output, retrying up to 12 rounds, then stream the final answer back to '
     'the chat.'),
]
for i, (h, b) in enumerate(cards2):
    l = 0.3 + i * 3.35
    card(s2, l, 1.55, 3.1, 1.85, h, body_runs=[(b, 9.5, False, TEXT_DARK)])

add_text(s2, 0.4, 3.52, 9.2, 0.3, [('Technology Stack', 12, True, NAVY)])
tech = [
    ('AutoGen Framework:', 'Multi-agent orchestration for both planning and execution phases'),
    ('Ollama (Local LLM):', 'On-premises inference. No data leaves the machine, no per-token cost'),
    ('FastAPI + React 18:', 'Backend REST/WebSocket server + real-time streaming chat frontend'),
    ('Session Memory:', 'Context_Manager compresses each turn into session_context.json for coherent multi-turn dialogue'),
]
for i, (label, desc) in enumerate(tech):
    bullet_row(s2, 0.3, 3.94 + i * 0.33, 9.1, label, desc)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — SYSTEM ARCHITECTURE (unchanged — still accurate at final stage)
# ══════════════════════════════════════════════════════════════════════════════
s3 = add_slide()
header_bar(s3, 'System Architecture Overview')
add_text(s3, 0.4, 0.9, 9.2, 0.4, [('Two-Phase Multi-Agent Pipeline', 14, True, NAVY)])

def phase_card(slide, l, header_text, header_color, accent_color, items):
    add_rect(slide, l, 1.35, 4.5, 3.5, CARD_BG)
    add_rect(slide, l, 1.35, 4.5, 0.45, header_color)
    add_text(slide, l, 1.35, 4.5, 0.45, [(header_text, 13, True, WHITE)],
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    y = 1.9
    for label, desc in items:
        add_text(slide, l + 0.25, y, 4.0, 0.22, [(label, 11, True, accent_color)])
        add_text(slide, l + 0.25, y + 0.21, 4.0, 0.28, [(desc, 9.5, False, TEXT_SUB)])
        y += 0.58

phase_card(s3, 0.3, 'Phase 1: Planning', NAVY, NAVY, [
    ('User Proxy Agent', 'Bridges user queries to the planning pipeline'),
    ('Manager Agent', 'Orchestrates planning agents and collects the plan'),
    ('Metadata Specialist', 'Analyses EDA metadata and produces the Implementation Plan'),
    ('Plan Annotation Studio', 'Human-in-the-loop review, highlight & comment before approval'),
])
phase_card(s3, 5.2, 'Phase 2: Execution', TEAL, TEAL, [
    ('Coder Agent', 'Generates Python analytics code from the approved plan'),
    ('Executor Agent', 'Runs code via subprocess; captures stdout/stderr'),
    ('Feedback Agent', 'Validates output against original query (up to 12 rounds)'),
    ('Context Manager', 'Compresses turn logs into session_context.json for memory'),
])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — TESTING, RESULTS & TECHNICAL SPECIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════
s4 = add_slide()
header_bar(s4, 'Testing, Results & Technical Specifications')
add_text(s4, 0.4, 0.9, 4.6, 0.35, [('Testing & Key Results', 13, True, NAVY)])

result_cards = [
    ('Defects Found & Fixed',
     'Tool-invocation mismatches and UI-streaming issues were identified and resolved '
     'across the build cycle (Builds 4.0-8.5).'),
    ('Functional Validation',
     '504-row holiday dataset and 276,577-row NA revenue dataset both produced correct, '
     'FeedbackAgent-approved answers end-to-end.'),
    ('Forecasting Case Study',
     'WMAPE benchmarking: 12.49% (USA) and 35.4% (Canada) vs. the existing enterprise '
     'forecast, correctly identified as more accurate.'),
    ('Known Limitations',
     'No execution sandboxing, a bounded 12-round retry loop, and a dev-mode CORS/auth '
     'posture are flagged for future hardening.'),
]
for i, (h, b) in enumerate(result_cards):
    t = 1.32 + i * 0.86
    add_rect(s4, 0.3, t, 4.6, 0.75, CARD_BG)
    add_text(s4, 0.45, t + 0.05, 4.3, 0.22, [(h, 10.5, True, NAVY)])
    add_text(s4, 0.45, t + 0.26, 4.3, 0.42, [(b, 9.5, False, TEXT_DARK)])

add_text(s4, 5.15, 0.9, 4.6, 0.35, [('Technical Specifications', 13, True, NAVY)])
add_table(s4, 5.15, 1.32, 4.6, 3.8,
    headers=['Parameter', 'Specification'],
    rows=[
        ['Backend', 'FastAPI + uvicorn (port 8000)'],
        ['Frontend', 'React 18 + Vite SPA'],
        ['Agent Framework', 'AutoGen (pyautogen)'],
        ['LLM', 'Ollama, minimax-m2.5:cloud (local)'],
        ['Max Rounds', 'Phase 1: 10  |  Phase 2: 12'],
        ['Input Formats', 'CSV, Apache Parquet'],
        ['Output Formats', 'CSV, TXT, HTML (Plotly charts)'],
        ['Code Execution', 'subprocess.run(), isolated process'],
    ],
    col_widths=[1.7, 2.9])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — DEVELOPMENT ROADMAP & FINAL STATUS
# ══════════════════════════════════════════════════════════════════════════════
s5 = add_slide()
header_bar(s5, 'Project Status')
add_text(s5, 0.4, 0.88, 9.2, 0.35, [('Development Roadmap & Final Status', 13, True, NAVY)])

legend = [('Completed', GREEN), ('In Progress', AMBER), ('Pending', GRAY)]
lx = 0.4
for label, color in legend:
    add_rect(s5, lx, 1.28, 0.18, 0.18, color)
    add_text(s5, lx + 0.22, 1.25, 1.3, 0.24, [(label, 10, False, TEXT_DARK)])
    lx += 1.4

add_table(s5, 0.3, 1.52, 9.4, 3.8,
    headers=['#', 'Phase', 'Description', 'Status'],
    rows=[
        ['1', 'Dissertation Outline', 'Expand knowledge base and prepare dissertation outline', 'COMPLETED'],
        ['2', 'Literature Review', 'Expand literature review and study of market data analysis', 'COMPLETED'],
        ['3', 'Design & Development', 'System design, multi-agent pipeline, frontend/backend build', 'COMPLETED'],
        ['4', 'Testing', 'Software testing, user evaluation, bug fixes (Builds 4.0-8.5)', 'COMPLETED'],
        ['5', 'Dissertation Review', 'Submit to supervisor and additional examiner for feedback', 'COMPLETED'],
        ['6', 'Final Submission', 'Final review and submission of dissertation to BITS Pilani', 'COMPLETED'],
    ],
    col_widths=[0.4, 1.7, 5.3, 2.0])

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — CONCLUSIONS & RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
s6 = add_slide()
header_bar(s6, 'Conclusions & Recommendations')
add_text(s6, 0.4, 0.9, 4.5, 0.35, [("What's Been Achieved", 13, True, NAVY)])
achieved = [
    'Full two-phase multi-agent pipeline designed, implemented, and tested end-to-end',
    'EDA-first metadata strategy validated across multiple real datasets',
    'Human-in-the-loop Plan Annotation Studio built and used in every run',
    'Iterative testing found and fixed tool-invocation and UI-streaming defects',
    'Applied as a forecasting case study, benchmarking WMAPE against an enterprise forecast',
    'All stated dissertation objectives met',
]
add_text(s6, 0.4, 1.32, 4.5, 3.5, [(f'•  {a}', 11, False, TEXT_DARK) for a in achieved])

add_text(s6, 5.15, 0.9, 4.5, 0.35, [('Recommendations for Future Work', 13, True, NAVY)])
recs = [
    ('Containerized Sandbox', AMBER,
     'Replace subprocess execution with a per-request Docker sandbox for safe multi-tenant use.'),
    ('Auth & Session Isolation', NAVY,
     'Add authentication and per-user session isolation; restrict CORS before production.'),
    ('Deeper Analytical Drill-Down', GREEN,
     'Extend to channel/product-level forecasting and allow larger cloud-hosted LLMs for complex requests.'),
]
for i, (label, color, desc) in enumerate(recs):
    t = 1.32 + i * 0.87
    add_rect(s6, 5.1, t, 4.6, 0.75, CARD_BG)
    add_text(s6, 5.25, t + 0.04, 4.2, 0.22, [(label, 10.5, True, color)])
    add_text(s6, 5.25, t + 0.26, 4.2, 0.4, [(desc, 9.5, False, TEXT_DARK)])

add_rect(s6, 0.3, 5.1, 9.4, 0.4, NAVY)
add_text(s6, 0.3, 5.1, 9.4, 0.4, [(
    'AIE Autocode Agent  |  Hariharan B  |  2024DA04024  |  BITS Pilani, August 2026',
    10.5, False, TEXT_LIGHT)], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ── Save ─────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), 'AIE_Final_Review.pptx')
prs.save(out)
print(f'Saved: {out}')
