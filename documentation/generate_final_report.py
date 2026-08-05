from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

doc = Document()

BLUE_DARK  = '1F4E79'
BLUE_MID   = '2E74B5'
BLUE_LIGHT = 'DEEAF1'
WHITE      = 'FFFFFF'

# ── Front-matter constants (edit here if any detail needs correction) ──────────
TITLE               = 'AIE AUTOCODE AGENT'
STUDENT_NAME         = 'Hariharan B'
BITS_ID              = '2024DA04024'
DISCIPLINE           = 'M.Tech in Data Science and Engineering'
COURSE_NO            = 'DSECLZG628T'
COURSE_TITLE         = 'Dissertation'
ORG_NAME             = 'O9 Solutions'
ORG_LOCATION         = 'Bangalore'
STATION              = 'Bangalore'
SUPERVISOR_NAME      = 'Abhishek Hegde'
SUPERVISOR_DESIG     = 'Lead Data Scientist'
EXAMINER_NAME        = 'Nitesh Mutkekar'
EXAMINER_DESIG       = 'Senior Data Scientist'
FACULTY_MENTOR       = '[Faculty Mentor Name – to be inserted]'
REPORT_MONTH_YEAR    = 'August 2026'
DATE_OF_START        = '22 April 2026'
DATE_OF_SUBMISSION   = '02 August 2026'
DURATION             = 'April 2026 – August 2026 (approx. 4 months)'
KEY_WORDS            = ('Multi-Agent Systems, Large Language Models, AutoGen, Natural Language '
                         'to Code, Exploratory Data Analysis, Agentic AI, CSV/Parquet Analytics')
PROJECT_AREAS        = 'Artificial Intelligence, Data Science, Agentic AI Systems, Software Engineering'

_bookmark_id = [0]

# ── Low-level helpers ───────────────────────────────────────────────────────────
def rgb(hex_str):
    b = bytes.fromhex(hex_str)
    return RGBColor(b[0], b[1], b[2])

def set_cell_bg(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)

def set_page_geometry(section, width_in=9, height_in=11, margin_in=1):
    section.page_width    = Inches(width_in)
    section.page_height   = Inches(height_in)
    section.top_margin    = Inches(margin_in)
    section.bottom_margin = Inches(margin_in)
    section.left_margin   = Inches(margin_in)
    section.right_margin  = Inches(margin_in)

def set_section_page_numbering(section, fmt='decimal', start=1):
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        pgNumType = OxmlElement('w:pgNumType')
        sectPr.append(pgNumType)
    pgNumType.set(qn('w:start'), str(start))
    pgNumType.set(qn('w:fmt'), fmt)

def add_page_number_footer(section):
    section.footer.is_linked_to_previous = False
    footer = section.footer
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    for r in list(p.runs):
        r.text = ''
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText'); instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(qn('w:fldCharType'), 'end')
    r_el = run._r
    r_el.append(fldChar1); r_el.append(instrText); r_el.append(fldChar2)

def add_bookmark(paragraph, name):
    _bookmark_id[0] += 1
    bid = _bookmark_id[0]
    start = OxmlElement('w:bookmarkStart')
    start.set(qn('w:id'), str(bid))
    start.set(qn('w:name'), name)
    end = OxmlElement('w:bookmarkEnd')
    end.set(qn('w:id'), str(bid))
    paragraph._p.insert(0, start)
    paragraph._p.append(end)

def add_pageref(paragraph, bookmark_name):
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText'); instrText.set(qn('xml:space'), 'preserve')
    instrText.text = f'PAGEREF {bookmark_name} \\h'
    fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(qn('w:fldCharType'), 'separate')
    t = OxmlElement('w:t'); t.text = '#'
    fldChar3 = OxmlElement('w:fldChar'); fldChar3.set(qn('w:fldCharType'), 'end')
    r = run._r
    r.append(fldChar1); r.append(instrText); r.append(fldChar2); r.append(t); r.append(fldChar3)
    run.font.size = Pt(10)
    run.font.name = 'Calibri'

# ── Content helpers ──────────────────────────────────────────────────────────────
def h1(text, bookmark=None):
    p = doc.add_heading(text, level=1)
    run = p.runs[0] if p.runs else p.add_run(text)
    run.font.name  = 'Calibri'
    run.font.bold  = True
    run.font.color.rgb = rgb(BLUE_DARK)
    run.font.size  = Pt(14)
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after  = Pt(8)
    p.paragraph_format.line_spacing = 1.0
    if bookmark:
        add_bookmark(p, bookmark)
    return p

def h2(text):
    p = doc.add_heading(text, level=2)
    run = p.runs[0] if p.runs else p.add_run(text)
    run.font.name  = 'Calibri'
    run.font.bold  = True
    run.font.color.rgb = rgb(BLUE_MID)
    run.font.size  = Pt(12)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    return p

def body(text, bold=False, italic=False, space_after=8, center=False, double=True):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name  = 'Calibri'
    r.font.size  = Pt(11)
    r.font.bold  = bold
    r.font.italic = italic
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    if double:
        p.paragraph_format.line_spacing = 2.0
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p

def bullet(text, bold_prefix=None, double=True):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        br = p.add_run(bold_prefix + ': ')
        br.font.bold = True
        br.font.size = Pt(11)
        br.font.name = 'Calibri'
    r = p.add_run(text)
    r.font.size  = Pt(11)
    r.font.name  = 'Calibri'
    p.paragraph_format.space_after = Pt(4)
    if double:
        p.paragraph_format.line_spacing = 2.0
    return p

def numbered(text, double=True):
    p = doc.add_paragraph(style='List Number')
    r = p.add_run(text)
    r.font.size = Pt(11)
    r.font.name = 'Calibri'
    p.paragraph_format.space_after = Pt(4)
    if double:
        p.paragraph_format.line_spacing = 2.0
    return p

def spacer(n=1):
    for _ in range(n):
        p = doc.add_paragraph()
        p.paragraph_format.space_after  = Pt(0)
        p.paragraph_format.space_before = Pt(0)

def table(headers, rows, col_widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = h
        r = cell.paragraphs[0].runs[0]
        r.font.bold      = True
        r.font.size      = Pt(10)
        r.font.name      = 'Calibri'
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(cell, BLUE_DARK)

    for ri, row in enumerate(rows):
        bg = BLUE_LIGHT if ri % 2 == 0 else WHITE
        for ci, val in enumerate(row):
            cell = t.rows[ri + 1].cells[ci]
            cell.text = str(val)
            r = cell.paragraphs[0].runs[0]
            r.font.size = Pt(10)
            r.font.name = 'Calibri'
            set_cell_bg(cell, bg)

    if col_widths:
        for ri in range(len(t.rows)):
            for ci, w in enumerate(col_widths):
                t.rows[ri].cells[ci].width = Inches(w)

    spacer()
    return t

def glossary_table(headers, rows, col_widths=None):
    """Like table(), but the 3rd column of each data row gets a live PAGEREF field
    pointing at the bookmark name supplied as the row's 3rd tuple element."""
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = h
        r = cell.paragraphs[0].runs[0]
        r.font.bold      = True
        r.font.size      = Pt(10)
        r.font.name      = 'Calibri'
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(cell, BLUE_DARK)

    for ri, (term, expansion, bookmark) in enumerate(rows):
        bg = BLUE_LIGHT if ri % 2 == 0 else WHITE
        row_cells = t.rows[ri + 1].cells
        row_cells[0].text = term
        row_cells[1].text = expansion
        for c in (row_cells[0], row_cells[1]):
            r = c.paragraphs[0].runs[0]
            r.font.size = Pt(10)
            r.font.name = 'Calibri'
            set_cell_bg(c, bg)
        pcell = row_cells[2]
        pcell.text = ''
        pp = pcell.paragraphs[0]
        pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_pageref(pp, bookmark)
        set_cell_bg(pcell, bg)

    if col_widths:
        for ri in range(len(t.rows)):
            for ci, w in enumerate(col_widths):
                t.rows[ri].cells[ci].width = Inches(w)
    spacer()
    return t

def add_toc_field():
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar'); fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText'); instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-2" \\h \\z \\u'
    fldChar2 = OxmlElement('w:fldChar'); fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:t')
    fldChar3.text = "Right-click here and choose 'Update Field' to generate the Table of Contents."
    fldChar4 = OxmlElement('w:fldChar'); fldChar4.set(qn('w:fldCharType'), 'end')
    r_element = run._r
    r_element.append(fldChar1); r_element.append(instrText)
    r_element.append(fldChar2); r_element.append(fldChar3); r_element.append(fldChar4)

def update_fields_note():
    body('Note: page numbers, the Table of Contents, and the Glossary page references below '
         'are live Word fields. In Microsoft Word, press Ctrl+A then F9 (or File → Print '
         'Preview) to refresh them to their final printed page numbers before submission.',
         italic=True, space_after=8, double=False)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 0 — COVER + TITLE PAGE  (unnumbered, per guideline convention)
# ══════════════════════════════════════════════════════════════════════════════
set_page_geometry(doc.sections[0])

# ── Cover (Appendix-A layout) ──
spacer(4)
body('A REPORT', bold=True, center=True, double=False)
body('ON', bold=True, center=True, double=False)
spacer(1)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(TITLE)
r.font.bold = True
r.font.size = Pt(18)
r.font.name = 'Calibri'
r.font.color.rgb = rgb(BLUE_DARK)
spacer(3)
body('BY', bold=True, center=True, double=False)
spacer(1)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(f'{STUDENT_NAME}          ID.No.: {BITS_ID}')
r.font.size = Pt(12)
r.font.name = 'Calibri'
spacer(3)
body('AT', bold=True, center=True, double=False)
spacer(1)
body(f'({STATION} Centre)', center=True, double=False)
body(f'{ORG_NAME}, {ORG_LOCATION}', bold=True, center=True, double=False)
spacer(4)
body('BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE, PILANI', bold=True, center=True, double=False)
body(f'({REPORT_MONTH_YEAR})', center=True, double=False)
doc.add_page_break()

# ── Title Page (Appendix-B layout) ──
spacer(2)
body('A REPORT', bold=True, center=True, double=False)
body('ON', bold=True, center=True, double=False)
spacer(1)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(TITLE)
r.font.bold = True
r.font.size = Pt(18)
r.font.name = 'Calibri'
r.font.color.rgb = rgb(BLUE_DARK)
spacer(3)
body('BY', bold=True, center=True, double=False)
spacer(1)
body(f'{STUDENT_NAME}          ID No.: {BITS_ID}          {DISCIPLINE}', center=True, double=False)
spacer(2)
body('Prepared in partial fulfilment of the', center=True, double=False)
body(f'{COURSE_NO}: {COURSE_TITLE}', bold=True, center=True, double=False)
spacer(3)
body('AT', bold=True, center=True, double=False)
spacer(1)
body(f'{ORG_NAME}, {ORG_LOCATION}', bold=True, center=True, double=False)
spacer(4)
body('BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE, PILANI', bold=True, center=True, double=False)
body(f'({REPORT_MONTH_YEAR})', center=True, double=False)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — FRONT MATTER (Acknowledgements → TOC), Roman numeral pages
# ══════════════════════════════════════════════════════════════════════════════
front_section = doc.add_section(WD_SECTION.NEW_PAGE)
set_page_geometry(front_section)
set_section_page_numbering(front_section, fmt='lowerRoman', start=1)
add_page_number_footer(front_section)

h1('ACKNOWLEDGEMENTS')

body(f'I would like to express my sincere gratitude to the leadership of {ORG_NAME}, '
     f'{ORG_LOCATION}, for providing me the opportunity and the organizational support to '
     'carry out this dissertation project.')

body(f'I am deeply thankful to my Supervisor, {SUPERVISOR_NAME} ({SUPERVISOR_DESIG}, '
     f'{ORG_NAME}), for his continuous guidance, technical direction, and valuable feedback '
     'throughout the design, development, and testing of this project.')

body(f'I would also like to thank {EXAMINER_NAME} ({EXAMINER_DESIG}, {ORG_NAME}), the '
     'Additional Examiner, for his review and constructive suggestions on the project '
     'approach and methodology.')

body(f'I sincerely thank my Faculty Mentor, {FACULTY_MENTOR}, at BITS Pilani WILP Division, '
     'for his/her academic guidance and periodic review of the dissertation progress.')

body('Finally, I would like to thank my colleagues at o9 Solutions and my family for their '
     'continuous support and encouragement throughout the duration of this dissertation.')

doc.add_page_break()

# ── Abstract Sheet (Appendix-C layout) ──
h1('ABSTRACT SHEET')

body('BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE, PILANI (RAJASTHAN)', bold=True, center=True, double=False)
body('WILP Division', bold=True, center=True, double=False)
spacer()

info_rows = [
    ('Organization', f'{ORG_NAME}          Location: {ORG_LOCATION}'),
    ('Duration', DURATION),
    ('Date of Start', DATE_OF_START),
    ('Date of Submission', DATE_OF_SUBMISSION),
    ('Title of the Project', TITLE),
    ('ID No. / Name of the Student', f'{BITS_ID} / {STUDENT_NAME}'),
    ('Supervisor', f'{SUPERVISOR_NAME}, {SUPERVISOR_DESIG}, {ORG_NAME}'),
    ('Additional Examiner', f'{EXAMINER_NAME}, {EXAMINER_DESIG}, {ORG_NAME}'),
    ('Faculty Mentor', FACULTY_MENTOR),
    ('Key Words', KEY_WORDS),
    ('Project Area(s)', PROJECT_AREAS),
]
for label, value in info_rows:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    lr = p.add_run(f'{label}: ')
    lr.font.bold = True
    lr.font.size = Pt(11)
    lr.font.name = 'Calibri'
    vr = p.add_run(value)
    vr.font.size = Pt(11)
    vr.font.name = 'Calibri'

spacer()
h2('Abstract')
ABSTRACT_TEXT = (
    "Agentic CSV Analyst (“AIE Autocode Agent”) is a web-based AI platform that lets "
    "business analysts query CSV and Parquet datasets in natural language, without writing "
    "code. A two-phase multi-agent pipeline, built on the AutoGen framework with a locally "
    "hosted LLM served via Ollama, first has a Manager and Metadata Specialist agent turn "
    "dataset EDA metadata and the user's request into a structured Implementation Plan, "
    "which the user reviews and annotates in a Plan Annotation Studio before approval. A "
    "Coder agent then generates Python code, an Executor runs it, and a Feedback Agent "
    "validates the output against the request, retrying until correctness is confirmed. The "
    "system was tested across multiple datasets, including a 504-row holiday-initiative "
    "dataset and a 276,577-row North America revenue dataset used as an applied forecasting "
    "case study. Iterative testing uncovered and fixed tool-invocation and UI-streaming "
    "defects, after which the pipeline reliably produced validated, business-ready answers "
    "end-to-end. The work demonstrates a practical, metadata-driven, human-in-the-loop "
    "approach to agentic tabular data analysis."
)
_word_count = len(ABSTRACT_TEXT.split())
assert _word_count <= 200, f'Abstract exceeds 200-word guideline limit: {_word_count} words'
body(ABSTRACT_TEXT)

spacer(2)
sig = doc.add_table(rows=2, cols=2)
sig.style = 'Table Grid'
labels = [
    ('Signature of Student', 'Signature of Supervisor'),
    (f'Date: {DATE_OF_SUBMISSION}', 'Date:'),
]
for ri, (left, right) in enumerate(labels):
    for ci, val in enumerate([left, right]):
        cell = sig.rows[ri].cells[ci]
        cell.text = val
        r = cell.paragraphs[0].runs[0]
        r.font.size = Pt(10)
        r.font.name = 'Calibri'
        if ri == 0:
            r.font.bold = True

doc.add_page_break()

# ── Table of Contents ──
h1('TABLE OF CONTENTS')
update_fields_note()
add_toc_field()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — MAIN BODY (Introduction → Glossary), Arabic pages starting at 1
# ══════════════════════════════════════════════════════════════════════════════
main_section = doc.add_section(WD_SECTION.NEW_PAGE)
set_page_geometry(main_section)
set_section_page_numbering(main_section, fmt='decimal', start=1)
add_page_number_footer(main_section)

# ── INTRODUCTION ──
h1('INTRODUCTION', bookmark='bk_intro')

body("Conversational agents and Large Language Models (LLMs) have significantly improved "
     "software development and data analysis workflows in recent years. However, performing "
     "analysis on tabular datasets such as CSV and Parquet files remains a challenging task "
     "for existing LLM-based coding tools: they typically require detailed manual prompting "
     "that includes column names, data types, relationships, and dataset context, and sharing "
     "complete datasets with external models raises confidentiality concerns for sensitive "
     "organizational data. As a result, users frequently spend considerable time in repeated "
     "back-and-forth prompting to obtain accurate, optimized analytical code.")

body("This dissertation, AIE Autocode Agent (also referred to as Agentic CSV Analyst), "
     "addresses this problem by introducing a metadata-driven, multi-agent workflow that "
     "improves the efficiency and reliability of automated data analysis. Analyzer agents "
     "first study the dataset's exploratory metadata to build an accurate understanding of "
     "its structure without requiring the user to describe it manually. Based on this "
     "metadata, the agents generate a structured Implementation Plan that the user can "
     "review and annotate before any code is written. A dedicated Coder agent then "
     "generates optimized analytical code according to the approved plan, which is executed "
     "and validated in a closed feedback loop before the result is presented to the user.")

body("The objectives of the project are to: (a) build an intelligent multi-agent system for "
     "analyzing CSV and Parquet datasets efficiently; (b) automate metadata extraction and "
     "implementation planning using analyzer agents; (c) generate optimized analytical code "
     "using a dedicated coder agent; and (d) validate the correctness of generated code "
     "through an automated feedback loop before presenting results to the analyst.")

body("The scope of this dissertation is limited to designing a conversational, dialogue-based "
     "data analysis agent that can write and execute code to analyze CSV and Parquet data "
     "files and summarize the results based on user requests, deployed as a locally hosted "
     "web application. It does not cover production-scale multi-tenant deployment, "
     "authentication, or containerized execution sandboxing, which are identified as future "
     "work in Section 6.")

body("A brief survey of recent literature on multi-agent LLM systems for tabular data and "
     "code generation informed the architecture of this system: multi-agent code generation "
     "for tabular question answering [1], competitive-programming code generation frameworks "
     "[2], collaborative multi-agent table-QA frameworks [3], memory-augmented multi-agent "
     "feature generation on tabular data [4], and multi-AutoML agentic systems for tabular "
     "data [5]. Common to this literature is the separation of planning/reasoning agents from "
     "execution agents, an approach this dissertation adopts and extends with a human-in-the-"
     "loop plan-review step. The remainder of this report describes the system's modules "
     "(Section 1), its functional data flow (Section 2), technical specifications (Section 3), "
     "design considerations (Section 4), the testing carried out and its results (Section 5), "
     "and concludes with a summary of outcomes and recommendations for future work "
     "(Section 6).")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — MODULES
# ══════════════════════════════════════════════════════════════════════════════
h1('1. SYSTEM MODULES', bookmark='bk_sec1')

body('The Agentic CSV Analyst / AIE Autocode Agent platform is composed of the following '
     'major modules:', bold=True)
spacer()

modules = [
    ('(a)', 'FastAPI Backend Server'),
    ('(b)', 'CSV Analysis & EDA Module'),
    ('(c)', 'Agentic Runner — Phase 1: Planning'),
    ('(d)', 'Agentic Runner — Phase 2: Execution'),
    ('(e)', 'Session Memory & Context Manager'),
    ('(f)', 'React Frontend (Chat, Code Editor, Filesystem, Metadata Viewer)'),
    ('(g)', 'Output & File Management Module'),
]
for code, name in modules:
    p = doc.add_paragraph()
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.left_indent  = Inches(0.3)
    r1 = p.add_run(f'{code}  ')
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.name = 'Calibri'
    r2 = p.add_run(name)
    r2.font.size = Pt(11)
    r2.font.name = 'Calibri'

spacer()
h2('Module Descriptions')

module_details = [
    ('(a)  FastAPI Backend Server',
     'api.py is the central backend, launched by start.bat via "python api.py", starting a '
     'uvicorn server on port 8000 and auto-opening the browser. It handles file upload, EDA '
     'triggering, REST APIs for plan/code/metadata resources, WebSocket endpoints for '
     'real-time agent streaming (/ws/run) and code execution (/ws/run_code), and serves the '
     'compiled React frontend from frontend/dist.'),

    ('(b)  CSV Analysis & EDA Module',
     'On every file upload, the CSVAnalysisAgent runs a ten-step EDA pipeline covering shape, '
     'data types, missing values, descriptive statistics, categorical and numeric summaries, '
     'temporal column detection, duplicate detection, and data preview. Results are written '
     'as a Markdown report per file (generated_code/metadata/<filename>_metadata.md) and '
     'aggregated into analysis.md, forming the knowledge base for the Metadata Specialist '
     'agent.'),

    ('(c)  Agentic Runner — Phase 1: Planning',
     'An AutoGen GroupChat of three agents (UserProxy, MANAGER, Metadata_Specialist) '
     'synthesises the EDA metadata and the user request into a structured Implementation '
     'Plan in Markdown, saved to implementation_plan.md. The plan is streamed to the '
     'frontend, where the user can highlight text and add comments in the Plan Annotation '
     'Studio before approving or rejecting it.'),

    ('(d)  Agentic Runner — Phase 2: Execution',
     'After approval, a second GroupChat (MANAGER, Coder, Executor, FeedbackAgent) generates '
     'Python code (saved to generated_code/main.py), runs it, and validates the output '
     'against the request. The loop retries up to 12 rounds until the FeedbackAgent confirms '
     'correctness and emits the final user-facing answer inside FINAL_ANSWER delimiters.'),

    ('(e)  Session Memory & Context Manager',
     'After each turn, a background Context_Manager agent compresses the full conversation '
     'into a structured JSON object (history_summary, key_findings, active_files, '
     'proactive_suggestions), saved to session_context.json and injected into subsequent '
     'turns, enabling coherent multi-turn conversations without repeating context.'),

    ('(f)  React Frontend',
     'A React 18 / Vite single-page application with four tabs: Conversations (live '
     'streaming chat with collapsible agent reasoning), Filesystem (FileExplorer and '
     'FileViewer), Source Code (Monaco editor for main.py with Save/Run), and Dataset '
     'Metadata (per-file EDA reports).'),

    ('(g)  Output & File Management Module',
     'All generated output files are written inside generated_code/Output/, cleaned on '
     'every server startup so stale outputs do not contaminate the current session. '
     'Supported outputs include CSV results, TXT summaries, and HTML Plotly charts, exposed '
     'to the frontend FileExplorer via the /api/files endpoint.'),
]

for title, detail in module_details:
    spacer()
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 2.0
    br = p.add_run(title + '\n')
    br.font.bold      = True
    br.font.size      = Pt(11)
    br.font.name      = 'Calibri'
    br.font.color.rgb = rgb(BLUE_DARK)
    dr = p.add_run(detail)
    dr.font.size = Pt(11)
    dr.font.name = 'Calibri'

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — FUNCTIONAL DESCRIPTION
# ══════════════════════════════════════════════════════════════════════════════
h1('2. FUNCTIONAL DESCRIPTION', bookmark='bk_sec2')

body('The system operates in two distinct phases after a user submits a query. The '
     'end-to-end data flow is described below.')

h2('2.1  System Startup')
for s in [
    'User double-clicks start.bat, which executes "python api.py".',
    'FastAPI initialises the directory structure and purges stale outputs from a previous session.',
    'A background thread opens the browser at http://127.0.0.1:8000 after a 1.5-second delay.',
    'The compiled React SPA is served as a static bundle from frontend/dist.',
]:
    numbered(s)

spacer()
h2('2.2  File Upload & EDA')
for s in [
    'User drags-and-drops a CSV or Parquet file onto the upload zone.',
    'Upload progress is polled via GET /api/upload_progress every 200 ms.',
    'CSVAnalysisAgent loads the file into a pandas DataFrame and runs the ten-step EDA pipeline.',
    'The Markdown metadata report is written and the Dataset Metadata tab is updated.',
]:
    numbered(s)

spacer()
h2('2.3  Query Execution — Phase 1: Planning')
for s in [
    'The user submits a natural-language query; the frontend opens a WebSocket to /ws/run.',
    'api.py spawns agentic_runner.py, which loads EDA metadata and session context and starts the Phase 1 GroupChat.',
    'MANAGER instructs Metadata_Specialist to synthesise metadata and the user request into an Implementation Plan.',
    'Upon plan generation, the frontend presents the Plan Annotation Studio for the user to annotate.',
    'The user clicks Approve & Execute (sends "yes") or Exit Chat (sends "no", terminating the subprocess).',
]:
    numbered(s)

spacer()
h2('2.4  Query Execution — Phase 2: Execution')
for s in [
    'On approval, the Phase 2 GroupChat (MANAGER, Coder, Executor, FeedbackAgent) performs code synthesis and execution.',
    'The Coder generates a Python script; the Executor runs it as a subprocess.',
    'The FeedbackAgent evaluates correctness and marks STATUS: APPROVED or STATUS: ERROR.',
    'On error, the loop retries (maximum 12 rounds) with the error details fed back to the Coder.',
    'On approval, the final validated answer is streamed to the frontend with full Markdown rendering.',
]:
    numbered(s)

spacer()
h2('2.5  Session Memory Update')
for s in [
    'After Phase 2, the Context_Manager compresses the turn logs into session_context.json.',
    'Phase timings (Planning, Plan Verification, Execution, Memory Update) are appended to phase_timings.txt and rendered in the frontend TimingsBar.',
    'The runner then waits for the next query.',
]:
    numbered(s)

spacer()
h2('2.6  Agent Communication Flow')

table(
    headers=['Source Agent', 'Target Agent', 'Signal / Content'],
    rows=[
        ['UserProxy',           'MANAGER (Ph.1)',       'User request text'],
        ['MANAGER (Ph.1)',      'Metadata_Specialist',  'Instruction to produce Implementation Plan'],
        ['Metadata_Specialist', 'MANAGER (Ph.1)',       'Implementation Plan + PLAN_GENERATED token'],
        ['Frontend (User)',     'agentic_runner.py',    '"yes" or "no" via stdin'],
        ['MANAGER (Ph.2)',      'Coder',                'Instruction to implement approved plan'],
        ['Coder',               'Executor',             'Python code block (saved to main.py)'],
        ['Executor',            'FeedbackAgent',        'stdout / stderr from subprocess'],
        ['FeedbackAgent',       'MANAGER (Ph.2)',       'STATUS: APPROVED or STATUS: ERROR + reason'],
        ['FeedbackAgent',       'Frontend',             'Final answer inside FINAL_ANSWER delimiters'],
        ['Context_Manager',     'session_context.json', 'Compressed JSON memory object'],
    ],
    col_widths=[1.5, 1.8, 3.0]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — TECHNICAL SPECIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════
h1('3. MAJOR TECHNICAL SPECIFICATIONS', bookmark='bk_sec3')

table(
    headers=['#', 'Technical Parameter', 'Specification'],
    rows=[
        ['1',  'Entry Point',              'start.bat → python api.py'],
        ['2',  'Backend Framework',        'FastAPI (Python) + uvicorn'],
        ['3',  'Server Port',               '8000 (0.0.0.0)'],
        ['4',  'Frontend Framework',       'React 18 + Vite (SPA)'],
        ['5',  'UI Components',            'Monaco Editor, ReactMarkdown, Lucide Icons, Axios'],
        ['6',  'Agent Framework',          'AutoGen (pyautogen)'],
        ['7',  'LLM Backend',              'Ollama — local inference server at localhost:11434'],
        ['8',  'LLM Model',                'minimax-m2.5:cloud (configurable)'],
        ['9',  'LLM API Type',             'OpenAI-compatible REST (base_url: localhost:11434/v1)'],
        ['10', 'Phase 1 Agents',           'UserProxy, MANAGER, Metadata_Specialist'],
        ['11', 'Phase 2 Agents',           'UserProxy, MANAGER, Coder, Executor, FeedbackAgent'],
        ['12', 'Memory Agent',             'Context_Manager (background thread, temperature = 0)'],
        ['13', 'Max Rounds — Phase 1', '10'],
        ['14', 'Max Rounds — Phase 2', '12'],
        ['15', 'Code Execution',           'subprocess.run() / subprocess.Popen() — no Docker'],
        ['16', 'Code Output Path',         'generated_code/main.py'],
        ['17', 'Input File Formats',       'CSV, Parquet'],
        ['18', 'Output File Formats',      'CSV, TXT, HTML (Plotly charts)'],
        ['19', 'Session Memory File',      'session_context.json (JSON)'],
        ['20', 'Phase Timing File',        'phase_timings.txt'],
        ['21', 'EDA Report Location',      'generated_code/metadata/<filename>_metadata.md'],
        ['22', 'WebSocket Endpoints',      '/ws/run (agent stream), /ws/run_code (code stream)'],
        ['23', 'CORS Policy',              'Allow all origins (development mode)'],
        ['24', 'OS / Platform',            'Windows 11 (WindowsProactorEventLoopPolicy)'],
        ['25', 'Primary Libraries',        'fastapi, uvicorn, autogen, pandas, numpy, statsmodels, plotly, duckdb'],
    ],
    col_widths=[0.3, 2.0, 3.9]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DESIGN CONSIDERATIONS
# ══════════════════════════════════════════════════════════════════════════════
h1('4. DESIGN CONSIDERATIONS', bookmark='bk_sec4')

considerations = [
    ('Two-Phase Agent Architecture',
     'Planning and execution are deliberately separated so that the LLM’s reasoning about '
     'the data is reviewed and approved by the human analyst before any code is generated or '
     'run, preventing wasted compute on incorrect plans.'),
    ('Human-in-the-Loop Plan Review',
     'The Plan Annotation Studio lets the analyst highlight parts of the plan and attach '
     'comments before approval. Annotations are persisted via /api/annotations and injected '
     'into subsequent agent prompts, closing the feedback loop without a full re-query.'),
    ('Local LLM via Ollama',
     'A locally hosted LLM keeps all data on-premises, eliminates per-token costs, and '
     'allows model swapping by changing a single MODEL constant in agentic_runner.py.'),
    ('Subprocess Isolation for Code Execution',
     'The Executor runs generated code as a separate subprocess with its own working '
     'directory, isolating execution from the FastAPI process and capturing stdout/stderr '
     'cleanly via PYTHONIOENCODING=utf-8.'),
    ('EDA-First Metadata Strategy',
     'The dataset is fully profiled before any agent conversation begins. The structured '
     'metadata is injected into the Metadata_Specialist’s system prompt, giving the planner '
     'accurate context without inspecting raw data.'),
    ('WebSocket Noise Filtering',
     'The frontend applies a NOISY_PATTERNS regex filter to suppress AutoGen’s internal log '
     'lines, ensuring only agent-authored content appears in the chat.'),
    ('DuckDB for Parquet Files',
     'The Coder agent is mandated to use DuckDB SQL (SQL [see Glossary]) for Parquet access, '
     'ensuring memory-efficient columnar reads on large files without loading them fully '
     'into pandas.'),
    ('Startup Cleanup',
     'On every server start, all files inside generated_code/ are removed (folder structure '
     'preserved), preventing stale outputs from contaminating the current session.'),
]

for title, detail in considerations:
    bullet(detail, bold_prefix=title)
    spacer()

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — TESTING AND RESULTS
# ══════════════════════════════════════════════════════════════════════════════
h1('5. TESTING AND RESULTS', bookmark='bk_sec5')

body('The system was tested iteratively through the design and development cycle by running '
     'a series of natural-language analytical queries against multiple real datasets, '
     'including a holiday-initiative dataset (504 rows) and a North America retail revenue '
     'dataset (276,577 rows across 10 dimensions). Each query was carried through the full '
     'Phase 1 (planning) and Phase 2 (execution) pipeline, and the FeedbackAgent’s '
     'STATUS: APPROVED / STATUS: ERROR verdicts, together with manual inspection of the '
     'generated output, were used to judge correctness.')

h2('5.1  Defects Found and Fixed')
for title, detail in [
    ('Tool-invocation mismatches',
     'Early execution runs showed the Coder/Executor/FeedbackAgent chat attempting to call '
     'tool names (e.g. Bash, execute_code, mcp_code_executor) that were not registered as '
     'callable functions, causing "Function not found" errors and wasted retry rounds. This '
     'was fixed by aligning the agents’ tool-call prompts with the actual registered '
     'code-execution function so that generated code is consistently routed through the '
     'Executor’s subprocess runner.'),
    ('Streaming and UI defects',
     'A series of UI issues were identified and fixed across the build history — the '
     'word-by-word text-stream renderer, the chat loading/typing indicator, and related '
     'front-end display bugs (Builds 8.1–8.5) — to ensure the live agent stream renders '
     'reliably without stalling or duplicating content.'),
    ('Plan-approval flow',
     'The yes/no handshake between the frontend and the agentic_runner.py subprocess was '
     'hardened so that a rejected plan cleanly terminates the subprocess instead of leaving '
     'a stale process running.'),
]:
    bullet(detail, bold_prefix=title)
    spacer()

h2('5.2  Functional Test Outcomes')
for s in [
    'Holiday-initiative dataset: the system correctly identified 504 unique holiday records and correctly determined that all records belonged to a single location (Canada), matching manual verification of the source CSV.',
    'North America revenue dataset (case study): the system correctly loaded 276,577 rows, auto-detected the forecast horizon start month (July 2024) for both USA and Canada, and computed WMAPE of 12.49% (USA) and 35.4% (Canada) for the existing enterprise forecast — correctly benchmarking it as more accurate than the system-generated statistical baseline for both locations.',
    'After the fixes described in Section 5.1, repeated runs of representative queries completed within the 12-round Phase 2 retry limit and produced FeedbackAgent-approved, business-ready answers end-to-end, without manual intervention beyond the plan-approval step.',
]:
    numbered(s)

spacer()
h2('5.3  Known Limitations')
for title, detail in [
    ('No sandbox containerization',
     'Generated code executes via subprocess.run() on the host machine rather than inside '
     'a container, which is acceptable for a locally hosted, single-user tool but is not '
     'suitable for untrusted multi-tenant deployment.'),
    ('Bounded retry loop',
     'Phase 2 is capped at 12 rounds; highly ambiguous or malformed requests can still '
     'exhaust the retry budget without producing an approved answer.'),
    ('Development-mode security posture',
     'CORS is configured to allow all origins and there is no authentication layer, both of '
     'which are appropriate for local development but must be hardened before any shared '
     'or production deployment.'),
]:
    bullet(detail, bold_prefix=title)
    spacer()

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — CONCLUSIONS AND RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
h1('6. CONCLUSIONS AND RECOMMENDATIONS', bookmark='bk_sec6')

h2('6.1  Conclusions')
body('This dissertation designed, implemented, and tested AIE Autocode Agent, a two-phase '
     'multi-agent system that lets a business analyst analyze CSV and Parquet datasets '
     'through natural language, without writing code. The EDA-first metadata strategy, the '
     'human-in-the-loop Plan Annotation Studio, and the Coder/Executor/FeedbackAgent '
     'retry loop together produce analytical answers that are both automatically generated '
     'and independently validated before being shown to the user.')

body('Testing across multiple datasets, including a 504-row holiday-initiative dataset and '
     'a 276,577-row North America revenue dataset used as an applied case study, confirmed '
     'that the pipeline correctly loads data, plans an approach, generates and executes '
     'code, and validates the result. Iterative testing surfaced concrete defects — '
     'mismatched tool-invocation names and several UI streaming issues — all of which were '
     'fixed during the development cycle (Builds 4.0 through 8.5), after which the system '
     'produced stable, correct, end-to-end results.')

body('The project met its stated objectives: an intelligent multi-agent system for '
     'analyzing CSV/Parquet datasets was built; metadata extraction and implementation '
     'planning were automated through analyzer agents; optimized analytical code was '
     'generated by a dedicated Coder agent; and correctness was validated through an '
     'automated feedback loop before results were presented to the analyst.')

spacer()
h2('6.2  Recommendations for Future Work')
for title, detail in [
    ('Containerized execution sandbox',
     'Replace direct subprocess execution with a per-request Docker (or similar) sandbox to '
     'safely support untrusted code execution in a shared or production deployment.'),
    ('Authentication and multi-user session isolation',
     'Add an authentication layer and per-user session/context isolation ahead of any '
     'shared or production rollout, and restrict CORS from the current development-mode '
     '"allow all origins" policy.'),
    ('Inline chart rendering',
     'Render Plotly HTML chart outputs directly inside the chat interface rather than as a '
     'separate output file, improving the analyst’s workflow.'),
    ('Automated regression test suite',
     'Add an automated test suite covering agent prompt/tool-name contracts (to catch the '
     'class of "function not found" defect found in Section 5.1) and the Phase 1 / Phase 2 '
     'WebSocket handshake.'),
    ('Deeper analytical drill-down',
     'Extend the system, as demonstrated in the revenue-forecasting case study, to support '
     'channel-level and product-planning-level drill-down analysis, and to allow larger or '
     'cloud-hosted LLMs to be swapped in for more complex analytical requests.'),
]:
    bullet(detail, bold_prefix=title)
    spacer()

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# APPENDICES
# ══════════════════════════════════════════════════════════════════════════════
h1('APPENDICES', bookmark='bk_appendices')

h2('Appendix I — System Architecture Diagram')
diagram_path = os.path.join(os.path.dirname(__file__), 'architecture_diagram.png')
if os.path.exists(diagram_path):
    doc.add_picture(diagram_path, width=Inches(6.2))
    last_p = doc.paragraphs[-1]
    last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
else:
    body('[architecture_diagram.png not found — regenerate via generate_diagram.py]')

doc.add_page_break()

h2('Appendix II — Sample Implementation Plan')
body('The following is a representative Implementation Plan produced by the Phase 1 '
     'Metadata_Specialist agent, taken from an actual run of the system '
     '(implementation_plan.md):')

plan_lines = [
    'Context: The user wants to know how many holidays are present in the dataset. Based on '
    'the provided metadata, the relevant dataset is Fact.Holiday Initiative.csv.',
    'Data Source: generated_code/Input/Fact.Holiday Initiative.csv — key column '
    'Initiative.[Initiative] contains holiday names with year suffixes (e.g. "Canada Day_2020").',
    'Analysis Summary: Total Rows: 504; Unique Values in Initiative.[Initiative]: 504; each row '
    'represents a unique holiday instance.',
    'Implementation Steps: (1) Load the CSV file from the input directory. (2) Count the '
    'unique values in the Initiative.[Initiative] column. (3) Return the count as the answer.',
    'Expected Output: The number of unique holidays present in the dataset (expected: 504).',
]
for s in plan_lines:
    bullet(s)

doc.add_page_break()

h2('Appendix III — Sample Session Memory Object')
body('The following JSON object illustrates the compressed memory produced by the '
     'Context_Manager agent and persisted to session_context.json after a completed turn:')

sample_json = '''{
  "history_summary": "User requested analysis of holiday initiative data to count unique
    holidays, identify locations, and count holidays per location. Code executed successfully
    using pandas to load and analyze Fact.Holiday Initiative.csv.",
  "key_findings": [
    "504 unique holidays found in the dataset",
    "Only 1 unique location: Canada",
    "All 504 holiday records are associated with Canada location",
    "Dataset contains 504 total rows with 9 columns",
    "Location column: Initiative Location Scope; Holiday column: Initiative.[Initiative]"
  ],
  "active_files": ["generated_code/Input/Fact.Holiday Initiative.csv"],
  "proactive_suggestions": [
    "Explore if there are other location-related columns with more location data",
    "Analyze holidays by other dimensions like Channel or Item",
    "Check if holiday names have year information for temporal analysis"
  ]
}'''
p = doc.add_paragraph()
r = p.add_run(sample_json)
r.font.name = 'Consolas'
r.font.size = Pt(9)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# REFERENCES
# ══════════════════════════════════════════════════════════════════════════════
h1('REFERENCES', bookmark='bk_references')

references = [
    'Osei-Brefo, E. and Liang, H., "A Multi-Agent LLM Code Generation Approach for '
    'Answering Tabular Questions," Proceedings of the 19th International Workshop on '
    'Semantic Evaluation (SemEval-2025), 2025, pp. 343–349.',
    'Islam, M. A., Ali, M. E. and Parvez, M. R., "MapCoder: Multi-Agent Code Generation '
    'for Competitive Problem Solving," Conference Paper, Monash University, 2024.',
    'Wang, T., Jin, C., Chen, Y., Deng, H., Kuang, X. and Zhao, G., "DataFactory: '
    'Collaborative Multi-Agent Framework for Advanced Table Question Answering," '
    'Information Processing & Management, 2026.',
    'Dong, F., Zheng, Z., Han, X., Chen, W., Ruan, J., Xu, T., Chen, Y. and Chen, E., '
    '"Memory-Augmented LLM-based Multi-Agent System for Automated Feature Generation on '
    'Tabular Data," ACL ARR 2026.',
    'Lapin, A., Hromov, I., Chumakov, S., Mitrovic, M., Simakov, D., Nikitin, N. O. and '
    'Savchenko, A. V., "LightAutoDS-Tab: Multi-AutoML Agentic System for Tabular Data," '
    'arXiv, 2025.',
]
for i, ref in enumerate(references, start=1):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 2.0
    r = p.add_run(f'{i}.  {ref}')
    r.font.size = Pt(11)
    r.font.name = 'Calibri'

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# GLOSSARY  (Term | Expansion | Page No. — live PAGEREF to first-occurrence section)
# ══════════════════════════════════════════════════════════════════════════════
h1('GLOSSARY', bookmark='bk_glossary')
body('Page numbers below reference the section in which each term first appears; refresh '
     'via Ctrl+A then F9 in Word before printing.', italic=True, double=False, space_after=8)

glossary_table(
    headers=['Term', 'Expansion', 'Page No.'],
    rows=[
        ['API',       'Application Programming Interface',                'bk_sec2'],
        ['CORS',      'Cross-Origin Resource Sharing',                    'bk_sec3'],
        ['CSV',       'Comma-Separated Values',                           'bk_intro'],
        ['EDA',       'Exploratory Data Analysis',                        'bk_sec1'],
        ['HTML',      'HyperText Markup Language',                        'bk_sec3'],
        ['JSON',      'JavaScript Object Notation',                       'bk_sec1'],
        ['LLM',       'Large Language Model',                             'bk_intro'],
        ['MAPE',      'Mean Absolute Percentage Error',                   'bk_sec5'],
        ['MD',        'Markdown',                                        'bk_sec1'],
        ['Ollama',    'Open-source local LLM inference server',          'bk_sec3'],
        ['RAF',       'requestAnimationFrame (browser rendering loop)',  'bk_sec5'],
        ['REST',      'Representational State Transfer',                 'bk_sec3'],
        ['SPA',       'Single-Page Application',                         'bk_sec1'],
        ['SQL',       'Structured Query Language',                        'bk_sec4'],
        ['SSD',       'Session State Document (session_context.json)',   'bk_sec3'],
        ['UI',        'User Interface',                                  'bk_sec5'],
        ['WebSocket', 'Full-duplex communication protocol over TCP',     'bk_sec2'],
        ['WMAPE',     'Weighted Mean Absolute Percentage Error',         'bk_sec5'],
        ['WS',        'WebSocket',                                       'bk_sec3'],
    ],
    col_widths=[1.3, 4.0, 1.0]
)

# ── Save ─────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), 'final_report.docx')
doc.save(out)
print(f'Saved: {out}')
print(f'Abstract word count: {_word_count} (limit 200)')
