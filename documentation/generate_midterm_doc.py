from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# ── Page margins ───────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.2)
    section.right_margin  = Cm(2.5)

# ── Style defaults ─────────────────────────────────────────────────────────────
doc.styles['Normal'].font.name = 'Calibri'
doc.styles['Normal'].font.size = Pt(11)

BLUE_DARK  = '1F4E79'
BLUE_MID   = '2E74B5'
BLUE_LIGHT = 'DEEAF1'
WHITE      = 'FFFFFF'

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

def h1(text):
    p = doc.add_heading(text, level=1)
    run = p.runs[0] if p.runs else p.add_run(text)
    run.font.name  = 'Calibri'
    run.font.bold  = True
    run.font.color.rgb = rgb(BLUE_DARK)
    run.font.size  = Pt(14)
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after  = Pt(8)
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
    return p

def body(text, bold=False, space_after=6):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name  = 'Calibri'
    r.font.size  = Pt(11)
    r.font.bold  = bold
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    return p

def bullet(text, bold_prefix=None):
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

def numbered(text):
    p = doc.add_paragraph(style='List Number')
    r = p.add_run(text)
    r.font.size = Pt(11)
    r.font.name = 'Calibri'
    p.paragraph_format.space_after = Pt(4)

def spacer(n=1):
    for _ in range(n):
        p = doc.add_paragraph()
        p.paragraph_format.space_after  = Pt(0)
        p.paragraph_format.space_before = Pt(0)

def table(headers, rows, col_widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header
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

    # Rows
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

# ══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ══════════════════════════════════════════════════════════════════════════════
spacer(3)

tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = tp.add_run('AGENTIC CSV ANALYST')
tr.font.name  = 'Calibri'
tr.font.size  = Pt(22)
tr.font.bold  = True
tr.font.color.rgb = rgb(BLUE_DARK)

tp2 = doc.add_paragraph()
tp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr2 = tp2.add_run('Mid-Term Report')
tr2.font.name   = 'Calibri'
tr2.font.size   = Pt(14)
tr2.font.italic = True
tr2.font.color.rgb = rgb(BLUE_MID)

spacer(2)

for label, value in [
    ('Prepared by',    'Hariharan Balaji'),
    ('Organization',   'o9 Solutions'),
    ('Date',           'June 2026'),
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lr = p.add_run(f'{label}:  ')
    lr.font.bold = True
    lr.font.size = Pt(12)
    lr.font.name = 'Calibri'
    vr = p.add_run(value)
    vr.font.size = Pt(12)
    vr.font.name = 'Calibri'

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# ABSTRACT
# ══════════════════════════════════════════════════════════════════════════════
h1('ABSTRACT')

for para in [
    ("Agentic CSV Analyst is a web-based AI platform that allows business analysts to upload "
     "structured datasets (CSV or Parquet) and interact with them through natural language "
     "queries. The system autonomously plans, writes, executes, and validates Python analytics "
     "code — returning clean, business-ready results — without requiring the analyst to write "
     "a single line of code."),

    ("The platform is built on a two-phase multi-agent pipeline powered by the AutoGen framework "
     "and a locally hosted Large Language Model (LLM) served via Ollama. In Phase 1 (Planning), "
     "a Manager agent and a Metadata Specialist agent collaborate to produce a structured "
     "Implementation Plan from the user's request and the dataset's EDA metadata. The user "
     "reviews and annotates the plan through a Plan Annotation Studio before approving execution. "
     "In Phase 2 (Execution), a Coder agent generates Python code, an Executor agent runs it "
     "in a sandboxed subprocess, and a FeedbackAgent validates the output against the original "
     "request — looping until correctness is confirmed."),

    ("The frontend is a React/Vite single-page application served by a FastAPI backend. It "
     "features a real-time streaming chat interface showing each agent's reasoning, a Monaco "
     "code editor for manual code inspection and editing, a file-system explorer for output "
     "files, and a dataset metadata viewer. Session memory is persisted across turns via a "
     "JSON context file, allowing multi-turn analytical conversations without loss of context."),

    ("The system has been applied to a North America retail revenue dataset (276,577 rows) to "
     "perform time-series forecasting and WMAPE-based forecast accuracy analysis, demonstrating "
     "its capability for end-to-end, agentic data analysis on real enterprise data."),
]:
    body(para, space_after=8)

spacer()

# Signature block
sig = doc.add_table(rows=4, cols=2)
sig.style = 'Table Grid'
labels = [
    ('Signature of the Employee', 'Signature of the Supervisor'),
    ('Name:  Hariharan Balaji',   'Name:  ______________________'),
    ('Date:  June 2026',          'Date:  ______________________'),
    ('Place: ___________________','Place: ______________________'),
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

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — MODULES
# ══════════════════════════════════════════════════════════════════════════════
h1('1. SYSTEM MODULES')

body('The Agentic CSV Analyst is composed of the following major modules:', bold=True)
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
     'api.py is the central backend. It is launched by start.bat via "python api.py" and starts '
     'a uvicorn server on port 8000, which also opens the browser automatically. It handles '
     'file upload, EDA triggering, REST APIs for plan/code/metadata, WebSocket endpoints for '
     'real-time agent streaming (/ws/run) and code execution (/ws/run_code), and serves the '
     'compiled React frontend from frontend/dist.'),

    ('(b)  CSV Analysis & EDA Module',
     'On every file upload, agents/csv_analyzer/csv_agent.py (CSVAnalysisAgent) runs a '
     '10-step EDA pipeline using eda_utils/eda.py: shape, data types, missing values, '
     'statistics, categorical summaries, numeric summaries, time column detection, duplicate '
     'detection, and data preview. The results are formatted into a Markdown report saved '
     'under generated_code/metadata/<filename>_metadata.md and aggregated into analysis.md. '
     'This metadata is the knowledge base for the Metadata Specialist agent.'),

    ('(c)  Agentic Runner — Phase 1: Planning',
     'When the user sends a query via the chat, api.py spawns agentic_runner.py as a '
     'subprocess. Phase 1 runs an AutoGen GroupChat with three agents: UserProxy (no LLM), '
     'MANAGER, and Metadata_Specialist. The Manager instructs the Metadata_Specialist to '
     'analyse the EDA metadata and the user request, then produce a formal Implementation '
     'Plan in Markdown. The plan is saved to implementation_plan.md and streamed to the '
     'frontend. The frontend then shows a Plan Annotation Studio modal where the user can '
     'highlight text and add comments, then Approve or Reject the plan.'),

    ('(d)  Agentic Runner — Phase 2: Execution',
     'After plan approval, Phase 2 runs a second AutoGen GroupChat: MANAGER, Coder, Executor, '
     'and FeedbackAgent. The Coder generates Python code (saved to generated_code/main.py). '
     'The Executor runs main.py as a subprocess and returns stdout/stderr. The FeedbackAgent '
     'validates the output against the user request. If output is incorrect, the loop retries '
     '(up to 12 rounds). On approval, FeedbackAgent emits the final user-facing answer inside '
     '<!-- FINAL_ANSWER_START --> tags, which api.py extracts and streams to the chat UI.'),

    ('(e)  Session Memory & Context Manager',
     'After each turn, a background thread runs a Context_Manager AutoGen agent which '
     'compresses the full conversation (Phase 1 + Phase 2 messages) into a structured JSON '
     'object: history_summary, key_findings, active_files, and proactive_suggestions. This '
     'is saved to session_context.json and injected into subsequent turns so agents retain '
     'full context across multi-turn conversations. Phase timings (Planning, Execution, '
     'Memory Update) are logged to phase_timings.txt and displayed in the UI as a timing bar.'),

    ('(f)  React Frontend',
     'The frontend (frontend/src/App.jsx) is a React/Vite SPA with four tabs:\n'
     '  Conversations: Live streaming chat showing each agent message in real-time. '
     'Agent thought process is collapsible per turn. A ThinkingIndicator pipeline shows '
     'which agent is active.\n'
     '  Filesystem: FileExplorer + FileViewer to browse and inspect generated output files '
     'in generated_code/.\n'
     '  Source Code: Monaco editor for generated_code/main.py with Save and Run buttons '
     '(runs via WebSocket).\n'
     '  Dataset Metadata: Per-file EDA reports from analysis.md.'),

    ('(g)  Output & File Management Module',
     'All generated output files are written inside generated_code/Output/. The folder is '
     'cleaned on every server startup. Supported outputs include: CSV results, TXT summaries, '
     'and HTML Plotly charts. The /api/files endpoint returns the full directory tree to '
     'the frontend FileExplorer. Users can also delete uploaded files via the sidebar, '
     'which also removes the associated metadata report and rebuilds analysis.md.'),
]

for title, detail in module_details:
    spacer()
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
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
h1('2. FUNCTIONAL DESCRIPTION')

body('The system operates in two distinct phases after a user submits a query. '
     'The end-to-end data flow is described below.', space_after=8)

h2('2.1  System Startup')
for s in [
    'User double-clicks start.bat → executes "python api.py".',
    'FastAPI initialises: cleans generated_code/ folder, ensures Input/, Output/, and metadata/ directories exist.',
    'A browser thread opens http://127.0.0.1:8000 after a 1.5s delay.',
    'The React frontend (frontend/dist) is served as a static SPA.',
]:
    numbered(s)

spacer()
h2('2.2  File Upload & EDA')
for s in [
    'User drags-and-drops a CSV or Parquet file onto the Upload Zone in the sidebar.',
    'Frontend POSTs the file to /upload. Progress is polled via GET /api/upload_progress every 200ms.',
    'CSVAnalysisAgent.load_csv() reads the file into a pandas DataFrame.',
    'CSVAnalysisAgent.analyze() runs 10 EDA steps: shape, dtypes, missing values, stats, categorical, numeric, time detection, duplicates, head/tail preview.',
    'MarkdownReportGenerator writes the report to generated_code/metadata/<filename>_metadata.md.',
    'analysis.md is rebuilt by concatenating all per-file metadata reports.',
    'Frontend displays EDA results in the Dataset Metadata tab.',
]:
    numbered(s)

spacer()
h2('2.3  Query Execution — Phase 1: Planning')
for s in [
    'User types a natural-language query and presses Enter or clicks Send.',
    'Frontend opens a WebSocket to /ws/run and sends the query string.',
    'api.py spawns agentic_runner.py as a subprocess, passing the query as a CLI argument.',
    'agentic_runner.py loads metadata from generated_code/metadata/ and session_context.json.',
    'AutoGen GroupChat (Phase 1) is started with: UserProxy, MANAGER, Metadata_Specialist.',
    'MANAGER instructs Metadata_Specialist to synthesise the metadata and user request into an Implementation Plan.',
    'Metadata_Specialist writes the plan to implementation_plan.md and emits PLAN_GENERATED.',
    'agentic_runner.py prints [ACTION_REQUIRED: VERIFY PLAN] to stdout.',
    'api.py streams this signal to the frontend via WebSocket.',
    'Frontend opens the Plan Annotation Studio modal. User can highlight any text and add comments.',
    'User clicks "Approve & Execute": frontend saves annotations, POSTs final plan to /api/plan, sends "yes" over WebSocket.',
    '(If rejected, user clicks "Exit Chat": WebSocket sends "no", subprocess terminates.)',
]:
    numbered(s)

spacer()
h2('2.4  Query Execution — Phase 2: Execution')
for s in [
    'agentic_runner.py receives "yes" from stdin and starts Phase 2 GroupChat: MANAGER, Coder, Executor, FeedbackAgent.',
    'MANAGER instructs Coder to implement the verified plan.',
    'Coder generates Python code inside a ```python``` block. The code is extracted and saved to generated_code/main.py.',
    'Executor runs generated_code/main.py via subprocess.run() and returns stdout/stderr.',
    'FeedbackAgent validates output against the user request and marks STATUS: APPROVED or STATUS: ERROR.',
    'On ERROR: MANAGER re-instructs Coder with the error details. Loop repeats (max 12 rounds).',
    'On APPROVED: FeedbackAgent emits the final answer inside <!-- FINAL_ANSWER_START --> tags.',
    'api.py strips the hidden tags and streams only the final answer to the frontend chat.',
    'Frontend renders the final answer as the assistant\'s response with Markdown formatting.',
]:
    numbered(s)

spacer()
h2('2.5  Session Memory Update')
for s in [
    'After Phase 2, a background thread runs Context_Manager.generate_reply() on the full turn logs.',
    'Context_Manager outputs a JSON object: history_summary, key_findings, active_files, proactive_suggestions.',
    'This is saved to session_context.json and used in the next turn\'s agent prompts.',
    'Phase timings (Planning, Plan Verification, Execution, Memory Update) are appended to phase_timings.txt.',
    'Frontend fetches timings on WebSocket close and displays them in the TimingsBar.',
    'agentic_runner.py waits for the next query from stdin ([WAITING_FOR_INPUT]).',
]:
    numbered(s)

spacer()
h2('2.6  Agent Communication Flow')

table(
    headers=['From Agent', 'To Agent', 'Signal / Content'],
    rows=[
        ['UserProxy',           'MANAGER (Ph1)',       'User request text'],
        ['MANAGER (Ph1)',       'Metadata_Specialist', 'Instruction to produce Implementation Plan'],
        ['Metadata_Specialist', 'MANAGER (Ph1)',       'Implementation Plan + PLAN_GENERATED token'],
        ['Frontend (User)',     'agentic_runner.py',   '"yes" or "no" via stdin'],
        ['MANAGER (Ph2)',       'Coder',               'Instruction to implement plan'],
        ['Coder',               'Executor',            'Python code block (saved to main.py)'],
        ['Executor',            'FeedbackAgent',       'stdout / stderr from subprocess'],
        ['FeedbackAgent',       'MANAGER (Ph2)',       'STATUS: APPROVED or STATUS: ERROR + reason'],
        ['FeedbackAgent',       'Frontend',            'Final Answer inside FINAL_ANSWER tags'],
        ['Context_Manager',     'session_context.json','Compressed JSON memory object'],
    ],
    col_widths=[1.5, 1.8, 3.4]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — TECHNICAL SPECIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════
h1('3. MAJOR TECHNICAL SPECIFICATIONS')

table(
    headers=['#', 'Parameter', 'Specification'],
    rows=[
        ['1',  'Entry Point',              'start.bat → python api.py'],
        ['2',  'Backend Framework',        'FastAPI (Python) + uvicorn'],
        ['3',  'Server Port',              '8000 (0.0.0.0)'],
        ['4',  'Frontend Framework',       'React 18 + Vite (SPA)'],
        ['5',  'UI Components',            'Monaco Editor, ReactMarkdown, Lucide Icons, Axios'],
        ['6',  'Agent Framework',          'AutoGen (pyautogen)'],
        ['7',  'LLM Backend',              'Ollama — local inference server at localhost:11434'],
        ['8',  'LLM Model',                'minimax-m2.5:cloud (configurable)'],
        ['9',  'LLM API Type',             'OpenAI-compatible REST (base_url: http://localhost:11434/v1)'],
        ['10', 'Phase 1 Agents',           'UserProxy, MANAGER, Metadata_Specialist'],
        ['11', 'Phase 2 Agents',           'UserProxy, MANAGER, Coder, Executor, FeedbackAgent'],
        ['12', 'Memory Agent',             'Context_Manager (background thread, temperature=0)'],
        ['13', 'Max Rounds — Phase 1',     '10'],
        ['14', 'Max Rounds — Phase 2',     '12'],
        ['15', 'Code Execution',           'subprocess.run() / subprocess.Popen() — no Docker'],
        ['16', 'Code Output Path',         'generated_code/main.py'],
        ['17', 'Input File Formats',       'CSV, Parquet'],
        ['18', 'Output File Formats',      'CSV, TXT, HTML (Plotly charts)'],
        ['19', 'Session Memory File',      'session_context.json (JSON)'],
        ['20', 'Phase Timing File',        'phase_timings.txt'],
        ['21', 'EDA Report Location',      'generated_code/metadata/<filename>_metadata.md'],
        ['22', 'WebSocket Endpoints',      '/ws/run (agent stream), /ws/run_code (code execution stream)'],
        ['23', 'CORS Policy',              'Allow all origins (development mode)'],
        ['24', 'OS / Platform',            'Windows 11 (asyncio.WindowsProactorEventLoopPolicy)'],
        ['25', 'Primary Libraries',        'fastapi, uvicorn, autogen, pandas, numpy, statsmodels, plotly, duckdb'],
    ],
    col_widths=[0.3, 2.2, 4.2]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DESIGN CONSIDERATIONS
# ══════════════════════════════════════════════════════════════════════════════
h1('4. DESIGN CONSIDERATIONS')

considerations = [
    ('Two-Phase Agent Architecture',
     'The planning and execution phases are deliberately separated. This ensures the LLM\'s '
     'reasoning about the data (Phase 1) is reviewed and approved by the human analyst before '
     'any code is generated or run (Phase 2), preventing wasted compute on incorrect plans.'),

    ('Human-in-the-Loop Plan Review',
     'The Plan Annotation Studio allows the analyst to highlight specific parts of the plan '
     'and attach comments before approval. These annotations are persisted via /api/annotations '
     'and visible to the agents in subsequent prompts, closing the feedback loop without '
     'requiring a full re-query.'),

    ('Local LLM via Ollama',
     'The system uses a locally hosted LLM (Ollama) instead of a cloud API. This keeps '
     'all data on-premise, avoids per-token costs, and allows model swapping by changing '
     'a single MODEL constant in agentic_runner.py.'),

    ('Subprocess Isolation for Code Execution',
     'The Executor agent runs generated Python code as a separate subprocess with its own '
     'working directory (generated_code/). This isolates execution from the FastAPI process, '
     'prevents crashes from propagating to the server, and captures stdout/stderr cleanly '
     'via PYTHONIOENCODING=utf-8.'),

    ('EDA-First Metadata Strategy',
     'Before any agent conversation begins, the uploaded dataset is fully profiled by the '
     'CSVAnalysisAgent. The structured Markdown metadata (column names, types, missing value '
     'percentages, sample values) is injected into the Metadata_Specialist\'s system prompt. '
     'This gives the planner accurate context without the LLM needing to inspect raw data.'),

    ('Noise Filtering in the WebSocket Stream',
     'AutoGen emits many internal log lines (speaker selection, termination checks, etc.) '
     'that are not meaningful to the user. The frontend applies a NOISY_PATTERNS regex '
     'filter to suppress these, ensuring only agent-authored content appears in the chat.'),

    ('Streaming Text Reveal Effect',
     'Agent messages are streamed word-by-word using a requestAnimationFrame loop at ~120 '
     'chars/sec, mimicking the feel of a live LLM stream even though the backend delivers '
     'complete lines over the WebSocket. This improves perceived responsiveness.'),

    ('Collapsible Agent Thought Process',
     'Once a final answer is available for a turn, the intermediate agent messages (Manager, '
     'Metadata_Specialist, Coder, Executor) are collapsed behind a "Show Agent thought '
     'process (N steps)" toggle, keeping the chat clean while preserving full transparency.'),

    ('DuckDB for Parquet Files',
     'The Coder agent\'s prompt mandates DuckDB SQL for Parquet file access, ensuring '
     'memory-efficient columnar reads on large files without loading them fully into pandas.'),

    ('Startup Cleanup',
     'On every server start, api.py removes all files inside generated_code/ (while keeping '
     'the folder structure). This prevents stale outputs from a previous session contaminating '
     'the current one.'),
]

for title, detail in considerations:
    bullet(detail, bold_prefix=title)
    spacer()

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — FUTURE PLAN
# ══════════════════════════════════════════════════════════════════════════════
h1('5. FUTURE PLAN')

table(
    headers=['#', 'Phase', 'Timeline', 'Work to be Done', 'Status'],
    rows=[
        ['1', 'Core Backend & Agent Pipeline',
              'Jan 2026 – Feb 2026',
              'FastAPI server, AutoGen Phase 1 + Phase 2 pipeline, Ollama LLM integration',
              'COMPLETED'],
        ['2', 'EDA Module & Metadata System',
              'Feb 2026 – Mar 2026',
              'CSVAnalysisAgent, MarkdownReportGenerator, eda_utils library, metadata directory management',
              'COMPLETED'],
        ['3', 'React Frontend — Chat & Upload',
              'Mar 2026 – Apr 2026',
              'SPA with chat UI, WebSocket streaming, file upload with progress, drag-and-drop',
              'COMPLETED'],
        ['4', 'Plan Annotation Studio',
              'Apr 2026',
              'Text highlight + comment system, annotation persistence via /api/annotations, approve/reject flow',
              'COMPLETED'],
        ['5', 'Code Editor, Filesystem & Metadata Tabs',
              'Apr 2026 – May 2026',
              'Monaco editor integration, FileExplorer, FileViewer with filter/sort/limit, Dataset Metadata tab',
              'COMPLETED'],
        ['6', 'Session Memory & Phase Timings',
              'May 2026',
              'Context_Manager background thread, session_context.json persistence, TimingsBar in UI',
              'COMPLETED'],
        ['7', 'Multi-file & Parquet Support',
              'Jun 2026',
              'Multi-file upload, per-file metadata reports, DuckDB Parquet reads in Coder agent',
              'IN PROGRESS'],
        ['8', 'Agent Self-Correction & Retry Logic',
              'Jun 2026 – Jul 2026',
              'Improved error recovery in Phase 2 loop, root-cause extraction by FeedbackAgent, smarter Coder re-prompting',
              'PENDING'],
        ['9', 'Chart & Visualisation Support',
              'Jul 2026 – Aug 2026',
              'Plotly HTML chart rendering inside the chat UI (inline iframe), chart output tab',
              'PENDING'],
        ['10','Production Hardening',
              'Aug 2026 – Sep 2026',
              'Authentication, rate limiting, Docker containerisation, HTTPS, LLM model selection UI',
              'PENDING'],
    ],
    col_widths=[0.3, 1.8, 1.4, 2.8, 1.0]
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — ABBREVIATIONS
# ══════════════════════════════════════════════════════════════════════════════
h1('6. ABBREVIATIONS')

table(
    headers=['Term', 'Expansion'],
    rows=[
        ['API',     'Application Programming Interface'],
        ['CORS',    'Cross-Origin Resource Sharing'],
        ['CSV',     'Comma-Separated Values'],
        ['EDA',     'Exploratory Data Analysis'],
        ['HTML',    'HyperText Markup Language'],
        ['JSON',    'JavaScript Object Notation'],
        ['LLM',     'Large Language Model'],
        ['MAPE',    'Mean Absolute Percentage Error'],
        ['MD',      'Markdown'],
        ['Ollama',  'Open-source local LLM inference server'],
        ['RAF',     'requestAnimationFrame (browser rendering loop)'],
        ['REST',    'Representational State Transfer'],
        ['SPA',     'Single-Page Application'],
        ['SQL',     'Structured Query Language'],
        ['SSD',     'Session State Document (session_context.json)'],
        ['UI',      'User Interface'],
        ['WebSocket','Full-duplex communication protocol over TCP'],
        ['WMAPE',   'Weighted Mean Absolute Percentage Error'],
        ['WS',      'WebSocket'],
    ],
    col_widths=[1.5, 5.2]
)

# ── Save ───────────────────────────────────────────────────────────────────────
out = r'c:\Users\hariharan.balaji\Desktop\Personal\Codebase\Agents_openai revised\documentation\mid_term_report.docx'
doc.save(out)
print(f'Saved: {out}')
