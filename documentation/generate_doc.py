from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Page margins ──────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.5)

# ── Styles helper ─────────────────────────────────────────────────────────────
normal_style = doc.styles['Normal']
normal_style.font.name = 'Calibri'
normal_style.font.size = Pt(11)

def set_cell_bg(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def heading(text, level=1, color=None, center=False):
    p = doc.add_heading(text, level=level)
    run = p.runs[0] if p.runs else p.add_run(text)
    run.font.name = 'Calibri'
    run.font.bold = True
    if color:
        run.font.color.rgb = RGBColor(*bytes.fromhex(color))
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p

def body(text, bold=False, italic=False, space_after=6):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name  = 'Calibri'
    run.font.size  = Pt(11)
    run.font.bold  = bold
    run.font.italic = italic
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_table(headers, rows, header_color='1F4E79'):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        run = cell.paragraphs[0].runs[0]
        run.font.bold  = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size  = Pt(10)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(cell, header_color)

    # Data rows
    for ri, row in enumerate(rows):
        tr = table.rows[ri + 1]
        bg = 'DEEAF1' if ri % 2 == 0 else 'FFFFFF'
        for ci, val in enumerate(row):
            cell = tr.cells[ci]
            cell.text = str(val)
            run = cell.paragraphs[0].runs[0]
            run.font.size = Pt(10)
            set_cell_bg(cell, bg)

    doc.add_paragraph()  # spacer

# ═══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_paragraph()
doc.add_paragraph()

title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title_p.add_run('AI-POWERED REVENUE FORECASTING AGENT SYSTEM')
tr.font.name  = 'Calibri'
tr.font.size  = Pt(20)
tr.font.bold  = True
tr.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

sub_p = doc.add_paragraph()
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = sub_p.add_run('Mid-Year Review Report')
sr.font.name  = 'Calibri'
sr.font.size  = Pt(14)
sr.font.italic = True
sr.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

doc.add_paragraph()

for label, value in [
    ('Prepared by', 'Hariharan Balaji'),
    ('Organization', 'o9 Solutions'),
    ('Date', 'June 2026'),
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lr = p.add_run(f'{label}: ')
    lr.font.name = 'Calibri'
    lr.font.size = Pt(12)
    lr.font.bold = True
    vr = p.add_run(value)
    vr.font.name = 'Calibri'
    vr.font.size = Pt(12)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# ABSTRACT
# ═══════════════════════════════════════════════════════════════════════════════
heading('ABSTRACT', level=1, color='1F4E79')

paras = [
    ("Revenue forecasting accuracy is a critical challenge in supply chain and retail planning. "
     "This project designs and develops an AI-powered agentic system capable of autonomously "
     "analyzing large-scale revenue data, generating time series forecasts, and evaluating "
     "forecast accuracy using industry-standard metrics."),

    ("The system ingests a North America (NA) retail revenue dataset comprising 276,577 rows "
     "across 10 dimensions — including location, channel, product planning level, and monthly "
     "time periods spanning July 2021 to December 2025. Using a multi-agent orchestration "
     "framework built on the OpenAI Agent SDK, the system automatically identifies the forecast "
     "horizon start point (July 2024), trains forecasting models on historical statistical "
     "actuals, and generates forward-looking revenue projections."),

    ("The forecasting engine employs Holt-Winters Exponential Smoothing with a damped trend "
     "component, with a fallback to Simple Moving Average when training data is insufficient. "
     "Forecast accuracy is measured using two complementary metrics: Mean Absolute Percentage "
     "Error (MAPE) and Weighted MAPE (WMAPE). WMAPE results from the existing Final Revenue "
     "Forecast stood at 12.49% for the United States of America and 35.4% for Canada, "
     "indicating good accuracy for the US market and a need for improvement in the Canada "
     "market. The comparison study confirms that the existing enterprise forecast outperforms "
     "the statistically generated baseline for both locations, providing a clear benchmark "
     "for future model improvement."),

    ("The system's modular architecture supports extension to additional dimensions including "
     "channel-level and product-planning-level forecasting, and is designed to integrate into "
     "production planning workflows at o9 Solutions."),
]
for text in paras:
    body(text, space_after=8)

# Signature block
doc.add_paragraph()
sig_table = doc.add_table(rows=4, cols=2)
sig_table.style = 'Table Grid'
labels = [
    ('Signature of the Employee', 'Signature of the Supervisor'),
    ('Name: Hariharan Balaji', 'Name: ___________________'),
    ('Date: June 2026', 'Date: ____________________'),
    ('Place: ________________', 'Place: ___________________'),
]
for ri, (left, right) in enumerate(labels):
    sig_table.rows[ri].cells[0].text = left
    sig_table.rows[ri].cells[1].text = right
    for ci in range(2):
        run = sig_table.rows[ri].cells[ci].paragraphs[0].runs[0]
        run.font.size = Pt(10)
        if ri == 0:
            run.font.bold = True

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – SYSTEM ARCHITECTURE & MODULES
# ═══════════════════════════════════════════════════════════════════════════════
heading('1. SYSTEM ARCHITECTURE & MODULES', level=1, color='1F4E79')

body('The system is composed of the following major modules:', bold=True)

modules = [
    '(a) Data Ingestion & Preparation Module',
    '(b) Forecast Horizon Identification Module',
    '(c) Time Series Forecasting Engine',
    '(d) MAPE / WMAPE Calculation Module',
    '(e) Forecast Comparison & Recommendation Module',
    '(f) Multi-Agent Orchestration Layer',
    '(g) Output & Reporting Module',
]
for m in modules:
    p = doc.add_paragraph(m, style='List Bullet')
    p.runs[0].font.size = Pt(11)

doc.add_paragraph()
heading('Module Descriptions', level=2, color='2E74B5')

module_details = [
    ('a) Data Ingestion & Preparation Module',
     'Loads the source CSV file (Rev_NA.csv) containing 276,577 rows of North America retail '
     'revenue data. Parses the Time.[Retail Planning Month] column (format: Jul-21) into '
     'datetime objects, sorts records by location and time, and validates data completeness. '
     'The dataset covers 54 monthly periods, 75 sales channels, 250 product planning levels, '
     'and 2 locations (USA and Canada).'),

    ('b) Forecast Horizon Identification Module',
     'Automatically identifies the forecast start month for each location by detecting the '
     'first month where Final Revenue Forecast values are present. For both USA and Canada, '
     'this was determined to be July 2024. All data prior to this point is designated as the '
     'training window for model fitting.'),

    ('c) Time Series Forecasting Engine',
     'For each location, builds a time series model on historical Stat Actual Amt values '
     'prior to the forecast start month. The primary algorithm is Holt-Winters Exponential '
     'Smoothing with an additive damped trend, implemented via statsmodels. A Simple Moving '
     'Average (3-period window) serves as the fallback when training data is insufficient '
     'or the model fails to converge.'),

    ('d) MAPE / WMAPE Calculation Module',
     'Computes two forecast accuracy metrics:\n'
     '  MAPE (Mean Absolute Percentage Error): Simple average of absolute percentage errors '
     'across all periods where actuals exist.\n'
     '  WMAPE (Weighted MAPE): Weights each period\'s error by its actual value magnitude, '
     'reducing the influence of low-volume periods.\n'
     '  Formula: WMAPE = Σ|Actual − Forecast| / Σ|Actual| × 100\n'
     'Both metrics are computed at the Location.[Country] granularity.'),

    ('e) Forecast Comparison & Recommendation Module',
     'Compares the MAPE/WMAPE of the system-generated forecast against the existing '
     'enterprise Final Revenue Forecast. Determines and outputs which forecast provides '
     'better accuracy (lower error) for each location, and issues a recommendation.'),

    ('f) Multi-Agent Orchestration Layer',
     'Built on the OpenAI Agent SDK, the orchestration layer coordinates specialized agents '
     '— including a Manager agent, a Data Analysis agent, an EDA agent, and a Code Execution '
     'agent — in a group-chat pattern. Each agent handles a discrete task, and the Manager '
     'routes tasks to the appropriate specialist.'),

    ('g) Output & Reporting Module',
     'Produces structured outputs:\n'
     '  forecast_analysis.csv — MAPE comparison results per location\n'
     '  WMape_by_Location.csv — WMAPE results per location\n'
     '  forecast_summary.txt — Human-readable summary with methodology, results, and recommendation'),
]

for title, detail in module_details:
    p = doc.add_paragraph()
    bold_run = p.add_run(title + '\n')
    bold_run.font.bold = True
    bold_run.font.size = Pt(11)
    bold_run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    body_run = p.add_run(detail)
    body_run.font.size = Pt(11)
    p.paragraph_format.space_after = Pt(10)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – FUNCTIONAL DESCRIPTION
# ═══════════════════════════════════════════════════════════════════════════════
heading('2. FUNCTIONAL DESCRIPTION', level=1, color='1F4E79')

body('The end-to-end data flow is as follows:', bold=True)

steps = [
    'Input: Raw revenue CSV (Rev_NA.csv) with actuals, forecasts, and baseline forecasts across location, channel, product, and time dimensions.',
    'Preparation: Time parsing, sorting, and null handling applied. Data split by location.',
    'Training Window: For each location, all rows where Month < Forecast_Start_Month form the training set.',
    'Model Fitting: Exponential Smoothing fitted on aggregated monthly Stat Actual Amt values.',
    'Forecast Generation: Model projects revenue for the forecast horizon (July 2024 – December 2025).',
    'Accuracy Evaluation: Generated forecast and existing Final Revenue Forecast both compared against realized actuals using MAPE and WMAPE.',
    'Comparison & Output: Lower-error forecast declared the better model; results written to output files.',
]
for i, step in enumerate(steps, 1):
    p = doc.add_paragraph(style='List Number')
    p.add_run(step).font.size = Pt(11)

doc.add_paragraph()
heading('Key Interface Points', level=2, color='2E74B5')

add_table(
    headers=['Interface', 'Description'],
    rows=[
        ['Input CSV', 'generated_code/Input/Rev_NA.csv — source revenue data'],
        ['Agent Orchestration', 'OpenAI Agent SDK group-chat with Manager, Analyst, EDA, and Executor agents'],
        ['Forecasting Library', 'statsmodels.tsa.holtwinters.ExponentialSmoothing'],
        ['Data Processing', 'pandas, numpy'],
        ['Output Files', 'CSV and TXT reports in generated_code/Output/'],
    ]
)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – TECHNICAL SPECIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════
heading('3. TECHNICAL SPECIFICATIONS', level=1, color='1F4E79')

add_table(
    headers=['#', 'Parameter', 'Specification'],
    rows=[
        ['1',  'Dataset',              'Rev_NA.csv — North America Retail Revenue'],
        ['2',  'Dataset Size',         '276,577 rows × 10 columns (130 MB)'],
        ['3',  'Time Granularity',     'Monthly (54 periods: Jul-21 to Dec-25)'],
        ['4',  'Locations',            'USA, Canada'],
        ['5',  'Channels',             '75 unique MPU Level 3 channels'],
        ['6',  'Products',             '250 product planning levels'],
        ['7',  'Forecast Start',       'July 2024 (auto-detected for both locations)'],
        ['8',  'Forecasting Method',   'Holt-Winters Exponential Smoothing (damped trend)'],
        ['9',  'Fallback Method',      'Simple Moving Average (3-period window)'],
        ['10', 'Accuracy Metrics',     'MAPE, WMAPE'],
        ['11', 'WMAPE — USA',          '12.49%'],
        ['12', 'WMAPE — Canada',       '35.4%'],
        ['13', 'Agent Framework',      'OpenAI Agent SDK (multi-agent group-chat)'],
        ['14', 'Language',             'Python 3.x'],
        ['15', 'Libraries',            'pandas, numpy, statsmodels'],
        ['16', 'Output Formats',       'CSV, TXT'],
        ['17', 'Benchmark Result',     'Existing Final Revenue Forecast outperforms generated forecast for both locations'],
    ]
)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – DESIGN CONSIDERATIONS
# ═══════════════════════════════════════════════════════════════════════════════
heading('4. DESIGN CONSIDERATIONS', level=1, color='1F4E79')

considerations = [
    ('Modularity',
     'Each pipeline step (data prep, forecast identification, model fitting, MAPE calculation) '
     'is implemented as an independent function, enabling isolated testing and reuse.'),
    ('Fallback Robustness',
     'The system gracefully degrades from Exponential Smoothing to Moving Average when training '
     'data is insufficient, ensuring coverage for all locations.'),
    ('Zero-value Handling',
     'MAPE calculation explicitly excludes rows where actual = 0 to avoid division errors and '
     'misleading error values.'),
    ('Multi-Agent Architecture',
     'Separating concerns across specialized agents (Manager, EDA, Analyst, Executor) mirrors '
     'production-grade agentic design patterns and enables parallel task delegation.'),
    ('Extensibility',
     'The location-level aggregation design can be extended to channel-level and product-level '
     'granularity without architectural changes.'),
    ('WMAPE over MAPE',
     'WMAPE was chosen as the primary metric for business reporting as it down-weights '
     'low-revenue periods that would otherwise distort MAPE in a sparse dataset.'),
]

for title, detail in considerations:
    p = doc.add_paragraph(style='List Bullet')
    bold_run = p.add_run(title + ': ')
    bold_run.font.bold = True
    bold_run.font.size = Pt(11)
    detail_run = p.add_run(detail)
    detail_run.font.size = Pt(11)
    p.paragraph_format.space_after = Pt(6)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 – RESULTS & KEY FINDINGS
# ═══════════════════════════════════════════════════════════════════════════════
heading('5. RESULTS & KEY FINDINGS', level=1, color='1F4E79')

add_table(
    headers=['Location', 'Forecast Start', 'WMAPE (Existing Forecast)', 'MAPE (Generated Forecast)', 'Better Forecast'],
    rows=[
        ['USA',    'July 2024', '12.49%',   'Very High', 'Existing Forecast'],
        ['Canada', 'July 2024', '35.4%',    'Very High', 'Existing Forecast'],
    ]
)

body('Key Observations:', bold=True)
observations = [
    'The existing enterprise Final Revenue Forecast significantly outperforms the statistically generated baseline for both locations.',
    'USA forecast accuracy (WMAPE 12.49%) is within the "good" range (10–20%).',
    'Canada forecast accuracy (WMAPE 35.4%) is above the acceptable threshold and warrants investigation.',
    'The generated Exponential Smoothing forecast shows high MAPE, indicating the model requires parameter tuning, seasonal decomposition, or a richer feature set to be competitive.',
]
for obs in observations:
    p = doc.add_paragraph(obs, style='List Bullet')
    p.runs[0].font.size = Pt(11)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 – FUTURE PLAN
# ═══════════════════════════════════════════════════════════════════════════════
heading('6. FUTURE PLAN', level=1, color='1F4E79')

add_table(
    headers=['#', 'Phase', 'Timeline', 'Work to be Done', 'Status'],
    rows=[
        ['1', 'Data Exploration & Planning',   'Jan 2026 – Feb 2026', 'Data profiling, EDA, implementation plan',                           'COMPLETED'],
        ['2', 'Agent Framework Setup',          'Feb 2026 – Mar 2026', 'Multi-agent orchestration, Manager/Analyst/Executor agent design',    'COMPLETED'],
        ['3', 'Forecasting Engine (v1)',         'Mar 2026 – Apr 2026', 'Exponential Smoothing implementation, MAPE/WMAPE calculation',        'COMPLETED'],
        ['4', 'Accuracy Benchmarking',          'Apr 2026 – May 2026', 'Comparison of generated vs existing forecast, WMAPE reporting',       'COMPLETED'],
        ['5', 'Model Improvement',              'Jun 2026 – Jul 2026', 'Parameter tuning, ARIMA/Holt-Winters with seasonality, channel WMAPE','IN PROGRESS'],
        ['6', 'Channel & Product Drill-down',   'Jul 2026 – Aug 2026', 'Extend analysis to channel and product planning level granularity',   'PENDING'],
        ['7', 'Production Integration',         'Aug 2026 – Sep 2026', 'Integrate agent pipeline into o9 Solutions planning workflows',       'PENDING'],
        ['8', 'Final Review & Documentation',   'Sep 2026',            'Full system documentation and sign-off',                             'PENDING'],
    ]
)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 – ABBREVIATIONS
# ═══════════════════════════════════════════════════════════════════════════════
heading('7. ABBREVIATIONS', level=1, color='1F4E79')

add_table(
    headers=['Term', 'Expansion'],
    rows=[
        ['API',   'Application Programming Interface'],
        ['ARIMA', 'Autoregressive Integrated Moving Average'],
        ['CSV',   'Comma-Separated Values'],
        ['EDA',   'Exploratory Data Analysis'],
        ['ETS',   'Error-Trend-Seasonality (Exponential Smoothing family)'],
        ['GSA',   'General Sporting Accounts'],
        ['LLM',   'Large Language Model'],
        ['MAPE',  'Mean Absolute Percentage Error'],
        ['MPU',   'Merchandise Planning Unit'],
        ['NA',    'North America'],
        ['SDK',   'Software Development Kit'],
        ['WMAPE', 'Weighted Mean Absolute Percentage Error'],
    ]
)

# ── Save ──────────────────────────────────────────────────────────────────────
output_path = r'c:\Users\hariharan.balaji\Desktop\Personal\Codebase\Agents_openai revised\documentation\mid_year_review.docx'
doc.save(output_path)
print(f'Saved: {output_path}')
